#!/usr/bin/env python3
"""Minimal KiCad 7 schematic/symbol generator.

Writes .kicad_sch files (format 20230121) from a component + net description.
Pin coordinates are read from the real symbol libraries, so wires generated
here land on actual pins rather than on guessed positions.

Only the subset of the file format that this project needs is implemented:
symbols, wires, junctions, local/global labels, no-connects, text and
hierarchical sheets. Symbol mirroring is not supported - use rotations.
"""

from __future__ import annotations

import hashlib
import os
import re

STOCK_LIB_DIR = "/usr/share/kicad/symbols"


# --------------------------------------------------------------------------
# s-expression parsing
# --------------------------------------------------------------------------

_TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|[()]|[^\s()]+')


def parse_sexpr(text: str):
    """Parse an s-expression into nested lists. Strings keep their quotes."""
    stack: list[list] = [[]]
    for tok in _TOKEN.findall(text):
        if tok == "(":
            new: list = []
            stack[-1].append(new)
            stack.append(new)
        elif tok == ")":
            stack.pop()
            if not stack:
                raise ValueError("unbalanced closing paren")
        else:
            stack[-1].append(tok)
    if len(stack) != 1:
        raise ValueError("unbalanced opening paren")
    return stack[0]


def dump_sexpr(node, indent: int = 0) -> str:
    """Render nested lists back to s-expression text."""
    pad = "  " * indent
    if isinstance(node, str):
        return pad + node
    if not node:
        return pad + "()"
    head = node[0]
    if isinstance(head, str) and all(isinstance(c, str) for c in node):
        return pad + "(" + " ".join(node) + ")"
    parts = [pad + "(" + (head if isinstance(head, str) else "")]
    start = 1 if isinstance(head, str) else 0
    for child in node[start:]:
        if isinstance(child, str):
            parts[-1] += " " + child
        else:
            parts.append(dump_sexpr(child, indent + 1))
    parts.append(pad + ")")
    return "\n".join(parts)


def unquote(s: str) -> str:
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return s


def quote(s: str) -> str:
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def find_all(node, tag: str):
    return [c for c in node if isinstance(c, list) and c and c[0] == tag]


def find_one(node, tag: str):
    got = find_all(node, tag)
    return got[0] if got else None


# --------------------------------------------------------------------------
# deterministic UUIDs - same input always yields the same file
# --------------------------------------------------------------------------

def uuid_for(*parts) -> str:
    h = hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


# --------------------------------------------------------------------------
# symbol libraries
# --------------------------------------------------------------------------

class SymbolLib:
    """Loads .kicad_sym files and exposes symbol definitions and pin geometry."""

    def __init__(self):
        self._defs: dict[str, list] = {}      # "Lib:Name" -> symbol s-expr
        self._files: dict[str, str] = {}      # lib nickname -> path

    def add_file(self, nickname: str, path: str) -> None:
        self._files[nickname] = path

    def add_stock(self, *nicknames: str) -> None:
        for nick in nicknames:
            self.add_file(nick, os.path.join(STOCK_LIB_DIR, nick + ".kicad_sym"))

    def _load(self, nickname: str) -> dict[str, list]:
        path = self._files[nickname]
        with open(path, encoding="utf-8") as fh:
            root = parse_sexpr(fh.read())[0]
        return {unquote(s[1]): s for s in find_all(root, "symbol")}

    def get(self, lib_id: str) -> list:
        """Return the symbol definition, renamed to its full "Lib:Name" id."""
        if lib_id in self._defs:
            return self._defs[lib_id]
        nickname, name = lib_id.split(":", 1)
        if nickname not in self._files:
            raise KeyError(f"no library registered for {lib_id!r}")
        table = self._load(nickname)
        if name not in table:
            raise KeyError(f"{name!r} not found in library {nickname!r}")
        sym = _deep_copy(table[name])
        sym[1] = quote(lib_id)
        # Child unit symbols keep their bare names; that is what KiCad writes.
        self._defs[lib_id] = sym
        return sym

    def pins(self, lib_id: str, unit: int = 1) -> dict[str, tuple[float, float, float]]:
        """Map pin number -> (x, y, angle) in symbol coordinates."""
        sym = self.get(lib_id)
        out: dict[str, tuple[float, float, float]] = {}
        for sub in find_all(sym, "symbol"):
            sub_name = unquote(sub[1])
            m = re.search(r"_(\d+)_(\d+)$", sub_name)
            if m and int(m.group(1)) not in (0, unit):
                continue
            for pin in find_all(sub, "pin"):
                at = find_one(pin, "at")
                num = find_one(pin, "number")
                if at is None or num is None:
                    continue
                angle = float(at[3]) if len(at) > 3 else 0.0
                out[unquote(num[1])] = (float(at[1]), float(at[2]), angle)
        return out

    def pin_names(self, lib_id: str, unit: int = 1) -> dict[str, str]:
        """Map pin name -> pin number. Duplicated names keep the first pin."""
        sym = self.get(lib_id)
        out: dict[str, str] = {}
        for sub in find_all(sym, "symbol"):
            m = re.search(r"_(\d+)_(\d+)$", unquote(sub[1]))
            if m and int(m.group(1)) not in (0, unit):
                continue
            for pin in find_all(sub, "pin"):
                nm = find_one(pin, "name")
                num = find_one(pin, "number")
                if nm is None or num is None:
                    continue
                out.setdefault(unquote(nm[1]), unquote(num[1]))
        return out

    def unit_count(self, lib_id: str) -> int:
        sym = self.get(lib_id)
        units = set()
        for sub in find_all(sym, "symbol"):
            m = re.search(r"_(\d+)_(\d+)$", unquote(sub[1]))
            if m:
                units.add(int(m.group(1)))
        units.discard(0)
        return max(units) if units else 1

    def used_defs(self, lib_ids) -> list:
        return [self.get(i) for i in sorted(set(lib_ids))]


def _deep_copy(node):
    if isinstance(node, str):
        return node
    return [_deep_copy(c) for c in node]


# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------

def transform(px: float, py: float, ox: float, oy: float, rot: float) -> tuple[float, float]:
    """Map a symbol-space point onto the sheet.

    Symbol space has +Y up, sheet space has +Y down, so the base offset is
    (px, -py). KiCad then rotates that offset counter-clockwise on screen.
    """
    dx, dy = px, -py
    rot = rot % 360
    if rot == 90:
        dx, dy = dy, -dx
    elif rot == 180:
        dx, dy = -dx, -dy
    elif rot == 270:
        dx, dy = -dy, dx
    return round(ox + dx, 4), round(oy + dy, 4)


def pin_angle(base: float, rot: float) -> float:
    return (base + rot) % 360


# --------------------------------------------------------------------------
# placed components
# --------------------------------------------------------------------------

class Part:
    def __init__(self, sch: "Schematic", lib_id: str, ref: str, value: str,
                 x: float, y: float, rot: float, unit: int, footprint: str,
                 fields: dict, dnp: bool, in_bom: bool):
        self.sch = sch
        self.lib_id = lib_id
        self.ref = ref
        self.value = value
        self.x, self.y, self.rot = float(x), float(y), float(rot)
        self.unit = unit
        self.footprint = footprint
        self.fields = fields or {}
        self.dnp = dnp
        self.in_bom = in_bom
        self._pins = sch.lib.pins(lib_id, unit)
        self._names = sch.lib.pin_names(lib_id, unit)

    def num(self, ref: str) -> str:
        """Resolve a pin name (e.g. "IO14") to its pin number."""
        ref = str(ref)
        return self._names.get(ref, ref)

    def pin(self, number: str) -> tuple[float, float]:
        """Absolute sheet coordinates of a pin, addressed by number or name."""
        number = self.num(number)
        if number not in self._pins:
            raise KeyError(f"{self.ref} ({self.lib_id}) has no pin {number!r}; "
                           f"have {sorted(self._pins)}")
        px, py, _ = self._pins[number]
        return transform(px, py, self.x, self.y, self.rot)

    def pin_numbers(self) -> list[str]:
        return sorted(self._pins, key=lambda n: (len(n), n))


# --------------------------------------------------------------------------
# schematic sheet
# --------------------------------------------------------------------------

FONT = "(effects (font (size 1.27 1.27)))"


class Schematic:
    def __init__(self, lib: SymbolLib, project: str, filename: str,
                 title: str = "", rev: str = "", company: str = "",
                 paper: str = "A3", date: str = ""):
        self.lib = lib
        self.project = project
        self.filename = filename
        self.title = title
        self.rev = rev
        self.company = company
        self.paper = paper
        self.date = date
        self.uuid = uuid_for(project, filename)
        self.parts: list[Part] = []
        self.wires: list[tuple[float, float, float, float]] = []
        self.junctions: list[tuple[float, float]] = []
        self.labels: list[tuple[str, float, float, float, str]] = []
        self.noconns: list[tuple[float, float]] = []
        self.texts: list[tuple[str, float, float, float]] = []
        self.sheets: list[dict] = []
        self.parent_path = "/" + self.uuid   # overridden for child sheets

    # -- placement ---------------------------------------------------------

    def part(self, lib_id: str, ref: str, value: str, x: float, y: float,
             rot: float = 0, unit: int = 1, footprint: str = "",
             fields: dict | None = None, dnp: bool = False,
             in_bom: bool = True) -> Part:
        p = Part(self, lib_id, ref, value, x, y, rot, unit, footprint,
                 fields, dnp, in_bom)
        self.parts.append(p)
        return p

    #: Rails not present in KiCad's stock power library are looked up here.
    power_fallback_lib = "exhaust-mic"

    def power(self, name: str, x: float, y: float, rot: float = 0) -> Part:
        idx = sum(1 for p in self.parts if p.ref.startswith("#PWR"))
        lib_id = f"power:{name}"
        try:
            self.lib.get(lib_id)
        except KeyError:
            lib_id = f"{self.power_fallback_lib}:{name}"
        return self.part(lib_id, f"#PWR{idx:04d}", name, x, y, rot, in_bom=False)

    # -- connectivity ------------------------------------------------------

    def wire(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.wires.append((round(x1, 4), round(y1, 4), round(x2, 4), round(y2, 4)))

    def route(self, *points) -> None:
        """Wire through a list of (x, y) points."""
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            if (x1, y1) != (x2, y2):
                self.wire(x1, y1, x2, y2)

    def elbow(self, a: tuple[float, float], b: tuple[float, float],
              horiz_first: bool = True) -> None:
        """Two-segment orthogonal connection between two points."""
        (x1, y1), (x2, y2) = a, b
        mid = (x2, y1) if horiz_first else (x1, y2)
        self.route(a, mid, b)

    def link(self, a: tuple[float, float], b: tuple[float, float],
             horiz_first: bool = True) -> None:
        """Orthogonal connection between two pin coordinates."""
        self.elbow(a, b, horiz_first)

    def junction(self, x: float, y: float) -> None:
        self.junctions.append((round(x, 4), round(y, 4)))

    def label(self, name: str, x: float, y: float, rot: float = 0) -> None:
        self.labels.append((name, round(x, 4), round(y, 4), rot, "local"))

    def glabel(self, name: str, x: float, y: float, rot: float = 0,
               shape: str = "bidirectional") -> None:
        self.labels.append((name, round(x, 4), round(y, 4), rot, shape))

    def noconn(self, x: float, y: float) -> None:
        self.noconns.append((round(x, 4), round(y, 4)))

    def text(self, body: str, x: float, y: float, size: float = 1.27) -> None:
        self.texts.append((body, round(x, 4), round(y, 4), size))

    # -- convenience: stub a pin out to a label ----------------------------

    def stub(self, part: Part, pin: str, name: str, length: float = 3.81,
             direction: str = "auto", glob: bool = False,
             shape: str = "bidirectional") -> tuple[float, float]:
        """Draw a short wire off a pin and put a label on its far end."""
        px, py = part.pin(pin)
        base = part._pins[part.num(pin)][2]
        ang = pin_angle(base, part.rot)
        if direction != "auto":
            ang = {"right": 180, "left": 0, "up": 270, "down": 90}[direction]
        # A pin drawn at angle 0 extends to the right into the body, so the
        # free end points left; the stub continues away from the body.
        dx, dy = {0: (-1, 0), 90: (0, 1), 180: (1, 0), 270: (0, -1)}[int(ang) % 360]
        ex, ey = px + dx * length, py + dy * length
        self.wire(px, py, ex, ey)
        # Label text must read away from the symbol, not back across it.
        lab_rot = {0: 180, 180: 0, 90: 270, 270: 90}[int(ang) % 360]
        if glob:
            self.glabel(name, ex, ey, lab_rot, shape)
        else:
            self.label(name, ex, ey, lab_rot)
        return ex, ey

    def sheet(self, name: str, filename: str, x: float, y: float,
              w: float = 44.45, h: float = 25.4, page: str = "2") -> None:
        self.sheets.append(dict(name=name, filename=filename, x=x, y=y,
                                w=w, h=h, page=page))

    # -- emit --------------------------------------------------------------

    def _symbol_block(self, p: Part) -> list[str]:
        u = uuid_for(self.filename, p.ref, p.lib_id, p.x, p.y, p.unit)
        rot = int(p.rot) % 360
        lines = [
            f'  (symbol (lib_id {quote(p.lib_id)}) (at {fmt(p.x)} {fmt(p.y)} {rot}) '
            f'(unit {p.unit})',
            f'    (in_bom {"yes" if p.in_bom else "no"}) (on_board yes) '
            f'(dnp {"yes" if p.dnp else "no"})',
            f'    (uuid {u})',
        ]
        hide_ref = p.ref.startswith("#PWR")
        (rx, ry, rj), (vx, vy, vj) = _field_spots(p, rot)
        lines += _prop("Reference", p.ref, rx, ry, hide=hide_ref, justify=rj)
        lines += _prop("Value", p.value, vx, vy,
                       hide=hide_ref and p.value.startswith("#"), justify=vj)
        lines += _prop("Footprint", p.footprint, p.x, p.y, hide=True, size=0.508)
        lines += _prop("Datasheet", p.fields.get("Datasheet", ""), p.x, p.y, hide=True)
        for key, val in p.fields.items():
            if key == "Datasheet":
                continue
            lines += _prop(key, val, p.x, p.y, hide=True)
        for num in p.pin_numbers():
            lines.append(f'    (pin {quote(num)} (uuid {uuid_for(u, "pin", num)}))')
        lines += [
            "    (instances",
            f"      (project {quote(self.project)}",
            f'        (path {quote(self.parent_path)}',
            f'          (reference {quote(p.ref)}) (unit {p.unit})',
            "        )",
            "      )",
            "    )",
            "  )",
        ]
        return lines

    # -- connectivity checks ----------------------------------------------

    @staticmethod
    def _interior(px: float, py: float, seg) -> bool:
        x1, y1, x2, y2 = seg
        if abs(x1 - x2) < 1e-6 and abs(px - x1) < 1e-6:
            return min(y1, y2) + 1e-6 < py < max(y1, y2) - 1e-6
        if abs(y1 - y2) < 1e-6 and abs(py - y1) < 1e-6:
            return min(x1, x2) + 1e-6 < px < max(x1, x2) - 1e-6
        return False

    def _split_wires(self) -> None:
        """Split wires wherever another wire or a pin lands mid-segment.

        KiCad connects wires reliably end-to-end; a segment merely crossed by
        another wire's endpoint is fragile. Splitting first makes every
        intended connection an explicit shared endpoint.
        """
        # Only other wires' endpoints count. Splitting at pin positions or at
        # plain crossings would fuse nets that merely pass over each other.
        breakpoints: set[tuple[float, float]] = set()
        for x1, y1, x2, y2 in self.wires:
            breakpoints.add((x1, y1))
            breakpoints.add((x2, y2))

        out: list[tuple[float, float, float, float]] = []
        for seg in self.wires:
            x1, y1, x2, y2 = seg
            cuts = [p for p in breakpoints if self._interior(p[0], p[1], seg)]
            if not cuts:
                out.append(seg)
                continue
            pts = sorted([(x1, y1)] + cuts + [(x2, y2)])
            if (x1, y1) > (x2, y2):
                pts.reverse()
            for a, b in zip(pts, pts[1:]):
                if a != b:
                    out.append((a[0], a[1], b[0], b[1]))
        self.wires = out

    def _auto_junctions(self) -> list[tuple[float, float]]:
        """Junctions KiCad needs but that are tedious to place by hand.

        A wire ending on the middle of another wire does not connect without
        one, which is an easy way to produce a silently broken netlist.
        """
        ends: dict[tuple[float, float], int] = {}
        for x1, y1, x2, y2 in self.wires:
            for p in ((x1, y1), (x2, y2)):
                ends[p] = ends.get(p, 0) + 1
        found = {p for p, n in ends.items() if n >= 3}
        for p in ends:
            if p in found:
                continue
            for seg in self.wires:
                if self._interior(p[0], p[1], seg):
                    found.add(p)
                    break
        return sorted(found)

    def check(self) -> list[str]:
        """Report wires that run across a pin they were not aimed at.

        Those are almost always accidental shorts introduced while placing
        parts, and they are invisible in a rendered plot.
        """
        problems = []
        pin_pts: dict[tuple[float, float], str] = {}
        for p in self.parts:
            for num in p.pin_numbers():
                pin_pts[p.pin(num)] = f"{p.ref}.{num}"
        for pt, label in pin_pts.items():
            # A pin may legitimately sit at a wire END and still be crossed by
            # a different wire, so do not skip endpoints here.
            for seg in self.wires:
                if self._interior(pt[0], pt[1], seg):
                    problems.append(
                        f"{self.filename}: wire {seg} passes across pin {label} "
                        f"at {pt} - likely an accidental connection")
                    break
        return problems

    def render(self) -> str:
        self._split_wires()
        out = ["(kicad_sch (version 20230121) (generator eeschema)", ""]
        out.append(f"  (uuid {self.uuid})")
        out.append("")
        out.append(f"  (paper {quote(self.paper)})")
        out.append("")
        out.append("  (title_block")
        if self.title:
            out.append(f"    (title {quote(self.title)})")
        if self.date:
            out.append(f"    (date {quote(self.date)})")
        if self.rev:
            out.append(f"    (rev {quote(self.rev)})")
        if self.company:
            out.append(f"    (company {quote(self.company)})")
        out.append("  )")
        out.append("")

        out.append("  (lib_symbols")
        for definition in self.lib.used_defs(p.lib_id for p in self.parts):
            out.append(dump_sexpr(definition, 2))
        out.append("  )")
        out.append("")

        for (x1, y1, x2, y2) in self.wires:
            out.append(f"  (wire (pts (xy {fmt(x1)} {fmt(y1)}) (xy {fmt(x2)} {fmt(y2)}))")
            out.append("    (stroke (width 0) (type default))")
            out.append(f"    (uuid {uuid_for(self.filename, 'w', x1, y1, x2, y2)})")
            out.append("  )")

        all_junctions = sorted(set(self.junctions) | set(self._auto_junctions()))
        for (x, y) in all_junctions:
            out.append(f"  (junction (at {fmt(x)} {fmt(y)}) (diameter 0) (color 0 0 0 0)")
            out.append(f"    (uuid {uuid_for(self.filename, 'j', x, y)})")
            out.append("  )")

        for (x, y) in self.noconns:
            out.append(f"  (no_connect (at {fmt(x)} {fmt(y)}) "
                       f"(uuid {uuid_for(self.filename, 'nc', x, y)}))")

        for (name, x, y, rot, kind) in self.labels:
            just = "left" if rot in (0, 90) else "right"
            u = uuid_for(self.filename, kind, name, x, y)
            if kind == "local":
                out.append(f"  (label {quote(name)} (at {fmt(x)} {fmt(y)} {int(rot)})")
                out.append(f"    (effects (font (size 1.27 1.27)) (justify {just} bottom))")
                out.append(f"    (uuid {u})")
                out.append("  )")
            else:
                out.append(f"  (global_label {quote(name)} (shape {kind}) "
                           f"(at {fmt(x)} {fmt(y)} {int(rot)}) (fields_autoplaced)")
                out.append(f"    (effects (font (size 1.27 1.27)) (justify {just}))")
                out.append(f"    (uuid {u})")
                out.append('    (property "Intersheetrefs" "${INTERSHEET_REFS}" '
                           f'(at {fmt(x)} {fmt(y)} 0)')
                out.append("      (effects (font (size 1.27 1.27)) hide)")
                out.append("    )")
                out.append("  )")

        for (body, x, y, size) in self.texts:
            out.append(f"  (text {quote(body)} (at {fmt(x)} {fmt(y)} 0)")
            out.append(f"    (effects (font (size {size} {size})) (justify left bottom))")
            out.append(f"    (uuid {uuid_for(self.filename, 't', body, x, y)})")
            out.append("  )")

        for p in self.parts:
            out.extend(self._symbol_block(p))

        for sh in self.sheets:
            u = uuid_for(self.project, sh["filename"])
            out.append(f'  (sheet (at {fmt(sh["x"])} {fmt(sh["y"])}) '
                       f'(size {fmt(sh["w"])} {fmt(sh["h"])})')
            out.append("    (stroke (width 0.1524) (type solid))")
            out.append("    (fill (color 0 0 0 0.0000))")
            out.append(f"    (uuid {u})")
            out.append(f'    (property "Sheetname" {quote(sh["name"])} '
                       f'(at {fmt(sh["x"])} {fmt(sh["y"] - 0.7)} 0)')
            out.append("      (effects (font (size 1.524 1.524)) (justify left bottom))")
            out.append("    )")
            out.append(f'    (property "Sheetfile" {quote(sh["filename"])} '
                       f'(at {fmt(sh["x"])} {fmt(sh["y"] + sh["h"] + 1.4)} 0)')
            out.append("      (effects (font (size 1.524 1.524)) (justify left top))")
            out.append("    )")
            out.append("    (instances")
            out.append(f"      (project {quote(self.project)}")
            out.append(f'        (path {quote("/" + self.uuid)} (page {quote(sh["page"])}))')
            out.append("      )")
            out.append("    )")
            out.append("  )")

        out.append("")
        out.append("  (sheet_instances")
        out.append('    (path "/" (page "1"))')
        out.append("  )")
        out.append(")")
        return "\n".join(out) + "\n"

    def write(self, directory: str) -> str:
        path = os.path.join(directory, self.filename)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.render())
        return path


def _field_spots(p: "Part", rot: int):
    """Where to hang Reference and Value so they miss the body and the wires.

    Two-pin parts get their text beside the part; anything larger gets it
    above and below the pin bounding box.
    """
    if p.ref.startswith("#PWR"):
        return (p.x, p.y - 3.81, "center"), (p.x, p.y + 3.81, "center")
    coords = list(p._pins.values())
    span_x = max([abs(c[0]) for c in coords] or [2.54])
    span_y = max([abs(c[1]) for c in coords] or [2.54])
    if len(coords) <= 2:
        if rot in (0, 180):                       # standing part, text beside it
            off = span_x + 2.54
            return ((p.x + off, p.y - 1.27, "left"),
                    (p.x + off, p.y + 1.905, "left"))
        off = span_x + 1.27                        # lying part, text above/below
        return ((p.x, p.y - off, "center"), (p.x, p.y + off, "center"))
    if rot in (90, 270):
        span_y, span_x = span_x, span_y
    off = span_y + 3.81
    return (p.x, p.y - off, "center"), (p.x, p.y + off, "center")


def _prop(name: str, value: str, x: float, y: float, hide: bool = False,
          size: float = 1.27, justify: str = "center") -> list[str]:
    tail = " hide" if hide else ""
    just = "" if justify == "center" else f" (justify {justify})"
    return [
        f"    (property {quote(name)} {quote(value)} (at {fmt(x)} {fmt(y)} 0)",
        f"      (effects (font (size {size} {size})){just}{tail})",
        "    )",
    ]


def fmt(v: float) -> str:
    s = f"{float(v):.4f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"

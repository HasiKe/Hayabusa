#!/usr/bin/env python3
"""Group the KiCad netlist into a BOM CSV.

Usage: build_bom.py <netlist.net> <out.csv>

Prices are deliberately absent - fill them in from a distributor once the
parts are actually sourced.
"""

from __future__ import annotations

import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kigen import parse_sexpr, find_all, find_one, unquote  # noqa: E402


def natural(ref: str):
    m = re.match(r"([A-Za-z#]+)(\d*)", ref)
    return (m.group(1), int(m.group(2) or 0)) if m else (ref, 0)


def main(net_path: str, out_path: str) -> None:
    root = parse_sexpr(open(net_path, encoding="utf-8").read())[0]
    groups: dict[tuple, list] = {}

    for comp in find_all(find_one(root, "components"), "comp"):
        ref = unquote(find_one(comp, "ref")[1])
        if ref.startswith(("#PWR", "#FLG")):
            continue
        value = unquote(find_one(comp, "value")[1])
        fp_node = find_one(comp, "footprint")
        footprint = unquote(fp_node[1]) if fp_node else ""
        extras: dict[str, str] = {}
        fields = find_one(comp, "fields")
        if fields:
            for f in find_all(fields, "field"):
                name = unquote(find_one(f, "name")[1])
                val = unquote(f[2]) if len(f) > 2 else ""
                extras[name] = val
        key = (value, footprint, extras.get("MPN", ""), extras.get("Bestueckung", ""))
        groups.setdefault(key, []).append(ref)

    rows = []
    for (value, footprint, mpn, fit), refs in groups.items():
        refs.sort(key=natural)
        rows.append({
            "Menge": len(refs),
            "Referenzen": " ".join(refs),
            "Wert": value,
            "Footprint": footprint.split(":")[-1],
            "MPN": mpn,
            "Bestueckung": fit or "ja",
        })
    rows.sort(key=lambda r: natural(r["Referenzen"].split()[0]))

    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["Menge", "Referenzen", "Wert",
                                           "Footprint", "MPN", "Bestueckung"])
        w.writeheader()
        w.writerows(rows)

    total = sum(r["Menge"] for r in rows)
    print(f"{out_path}: {len(rows)} Positionen, {total} Bauteile")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

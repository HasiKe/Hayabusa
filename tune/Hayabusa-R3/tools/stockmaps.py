"""Read the stock Hayabusa maps from tune/setup/maps.ods and resample onto Speeduino 16x16 axes."""
import sys, re
from odf.opendocument import load
from odf.table import Table, TableRow
from odf.text import P
from odf.namespaces import TABLENS, OFFICENS

def sheet_rows(fn, sheetname):
    doc = load(fn)
    for sheet in doc.spreadsheet.getElementsByType(Table):
        if sheet.getAttrNS(TABLENS, "name") != sheetname: continue
        out = []
        for row in sheet.getElementsByType(TableRow):
            cells = []
            for c in row.childNodes:
                if c.qname[1] not in ("table-cell", "covered-table-cell"): continue
                rep = int(c.getAttrNS(TABLENS, "number-columns-repeated") or 1)
                v = c.getAttrNS(OFFICENS, "value")
                if v is None:
                    v = " ".join(str(p) for p in c.getElementsByType(P)).strip()
                if rep > 50: rep = 1
                cells.extend([v] * rep)
            while cells and cells[-1] == "": cells.pop()
            out.append(cells)
        return out
    raise KeyError(sheetname)

def num(x):
    try: return float(x)
    except: return None

def fix_rpm_axis(rpms, label):
    """Repair obvious typos (a value that breaks monotonicity by a factor ~10)."""
    fixed = list(rpms)
    for i in range(1, len(fixed)):
        if fixed[i] <= fixed[i-1]:
            cand = fixed[i] * 10
            if fixed[i-1] < cand < (fixed[i+1] if i+1 < len(fixed) else 1e9):
                print(f"  [{label}] Achsen-Tippfehler Zeile {i}: {fixed[i]:g} -> {cand:g}", file=sys.stderr)
                fixed[i] = cand
            else:
                raise ValueError(f"{label}: RPM-Achse nicht monoton bei {fixed[i]}")
    return fixed

def read_block(rows, title_row_idx, ncols, label):
    """rows[title_row_idx] holds the title, next row the load axis, following rows rpm + values."""
    axis = [num(x) for x in rows[title_row_idx+1][1:1+ncols]]
    assert all(a is not None for a in axis), axis
    rpms, grid = [], []
    for r in rows[title_row_idx+2:]:
        if not r or num(r[0]) is None: break
        vals = [num(x) for x in r[1:1+ncols]]
        assert len(vals) == ncols and all(v is not None for v in vals), (label, r[:3])
        rpms.append(num(r[0])); grid.append(vals)
    rpms = fix_rpm_axis(rpms, label)
    return axis, rpms, grid

def stock_maps(fn):
    ve = sheet_rows(fn, "VE_org")
    ign = sheet_rows(fn, "IGN_org")
    # locate titles
    def find(rows, text):
        for i, r in enumerate(rows):
            if r and str(r[0]).strip() == text: return i
        raise KeyError(text)
    tps_axis, ve_rpm, ve_grid = read_block(ve, find(ve, "TPS fuelmap"), 23, "TPS fuelmap")
    iap_axis, iap_rpm, iap_grid = read_block(ve, find(ve, "IAP fuelmap"), 21, "IAP fuelmap")
    ign_axis, ign_rpm, ign_grid = read_block(ign, find(ign, "Ignitionmap"), 23, "Ignitionmap")
    return dict(tps=(tps_axis, ve_rpm, ve_grid), iap=(iap_axis, iap_rpm, iap_grid), ign=(ign_axis, ign_rpm, ign_grid))

def interp1(xs, ys, x):
    if x <= xs[0]: return ys[0]
    if x >= xs[-1]: return ys[-1]
    for i in range(1, len(xs)):
        if x <= xs[i]:
            t = (x - xs[i-1]) / (xs[i] - xs[i-1]); return ys[i-1] + t * (ys[i] - ys[i-1])

def bilinear(load_axis, rpm_axis, grid, load, rpm):
    col = [interp1(load_axis, row, load) for row in grid]   # value at 'load' for each rpm row
    return interp1(rpm_axis, col, rpm)

def resample(load_axis, rpm_axis, grid, new_loads, new_rpms):
    return [[bilinear(load_axis, rpm_axis, grid, l, r) for l in new_loads] for r in new_rpms]

if __name__ == "__main__":
    m = stock_maps(sys.argv[1])
    for k, (ax, rp, g) in m.items():
        print(f"{k}: load axis {ax}\n   rpm {rp[0]:g}..{rp[-1]:g} ({len(rp)} rows), value range {min(map(min,g)):g}..{max(map(max,g)):g}")
    # cross-check against the user's own 16x16 resample sheets
    ve = sheet_rows(sys.argv[1], "VE_org")
    hdr = ve[1]; user_loads = [num(x) for x in hdr[29:45]]
    print("user 16x16 VE loads:", user_loads)
    maxdiff = 0
    for r in ve[2:18]:
        rpm = num(r[28]); vals = [num(x) for x in r[29:45]]
        mine = [bilinear(*m['tps'], l, rpm) for l in user_loads]
        d = max(abs(a-b) for a,b in zip(vals, mine)); maxdiff = max(maxdiff, d)
        if d > 1.5: print(f"  VE rpm {rpm:g}: user {vals}\n            mine {[round(x,1) for x in mine]}")
    print("VE cross-check max |diff| vs user's 16x16:", round(maxdiff,2))
    ing = sheet_rows(sys.argv[1], "ING")
    user_loads2 = [num(x) for x in ing[1][1:17]]
    print("user 16x16 IGN loads:", user_loads2)
    maxdiff = 0
    for r in ing[2:18]:
        rpm = num(r[0]); vals = [num(x) for x in r[1:17]]
        mine = [bilinear(*m['ign'], l, rpm) for l in user_loads2]
        d = max(abs(a-b) for a,b in zip(vals, mine)); maxdiff = max(maxdiff, d)
        if d > 1.5: print(f"  IGN rpm {rpm:g}: user {vals}\n             mine {[round(x,1) for x in mine]}")
    print("IGN cross-check max |diff| vs user's 16x16:", round(maxdiff,2))

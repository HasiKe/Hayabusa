import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from msqinfo import load
vi, bib, c = load(sys.argv[1])
def arr(name):
    v = c[name][0].split()
    return v, c[name][1], c[name][2]
for name in sys.argv[2:]:
    if name not in c: print("MISSING", name); continue
    v, cols, rows = arr(name)
    print(f"--- {name} cols={cols} rows={rows} n={len(v)} units={c[name][4]} page={c[name][5]}")
    cols = int(cols or 1)
    if cols > 1:
        for i in range(0, len(v), cols):
            print("  " + " ".join(f"{float(x):6.1f}" for x in v[i:i+cols]))
    else:
        print("  " + " ".join(f"{float(x):g}" for x in v))

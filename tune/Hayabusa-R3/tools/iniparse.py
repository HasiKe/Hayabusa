import re, sys
def split_top(s):
    """split on commas that are outside quotes and outside {} [] ()"""
    out, cur, depth, q = [], '', 0, False
    for ch in s:
        if ch == '"': q = not q
        if not q:
            if ch in '{[(': depth += 1
            elif ch in '}])': depth -= 1
        if ch == ',' and not q and depth == 0:
            out.append(cur.strip()); cur = ''
        else: cur += ch
    out.append(cur.strip())
    return out
def parse_ini(fn, defines=None):
    """Parse TS ini [Constants] section incl. #if/#else/#endif using given defines (set of true symbols).
    Returns dict page->list of (name, kind, type, offset, rest) and dict name->info, plus pcVariables, plus #define lists."""
    defines = defines or set()
    lines = open(fn, encoding='latin-1').read().splitlines()
    section = None
    stack = [[True, True]]
    consts = {}
    order = []
    page = None
    pages = {}
    defs = {}
    for raw in lines:
        m = re.match(r'\s*#define\s+(\w+)\s*=\s*(.*)', raw)
        if m: defs.setdefault(m.group(1), re.sub(r';(?=(?:[^"]*"[^"]*")*[^"]*$).*$', '', m.group(2)).strip())
    pagesizes = None
    npages = None
    for raw in lines:
        line = re.sub(r';(?=(?:[^"]*"[^"]*")*[^"]*$).*$', '', raw).rstrip()
        s = line.strip()
        if not s: continue
        if s.startswith('#if'):
            m = re.match(r'#if\s+!?\s*(\w+)', s)
            sym = m.group(1) if m else ''
            neg = '!' in s.split(sym)[0]
            val = (sym in defines)
            if neg: val = not val
            parent = stack[-1][0]
            stack.append([parent and val, val]); continue   # [active, any branch taken]
        if s.startswith('#elif'):
            m = re.match(r'#elif\s+!?\s*(\w+)', s); sym = m.group(1) if m else ''
            val = (sym in defines)
            if '!' in s.split(sym)[0]: val = not val
            parent = stack[-2][0]; taken = stack[-1][1]
            stack[-1] = [parent and val and not taken, taken or val]; continue
        if s.startswith('#else'):
            parent = stack[-2][0]; taken = stack[-1][1]
            stack[-1] = [parent and not taken, True]; continue
        if s.startswith('#endif'):
            stack.pop(); continue
        if not stack[-1][0]: continue
        if s.startswith('#define'):
            m = re.match(r'#define\s+(\w+)\s*=\s*(.*)', s)
            if m: defs[m.group(1)] = m.group(2)
            continue
        if s.startswith('#'): continue
        m = re.match(r'\[(\w+)\]', s)
        if m: section = m.group(1); continue
        if section == 'Constants':
            m = re.match(r'pageSize\s*=\s*(.*)', s)
            if m: pagesizes = [int(x) for x in m.group(1).split(',')]; continue
            m = re.match(r'nPages\s*=\s*(\d+)', s)
            if m: npages = int(m.group(1)); continue
            m = re.match(r'page\s*=\s*(\d+)', s)
            if m: page = int(m.group(1)); pages.setdefault(page, []); continue
            m = re.match(r'(\w+)\s*=\s*(scalar|bits|array|string)\s*,\s*(.*)', s)
            if m and page is not None:
                name, kind, rest = m.groups()
                parts = split_top(rest)
                info = dict(name=name, kind=kind, page=page, type=parts[0], offset=parts[1], parts=parts, raw=s)
                if kind == 'bits':
                    info['bitpos'] = parts[2]
                    def expand(tok, depth=0):
                        tok = tok.strip()
                        if tok.startswith('$') and depth < 6:
                            d = defs.get(tok[1:])
                            if d is None: return [tok]
                            out = []
                            for x in re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', d):
                                out.extend(expand(x, depth+1))
                            return out
                        return [tok.strip('"')]
                    opts = []
                    for p in parts[3:]:
                        opts.extend(expand(p))
                    info['options'] = opts
                elif kind == 'array':
                    info['shape'] = parts[2]; info['units'] = parts[3].strip('"') if len(parts)>3 else ''
                    info['scale'] = parts[4] if len(parts)>4 else '1'; info['translate'] = parts[5] if len(parts)>5 else '0'
                    info['lo'] = parts[6] if len(parts)>6 else ''; info['hi'] = parts[7] if len(parts)>7 else ''; info['digits'] = parts[8] if len(parts)>8 else '0'
                elif kind == 'scalar':
                    info['units'] = parts[2].strip('"'); info['scale'] = parts[3] if len(parts)>3 else '1'; info['translate'] = parts[4] if len(parts)>4 else '0'
                    info['lo'] = parts[5] if len(parts)>5 else ''; info['hi'] = parts[6] if len(parts)>6 else ''; info['digits'] = parts[7] if len(parts)>7 else '0'
                if name in consts and name != 'unused':
                    # duplicate name (e.g. different #if branch) -> keep first
                    pass
                consts.setdefault(name, info)
                pages[page].append(info)
                order.append(name)
    return dict(consts=consts, pages=pages, order=order, defs=defs, pagesizes=pagesizes, npages=npages)

if __name__ == '__main__':
    old = parse_ini(sys.argv[1], set(sys.argv[3].split(',')) if len(sys.argv)>3 else set())
    new = parse_ini(sys.argv[2], set(sys.argv[3].split(',')) if len(sys.argv)>3 else set())
    print("old pages:", old['npages'], old['pagesizes']); print("new pages:", new['npages'], new['pagesizes'])
    on = set(old['consts']) - {'unused'}; nn = set(new['consts']) - {'unused'}
    print("only in old:", sorted(on-nn)); print("only in new:", sorted(nn-on))
    print("--- changed definitions (same name) ---")
    for n in sorted(on & nn):
        a, b = old['consts'][n], new['consts'][n]
        if a['raw'] != b['raw'] or a['page'] != b['page']:
            print(f"{n}: p{a['page']} {a['raw']}\n   -> p{b['page']} {b['raw']}")
        if a['kind']=='bits' and a.get('options') != b.get('options'):
            print(f"   OPTIONS old={a.get('options')}\n           new={b.get('options')}")

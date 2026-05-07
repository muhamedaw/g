import os, re
from collections import Counter

scr_dir = r'D:\mods\mods\mods\mohaa mods\_extracted_scr'
files = os.listdir(scr_dir)

spawn_classes = Counter()
player_patterns = Counter()
interesting = []

for fn in files:
    path = os.path.join(scr_dir, fn)
    try:
        txt = open(path, encoding='utf-8', errors='ignore').read()

        for m in re.findall(r'spawn\s+(\w+)', txt, re.I):
            spawn_classes[m] += 1

        if 'getentitylist' in txt.lower(): player_patterns['getentitylist'] += 1
        if 'parm.other' in txt: player_patterns['parm.other'] += 1
        if 'local.player' in txt: player_patterns['local.player'] += 1
        if '$player ' in txt: player_patterns['$player_global'] += 1

        if any(x in txt.lower() for x in ['vehicletank', 'spawntank']):
            interesting.append(('tank', fn))
        if 'huddraw' in txt.lower():
            interesting.append(('hud', fn))
        if 'teleport' in txt.lower() or 'setorigin' in txt.lower():
            interesting.append(('teleport', fn))
        if 'getentitylist' in txt.lower():
            interesting.append(('getentitylist', fn))
        if 'stufftext' in txt.lower():
            interesting.append(('stufftext', fn))

    except:
        pass

print('=== SPAWN CLASSES (top 30) ===')
for k, v in spawn_classes.most_common(30):
    print(f'  {v:4d}x  spawn {k}')

print()
print('=== PLAYER PATTERNS ===')
for k, v in player_patterns.most_common():
    print(f'  {v:4d}x  {k}')

print()
print('=== INTERESTING FILES (top 3 each category) ===')
seen = {}
for cat, fn in interesting:
    if cat not in seen:
        seen[cat] = []
    if len(seen[cat]) < 3:
        seen[cat].append(fn)
for cat, fns in seen.items():
    print(f'  [{cat}]')
    for f in fns:
        print(f'    {f}')

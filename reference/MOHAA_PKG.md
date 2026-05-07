# MOHAA pk3 Packaging Reference

## What is a pk3

A pk3 file is a **renamed ZIP archive** (standard ZIP/DEFLATE).
Place it in `C:\Program Files\MOHAA\main\` to load it.

## File Loading Order

pk3 files load in **alphabetical order** — **higher letter = higher priority** (overrides earlier files).

| Priority | Example | Why |
|---|---|---|
| Lowest | `pak0.pk3` (base game) | Loaded first |
| Higher | `mypatch.pk3` | Overrides base |
| Highest | `zzz-mymod.pk3` | Loaded last, wins all conflicts |

**Use `zzz-` prefix** for your mod to guarantee priority over everything else.

## Internal File Structure

```
mypk3/
├── maps/
│   ├── obj/
│   │   ├── obj_team1.scr           map server script
│   │   ├── obj_team1_precache.scr  loaded for every map load
│   │   └── obj_team2.scr
├── global/
│   ├── myfeature.scr               shared feature script
│   ├── fworks.scr
│   └── fworks/
│       └── v2/
│           ├── fworks1.scr
│           └── fworks2.scr
├── sound/
│   └── items/
│       └── mysound.wav
└── textures/
    └── myshader.tga
```

## Creating a pk3 with Python

```python
import zipfile, os

output = r'C:\Users\Me\Desktop\zzz-mymod-v1.0.pk3'
source_dir = r'C:\mods\mymod_files'

with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            full_path = os.path.join(root, file)
            # arc_path is the path INSIDE the pk3
            arc_path = os.path.relpath(full_path, source_dir)
            zf.write(full_path, arc_path.replace(os.sep, '/'))
```

## Reading/Modifying a pk3 with Python

```python
import zipfile

# Read all files
with zipfile.ZipFile('zzz-mymod.pk3', 'r') as z:
    files = {n: z.read(n) for n in z.namelist()}

# Modify a script
text = files['maps/obj/obj_team1.scr'].decode('utf-8').replace('\r\n', '\n')
text = text.replace('old pattern', 'new pattern')
files['maps/obj/obj_team1.scr'] = text.encode('utf-8')

# Write new pk3
with zipfile.ZipFile('zzz-mymod-v2.pk3', 'w', zipfile.ZIP_DEFLATED) as z:
    for name, data in files.items():
        z.writestr(name, data)
```

## Version Naming Convention

```
zzz-mymod-v1.0.pk3    initial release
zzz-mymod-v1.1.pk3    bugfix
zzz-mymod-v2.0.pk3    major update
```

Keep only ONE version in `main/` when testing. Multiple versions coexist but highest wins per-file.

## Checklist Before Release

- [ ] No duplicate labels in any .scr file
- [ ] `$player` uses NULL guard before `stufftext`
- [ ] Call sites use `thread label` (not `goto`) for background loops
- [ ] Internal loop-continuations use `goto label` (not `thread`)
- [ ] `exec ::prepare` called before `level waittill prespawn` for sound precache
- [ ] All referenced .tik and sound files exist (or are in base game)
- [ ] Test on all maps the mod covers
- [ ] Check game console for `^~^~^ Script Error:` lines

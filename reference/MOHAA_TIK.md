# MOHAA TIKI Files (.tik) Reference

## What is a .tik File

TIKI (Tool Integration Kit) files define entities — models with animations, skins, collision, and scripts.
They're referenced in scripts like `models/static/mytree.tik`.

## Common Model Paths

```
models/static/          static props (trees, barrels, crates)
models/statweapons/     weapon props (mg42, flak88)
models/animate/         animated models
models/vehicles/        vehicles (tiger tank, plane)
models/fx/              effects (fire, sparks, corona)
models/emitters/        particle emitters
models/items/           pickups (binoculars, etc.)
models/weapons/         weapon models
models/player/          player models (*.tik)
models/human/           human characters
```

## Useful Static Props

| Model | Description |
|---|---|
| `models/static/tree_winter_tallpine.tik` | Christmas tree |
| `models/static/corona_reg.tik` | Light corona/glow |
| `models/fx/corona_red.tik` | Red corona |
| `models/static/indycrate.tik` | Wooden crate |
| `models/static/static_nazibanner.tik` | Nazi banner |

## FX Models

| Model | Description |
|---|---|
| `models/fx/grenexp_base.tik` | Grenade explosion |
| `models/fx/dummy.tik` | Invisible anchor point |
| `models/fx/searchlight.tik` | Searchlight beam |
| `models/emitters/fire.tik` | Fire emitter |
| `models/emitters/generic_spark.tik` | Spark emitter |
| `models/emitters/ddaysmoke.tik` | Smoke emitter |

## Spawning Models in Script

```scr
// Spawn a static model
local.tree = spawn StaticModelEntity model models/static/tree_winter_tallpine.tik
local.tree origin (100 200 -500)

// Spawn a script model (can animate)
local.tank = spawn ScriptModel targetname my_tank model models/vehicles/tigertank.tik

// Spawn an emitter
local.fire = spawn StaticModelEntity model models/emitters/fire.tik
local.fire origin self.origin

// Spawn a corona (light glow)
local.glow = spawn StaticModelEntity model models/static/corona_reg.tik
local.glow origin (0 0 50) + self.origin
local.glow setscale 0.5

// Clean up
local.tree remove
```

## cache Command (in _precache.scr)

To prevent "Add cache" warnings, add to `maps/obj/obj_team1_precache.scr`:
```scr
cache models/static/tree_winter_tallpine.tik
cache models/static/corona_reg.tik
cache models/fx/grenexp_base.tik
```

## Surface Control

```scr
$entity surface +nodraw    // hide a surface
$entity surface -nodraw    // show a surface
$entity surface +skin1     // switch to alternate skin (defined in .tik)
$entity surface -skin1     // reset skin
```

## moveanim (ScriptModel only)

```scr
while (1)
{
    $tank moveanim drive
    $tank waittill animdone
}
```

## Common Player Model Names

```
models/player/allied_airborne.tik
models/player/german_panzer_obershutze.tik
models/player/allied_oss.tik          (may not exist in base)
models/player/german_elite_gestapo.tik (may not exist in base)
```

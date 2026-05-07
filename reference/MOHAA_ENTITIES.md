# MOHAA Entity Reference

## Entity Spawn Types

```scr
local.e = spawn ScriptMaster                        // sound alias container
local.e = spawn ScriptModel targetname mymodel      // animated/moveable model
local.e = spawn StaticModelEntity                   // static prop (no animation)
local.e = spawn ScriptOrigin targetname myspot      // invisible origin point
local.e = spawn Camera targetname mycam             // cinematic camera
local.e = spawn Trigger_Use targetname mytrigger    // use-activated trigger
local.e = spawn Trigger_Multiple targetname mytrig  // multi-fire trigger
```

## Spawn with Properties

```scr
local.e = spawn ScriptModel targetname mytank model models/vehicles/tigertank.tik
local.e.origin = (100 200 -500)
local.e.angles = (0 90 0)
local.e health 500
```

## Entity Commands (apply to any entity)

```scr
// Position & rotation
$e.origin              // get/set position vector
$e.angles              // get/set rotation vector
$e angle 90            // set yaw
$e moveto $target 200  // move toward entity at speed

// Physics & collision
$e solid               // enable collision
$e notsolid            // disable collision
$e setsize (-20 -20 0) (20 20 80)   // set bounding box
$e physics_on
$e physics_off

// Visibility
$e hide
$e show
$e surface +nodraw     // hide surface
$e surface -nodraw     // show surface
$e surface +skin1      // alternate skin

// Health & damage
$e health 100
$e nodamage
$e takedamage
$e kill                // kill entity (triggers death)
$e remove              // delete entity from world

// Scale & appearance
$e setscale 1.5
$e setscale (1 1 2)    // non-uniform scale

// Attachment
$e attach $parent "bone_name" 1 (0 0 0)   // attach to bone
$e detach

// Light
$e lightStyle 1        // set light style (0–7 for animated lights)
```

## Trigger Events

```scr
$trigger waittill trigger        // wait for trigger activation
$entity waittill death           // wait for entity death
$entity waittill animdone        // wait for animation end
$entity waittill movedone        // wait for movement end
level waittill prespawn          // before entity spawn
level waittill spawn             // after entity spawn
level waittill ObjectiveDestroyed
level waittill AlliesWin
level waittill AxisWin
$player waittill sounddone
$player waittill player_spawned  // player connects
```

## notify (fire event manually)

```scr
$entity notify "myevent"
// In another thread waiting on it:
$entity waittill myevent
```

## Player Entity

```scr
$player                      // group of ALL players
$player.size                 // connected player count
$player[1]                   // first player
$player[1].origin            // first player's position
$player[1].angles            // first player's view angles
$player.dmteam               // "allies" or "axis"
$player.health               // player health
$player stufftext ("cmd")    // send console command to all players
$player playsound alias      // play sound for all players
$player physics_off          // disable movement (cinematic)
$player physics_on
$player.viewangles = (0 0 0) // force view direction
$player.fireheld             // 1 if fire button held
```

## FX Entity Spawn Pattern

```scr
// Spawn corona light
local.corona = spawn StaticModelEntity model models/static/corona_reg.tik
local.corona.origin = self.origin + (0 0 30)
local.corona setscale 0.3

// Spawn fire emitter
local.fire = spawn StaticModelEntity model models/emitters/fire.tik
local.fire.origin = self.origin

// Clean up after delay
wait 5
local.corona remove
local.fire remove
```

## ScriptMaster (sound alias container)

```scr
local.master = spawn ScriptMaster
local.master aliascache my_snd sound/path.wav soundparms 1.0 0.0 1.0 0.0 300 3000 item loaded maps "dm obj"
// ScriptMaster does NOT need to be removed — aliases persist for map duration
```

## Moving Objects (script_object / ScriptModel)

```scr
// Move entity to another entity's position
$gate moveto $gate_open.origin
$gate waitmove                    // block until done

// Set speed or time before moving
$gate speed 200                   // units/sec
$gate time 2.5                    // seconds to travel

// Directional movement
$flag moveUp 100                  // move up 100 units
$flag moveDown 100
$flag waitmove

// Loop sound during movement
$gate loopsound creak
$gate waitmove
$gate stoploopsound creak

// Reusable move thread with parameters
movegate local.dest local.speed:
    if (local.speed == NIL)
        local.speed = 200
    self speed local.speed
    self moveto local.dest.origin
    self waitmove
end

// Caller (blocks until done):
$gate waitthread movegate $gate_open 150
// Caller (non-blocking):
$gate thread movegate $gate_open 150
```

## Trigger Setup (Script-Spawned)

```scr
// Use trigger — player must press USE key
local.t = spawn Trigger_Use targetname mytrigger
local.t.origin = (100 200 -500)
local.t setsize (-40 -40 -40) (40 40 40)
local.t setthread myaction

// Multi-fire trigger — fires on touch
local.t = spawn Trigger_Multiple targetname myzone
local.t.origin = (100 200 -500)
local.t setsize (-100 -100 -100) (100 100 100)

// Bot-compatible trigger: spawnflags 12
local.t = spawn trigger_multiple "targetname" "btrigger" "spawnflags" "12"
local.t.origin = (100 200 -500)
local.t setsize (-40 -40 0) (40 40 80)
local.t.triggerteam = axis          // which team's bots use it
local.t.weight = 2.0                // bot attraction (negative = repel)
local.t setthread onbot

// Trigger callback label
onbot:
    local.ent = parm.other
    // ... react to bot
end
```

## Trigger Enable / Disable

```scr
$mytrigger nottriggerable    // disable — no more activations
$mytrigger triggerable       // re-enable
```

## Script Origins (position markers)

```scr
// Invisible point in world — useful as movement targets
local.pt = spawn ScriptOrigin targetname myspot
local.pt.origin = (100 200 -500)

// Move entity to origin point
$gate moveto local.pt.origin
```

## Multiplayer Objective Exploder System

Entity keys used in Radiant/editor — connect via `#set N` / `#exploder_set N`:

| Key | Value | Entity | Purpose |
|---|---|---|---|
| `#exploder_set 1` | (number) | script_model (bomb) | Ties all parts together |
| `#set 1` | (same number) | script_object (target/debris/etc.) | Members of the exploder |
| `$explosion_fx` | `models/fx/fx_explosion.tik` | bomb | FX model |
| `$killarea` | targetname of trigger_multiple | bomb | Blast radius trigger |
| `$trigger_name` | targetname of trigger_use | bomb | Player plant trigger |
| `#pause 0.5` | seconds | script_model | Delay before exploder fires |
| `model` | tik path | script_model | Visual model |
| `targetname` | string | any | Name for script reference |

Script integration for exploder:
```scr
// After level waittill spawn
level.targets_to_destroy = 1
level.bomb_damage = 200
level.bomb_explosion_radius = 2048
level.defusing_team = "axis"
level.planting_team = "allies"

$panel_bomb thread global/obj_dm.scr::bomb_thinker
thread allies_win_bomb

allies_win_bomb:
while (level.targets_destroyed < level.targets_to_destroy)
    waitframe
teamwin allies
end
```

## Bot Pathnode Spawn

```scr
// Full bot objective node setup
level.obj_model[108] = spawn trigger_use
level.obj_model[108].targetname = bot_objective
level.obj_model[108].origin = (100 200 -500)
level.obj_model[108].triggerteam = axis
level.obj_model[108].weight = 2.0
level.obj_model[108] setsize (-50 -50 0) (50 50 50)

level.obj_model[109] = spawn info_pathnode
level.obj_model[109].targetname = bot_node
level.obj_model[109].origin = (100 200 -500)
level.obj_model[109].target = bot_objective   // links node to trigger

// Bot stat properties
level.obj_model[109].hearing = 1000
level.obj_model[109].sight = 1000
level.obj_model[109].accuracy = 150
level.obj_model[109].ammo_grenade = 5
```

## Campnode Iteration

```scr
// Iterate all entities with targetname "camper"
for (local.i = 1; local.i <= $camper.size; local.i++)
{
    if ($camper[local.i].tag == sniper_pos)
    {
        $camper[local.i].noaxis = 1      // axis bots won't use this node
        $camper[local.i].noallies = 0    // allies bots can use it
    }
}
```

## Entity Classes Reference

| Class | Purpose |
|---|---|
| `script_model` | Scripted static/animated model (moveable, damageable) |
| `script_object` | Solid objective/prop with logic callbacks |
| `script_origin` | Invisible point marker (positioning, attachment target) |
| `ScriptMaster` | Sound alias container |
| `StaticModelEntity` | Non-interactive visual model |
| `Animate` | Animated model entity (plays skeletal animation) |
| `trigger_multiple` | Area trigger — fires on touch, repeatable |
| `trigger_use` | Use-key trigger — player must press E |
| `trigger_useonce` | Use-key trigger — fires once then removes |
| `func_beam` | Visual beam/line entity |
| `VehicleTank` | Drivable tank with turret slot, hull physics |
| `camera` | Camera entity — can be glued to objects for cinematic/missile views |
| `info_pathnode` | AI bot path node |
| `info_vehiclepoint` | Vehicle AI path node (chained with `.target`) |
| `createListener` | Lightweight data-only entity (no visuals, no physics — store data on it) |

## func_beam — Visual Line / Beam Entity

```scr
// Colored beam between two points
local.beam = spawn func_beam targetname mybeam
local.beam.origin = (100 200 300)               // start point
local.beam endpoint (100 200 400)               // end point (static)
local.beam endpoint $player.origin              // end point tracks entity
local.beam color (0 0 1)                        // RGB 0-1 (blue)
local.beam scale 2                              // beam width
local.beam numsegments 1                        // 1 = straight line
local.beam alpha 0.75
local.beam shader "textures/hud/allies_headicon"  // texture/icon on beam
local.beam activate                             // show beam
local.beam deactivate                           // hide beam
local.beam remove

// func_beam used as icon marker (1 segment, shader = icon texture)
local.marker = spawn func_beam targetname marker
local.marker.origin = $objective.origin + (0 0 98)
local.marker endpoint (local.marker.origin + (0 0 15))
local.marker shader "textures/hud/allies_headicon"
local.marker numsegments 1
local.marker alpha 0.75
local.marker activate
```

## func_beam Extra Options

```scr
local.beam tileshader "textures/hud/allies.tga"  // tile-mapped texture on beam
local.beam minoffset 1.0                          // min beam width offset
local.beam maxoffset 1.0                          // max beam width offset
local.beam scale 25                               // visual width scale

// Dynamic light on entity
$entity light 1 0 0 200     // RGB 0-1, radius — red light radius 200
$entity light 0 0 1 100     // blue light radius 100
$entity light 0 0 0 0       // remove light
```

## VehicleTank Entity

```scr
// Spawn drivable tank
local.tank = spawn VehicleTank model models/vehicles/tigertank.tik targetname mytank origin (X Y Z) angles (0 90 0)
waitframe   // required before accessing properties

local.tank lock
local.tank unlockmovement
local.tank removeondeath 0              // don't auto-remove on death/destruction
local.tank vehiclespeed 220             // max speed
local.tank turnrate 22                  // hull turn rate
local.tank setsize (-294 -128 0) (150 128 115)

// Immunity setup
local.tank immune bash
local.tank immune bullet
local.tank immune explosion
local.tank removeimmune rocket          // CAN be killed by rockets
local.tank removeimmune falling

// Turret access (turret slot 0 = main gun)
local.gun = local.tank queryturretslotentity 0
local.gun turnspeed 32
local.gun setsize (-112 -72 0) (94 64 69)
local.gun solid

// Turret aim + fire
local.gun setaimtarget $player
local.gun waittill ontarget
if (local.gun cansee $player) { local.gun anim fire }
local.gun clearaimtarget

// Custom turret rendering (selective surface show/hide)
local.dup = spawn Animate model local.tank.model
local.dup surface all "+nodraw"                   // hide everything
local.dup surface turret_dtl "-nodraw"            // show only these surfaces
local.dup surface turretbase "-nodraw"
local.dup attach local.tank "turret0" 1 (0 0 0)  // attach to bone tag
```

## spawn camera — Cinematic / Missile Camera

```scr
// Create a follow camera (used for guided missiles, cutscenes)
local.cam = spawn camera origin (X Y Z) targetname missilecam
local.cam bind local.missile           // camera follows missile

// Player sees through this camera
$player glue local.cam                 // player "is" the camera
// To release player:
$player unglue
$player.origin = local.exit_pos
```

## spawn Animate — Skeletal Animation Entity

```scr
// Spawn entity that can play skeletal animations
local.anim_ent = spawn Animate model models/vehicles/tigertank.tik
local.anim_ent.origin = (100 200 -500)
local.anim_ent.angles = (0 90 0)
local.anim_ent surface all "+nodraw"    // start invisible, show selectively
local.anim_ent anim idle               // play named animation
```

## attach — Attach Entity to Bone Tag

```scr
// Attach entity B to a named tag/bone on entity A
local.dup attach local.tank "turret0" 1 (0 0 0)
// Args: parent entity, tag name, use parent angles (1=yes), offset vector

// Used for: custom turret rendering, mounted weapons, decorative models
```

## attachmodel — Attach Visual to Bone

```scr
// Attach model to entity's bone (visual only, no collision)
$player attachmodel "models/static/toilet_short.tik" "Bip01 Head" 1.0 "alattach" 1 -1 -1 -1 -1 ( -30 0 0 )
// args: model, bone, scale, tagname, detach_on_death, [blend args...], offset

// Fix attachment angles
$alattach[$alattach.size].angles = (0 90 90)

// Attach breath steam emitter to player head
$player attachmodel models/emitters/breath_steam_emitter.tik "Bip01 Head" 1 1

// Detach all attachments
$player detachall
```

## glue / unglue — Bind Entity to Parent

```scr
// Trigger follows the grenade entity
local.t = spawn trigger_use ...
local.t glue $grenade 1             // glue with relative offset preserved
// entity now moves with parent

local.t unglue                      // detach from parent

// Nested glue hierarchy (vehicle seats)
local.seat glue local.vehicle 1     // seat follows vehicle
```

## Vehicle System (script_model as vehicle)

```scr
// Spawn vehicle
local.car = spawn script_model model models/vehicles/sdkfz.tik
local.car.origin = (100 200 -500)
local.car.angles = (0 90 0)
local.car solid
local.car.health = 1000

// AI path node chain
local.n1 = spawn script_origin targetname node1
local.n1.origin = (100 200 -500)
local.n2 = spawn script_origin targetname node2
local.n2.origin = (500 200 -500)
local.n1.target = local.n2
local.n2.target = NULL             // end of chain

// Drive vehicle along node chain
local.car drive local.n1 200 100 100 500   // path, speed, accel, closerange, lookahead
local.car waittill drive                   // wait until node reached
local.car nextdrive local.n2              // queue next path segment
local.car modifydrive 150 50 200          // change speed without stopping
local.car stop

// Turret/gun control
local.gun = local.car QueryTurretSlotEntity 0   // get turret entity from slot
local.gun setaimtarget $player                   // aim at player
local.gun waittill ontarget                      // block until aimed
if (local.gun cansee $player) { local.gun anim fire }
local.gun clearaimtarget
local.gun maxyawoffset 120                       // max yaw rotation
local.gun pitchcaps "-50 50 -50"                 // pitch min/max
local.gun turnspeed 30
local.gun pitchspeed 7.5
local.gun viewjitter 7                           // gun sway
local.gun firedelay 2                            // seconds between shots

// Player driver: attach to vehicle slot
$player safeholster 1
$player attachdriverslot 0
$player hide
// Exit: detach and teleport out
$player unglue
$player.origin = local.car.origin + (0 0 80)
$player show
$player safeholster 0
```

## Snow / Particle Emitter Grid Pattern

```scr
// 5x5 grid of emitters following player (snow effect)
snow local.player:
    local.num = 25
    for (local.i = 1; local.i <= local.num; local.i++)
        local.ent[local.i] = spawn emitters/drip.tik
    while (isAlive local.player)
    {
        local.center = local.player.origin + local.player.velocity * 0.4
        local.center[2] = local.player.origin[2] + 400
        local.i = 0
        for (local.x = -2; local.x <= 2; local.x++)
        {
            for (local.y = -2; local.y <= 2; local.y++)
            {
                local.i++
                local.ent[local.i].origin = local.center + (local.x local.y 0) * 250.0
            }
        }
        wait 0.5
    }
    for (local.i = 1; local.i <= local.num; local.i++)
        local.ent[local.i] commanddelay 0.05 remove
end

## Spawnpoint Disable

```scr
// Disable specific spawns by tag
for (local.i = 1; local.i <= $alliesspawn.size; local.i++)
{
    if ($alliesspawn[local.i].tag == closed)
        $alliesspawn[local.i].disablespawn = 1
}
```

# MOHAA Morpheus Script (.scr) Reference

## Variable Scopes

| Scope | Lifetime | Use |
|---|---|---|
| `game.x` | Across maps | Persistent score, flags |
| `level.x` | This map | Round state, counters |
| `local.x` | This thread | Temp vars, loop counters |
| `parm.x` | Thread call | Pass data to spawned thread |
| `self.x` | Object | Entity's own properties |
| `group.x` | Thread group | Shared within group |

## Operators & Precedence (low → high)

```
||  &&  |  ^  &  ==  !=  <  >  <=  >=  +  -  *  /  %
```

Unary: `-  ~  !`   Comparison outputs 0 or 1.

## Control Flow

```scr
if (expr) { ... } else { ... }

while (expr) { ... }

for (local.i = 1; local.i <= 10; local.i++) { ... }

switch (expr)
{
    case 0: ... break
    "label": ... break
    default: ... break
}

try { ... } catch { ... }

break          // exit loop
continue       // next iteration
end            // end thread / label block
```

## Thread System

```scr
thread labelname              // spawn background thread (same self), returns immediately
thread file.scr::labelname    // spawn thread in other file
object thread labelname       // spawn thread, self = object
waitthread                    // wait for ALL spawned threads to finish
goto labelname                // jump in SAME thread (no return — dead code after it)
```

**Rule: call sites use `thread`, loop-continuation inside a label uses `goto`.**

```scr
main:
    thread cheats               // spawn background loop — main continues
    exec global/g2teams.scr     // this line RUNS because thread returned
end

cheats:
    setcvar "cheats" "0"
    if ($player != NULL) { $player stufftext ("set r_lightmap 0") }
    wait 1
    goto cheats                 // loop within THIS thread — no leak
end
```

## NULL / NIL

| Value | Meaning |
|---|---|
| `NULL` | Valid null entity reference |
| `NIL` | Uninitialized — causes Script Error if used |

```scr
if ($player != NULL) { ... }      // safe entity check
if (local.entity)                  // truthy — NIL and NULL are falsy
```

## Arrays

### Constant (read-only, index from 1)
```scr
local.a = hello::world::123
local.a[1]   // hello
local.a[3]   // 123
```

### Hash table (dynamic)
```scr
local.t["key"] = "value"
local.t[1][2] = 99
```

### Targetname array (multiple entities)
```scr
$player[1]         // first player
$player[2]         // second player
$player.size       // total players connected
```

### makeArray block
```scr
local.data = makeArray
row1  val1  val2
row2  val3
endArray
// local.data[1][1] = "row1", [1][2] = "val1"
```

## Events (waittill / notify)

```scr
$entity waittill death           // wait for entity to die
$entity waittill trigger         // wait for trigger activation
level waittill prespawn          // before entities spawn (sound aliases, exec prepare)
level waittill spawn             // after all entities spawn
$player waittill sounddone       // wait for player sound to finish
```

## $player — Group Entity

```scr
$player stufftext ("set r_lightmap 0")   // broadcast console cmd to ALL players
$player.size                              // number of connected players
$player[1]                               // first player entity
if ($player != NULL) { ... }             // NULL when no players connected
```

## Common Entity Commands

```scr
$entity remove              // delete entity
$entity solid               // enable collision
$entity notsolid            // disable collision
$entity nodamage            // take no damage
$entity health 100          // set health
$entity setscale 1.5        // scale model
$entity origin              // get/set position (vector)
$entity angles              // get/set rotation (vector)
$entity angle 90            // set yaw only
$entity moveto $target 200  // move to entity at speed 200
$entity hide                // invisible
$entity show                // visible
$entity surface +nodraw     // hide surface
$entity surface -nodraw     // show surface
$entity surface +skin1      // switch skin
$entity attach $other "bone" 1 (0 0 0)  // attach to bone
$entity anim idle           // play animation
$entity waittill animdone   // wait for animation
$entity playsound alias     // play sound on entity
```

## Spawning Entities

```scr
local.e = spawn ScriptMaster
local.e = spawn ScriptModel targetname mymodel model models/path.tik
local.e = spawn Camera targetname mycam
local.obj = spawn ScriptOrigin targetname myspot
```

## exec vs thread for External Scripts

```scr
exec global/myscript.scr              // run file from top, blocking
exec global/myscript.scr::label       // run specific label, blocking
thread global/myscript.scr::label     // run specific label as background thread
waitthread global/objectives.scr::add_objectives 1 2 "Destroy it." $t.origin
```

## setcvar / getcvar

```scr
setcvar "myvar" "1"
local.val = getcvar (myvar)

// Broadcast cvar set to players
$player stufftext ("set r_lightmap 0")
$player stufftext ("developer 0")
$player stufftext ("spmap m1l1a")     // change map for all players
```

## Level Events & Timing

```scr
wait 1          // wait 1 second
wait 0.1        // wait 100ms
waitframe       // wait 1 server frame
```

## Level Variables (Objective Maps)

```scr
level.script = maps/obj/obj_custom.scr  // register level script

// Round settings (set after level waittill spawn)
level.defusing_team    = "axis"         // team defending bomb
level.planting_team    = "allies"       // team planting bomb
level.targets_to_destroy = 1            // how many objectives needed
level.bomb_damage      = 200
level.bomb_explosion_radius = 2048

level.dmrespawning     = 0              // 0 = no respawn, 1 = respawn
level.dmroundlimit     = 5              // round time limit (minutes)
level.clockside        = axis           // who the clock counts against: axis/allies/kills/draw
level.roundbased       = 1             // 1 if game mode is round-based

// Victory tracking (read-only, managed by obj_dm.scr)
level.targets_destroyed                 // incremented by exploder system

// prespawn → spawn → roundstart execution order:
level waittill prespawn    // sound aliases, exec precache
level waittill spawn       // entity references, thread starts
level waittill roundstart  // round-specific init (if level.roundbased)
```

## Vectors

```scr
local.v = (10 20 30)
local.v[0]   // x = 10
local.v[1]   // y = 20
local.v[2]   // z = 30
local.pos = $player.origin + (0 0 64)   // 64 units above player
( -1 2 3 )   // negative first component needs space after (
```

## Printing / Debugging

```scr
println "debug message"
iprintln "message"           // print to all players (server console)
iprintlnbold "message"       // print bold centered to all players
print local.myvar
```

## Thread Parameters & Return Values

```scr
// Pass parameters — listed after label name in call, named in definition
waitthread movedoor $eastdoor 200       // call with params

movedoor local.door local.speed:       // definition receives them
    if (local.speed == NIL)
        local.speed = 100
    local.door speed local.speed
    local.door moveto $door_open.origin
    local.door waitmove
end

// Return a value
checkflag local.flag:
    local.done = false
    // ... logic ...
    end local.done          // return value to caller

local.result = waitthread checkflag $f  // capture return
if (local.result == true) { ... }
```

## Random & Math

```scr
randomint 10            // integer 0–9
randomint 5 + 1         // integer 1–5
randomfloat 1           // float ~0.001–0.999
randomfloat 1 + 0.5     // float ~0.5–1.5
```

## Player State Queries

```scr
local.player.useheld        // 1 if USE key held, 0 otherwise
local.player.fireheld       // 1 if fire button held
isAlive local.player        // 1 if alive
local.player isTouching $zone   // 1 if player overlaps trigger volume
local.stance = local.player getposition
// getposition returns: "crouching", "standing"
local.move = local.player getmovement
// getmovement returns: "running", "walking", "offground"
```

## Dynamic Entity Targeting

```scr
// Build entity name from strings/vars at runtime
$("trig_" + local.side + "_open") triggerable
$(local.targetname) thread mythread

// Useful for generic functions that work on multiple named entities
```

## String Operations

```scr
local.s = "Hello" + " " + "World"   // concatenation
local.n = "b_" + local.num          // mix string + int
```

## Bitwise Operations

```scr
local.result = local.flags & 8       // check bit 3 set
local.flags = local.flags | 16       // set bit 4
local.flags = local.flags ^ 4        // toggle bit 2
// Powers of 2: 1,2,4,8,16,32,64,128,256,...
```

## Player Commands (Real Mod Patterns)

```scr
// Health
$player heal 25                             // restore N hp
$player hurt 50                             // deal N damage directly
radiusdamage self.origin 200 2048           // AoE damage: point, damage, radius

// Team
$player join_team "allies"                  // move to team
$player join_team "axis"
$player spectator                           // move to spectator
$player.dmteam                              // current team string: "allies"/"axis"

// Weapons
$player takeall                             // strip all weapons + ammo
$player ammo grenade 1                      // give 1 grenade
$player useweaponclass grenade              // switch to weapon class
$player primarydmweapon rifle               // lock weapon: rifle/sniper/smg/mg/heavy

// Animation
$player forcelegsstate CROUCH_IDLE          // force legs anim state

// Identification
$player.entnum                              // unique slot number
$player.netname                             // name string
$player.velocity                            // current velocity vector
```

## Line-of-Sight & Proximity

```scr
if ($entity cansee $player)  { ... }             // basic LOS check
if ($entity cansee $player 90 500)  { ... }      // 90deg FOV, 500 unit range

// Vector math (from real mods)
local.dist = vector_length ($a.origin - $b.origin)
local.dot  = vector_dot local.v1 local.v2
local.norm = vector_normalize local.v
local.fwd  = angles_toforward $player.angles      // forward unit vector
local.left = angles_toleft    $player.angles      // left (strafe-left) unit vector
local.up   = angles_toup      $player.angles      // up unit vector
// Usage: offset forward from player
local.pos = $player.origin + (angles_toforward $player.angles) * 200

// Get bone position
local.eyepos = $player gettagposition "Bip01 Head"

// Manual bounding box check (no trigger needed)
if (local.p.origin[0] > local.bmin[0] && local.p.origin[0] < local.bmax[0] &&
    local.p.origin[1] > local.bmin[1] && local.p.origin[1] < local.bmax[1] &&
    local.p.origin[2] > local.bmin[2] && local.p.origin[2] < local.bmax[2])
{ ... }
```

## Timing & Delayed Execution

```scr
level.time                              // current server time in seconds (float)
commanddelay 0.5 remove                 // schedule command on self after delay
commanddelay 2.0 thread mythread        // delayed thread start
stopwatch 6.0                           // show 6-sec countdown HUD bar on player
```

## Dynamic Thread Routing

```scr
// Build function name from variable and call it
local.type = "bomb"
thread ("setup_" + local.type)          // calls label  setup_bomb:
// Pattern used for: objective type dispatch, map-specific routing
```

## makeArray — Predefined Data Tables

```scr
local.data = makeArray
(100 200 300)
(400 500 600)
"allies"
endArray
// Indexed 1-based: local.data[1], local.data[2], local.data[3]
// local.data.size == 3

// Append to array at runtime (self-expanding):
level.mylist[level.mylist.size] = local.item   // appends to end
```

## Environment & World

```scr
$world.farplane = 4000                          // fog/draw distance
$world.farplane_color = (0.5 0.6 0.8)           // fog color RGB 0-1
setcvar "r_gammabias" "0.3"                     // brightness shift (-1 dark, 1 bright)
setcvar "forcemusic" "sound/music/track.mp3"    // override background music
```

## Entity Physics & Properties

```scr
local.ent solid                         // enable collision
local.ent nodamage                      // make invulnerable
local.ent takedamage                    // re-enable damage
local.ent immune explosion              // resist explosion
local.ent immune bash                   // resist melee
local.ent.velocity = (100 0 300)        // set velocity directly
local.ent immediateremove               // delete instantly (no death anim)
local.ent surface "wheel" "+nodraw"     // hide named mesh surface
local.ent surface "door" "-nodraw"      // show hidden surface
local.ent rendereffects "+viewlensflare"// add lens flare glow
local.ent setscale 1.5                  // resize entity uniformly
```

## Raycasting — trace()

```scr
// trace(start, end) — returns the impact point of a line cast
local.hit = trace (self.origin + (0 0 60))  (self.origin + (0 0 -10000))
// Returns a vector — the first solid surface hit

// Binocular sight → ground impact (used by fire-for-effect artillery):
local.eye  = self gettagposition "Bip01 Head"
local.fwd  = angles_toforward self.viewangles
local.far  = local.eye + local.fwd * 4096       // 4096 unit sight range
local.hit  = trace local.eye local.far           // horizontal hit
local.gnd  = trace (local.hit + (0 0 16)) (local.hit + (0 0 -16384))  // drop to ground
```

## Individual Player Print / HUD Text

```scr
self iprint "You are camping!"          // private message to one player
self iprint "You are camping!" 1        // centered on screen
// iprint vs iprintln: iprint = individual player only, iprintln = all players
self stufftext ("subtitle3 Flight-Time-5")   // show subtitle on player HUD
```

## Give / Take Weapons

```scr
self give models/weapons/colt45.tik          // give weapon
self give models/weapons/thompsonsmg.tik
self give models/weapons/m2frag_grenade.tik
self take models/weapons/steilhandgranate.tik  // remove specific weapon
self takeall                                  // strip everything
self useweaponclass smg                       // switch to weapon class

// Change player model skin
self model "models/player/american_army.tik"
self model "models/player/german_elite_sentry.tik"
```

## Proximity — vector_within

```scr
// Returns 1 if point A is within radius of point B
local.close = vector_within $player.origin self.origin 200
if (local.close) { ... }
// Used for camping detection, proximity triggers without trigger entities
```

## Persistent State via CVars (Cross-Round Data)

```scr
// Store per-player counters that survive death/round restarts
local.key = "score_" + local.player.entnum
setcvar local.key (int(getcvar local.key) + 1)
local.count = int(getcvar local.key)
// Reset: setcvar local.key "0"
```

## Map Changing

```scr
bsptransition nextmap           // change to next map in rotation
bsptransition "dm/mohdm1"       // change to specific map
setcvar "g_gametype" "0"        // set gametype before transition if needed
```

## String Character Indexing

```scr
// Strings work like arrays — index each character
local.s = "hello"
local.s[0]              // "h"
local.s[4]              // "o"
local.s.size            // 5 (number of chars)

// Loop through chars (used for command parsing):
for (local.i = 0; local.i < local.s.size; local.i++)
{
    if (local.s[local.i] == ":")
        local.found = 1
}

// Used in admin systems to split "command:argument" strings
```

## Player Freeze / Unfreeze

```scr
$player freeze              // lock player in place (can't move)
$player unfreeze            // release freeze
$player holster             // holster current weapon
$player dropweap            // drop current weapon to ground
```

## waitexec — Execute File and Return Value

```scr
// Load config data from a .txt or .scr file
local.settings = waitexec global/settings.scr::getcmd "time"
// waitexec blocks until script returns, captures return value
// Used for: settings files, string utility libraries, config loaders
```

## Player Movement Speed Detection (via position delta)

```scr
// Detect if player is moving (no event needed)
check_movement:
    local.old_pos = $player.origin
    wait 1
    local.dx = ($player.origin[0] - local.old_pos[0])
    local.dy = ($player.origin[1] - local.old_pos[1])
    local.speed_sq = local.dx * local.dx + local.dy * local.dy
    if (local.speed_sq > 30000)
        local.moving = 1   // running
    else if (local.speed_sq > 100)
        local.moving = 1   // walking
    else
        local.moving = 0   // standing/camping
end
```

## Printing / Debugging

```scr
println "debug message"
iprintln "message"           // print to all players
iprintlnbold "message"       // bold centered to all players
print local.myvar
// Server debug cvars:
// logfile 1         — enable server log
// sv_showbboxes 4   — visualize trigger bounding boxes
// whereami 1        — print current coordinates
```

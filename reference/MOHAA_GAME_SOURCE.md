# MOHAA Game Source — Verified from Pak0–Pak7 Scripts

All data below is extracted directly from the game's pak files.
Do NOT deviate from these paths, names, and patterns.

---

## Verified Objective Map Structure (from Pak5: maps/obj/obj_teamN.scr)

The EXACT sequence required for any obj map:

```scr
main:
setcvar "g_obj_alliedtext1" "Allied objective line 1"
setcvar "g_obj_alliedtext2" ""
setcvar "g_obj_alliedtext3" ""
setcvar "g_obj_axistext1"   "Axis objective line 1"
setcvar "g_obj_axistext2"   ""
setcvar "g_obj_axistext3"   ""
setcvar "g_scoreboardpic"   "objdm1"   // objdm1..objdm5

level waittill prespawn

    exec global/DMprecache.scr
    level.script = maps/obj/obj_team1.scr
    exec global/ambient.scr obj_team1

level waittill spawn

    level.defusing_team = "axis"        // "axis" or "allies"
    level.planting_team = "allies"      // "allies" or "axis"
    level.targets_to_destroy = 1        // 1 or 2
    level.bomb_damage = 200
    level.bomb_explosion_radius = 2048
    level.dmrespawning = 0              // 0 = round-based, 1 = wave-based
    level.dmroundlimit = 5              // minutes
    level.clockside = axis              // axis, allies, kills, draw

level waittill roundstart              // ← REQUIRED — bomb threads MUST start here

    $my_explosive thread global/obj_dm.scr::bomb_thinker

    thread allies_win_thread
    $my_explosive thread axis_win_timer

end

allies_win_thread:
    while (level.targets_destroyed < level.targets_to_destroy)
        waitframe
    teamwin allies
end

axis_win_timer:
    level waittill axiswin
end
```

**obj_team map names and scoreboardpic values:**
- obj_team1 = "objdm1"  (The Hunt)
- obj_team2 = "objdm2"  (V2 Facility)
- obj_team3 = "objdm5"  (Omaha Beach, script uses obj_team5)
- obj_team4 = "objdm4"  (The Bridge)

---

## Verified obj_dm.scr — Real Bomb Plant Logic (global/obj_dm.scr from Pak0)

The explosive entity MUST have these properties set in the BSP editor or script:
- `self.trigger_name`     — targetname of the trigger_use entity near the bomb
- `self.target`           — the destructible model entity
- `self.exploder_set`     — (optional) exploder group name
- `self.explosion_fx`     — (optional) fx model path
- `self.explosion_sound`  — (optional) sound alias
- `self.killarea`         — (optional) trigger to volumedamage on explosion

**Default values set by bomb_thinker (do NOT override unless intentional):**
```scr
level.bomb_defuse_time = 60   // tenths of a second = 6 real seconds
level.bomb_set_time    = 50   // tenths of a second = 5 real seconds
level.bomb_tick_time   = 45   // seconds until explosion
level.bomb_use_distance = 128  // quake units proximity
level.bombusefov       = 30   // FOV degrees for cansee check
level.bomb_explosion_radius = 1054  // default (override in map script)
level.bomb_damage      = 200  // default (override in map script)
```

**Real bomb sound aliases (built-in, no aliascache needed):**
- `plantbomb`        — one-shot when bomb planted
- `bombtick`         — looping tick during countdown
- `final_countdown`  — looping sound in last 10 seconds
- `dfr_objective_o`  — "objective planted" for allies team
- `den_objective_o`  — "objective planted" for axis team
- `dfr_diffused_d`   — "bomb defused" for allies team
- `den_diffused_d`   — "bomb defused" for axis team

**Real bomb model paths (built-in game assets):**
- `items/pulse_explosive.tik`  — unplanted bomb (pulsing)
- `items/explosive.tik`        — planted/live bomb

**Stopwatch HUD (shown to planting/defusing player):**
```scr
local.player stopwatch (level.bomb_set_time * .1)   // shows timer
local.player stopwatch 0                             // clears timer
```

**Explosion logic (from bomb_explode label):**
```scr
radiusdamage self.origin level.bomb_damage level.bomb_explosion_radius
level.targets_destroyed = level.targets_destroyed + 1
level.bombs_planted --
self.exploded = 1
self.live = 0
```

---

## Verified Weapon Model Paths (from global/DMprecache.scr, Pak0)

These are the ONLY verified multiplayer weapon paths:
```
models/weapons/colt45.tik
models/weapons/p38.tik
models/weapons/silencedpistol.tik
models/weapons/m1_garand.tik
models/weapons/kar98.tik
models/weapons/kar98sniper.tik
models/weapons/springfield.tik
models/weapons/thompsonsmg.tik
models/weapons/mp40.tik
models/weapons/mp44.tik
models/weapons/bar.tik
models/weapons/bazooka.tik
models/weapons/panzerschreck.tik
models/weapons/shotgun.tik
models/weapons/m2frag_grenade.tik
models/weapons/steilhandgranate.tik
```

---

## Verified Player Model Paths (from global/DMprecache.scr, Pak0)

Allied:
```
models/player/allied_airborne.tik
models/player/allied_airborne_fps.tik
models/player/allied_manon.tik
models/player/allied_manon_fps.tik
models/player/allied_oss.tik
models/player/allied_oss_fps.tik
models/player/allied_pilot.tik
models/player/allied_pilot_fps.tik
models/player/american_army.tik
models/player/american_army_fps.tik
models/player/american_ranger.tik
models/player/american_ranger_fps.tik
```

Axis:
```
models/player/german_afrika_officer.tik
models/player/german_afrika_private.tik
models/player/german_elite_gestapo.tik
models/player/german_elite_sentry.tik
models/player/german_kradshutzen.tik
models/player/german_panzer_grenadier.tik
models/player/german_panzer_obershutze.tik
models/player/german_panzer_shutze.tik
models/player/german_panzer_tankcommander.tik
models/player/german_scientist.tik
models/player/german_waffenss_officer.tik
models/player/german_waffenss_shutze.tik
models/player/german_Wehrmacht_officer.tik
models/player/german_Wehrmacht_soldier.tik
models/player/german_winter1.tik
models/player/german_winter2.tik
models/player/german_worker.tik
```

---

## Verified MG42 Script API (from global/mg42.scr, Pak0)

```scr
// Attach to an MG42 entity placed in BSP:
$mg42 thread global/mg42.scr::main $target $path $trigger1 $trigger2 $gunner 100

// Inside mg42.scr, the setup is:
self TurnSpeed 45
self burstFireSettings 10 15 4 5   // burstmin burstmax pausemin pausemax
self tracerFrequency 1
self accuracy 100
self setAimTarget local.target
self startFiring
self stopFiring
```

---

## Verified Weather Script API (from global/weather.scr, Pak0)

Requires BSP entities with these targetnames:
- `weatherF` — flash/lightning models (shown during lightning)
- `weatherR` — roof rain sound emitters
- `weatherI` — interior zone triggers
- `weatherW` — window rain sound emitters
- `wind`     — wind effect models

To activate weather on a map:
```scr
// In main: before prespawn
exec global/weather.scr

// Set weather intensity (0=none, 1=light, 2=moderate, 3=heavy storm)
level.weatherpattern = 2
```

Built-in weather sound aliases (no aliascache needed):
- `rain_ext`    — exterior rain
- `rain_puddle` — rain on puddles
- `rain_int`    — interior rain
- `rain_roof`   — rain on roof
- `rain_window` — rain on window
- `thunder`     — thunder crack

Thunder flash: `setcvar "r_fastsky" "1"` (on) / `"0"` (off)

---

## Verified Earthquake/Jitter (from global/obj_dm.scr, Pak0)

```scr
// Used after explosion to shake player views:
jitter_large local.time:
    if (local.time)
        wait local.time
    waitexec global/earthquake.scr .35 10 0 0
    waitexec global/earthquake.scr .23 6 0 0
    waitexec global/earthquake.scr 1 1 0 0
    waitexec global/earthquake.scr 1.25 .3 0 1
end

// earthquake.scr args: duration magnitude xonly endthis
```

---

## Verified Exploder Script API (from global/exploder.scr, Pak0)

The exploder system handles BSP-placed destructible objects.
```scr
// Activate at spawn:
thread global/exploder.scr::main

// Trigger a specific exploder group by name:
exec global/exploder.scr::explode "groupname"

// Properties on explosive entities (set in BSP editor):
// self.exploder_set  — name of the exploder group
// self.explosion_fx  — path to fx .tik model
// self.explosion_sound — sound alias
// self.killarea      — targetname of kill volume trigger
```

---

## Verified Ambient System (from global/ambient.scr, Pak0)

```scr
// Always called with map name as argument:
exec global/ambient.scr obj_team1

// ambient.scr reads BSP zone triggers for interior/exterior music transitions.
// Music zones: aux1-aux6 (exterior: aux1,3,5 / interior: aux2,4,6)
// Fog/haze adjustments via r_fogenable, r_fogdensity cvars
```

---

## Verified Bomber Script (from global/bomber.scr, Pak0)

```scr
// Flyby bomber (used in obj_team2):
exec global/bomber.scr      // precache (before prespawn)
thread global/bomber.scr::bomb 4    // args: waypoint number (1-7)
thread global/bomber.scr::bomb 5
```

---

## Verified Door Lock Script (from global/door_locked.scr, Pak0)

```scr
exec global/door_locked.scr::lock
// Locks all doors with targetname matching "door_locked*" in BSP
```

---

## Verified Minefield Script (from global/minefield.scr, Pak0)

```scr
thread global/minefield.scr::minefield_setup
// Activates all mine entities (targetname "mine*") placed in BSP
```

---

## Key Rules From Reading Real Game Scripts

1. **`level waittill roundstart`** is REQUIRED between spawn setup and bomb thread start in ALL obj maps.
   Without it, bomb scripts start immediately and bypass round reset logic.

2. **Bomb entity properties** (`self.trigger_name`, `self.target`, etc.) must be set in the BSP
   editor (entity properties), not in script — they're read by obj_dm.scr at init time.

3. **`$(self.trigger_name)`** — dollar-paren dereferences a string variable as an entity reference.
   e.g. if `self.trigger_name = "bomb_trigger"` then `$(self.trigger_name)` = `$bomb_trigger`

4. **`radiusdamage origin damage radius`** — world-space origin, damage points, radius in quake units.

5. **`teamwin allies`** / **`teamwin axis`** — immediately ends the round with that team winning.

6. **`level waittill axiswin`** / **`level waittill allieswin`** — fires when the game engine
   detects the timer ran out (clockside team wins on timeout).

7. **`self.live = 1`** / **`self.live = 0`** — bomb armed/disarmed flag read by bomb_waittill_explode.

8. **`self.exploded = 1`** — set after detonation; scripts can poll this to detect explosion.

9. **`level.targets_destroyed`** — incremented by bomb_explode; the win condition checks this.

10. **`level.bombs_planted`** — tracks currently armed bombs (decremented on defuse or explode).

---

## Verified DM / TDM Map Structure (from Pak files: maps/DM/mohdm1–7.scr)

**DM and TDM use the EXACT SAME map script.** The game mode (FFA vs Teams) is controlled by
the server cvar `g_gametype`, NOT by the map script.

The EXACT boilerplate for any DM/TDM map:

```scr
main:
setcvar "g_obj_alliedtext1" "Map Name Here"
setcvar "g_obj_alliedtext2" ""
setcvar "g_obj_alliedtext3" ""
setcvar "g_obj_axistext1"   ""
setcvar "g_obj_axistext2"   ""
setcvar "g_obj_axistext3"   ""
setcvar "g_scoreboardpic"   "mohdm1"   // mohdm1..mohdm7

    // only start round thread if server is in round-based mode
    if (level.roundbased)
        thread roundbasedthread

    level waittill prespawn

        exec global/DMprecache.scr
        level.script = maps/dm/mohdm1.scr
        exec global/ambient.scr mohdm1

    level waittill spawn

end

//-----------------------------------------------------------------------------

roundbasedthread:

    level waittill prespawn

    level waittill spawn

        level.dmrespawning = 0   // 0 = round-based, 1 = wave-based
        level.dmroundlimit = 5   // minutes
        level.clockside = kills  // DM/TDM always uses "kills" (not axis/allies)

    level waittill roundstart

end
```

**Key differences from obj maps:**
- No `level.defusing_team`, `level.planting_team`, `level.targets_to_destroy`
- No `$my_explosive thread global/obj_dm.scr::bomb_thinker`
- `level.clockside = kills` (obj uses `axis` or `allies`)
- `roundbasedthread` is OPTIONAL — only runs when `level.roundbased` is true (server setting)
- `level.script = maps/dm/mapname.scr` (lowercase `dm`, not `obj`)
- `g_scoreboardpic` values for DM: `mohdm1` through `mohdm7`

**Scoreboard pic values for DM maps:**
- mohdm1 = Southern France
- mohdm2 = Destroyed Village
- mohdm3 = Gibraltar
- mohdm4 = Hunt (crossover with obj)
- mohdm5 = Remagen
- mohdm6 = Stalingrad
- mohdm7 = Algiers (North Afrika)

**HUD index range:** 1–255, all free to use — the engine does NOT reserve any indices.

---

## Game Mode Reference (g_gametype cvar)

The server sets the game mode — the map script does NOT control this:
- `g_gametype 0` = FFA Deathmatch (DM)
- `g_gametype 1` = Team Deathmatch (TDM)
- `g_gametype 2` = Round-based (sets `level.roundbased = 1` — triggers `roundbasedthread`)
- `g_gametype 3` = Objective (OBJ) — requires full obj map script with bomb system

The map script detects round-based mode via `if (level.roundbased)` only.

---

## Verified Player Iteration (from 204 real mods)

`$player` is a **global ARRAY** — NOT a single player reference.
- `$player.size`  — number of currently connected players
- `$player[i]`   — player entity at index i (1-based)
- `$player`      — used in single-player context or as the group; in MP always index with [i]

**Standard loop to affect all players:**
```scr
for (local.i = 1; local.i <= $player.size; local.i++)
{
    local.p = $player[local.i]
    if (local.p != NULL)
    {
        // do something to local.p
    }
}
```

**Real example — give all players a weapon:**
```scr
for (local.i = 1; local.i <= $player.size; local.i++)
{
    if ($player[local.i] != NULL && $player[local.i].ingame)
    {
        $player[local.i] takeall
        $player[local.i] give models/weapons/thompsonsmg.tik
    }
}
```

**`parm.other`** — the specific player who triggered an event (E key, walked into trigger, etc.)
**`self`** — the entity the thread is running on (use for per-player threads)

---

## Verified Spawn Classes (from 1987 mod scripts)

All classes usable with the `spawn` command:

| Class | Use |
|---|---|
| `script_model` | Visible object with model — most common |
| `script_object` | Basic entity, no model |
| `script_origin` | Invisible anchor/position point |
| `trigger_multiple` | Reusable proximity trigger (players walk through) |
| `trigger_use` | E-key interaction trigger |
| `trigger_once` | One-shot trigger |
| `trigger_hurt` | Damages anything inside it |
| `trigger_push` | Pushes players |
| `TriggerAll` | Trigger that fires for all entities (used in KOTH zones) |
| `func_beam` | Visual laser beam |
| `func_camera` | Camera entity |
| `func_rotatingdoor` | Rotating door |
| `func_rain` | Rain effect entity |
| `info_player_deathmatch` | DM spawn point |
| `info_player_axis` | Axis spawn point |
| `info_player_allied` | Allied spawn point |
| `info_player_intermission` | Camera position for end-of-round |
| `info_splinepath` | Waypoint for path following |
| `info_vehiclepoint` | Vehicle waypoint |
| `trigger_camerause` | Camera trigger |
| `trigger_multipleall` | Multi-trigger for all entities |
| `trigger_useonce` | Single-use E-key trigger |
| `trigger_clickitem` | Click/item trigger |
| `DM_Manager` | Deathmatch game manager entity |

**Setting trigger size and thread:**
```scr
local.zone = spawn trigger_multiple
local.zone.origin = ( 0 0 0 )
local.zone setsize ( -100 -100 0 ) ( 100 100 80 )  // mins then maxs, relative to origin
local.zone setthread myzone_handler                 // label to call when triggered
```

**func_beam (laser beam) setup:**
```scr
local.beam = spawn func_beam
local.beam.origin = self.origin
local.beam minoffset 0.0
local.beam maxoffset 0.0
local.beam color ( 1 0 0 )    // RGB
local.beam alpha 0.4
```

---

## Verified Player Commands (from real mods)

Commands that can be called ON a player entity:

```scr
local.p = $player[local.i]

local.p stufftext "say hello"           // send console command to that player's client
local.p stufftext ("alias x say " + local.msg)  // dynamic alias
local.p iprint "Private message"        // print message to that player only
local.p iprint "Centered" 1             // centered print
local.p addkills 5                      // add 5 kills to player's score
local.p tele ( 100 200 300 )            // teleport player to world coordinates
local.p.origin = ( 100 200 300 )        // also works for teleport
local.p takeall                         // remove all weapons
local.p give models/weapons/thompsonsmg.tik  // give weapon
local.p model "models/player/american_army.tik"  // change player model
local.p damage $world 100               // deal 100 damage to player (from world)
local.p kill                            // instant kill
local.p heal 100                        // heal player (if supported)
local.p.dmteam                          // read team: "allies", "axis", "spectator", "freeforall"
local.p.ingame                          // 1 if player is in the game (not spectating)
```

**Per-player individual HUD (`ihuddraw` — different from global `huddraw`):**
```scr
// ihuddraw draws on ONE player's screen only — call as: player ihuddraw_* index ...
self ihuddraw_align  10 left bottom
self ihuddraw_font   10 "facfont-20"
self ihuddraw_rect   10 5 -30 200 20
self ihuddraw_color  10 0 1 0
self ihuddraw_alpha  10 1.0
self ihuddraw_string 10 ( "Score: " + self.myscore )
```

**Global HUD (`huddraw` — shows on ALL players' screens):**
```scr
huddraw_virtualsize 50 1
huddraw_font        50 "facfont-20"
huddraw_rect        50 5 -5 300 20
huddraw_color       50 0.8 0.7 0.2
huddraw_alpha       50 1.0
huddraw_string      50 ( "Time left: " + local.timeleft )
```

---

## Verified Proximity & Trigger Commands

```scr
// Check if two entities are touching:
if (local.zone istouching local.player) { ... }

// Vector-based proximity (no trigger entity needed):
if (vector_within local.player.origin self.origin 200) { ... }

// Trigger waittill (blocks thread until trigger fires):
local.zone waittill trigger
local.player = parm.other    // who triggered it
```

---

## Verified Working Teleporter Pattern (from real mods)

```scr
// Setup — create a trigger zone at origin, teleport player to destination
make_teleporter local.origin local.dest:
    local.tele = spawn trigger_multiple
    local.tele.origin = local.origin
    local.tele setsize ( -30 -30 0 ) ( 30 30 60 )
    local.tele setthread teleporter_action
    local.tele.dest = local.dest
end

teleporter_action:
    local.player = parm.other
    local.player tele self.dest      // tele takes a vector
end
```

---

## Verified King of the Hill Pattern (from real mods)

```scr
koth_main:
    level.hill_origin = ( 748 1556 24 )
    local.zone = spawn TriggerAll
    local.zone.origin = level.hill_origin
    local.zone setsize ( -230 -230 0 ) ( 230 230 50 )
    local.zone targetname hilltrig

    while (1)
    {
        $hilltrig waittill trigger
        local.king = parm.other

        while ( isAlive local.king && $hilltrig istouching local.king )
        {
            wait 1
            local.king addkills 1
        }
    }
end
```

---

## Common Broken Patterns Found in Real Mods (DO NOT copy these)

**1. No NULL check on player array elements — CRASHES:**
```scr
// BAD:
local.p = $player[local.i]
local.p stufftext "command"   // crashes if slot is empty

// GOOD:
if ($player[local.i] != NULL)
{
    local.p = $player[local.i]
    local.p stufftext "command"
}
```

**2. Thread spawned every frame inside loop — causes runaway threads:**
```scr
// BAD — spawns a new thread every frame per player:
while (1)
{
    for (local.i = 1; local.i <= $player.size; local.i++)
        $player[local.i] thread mythinker
    waitframe
}

// GOOD — use a flag to start thread only once per player:
while (1)
{
    for (local.i = 1; local.i <= $player.size; local.i++)
    {
        if ($player[local.i] != NULL && !$player[local.i].thinker_started)
        {
            $player[local.i].thinker_started = 1
            $player[local.i] thread mythinker
        }
    }
    wait 1
}
```

---

## Verified ubersound.scr — Global Sound System (from real mods)

`ubersound/ubersound.scr` is loaded automatically by the MOHAA engine on EVERY map from ANY pk3.
It is the global sound alias registry. To register sounds that work on all maps, put them here.

**File location inside pk3:** `ubersound/ubersound.scr`
**Must start with:** `settiki none`

```scr
settiki none

aliascache my_sound sound/mymod/mysound.wav soundparms 1.0 0.0 1.0 0.0 300 3000 auto loaded maps "dm obj"
```

**All valid sound channels (from real ubersound.scr documentation):**
| Channel | Priority | Description |
|---|---|---|
| `auto` | 0 lowest | General sounds — plays if hardware channel available, never overrides |
| `body` | 1 | Body movement sounds (impacts, equipment jingles) |
| `item` | 2 | Item/equipment sounds, also used for weapon reload |
| `weaponidle` | 3 | Constant weapon hum sounds |
| `voice` | 4 | Vocal sounds (pain, death, combat yells) — lower priority dialog |
| `local` | 5 | Omni-directional sounds (rain, ambient) — no 3D spatialization |
| `weapon` | 6 | Weapon firing sounds |
| `dialog_secondary` | 7 | Lower priority dialog with subtitle |
| `dialog` | 8 | Primary character dialog with subtitle |
| `menu` | 9 | Menu UI sounds |

**Map filter strings:** `"dm"` = all DM maps, `"obj"` = all obj maps, `"m"` = all SP maps, `"train"` = training

---

## Verified Death Detection & Player Events (from real mods)

```scr
// Detect when an entity (player, vehicle, NPC) dies — blocks thread until death:
self waittill death

// Pattern — run cleanup when entity dies:
watch_player_death:
    self waittill death
    // self is now dead — run cleanup
    self.mymod_active = 0
    local.body = spawn script_model
    local.body model self.model
    local.body.origin = self.origin
end

// Detect player respawn after death (blocks until next spawn):
self waittill respawn

// Check if entity is alive:
if (isAlive local.player) { ... }

// Force a player to respawn immediately:
local.player respawn
```

---

## Verified Force Team Command (from real mods)

Team is forced by sending a client console command via stufftext:
```scr
// Force player to a specific team:
local.player stufftext "join_team allies"
local.player stufftext "join_team axis"
local.player stufftext "join_team spectator"

// Check current team:
if (local.player.dmteam == "allies") { ... }
if (local.player.dmteam == "axis") { ... }
if (local.player.dmteam == "spectator") { ... }
if (local.player.dmteam == "freeforall") { ... }   // DM mode
```

---

## Verified Advanced Player Commands (from real mods)

```scr
local.p = $player[local.i]

// Damage & kill:
local.p hurt 50                  // deal 50 damage to player
local.p hurt 10000               // instant kill via damage
local.p kill                     // instant kill (no damage, just kill)

// Weapon management:
local.p weapnext                 // cycle to next weapon
local.p weapdrop                 // drop current weapon
local.p safeholster 1            // holster weapon safely

// Player height:
local.p modheight stand          // force standing height
local.p modheight duck           // force crouching height

// Entity number (unique ID per player):
local.id = local.p.entnum        // integer, unique per entity

// Chat commands:
local.p stufftext "say message"              // global chat
local.p stufftext "teamsay message"         // team-only chat
local.p stufftext "sayteam message"         // same as teamsay
```

---

## Verified Advanced func_beam Properties (from real mods)

```scr
// Full func_beam setup with all properties:
local.beam = spawn func_beam origin ( X Y Z ) endpoint ( X2 Y2 Z2 )
local.beam targetname "mybeam"
local.beam numsegments 40        // number of segments (more = smoother curve)
local.beam maxoffset 20          // random offset per segment (lightning effect)
local.beam alpha 0.7
local.beam color ( 0.7 0.7 1 )   // R G B
local.beam scale 8.0             // beam width
local.beam activate              // make visible/active
local.beam svflags "+broadcast"  // broadcast to all clients (REQUIRED for MP visibility)

// Animate alpha over time (fade out):
for (local.it = 1; local.it >= 0; local.it -= 0.1)
{
    local.beam alpha local.it
    waitframe
}
local.beam remove
```

---

## Verified World Commands (from real mods)

```scr
// Far plane (fog/view distance):
$world farplane 5000                         // set view distance in units
$world farplane_color ( 0.039 0.039 0.039 ) // R G B fog color (dark = night)
$world farplane_color ( 0.99 0.99 0.99 )    // white = lightning flash

// Spawn an FX tik directly:
local.fx = spawn "fx/scriptbazookaexplosion.tik"
local.fx.origin = local.pos
local.fx setsize ( -150 -150 -150 ) ( 150 150 150 )
local.fx.scale = 1
local.fx light 1 0 0 75    // R G B radius — dynamic light
local.fx anim start
local.fx notsolid
// ... later:
local.fx anim stop
local.fx remove
```

---

## Verified Vehicle System (from real mods)

```scr
// Spawn a drivable vehicle:
local.tank = spawn models/vehicles/tigertank.tik
local.tank.origin = ( X Y Z )
local.tank.angles = ( 0 90 0 )
local.tank.gun = local.tank queryturretslotentity 0   // get turret entity

// Player enters vehicle:
self.driver = parm.other                 // player who triggered entry
self.driver safeholster 1                // put away weapon
self.driver hide                         // hide player model
self.driver nodamage                     // player takes no damage
self.driver notsolid                     // no collision while driving
self attachdriverslot 0 self.driver      // attach player as driver

// Each frame — copy player view:
self.driver.viewangles = self.angles + ( 10 0 0 )

// Player exits:
self detachdriverslot 0 self.driver      // detach player
self.driver show
self.driver solid
self.driver takedamage
self.driver.origin = self.origin + ( 0 0 150 )   // eject upward
self.driver = NIL

// Turret system:
self spawnturret 0 "models/vehicles/tigerturret.tik"  // spawn turret in slot 0
local.gun = self queryturretslotentity 0              // get turret ref
local.gun dmprojectile projectiles/tigercannonshell.tik   // fire projectile

// Stop vehicle:
self fullstop

// Vehicle death explosion:
self waittill death
local.wreck = spawn script_model model "models/vehicles/tigertank_d.tik"
local.wreck.origin = self.origin
local.wreck.angles = self.angles
local.boom = spawn script_model model "emitters/explosion_tank.tik"
local.boom.origin = self.origin
local.boom anim start
radiusdamage self.origin 640 384
```

---

## Verified Entity Movement Commands (from real mods)

```scr
// Move entity to a BSP waypoint/targetname:
$gate speed 160          // units per second
$gate moveto gate_open   // move to entity named "gate_open" in BSP
$gate waitmove           // BLOCKS until movement complete

// Time-based movement (exact duration):
$platform time 3.0       // takes exactly 3 seconds
$platform moveto top
$platform waitmove

// Directional movement (units):
$obj moveNorth 600
$obj moveSouth 600
$obj moveEast 400
$obj moveWest 400
$obj moveUp 200
$obj moveDown 200
$obj waitmove

// Rotation commands:
$door time 1.5
$door rotatexdown 90     // rotate X axis downward by 90 degrees
$door rotatexup 45       // rotate X axis upward
$door rotateydown 180
$door rotateyup 180
$door rotatezdown 90
$door rotatezup 90
$door rotatexdownto 90   // rotate TO exact angle (not relative)
$door waitmove

// Loop movement (e.g. fan):
$fan rotatey 250         // continuous rotation, no waitmove needed

// Looping sound DURING movement:
$crane speed 60
$crane moveto crane_end
$crane loopsound crane_run
$crane waitmove
$crane stoploopsound
```

---

## Verified bind vs glue (from real mods)

**`bind`** — rigid structural link, entity physically moves/rotates WITH target (no script loop needed):
```scr
$gate_switch bind $gate_switch_origin    // switch rotates with origin
$lamp bind $elevator                     // lamp moves with elevator
// To release:
$gate_switch unbind
```

**`glue`** — script-driven following, must be updated in a loop:
```scr
local.healthbox glue local.org    // healthbox follows org entity
// Or manually in loop:
while (isAlive local.ent)
{
    self.origin = local.ent.origin
    waitframe
}
// To release:
local.healthbox unglue
```

**Rule:** Use `bind` for mechanical assemblies (doors, platforms, guns on turrets). Use `glue` when you need conditional or physics-based following.

---

## Verified switch Statement Syntax (from real mods)

```scr
switch (local.action)
{
    case "plant":
        thread do_plant
        break
    case "defuse":
        thread do_defuse
        break
    case "dead":
        self.active = 0
        break
    default:
        end
}

// Switch on model path:
switch (self.model)
{
    case "models/player/american_army.tik":
        local.skin = "models/human/multiplayer_allied_29th_private.tik"
        break
    case "models/player/german_Wehrmacht_soldier.tik":
        local.skin = "models/human/multiplayer_german_Wehrmacht_private.tik"
        break
    default:
        local.skin = self.model
        break
}

// Multiple cases same handler (fall-through):
switch (local.type)
{
    case "trig_touch":
    case "trig_use":
    case "trig_fire":
        local.t = spawn trigger_multiple
        break
    default:
        end
}
```

---

## Verified Trigger setthread Pattern (from real mods)

```scr
// Create trigger, assign callback:
local.t = spawn trigger_multiple
local.t.origin = self.origin
local.t setsize ( -50 -50 0 ) ( 50 50 80 )
local.t setthread my_callback       // label in same file
local.t setthread "global/mod.scr::my_callback"   // label in another file

// Store custom data on trigger:
local.t.owner = self
local.t.team  = "allies"
local.t.delay ( 0.5 )               // min delay between firings

// In callback:
my_callback:
    local.player = parm.other        // who triggered it
    if (parm.other.dmteam != self.team)
        end
    // do something
end
```

---

## Verified Damage & Collision Toggles (from real mods)

```scr
self nodamage          // entity takes no damage
self takedamage        // restore damage taking
self notsolid          // no collision (players pass through)
self solid             // restore collision
self immune bullet     // immune to bullet damage
self immune explosion  // immune to explosion damage
self immune bash       // immune to melee
self immune mg         // immune to MG fire
self immune rocket     // immune to rockets (removeable: self removeimmune rocket)

// Radius damage with kill credit:
scored_radiusdamage local.origin local.attacker local.damage local.radius

// Volume damage (everything inside trigger):
local.killzone volumedamage 1000
```

---

## Verified Health Item & Medic Patterns (from real mods)

```scr
// Spawn a health pickup:
local.pack = spawn Health model "models/items/dm_50_healthbox.tik" \
    origin local.origin angles local.angles amount 25
local.pack setthread healthbox_pickedup   // fires when player picks it up

// Throw health pack with physics:
local.org = spawn script_origin
local.org.origin = self gettagposition "Bip01 Head"
local.pack glue local.org
local.org physics_on
local.org gravity 1.0
local.org.velocity = (angles_toforward self.viewangles) * 1000

// Heal player directly:
self heal 25

// Stopwatch HUD timer for interactions (plant/defuse/revive):
local.player stopwatch 3.0    // show 3-second countdown timer
local.player stopwatch 0      // clear timer
```

---

## Verified Actor / AI Spawn (from real mods)

```scr
// Spawn an AI-controlled actor:
local.bot = spawn Actor model "models/human/multiplayer_allied_1st-ranger_sergeant.tik" \
    origin ( X Y Z )

// Initialize bot AI with script:
local.bot waitthread global/teamcommand/ai.scr::initbot "smg" self 0
```

---

## Verified Array Patterns (from real mods)

```scr
// Arrays use [index] notation, 1-based:
level.mylist[1] = "first"
level.mylist[2] = "second"
level.mylist.size    // number of elements

// Dynamic array from entities (all entities with targetname):
level.myarray = exec global/makearray.scr $mytargetname

// Compress array (remove NIL slots):
local.j = 1
for (local.i = 1; local.i <= local.mylist.size; local.i++)
{
    if (local.mylist[local.i] != NIL && local.mylist[local.i] != NULL)
    {
        local.clean[local.j] = local.mylist[local.i]
        local.j++
    }
}
```

---

## Verified Model Surface Commands (from real mods)

```scr
// Hide a surface tag on a model (e.g. hide helmet):
self surface "us_helmet" "+nodraw"

// Show it again:
self surface "us_helmet" "-nodraw"
```

---

## Verified Player Properties (from real mods)

```scr
// Player identity:
local.p.netname          // player's name (string) — check != NIL && != ""
local.p.entnum           // unique entity number (int) — use as array index

// Input state (polling, 0 or 1):
local.p.useheld          // 1 while USE key held
local.p.fireheld         // 1 while FIRE key held

// Team and game state:
local.p.dmteam           // "allies", "axis", "spectator", "freeforall"
local.p.ingame           // 1 if player is active in match
local.p.health           // current health (read/write)
local.p.maxhealth        // max health (read/write)

// NOT available in MOHAA scripting (confirmed missing):
// .crouched, .prone, .jumping, .leanright, .leanleft, .run — DO NOT USE
// There is no built-in .activeweapon command — use a custom .hasweapon flag

// Read player name safely:
if (local.p.netname != NIL && local.p.netname != "")
    local.name = local.p.netname
```

---

## Verified Print Commands (from real mods)

```scr
// Console only (server log, not visible to players):
println "debug message"
println ("value = " + local.val)

// All players — centered screen text (fades out):
iprintln "Server message to everyone"

// All players — bold/larger (more prominent, fades out):
iprintlnbold "A Bomb has been planted!"

// Specific player only:
local.p iprint "Private message to you"
local.p iprint "Centered message" 1      // 1 = centered

// Positioned HUD text at screen coordinates (X Y):
locprint 100 50 "message"
locprint level.subtitleX level.subtitleY ("Counter: " + local.count)
locprint 450 70 "Join Allies!\nAxis chosen randomly."   // \n = newline
// Coordinates: 0-640 horizontal, 0-480 vertical (approx)
```

---

## Verified weaponcommand Subcommands (from real mods)

Format: `self weaponcommand <slot> <subcommand> [value]`
Slots: `dual` (current weapon), `mainhand`, `secondary`

```scr
// Damage:
self weaponcommand dual dmbulletdamage 111          // bullet damage amount

// Fire rate:
self weaponcommand dual dmfiredelay 0.08            // seconds between shots (lower = faster)

// Movement speed modifier:
self weaponcommand dual dmmovementspeed 1.10        // 110% speed while holding weapon

// Ammo:
self weaponcommand dual dmammorequired 0            // 0 = no ammo needed to fire
self weaponcommand dual usenoammo 1                 // fire without consuming ammo
self weaponcommand dual ammotype none               // set ammo type to none

// Accuracy / spread:
self weaponcommand dual dmbulletspread 25 25 150 150  // W H W2 H2 spread values

// Fire type:
self weaponcommand dual firetype bullet             // hitscan
self weaponcommand dual firetype projectile         // spawns projectile
self weaponcommand mainhand firetype melee          // melee

// Zoom (scope):
self weaponcommand dual zoom 10                     // zoom level

// Targeting name (for entity reference):
self weaponcommand dual targetname ("weapon" + self.entnum)

// Misc:
self weaponcommand dual notdroppable                // prevent weapon drop
self weaponcommand mainhand attachtohand mainhand   // attach to hand
self weaponcommand mainhand anim fire               // play fire animation
self weaponcommand mainhand secondary meansofdeath bash  // melee damage type
```

---

## Verified level.time Patterns (from real mods)

```scr
// Cooldown — only fire every N seconds:
if (level.time > local.last_action + 5.0)
{
    local.last_action = level.time
    // do action
}

// Timestamp for expiry:
local.expire = level.time + 30.0
while (level.time < local.expire)
    waitframe

// Periodic update with timestamp:
if (level.update_time == NIL || level.time >= level.update_time)
{
    // do update
    level.update_time = level.time + 2.0
}

// Measure elapsed time:
local.start = level.time
// ... do work ...
local.elapsed = level.time - local.start
```

---

## Verified Type Conversion (from real mods)

```scr
int(local.val)              // convert to integer (truncates decimals)
float(local.val)            // convert to float
int(getcvar "g_gametype")   // common: read cvar as int

// String concatenation with + operator:
"Player: " + local.p.netname
"Score: " + local.kills + "/" + local.deaths
"k" + local.p.entnum + ";"

// Semicolons to chain statements on one line:
local.x = float(local.x) ; local.y = float(local.y) ; local.z = float(local.z)
```

---

## Verified waittill Event Names (from real mods)

```scr
// Level events:
level waittill prespawn          // before entity spawn
level waittill spawn             // after map load
level waittill roundstart        // each round start (fires every round)
level waittill allieswin         // allies win (timer ran out = clockside team wins)
level waittill axiswin           // axis win

// Entity events:
self waittill death              // entity dies
self waittill trigger            // trigger_* touched
self waittill touch              // entity touched by anything
self waittill movedone           // movement finished (alternative to waitmove)
self waittill animdone           // default animation finished
self waittill upperanimdone      // upper body animation finished
self waittill flaggedanimdone    // flagged animation finished
self waittill sounddone          // sound playback finished
self waittill ontarget           // turret on-target event

// NOT VALID — these do NOT exist in MOHAA:
// waittill use, waittill respawn (use polling instead)
```

---

## Verified cansee Command (from real mods)

```scr
// Syntax: entity cansee target fov distance
// Returns: 1 if target is visible, 0 if not

if (local.player cansee self 30 128)          // narrow 30° FOV, 128 unit range
if (local.player cansee $bomb 180 80)          // wide 180° FOV, 80 unit range
if (local.player cansee self level.bombusefov level.bomb_use_distance)

// Combined with other checks (standard bomb pattern):
while ( (isAlive local.player) &&
        (local.player cansee self level.bombusefov level.bomb_use_distance) &&
        (local.player.useheld == 1) )
{
    wait .1
}

// Also works on non-player entities:
if (local.weapon cansee local.target 180 500)
```

---

## Verified trace Command Full Return (from real mods)

```scr
// Simple trace — returns endpoint vector:
local.hit = trace local.start local.end

// Full trace — returns dictionary:
local.result = trace local.start local.end 0 ( -16 -16 -16 ) ( 16 16 16 )
// args: startPos endPos passEntity mins maxs [mask]
// passEntity = 0 means pass through nothing special

// Return value keys:
local.result["fraction"]      // 0.0-1.0 — how far trace went (1.0 = nothing hit)
local.result["endPos"]        // vector — where trace stopped
local.result["entity"]        // entity reference hit (NIL if world/nothing)
local.result["entityNum"]     // entity number hit
local.result["surfaceFlags"]  // int — surface properties
local.result["contents"]      // int — content type
local.result["allSolid"]      // bool — entire trace in solid
local.result["startSolid"]    // bool — started inside solid
local.result["location"]      // int — body location hit

// Common usage patterns:
// Get ground position below a point:
local.ground = trace (local.pos + (0 0 16)) (local.pos + (0 0 -16384))

// Raycast from player eye:
local.eye = self gettagposition "Bip01 Head"
local.hit = trace local.eye (local.eye + (angles_toforward self.viewangles) * 4096)

// Check if hit an entity:
if (local.result["entity"] != NIL && local.result["entity"] != $world)
    local.hitent = local.result["entity"]
```

---

## Verified AI & Vehicle Commands (from real mods)

```scr
// Vehicle speed and turning:
self vehiclespeed 200          // set movement speed
self turnrate 3                // set turn rate (lower = slower turns)
self TurnSpeed 45              // turret turn speed (degrees/sec)

// AI turret targeting:
self setaimtarget local.target    // set what entity to aim at
self setaimtarget NULL            // stop targeting
self startFiring                  // start auto-fire
self stopFiring                   // stop auto-fire
self burstFireSettings 10 15 4 5  // burstmin burstmax pausemin pausemax
self tracerFrequency 1            // every Nth shot is a tracer
self accuracy 100                 // accuracy 0-100

// removeondeath — keep entity corpse on map after death:
self removeondeath 0              // DON'T remove on death (keep wreck)
self removeondeath 1              // remove on death (default)

// Weapon deactivation (used when mounting vehicles):
self.driver deactivateweapon righthand    // disable driver's weapon
self.driver activateweapon righthand      // re-enable weapon

// Network broadcast flag:
self svflags "+broadcast"         // make entity visible to all clients (required for MP!)
self svflags "-broadcast"         // hide from clients

// NOT VALID commands — do NOT use:
// forceactivateweapon — does NOT exist
// attachpassengerslot / detachpassengerslot — do NOT exist (use glue)
// warpback — does NOT exist
```

---

## Verified Animation State Names (from real mods)

```scr
// Force player leg/torso animation:
local.player forcelegsstate STAND
local.player forcetorsostate STAND
local.player forcetorsostate "USE_LADDER_SORRID"     // climbing ladder
local.player forcetorsostate "GET_OFF_LADDER_TOP"    // dismount top
local.player forcetorsostate "GET_OFF_LADDER_BOTTOM" // dismount bottom
local.player forcetorsostate JARMUBEN                // sitting in vehicle
```

---

## Verified self.angles vs self.viewangles (from real mods)

```scr
// self.angles — entity's BODY orientation in the world (pitch yaw roll)
// Used for: entity facing direction, vehicle heading, world-space calculations
local.forward = angles_toforward self.angles          // entity's forward direction

// self.viewangles — player's VIEW/HEAD direction (pitch yaw roll)
// Used for: where player is looking, aiming, raycasting
local.aim = angles_toforward self.viewangles          // where player is aiming

// Access individual components:
local.yaw   = self.viewangles[1]    // left-right (0=north, 90=east, 180=south, 270=west)
local.pitch = self.viewangles[0]    // up-down (negative = looking up)
local.roll  = self.viewangles[2]    // tilt

// Hybrid — mix body yaw with view pitch (e.g. for turret camera):
local.cam.angles = ( self.viewangles[0]  self.angles[1]  self.angles[2] )

// Vehicle: match vehicle body direction to driver's look direction:
self.angles = ( 0  self.driver.viewangles[1]  0 )
```

---

## Verified Multi-Seat Vehicle Pattern (from real mods)

```scr
// Seats are script_origin entities bound to vehicle, passengers glued to seats:

// Setup seats (relative offsets from vehicle center):
local.seat1 = spawn script_origin
local.seat1.origin = local.vehicle.origin + ( -40  22 -5 )   // front-right
local.seat1 bind local.vehicle

local.seat2 = spawn script_origin
local.seat2.origin = local.vehicle.origin + ( -40 -22 -5 )   // front-left
local.seat2 bind local.vehicle

// Attach passenger:
local.passenger glue local.seat1     // passenger follows seat
local.seat1.passenger = local.passenger
local.passenger.is_in_vehicle = 1
local.vehicle.free_seats--

// Detach passenger:
local.passenger unglue
local.passenger.is_in_vehicle = 0
local.vehicle.free_seats++
```

---

## Verified Extra weaponcommand Subcommands (from real mods)

```scr
// Scope / zoom:
self weaponcommand mainhand zoom 10          // scope zoom level
self weaponcommand mainhand zoom 20          // higher = more zoom
self weaponcommand mainhand dmzoomspreadmult 0   // spread while zoomed (0 = perfect)

// Clip management:
self weaponcommand mainhand clipsize 10      // magazine size
self weaponcommand mainhand ammo_in_clip 10  // current ammo in clip
```

---

## Verified Thread Return Values (from real mods)

```scr
// Return a value from a thread/label using "end <value>":
get_player_name local.player:
    if (local.player.netname != NIL && local.player.netname != "")
        end local.player.netname
    end ""
end

random_pick local.max:
    local.result = randomint local.max + 1
end local.result

// Capture return value with waitthread:
local.name   = waitthread get_player_name local.p
local.chosen = waitthread random_pick 5

// waitexec also captures return (blocking, from another file):
local.hit = waitexec global/trace.scr local.start local.end 0 (-1 -1 -1) (1 1 1)
```

---

## Verified Thread Management (from real mods)

```scr
// Store thread reference using parm.previousthread:
local.p thread my_background_loop
local.p.loop_thread = parm.previousthread    // store ref right after thread call

// Stop a thread later:
if (local.p.loop_thread)
    local.p.loop_thread.terminate = 1        // signal thread to stop

// Remove/delete a spawned entity (also stops its threads):
local.entity remove

// Pattern — per-player thread that only starts once:
if (local.p.my_thread)
    local.p.my_thread.terminate = 1         // stop old one first
local.p thread player_loop
local.p.my_thread = parm.previousthread    // store new ref
```

---

## Verified huddraw_shader (from real mods)

```scr
// Global HUD image (all players):
huddraw_shader 10 "textures/hud/allies"         // allied team icon
huddraw_shader 11 "textures/hud/axis"           // axis team icon
huddraw_shader 20 "textures/mohmenu/black.tga"  // black background/overlay
huddraw_shader 21 "textures/common/white.tga"   // white dot/crosshair

// Per-player HUD image (ihuddraw):
self ihuddraw_shader 31 "textures/common/white.tga"
self ihuddraw_align  31 center center
self ihuddraw_rect   31 0 0 4 4                  // tiny 4x4 center dot
self ihuddraw_color  31 1 0 0                    // red
self ihuddraw_alpha  31 1.0

// huddraw_virtualsize — coordinate mode:
huddraw_virtualsize 10 1    // 1 = virtual/scaled (recommended — scales with resolution)
huddraw_virtualsize 10 0    // 0 = fixed screen pixels
```

---

## Verified Map Name Detection (from real mods)

```scr
// Read current map name:
local.mapname = getcvar "mapname"

// Use with switch for map-specific behavior:
switch (local.mapname)
{
    case "mohdm1":
        // southern france specific
        break
    case "mohdm6":
        // stalingrad specific
        break
    case "obj_team1":
        // the hunt specific
        break
    default:
        // all other maps
        break
}
```

---

## Verified $world Commands (from real mods)

```scr
// Far plane (view distance / fog):
$world farplane 5000                          // set view distance
$world farplane_color ( 0.039 0.039 0.039 )  // fog color (R G B)
$world farplane_cull 1                        // enable farplane culling
$world farplane_cull 0                        // disable culling

// Read current values:
local.dist  = $world.farplane
local.color = $world.farplane_color

// World up vector:
local.up = $world.upvector    // always ( 0 0 1 )
```

---

## Verified Inline Spawn with Properties (from real mods)

```scr
// All properties on spawn line:
local.box = spawn script_model model "models/items/item_mg_ammobox.tik" \
    origin ( 100 200 300 ) \
    angles ( 0 90 0 )

// With targetname:
local.trig = spawn trigger_multiple targetname "my_trigger" \
    origin ( 0 0 0 )

// With spawnflags:
local.seat = spawn script_origin targetname "seat1" \
    origin ( -40 22 -5 ) spawnflags "1"

// Compact format (no backslash, all on one line):
local.model = spawn script_model model "models/static/indycrate.tik" origin "-885 -755 -16" angles "0 0 0"
```

---

## Verified Projectile System (from real mods)

```scr
// Set weapon to fire a projectile:
local.weapon projectile "models/projectiles/bazookashell.tik"
local.weapon dmprojectile "models/projectiles/bazookashell.tik"

// Fire type must be projectile:
local.weapon weaponcommand mainhand firetype projectile

// Verified projectile model paths (from real mods):
// projectiles/bazookashell.tik
// models/projectiles/heatseekershell.tik
// models/projectiles/mortarshell_ap.tik
// models/projectiles/mortarshell_he.tik
// models/projectiles/planebomb.tik
// projectiles/tigercannonshell.tik

// Per-entity gravity (for physics projectiles):
local.missile physics_on
local.missile gravity 1.0    // 1.0 = normal gravity
local.missile gravity 2.0    // 2.0 = falls faster (bombs)
local.missile gravity 0.0    // 0.0 = no gravity (floats)
local.missile.velocity = (angles_toforward self.viewangles) * 1500

// NOT FOUND / does NOT exist:
// scored_radiusdamage — use radiusdamage instead
// disconnect_paths / connect_paths — not in MP scripts
```

---

## Verified Vector Math Commands (from real mods)

```scr
vector_length  local.v                          // length/magnitude of a vector
vector_normalize local.v                        // unit vector (length=1)
vector_dot     local.a local.b                  // dot product (scalar)
vector_cross   local.a local.b                  // cross product (perpendicular vector)
vector_within  local.a local.b 200              // 1 if within 200 units, else 0
angles_toforward local.angles                   // convert angles to forward vector
angles_toleft   local.angles                    // convert angles to left vector
angles_toup     local.angles                    // convert angles to up vector
```

---

## Verified Entity Visibility & Physics (from real mods)

```scr
// Show / hide an entity (from all clients):
self hide
self show

// Physics on entity:
self physics_on             // enable physics (gravity, collision)
self physics_off            // disable physics (freeze in place)
self physics_on 1           // enable with collision detection
local.ent.velocity = ( 0 0 500 )      // set velocity directly
self physics_velocity ( 0 0 200 )     // apply velocity impulse

// Get position of a model bone by name:
local.eye = self gettagposition "Bip01 Head"
local.hand = self gettagposition "tag_weapon_right"
local.hand_left = self gettagposition "tag_weapon_left"

// Get player kills (for ranking/scoring):
local.kills = self getkills             // returns int kill count

// Per-player movement speed modifier:
self weaponcommand dual dmmovementspeed 1.10   // 110% speed for this player
```

---

## Verified Horror / Asymmetric Mode Pattern (from real mods)

```scr
// Make entity invisible to all players:
self hide

// Make entity visible again:
self show

// Become visible only while firing, then hide:
monster_loop:
    if (self.fireheld)
        self show
    else
        self hide
    wait 0.1
    goto monster_loop
end

// Move player to specific team for game logic:
local.player stufftext "join_team axis"
local.player stufftext "join_team allies"
```

---

## Verified Portal / Teleport with Velocity (from real mods)

```scr
// Teleport entity and preserve/transform velocity:
local.ent.origin = local.dest
local.ent.velocity = ( 0 0 0 )    // zero first
waitframe
local.ent.velocity = local.new_vel  // apply new velocity next frame

// Raycast for surface detection:
local.hit = trace local.start local.end
// local.hit = hit position vector

// Full trace with bounds:
local.hit = trace local.start local.end 0 local.mins local.maxs
```

---

## Verified Ranking / Progression Pattern (from real mods)

```scr
// Read player kill count:
local.kills = self getkills

// Monitor kills and update rank:
rank_watcher:
    while (isAlive self)
    {
        local.kills = self getkills
        if (local.kills >= 10 && self.rank < 2)
        {
            self.rank = 2
            self iprint "Promoted to Corporal!" 1
            self playsound promote
        }
        wait 0.4
    }
end

// Sound aliases used in real ranking mods:
// promote  — plays on rank promotion
// demote   — plays on rank demotion
```

---

## Verified Round Detection (from real mods)

`level waittill roundstart` fires **once per game round** — at the START of each new round.
It is NOT a one-time event. Mods that need to react to each round re-enter the wait:

```scr
// Loop for each round:
round_loop:
    level waittill roundstart
    // this fires at the start of EVERY round

    // reset state, start threads for this round
    level.round_kills = 0
    thread start_round_logic

    goto round_loop
end
```

For continuous state monitoring (kills, teams, etc.), mods use polling loops:
```scr
state_monitor:
    while (1)
    {
        for (local.i = 1; local.i <= $player.size; local.i++)
        {
            if ($player[local.i] != NULL)
            {
                local.kills = $player[local.i] getkills
                if (local.kills != $player[local.i].prev_kills)
                {
                    $player[local.i].prev_kills = local.kills
                    // kills changed — do something
                }
            }
        }
        wait 0.4
    }
end
```

---

## Verified Bot / AI Lifecycle Pattern (from real mods)

```scr
// Bot entry — called once per bot:
bot_main:
    // Bot is a script_model entity — set team and skin
    self stufftext "join_team allies"
    self model "models/player/american_army.tik"

    // Bot name display:
    iprintlnbold (self.netname + " has entered the battle")

    // Bot respawn loop:
    while (1)
    {
        self waittill death
        wait (randomfloat 3.0)   // random respawn delay
        self respawn
    }
end

// Team balance check:
balance_teams:
    local.allies = 0
    local.axis   = 0
    for (local.i = 1; local.i <= $player.size; local.i++)
    {
        if ($player[local.i] != NULL)
        {
            if ($player[local.i].dmteam == "allies") local.allies++
            else if ($player[local.i].dmteam == "axis") local.axis++
        }
    }
    if (local.allies > local.axis)
        self stufftext "join_team axis"
    else
        self stufftext "join_team allies"
end
```

---

## Verified Firefighters / Projectile Pattern (from real mods)

```scr
// Spawn a physics-enabled projectile from player's hand:
local.proj = spawn script_model
local.proj model "models/emitters/waterfall.tik"
local.proj.origin = self gettagposition "tag_weapon_left"
local.proj physics_on
local.proj notsolid
local.proj.velocity = (angles_toforward self.viewangles) * 1250

// Expire after time or low velocity:
while (level.time - local.proj.spawn_time < 7.5)
{
    if (vector_length local.proj.velocity < 20)
        break
    waitframe
}
local.proj remove
```

---

## Verified Dynamic Lighting on Entity (from real mods)

```scr
// Attach a dynamic light to an entity:
local.ent light 1.0 0.5 0.0 150     // R G B radius — orange light, 150 unit radius
local.ent light 0 0 0 0             // remove light

// Animated light (flicker effect):
flicker_loop:
    local.ent light (randomfloat 1) (randomfloat 1) (randomfloat 1) (randomfloat 100 + 50)
    wait 0.05
    goto flicker_loop
end
```

---

## Verified Player State Detection (from real mods)

```scr
// Detect if player is crouching:
if ((local.p getposition)[0] == "c")   { ... }   // "c" = crouching

// Detect player movement state:
if ((local.p getmovement)[0] == "s")   { ... }   // "s" = standing still
if ((local.p getmovement)[0] == "r")   { ... }   // "r" = running

// Force a player animation/state:
local.p forcetorsostate "USE_LADDER_SORRID"   // ladder climb animation

// Physics control:
local.p physics_off    // disable gravity/collision for player
local.p physics_on     // re-enable physics

// Weapon control:
local.p takeall                              // remove all weapons
local.p weapon models/weapons/kar98.tik     // give specific weapon
local.p useweaponclass sniper               // force weapon class active
local.p ammo grenade 1                      // give 1 grenade ammo

// Speed control (server-wide):
setcvar "sv_runspeed" "500"    // building phase (default ~280)
setcvar "sv_runspeed" "280"    // combat phase (default)
```

---

## Verified Entity Attachment & Physics (from real mods)

```scr
// Attach a visual model to a player's bone:
local.p attachmodel "models/emitters/breath_steam_emitter.tik" "Bip01 Head"

// Glue one entity to another (moves with it):
local.trigger glue local.grenade     // trigger follows grenade

// Set entity velocity (e.g. kick a grenade):
local.forward = angles_toforward local.player.viewangles
self.nade.velocity = local.forward * 600 + ( 0 0 450 )

// Raycasting (line of sight / placement detection):
local.hit = trace local.eye_origin (local.eye_origin + (angles_toforward self.viewangles) * 350)

// Disable/enable a trigger:
local.trigger nottriggerable    // disable
local.trigger triggerable       // re-enable
```

---

## Verified Sound Alias Registration (from real mods)

Full soundparms format with map filtering:
```scr
// Register before level waittill prespawn:
aliascache snd_step_snow sound/characters/fs_snow_01.wav soundparms 0.4 0.3 0.9 0.2 200 2500 auto loaded maps "dm obj"
// args: volume pitch_low pitch_high randomvolume minnudist maxdist channel loaded maps "list"
// channel: auto, item, local, body, dialog, voice
// "maps" filter: only registers on listed map types
```

---

## Verified CVar-Based Mod Configuration (from real mods)

Mods use cvars for admin control and configuration:
```scr
// Read a cvar as string:
local.val = getcvar "mymod_enabled"

// Read and cast to int:
local.gametype = int(getcvar "g_gametype")

// Conditional enable:
if (getcvar "koh" != "0")
    thread koth_main

// Modify game rules at runtime:
setcvar "timelimit" (int(getcvar "timelimit") + 5)   // add 5 minutes
setcvar "g_kblock" "1"   // block kill button (prevents suicide)
```

---

## Verified Global Mod Loading Technique (from real mods)

How a mod runs on ANY map without editing the map script:

The mod puts its entry script in `global/` and the map's ubersound.scr or a zzz-prefixed pk3
calls it via the map's own script override. The key is the pk3 filename order — `zzz` prefix
loads last and overrides earlier scripts. The mod script then:

```scr
main:
    // 1. Check if mod is enabled via cvar
    if (getcvar "mymod" == "0")
        end

    // 2. Hook into game events
    level waittill prespawn
        // register sounds, precache models

    level waittill spawn
        // initialize state, spawn entities

    level waittill roundstart
        // start gameplay threads
end
```

The `global/` folder scripts are executed by the map script via:
```scr
exec global/mymod.scr         // blocking
thread global/mymod.scr       // background
```

Or placed in `ubersound.scr` which many maps auto-execute.

---

## Verified Dynamic Property Names (from real mods)

MOHAA script supports dynamic property names using string concatenation:
```scr
// Store per-player data using player index as part of property name:
level.score_player1 = 0    // normal way
level.("score_player" + local.i) = 0   // dynamic — same thing

// From real KOTH mod — track king score per player:
level.hking$player[local.id]++    // dynamic property on level using player ref as key
```

---

## Verified Func_Beam (Laser) Full Setup (from real mods)

```scr
local.beam = spawn func_beam
local.beam.origin = self.origin
local.beam minoffset 0.0
local.beam maxoffset 0.0
local.beam color ( 1 0 0 )      // R G B (red laser)
local.beam alpha 0.5
local.beam light 1 0 0 200      // R G B radius (dynamic light)
// Check if beam is touching an entity:
if (local.beam isTouching local.target) { ... }
```

---

## Verified Full Mod Patterns by Category

### Snowball / Grenade Award Mod
```scr
// Give a grenade on condition (crouching + still):
if ((local.p getposition)[0] == "c" && (local.p getmovement)[0] == "s")
{
    if (!local.p.awardingnade)
    {
        local.p.awardingnade = 1
        local.p thread awardnade
    }
}

awardnade:
    wait 1.75
    self ammo grenade 1
    self.awardingnade = 0
end
```

### Self-Healing / Regen Mod
```scr
// Per-player heal loop — thread this on each player:
player_regen:
    while (isAlive self)
    {
        wait 3
        if (self.health < 100)
            self heal 10
    }
end
```

### Teleporter Mod (complete)
```scr
// Create teleporter pair:
make_teleporter local.from local.to:
    local.t = spawn trigger_multiple
    local.t.origin = local.from
    local.t setsize ( -30 -30 0 ) ( 30 30 70 )
    local.t setthread do_teleport
    local.t.dest = local.to
    local.t.visual = spawn script_model
    local.t.visual model "items/pulse_explosive.tik"
    local.t.visual.origin = local.from
end

do_teleport:
    local.p = parm.other
    local.p tele self.dest
end
```

### King of the Hill (complete)
```scr
koth_main:
    local.zone = spawn TriggerAll
    local.zone.origin = level.hill_origin
    local.zone setsize ( -200 -200 0 ) ( 200 200 80 )
    local.zone targetname koth_zone

    while (1)
    {
        $koth_zone waittill trigger
        local.king = parm.other

        while (isAlive local.king && $koth_zone istouching local.king)
        {
            wait 1
            local.king addkills 1
            local.king iprint ( "Holding the hill: " + local.secs + "s" ) 1
        }
    }
end
```

---

## Verified makeArray / endArray (Multi-Dimensional Arrays)

Used to build lookup tables for rank systems, item lists, etc.

```scr
// Define a 2D array — each row has 4 columns
level.ranks = makeArray
"Private"            0  "textures/ranks/private"            "Pvt."
"Private-First-Class" 1  "textures/ranks/private_first_class" "Pfc."
"Corporal"           2  "textures/ranks/corporal"            "Cpl."
"Sergeant"           5  "textures/ranks/sergeant"            "Sgt."
"General-of-the-Army" 40 "textures/ranks/general_of_the_army" "GOA."
endArray

// Access:
local.name    = level.ranks[local.i][1]    // col 1 = rank name
local.kills   = level.ranks[local.i][2]    // col 2 = kill threshold
local.shader  = level.ranks[local.i][3]    // col 3 = texture path
local.abbrev  = level.ranks[local.i][4]    // col 4 = abbreviation

// Total rows: level.ranks.size
for (local.i = 1; local.i <= level.ranks.size; local.i++) { ... }
```

Associative array (key = string):
```scr
self.rankbonus["silencer"]   = 1
self.rankbonus["planes"]     = 1
self.rankbonus["regenerate"] = 1

if (self.rankbonus["silencer"] == 1) { ... }
```

---

## Verified Dynamic Entity Name Targeting

```scr
// Build entity name from variable, then reference it with $():
local.name = "firem" + self.entnum
local.ent  = $( "firem" + local.cn )     // inline reference
$( "bombp" + local.cn ) remove            // remove by dynamic name
$( "tank"  + local.id  ) vehiclespeed 0

// Pattern for cleanup — all entities share a name prefix:
local.i = 1
while ( $( "firem" + local.i ) != NULL )
{
    $( "firem" + local.i ) remove
    local.i++
}
```

---

## Verified `continue` Statement in Loops

Skips remaining code in the current loop iteration (does NOT exit loop).

```scr
while (1)
{
    waitframe
    if (local.weapon.isreloading == 1)
        continue                // jump to next waitframe — skip rest of loop body

    if (local.weapon.laseron != 1)
    {
        self stoploopsound
        continue
    }
    // ... rest of state machine
}
```

---

## Verified `loopsound` / `stoploopsound`

```scr
self loopsound heatseeker_locked       // start looping sound alias
self stoploopsound heatseeker_proj_loop // stop specific looping sound
self stoploopsound                      // stop ANY current looping sound
self playsound heatseeker_lockon        // one-shot sound (no args = stop all)
```

Note: `loopsound` requires a valid alias from ubersound.scr or aliascache.

---

## Verified `attach` Command (Rigid Offset Attachment)

Different from `glue` (which binds to origin) — `attach` places entity at a bone with offset.

```scr
// Attach a model to another entity with offset:
local.scope = spawn script_model
local.scope model "models/weapons/kar98sniper.tik"
local.scope attach local.weapon "origin" 1 ( 8 2.6 -2.1 )
// arg1=target, arg2=bone name, arg3=use_angles(0/1), arg4=offset vector

local.scope notsolid
local.scope surface KAR981 "+nodraw"   // hide a specific surface

// Detach:
local.scope detach
```

---

## Verified Entity Forward/Up Vectors (Axes)

```scr
// Get entity's world-space direction vectors:
local.fwd  = self.forwardvector     // forward direction (unit vector)
local.right = self.rightvector      // right direction
local.up   = self.upvector          // up direction

// Use with velocity:
self.velocity = self.forwardvector * 2000.0   // fly forward at speed 2000
```

---

## Verified `dmmessage` (Global Server Message)

```scr
// Broadcast a message to all players — appears in kill feed area:
self dmmessage -1 "Message text here"
self dmmessage -1 ( "You can call for Airstrike " + self.current_airstrike + " times." )
// -1 = all players (positive number = specific player entnum)
```

---

## Verified `item` Command (Give Item Without Equipping)

Different from `give` — `item` adds to inventory without switching weapon.

```scr
self item models/weapons/M18_smoke_grenade.tik    // give smoke grenade (allies)
self item models/weapons/nebelhandgranate.tik      // give smoke grenade (axis)
self item models/weapons/stielhandgranate.tik      // give stick grenade

// give = give weapon + equip
// item = give item + add to inventory quietly
```

---

## Verified `anim` Command (Script Model Animation)

```scr
local.mortar anim fire     // play "fire" animation
local.mortar anim idle     // return to idle animation

// Animation names depend on the .tik file's animation definitions
// Common names: idle, fire, reload, run, walk, death
```

---

## Verified `ihuddraw_*` Full Syntax (Per-Player HUD)

Unlike `huddraw_*` (all players), `ihuddraw_*` targets a specific player entity.

```scr
// Always: first arg is the player entity, second is slot (1-255)
ihuddraw_string  self 28 ( "Horizontal angle: " + self.angles[1] )
ihuddraw_string  self 29 "Vertical angle: ..."
ihuddraw_alpha   self 28 0.0    // hide
ihuddraw_alpha   self 28 1.0    // show
ihuddraw_color   self 28 1 0 0  // R G B
ihuddraw_rect    self 28 10 400 200 20   // X Y W H
ihuddraw_font    self 28 "courier-20"
ihuddraw_align   self 28 left top
ihuddraw_virtualsize self 28 1

// Can also target any player variable (not just self):
ihuddraw_string local.player 30 "Only you see this"
```

---

## Verified `globalwidgetcommand` (Client HUD Menus)

Sent via `stufftext` to push a widget command to one player's client:

```scr
// Set up a HUD widget:
local.player stufftext "globalwidgetcommand dday1 shader townhallwindow"
local.player stufftext "globalwidgetcommand dday1 fgcolor 1.00 0.00 1.00 1.00"  // RGBA 0-1
local.player stufftext "globalwidgetcommand dday1 bgcolor 0.00 0.00 0.00 0.00"  // transparent bg
local.player stufftext "globalwidgetcommand dday1 fadein 0"
local.player stufftext "globalwidgetcommand dday1 rect 64 10 1765 64"           // X Y W H
local.player stufftext "globalwidgetcommand dday1 font facfont-20"
local.player stufftext ("globalwidgetcommand dday1 title Your-Rank:-" + self.rank)
local.player stufftext "globalwidgetcommand dday1 virtualres 1"
local.player stufftext "globalwidgetcommand dday1 fullscreen 1"
local.player stufftext "showmenu dday1"

// Update a specific widget by name:
local.player stufftext ("globalwidgetcommand playerrank shader " + level.ranks[local.i][3])
```

Note: `globalwidgetcommand` targets named UI widgets defined in .urc files in the pk3.

---

## Verified Ballistic Physics Pattern (Mortar / Custom Projectile)

Full kinematic equations for parabolic trajectory — simulated per-frame:

```scr
// Setup:
local.g       = 9.8        // gravity constant
local.V0      = 1200.0     // initial speed
local.alpha   = 45.0       // launch angle (degrees)
local.cosalfa = waitthread global/AA/math.scr::cos local.alpha
local.sinalfa = waitthread global/AA/math.scr::sin local.alpha
local.dt      = 0.05       // frame timestep
local.t       = 0.0
local.startorigin = self.origin
local.startangles = self.angles

// Per-frame thinker loop:
while ( self.impact != 1 && local.t < local.lifetime )
{
    local.Vx = local.V0 * local.cosalfa
    local.Vy = local.V0 * local.sinalfa - (local.g * local.t)
    local.x  = local.V0 * local.cosalfa * local.t
    local.y  = local.V0 * local.sinalfa * local.t - ( (local.g / 2.0) * (local.t * local.t) )

    self.origin = local.startorigin
        + angles_toforward ( 0 local.startangles[1] 0 ) * local.x
        + angles_toup      ( 0 local.startangles[1] 0 ) * local.y

    wait local.dt
    local.t += local.dt
}
```

---

## Verified Aircraft/Vehicle Spawn and Flyby Pattern

```scr
// Spawn a plane that flies across the map:
local.plane         = spawn script_model model "models/vehicles/p47fly.tik"
local.plane.origin  = local.startpoint
local.plane.angles  = ( 0 local.dir_yaw 0 )
local.plane.speed   = 2000.0
local.plane.velocity = local.plane.forwardvector * local.plane.speed
local.plane nodamage
local.plane notsolid
local.plane loopsound airstrike

// Attach an invisible weapon to fire from:
local.plane.weapon = spawn script_model model "models/weapons/weapon.tik"
local.plane.weapon notsolid
local.plane.weapon hide
local.plane.weapon glue local.plane
local.plane.weapon firetype heavy
local.plane.weapon projectile "models/projectiles/planebomb.tik"
local.plane.weapon dmprojectile "models/projectiles/planebomb.tik"

// Wait until plane is above target (XY only, ignore Z):
while ( vector_length ( local.plane.origin - ( local.targetpos[0] local.targetpos[1] local.plane.origin[2] ) ) > local.plane.speed * 1.6 )
    waitframe

// Fire:
local.plane bindweap local.plane.weapon
local.plane.weapon shoot
```

---

## Verified Per-Team Resource Limiting Pattern

```scr
// Global quota per team (e.g. max 2 heatseekers per team):
level.allies_heatseeker = 0
level.axis_heatseeker   = 0
level.max_hs = 2

// On pickup:
if (local.player.dmteam == "allies")
{
    if (level.allies_heatseeker >= level.max_hs)
    {
        local.player iprint "Your team already has max launchers." 1
        goto pickup_loop          // restart waittill loop
        end
    }
    level.allies_heatseeker++
}
else if (local.player.dmteam == "axis")
{
    if (level.axis_heatseeker >= level.max_hs)
    {
        local.player iprint "Your team already has max launchers." 1
        goto pickup_loop
        end
    }
    level.axis_heatseeker++
}

// On drop/death — decrement:
if (local.player.dmteam == "allies")
    level.allies_heatseeker--
```

---

## Verified Per-Player Attribute Init (Associative Properties)

Player properties persist until explicitly cleared. Set on spawn:

```scr
self.killcount     = 0
self.deathcount    = 0
self.prevrank      = 0
self.spawnprotected = 1
self.inveh         = 0
self.has_mortar    = 0
self.ismortarman   = 0
self.has_heatseeker = 0

// Associative (keyed) boolean flags:
self.rankbonus["silencer"]   = 1
self.rankbonus["planes"]     = 1
self.rankbonus["regenerate"] = 1

// Bonus display string build:
local.display = ""
if (self.rankbonus["silencer"]   == 1) local.display += "[Si]"
if (self.rankbonus["planes"]     == 1) local.display += "[Pla]"
if (self.rankbonus["regenerate"] == 1) local.display += "[Reg]"
self stufftext ("set bonus_cvar BONUS: " + local.display)
```

---

## Verified Ban List Pattern (CVar as Semicolon-Separated List)

```scr
// Add a ban to a cvar-based list:
local.current = getcvar "FST_Clientban"
setcvar "FST_Clientban" (local.current + ";" + local.newban)

// Check if player is in the list:
local.banlist = getcvar "FST_Clientban"
// (then search string manually — MOHAA has no split() function)
// Pattern: use getcvar in a while loop checking substrings
```

---

## Verified `vector_toangles` (Direction → Angles Conversion)

```scr
// Convert a direction vector to pitch/yaw/roll angles:
local.dir    = local.target.origin - self.origin
local.angles = vector_toangles local.dir
self.angles  = local.angles

// Adjust for weapon barrel orientation (rotate 90° pitch):
local.angles = vector_toangles ( local.missile.origin - local.nextpos )
local.missile.angles = local.angles - ( 90 0 0 )
```

---

## Verified `istouching` (Bounding Box Overlap)

```scr
// Returns 1 if two entities' bounding boxes overlap:
if (local.zone istouching local.player) { ... }
if (local.beam.laser_org istouching local.vehicle) { ... }

// Use for: zone detection, lock-on systems, trigger substitutes
// Cheaper than trace for proximity checks
```

---

## Verified Cvar-Driven Feature Toggle (Init + Enable Pattern)

```scr
// Standard pattern for configurable features:
local.val = getcvar "myfeature_enabled"
if (local.val == "")
{
    setcvar "myfeature_enabled" "0"    // set default on first run
    end
}
local.enabled = int ( getcvar "myfeature_enabled" )
if (local.enabled == 0)
    end                                // feature disabled — stop thread

local.amount = getcvar "myfeature_amount"
if (local.amount == "")
    setcvar "myfeature_amount" "5"
local.amount = int ( getcvar "myfeature_amount" )
```

---

## Verified `randomfloat` / `randomint`

```scr
local.f = randomfloat 1.0        // returns 0.0 to 1.0 (exclusive)
local.f = randomfloat 360.0      // returns 0.0 to 360.0

local.i = randomint 5            // returns 0 to 4 (exclusive upper bound)
local.i = randomint(10) + 1      // returns 1 to 10 (common pattern for 1-based)
```

---

## Verified `println` (Server Console Debug)

```scr
println "Debug message"
println ( "[HORROR]: player count = " + $player.size )
// Output goes to server console only — not visible to players
```

---

## Verified `cache` (Model Pre-load)

```scr
// Pre-load models before spawn to avoid hitches:
cache "models/static/barrel.tik"
cache "models/emitters/breadsmoke.tik"
// Usually called during level waittill prespawn block
```

---

## Verified Dynamic Lighting (`light` / `lightOff`)

```scr
// Add a colored dynamic light to an entity:
local.ent light 1 0 0 300      // R G B radius (red light, radius 300)
local.ent light 0 1 0 200      // green light
local.ent light 1 1 0.5 400    // yellow-ish light

// Remove the light:
local.ent lightOff
```

---

## Verified Music Control (`tmstop` / `tmstart`)

Sent via stufftext to control the background music:

```scr
self stufftext "tmstop"                               // stop current music
self stufftext ("tmstop;tmstart sound/music/track.mp3") // stop + start new track
// tmstart takes a relative sound path
```

---

## Verified `commanddelay` (Scheduled Command)

```scr
// Execute a command on an entity after N seconds:
local.ent commanddelay 0.1 delete    // delete after 0.1 seconds
local.ent commanddelay 5.0 remove    // remove after 5 seconds
local.ent commanddelay 3.0 hide      // hide after 3 seconds
// Useful for timed cleanup without a thread
```

---

## Verified `sighttrace` (Boolean LOS Check)

Unlike `trace` (which returns a dict), `sighttrace` returns a simple bool:

```scr
// Returns 1 if the line is clear (no solid geometry between points):
local.clear = sighttrace local.start local.end ( -1 -1 -1 ) ( 1 1 1 )
if (local.clear)
{
    // line of sight is unobstructed
}

// Full form: sighttrace start end [mins] [maxs]
// Optional bounding box args expand the trace volume
```

---

## Verified `compress_array` (Array Cleanup)

```scr
// Remove NULL/empty entries from an array variable:
compress_array level.ca_landmines
// After deaths or removals, items become NULL in the array.
// compress_array shifts all non-NULL entries to the front and
// updates .size accordingly.
```

---

## Verified `radiusdamage` (Area-of-Effect Damage)

```scr
// Deal damage to all entities within radius:
radiusdamage local.origin local.damage local.radius
radiusdamage self.origin 200 512

// With attacker reference (so kill credits go to right player):
self radiusdamage self.origin 200 512
```

---

## Verified `stopwatch` (Client Timer Display)

```scr
// Show a countdown timer HUD to a specific player:
local.player stopwatch 3     // shows 3-second countdown
local.player stopwatch 10    // shows 10-second countdown
self stopwatch 0             // stop/hide the stopwatch
```

---

## Verified `take` (Remove Item from Inventory)

```scr
// Remove a specific item (weapon/equipment) from player:
self take models/weapons/steilhandgranate.tik    // remove grenade
self take models/weapons/thompson.tik            // remove weapon
// vs takeall — removes everything at once
```

---

## Verified `angles_pointat` (Orient Entity Toward Target)

```scr
// Return angles needed to point from entity1 toward entity2:
local.angles = angles_pointat local.origin_ent local.target_ent

// Often used to rotate an arrow/indicator model:
local.indicator.angles = angles_pointat local.indicator local.target
```

---

## Verified AI Commands (Actor Behavior)

```scr
// Threat bias — how the AI responds to other entities:
self threatbias ignoreme       // AI ignores self completely
self threatbias 0              // neutral (default)
self threatbias -100           // AI treats as friendly

// AI nationalization (sets uniform/model set):
self.actor german              // use German soldier model variants
self.actor american            // use American soldier model variants

// AI movement command:
self.actor runto local.target_entity   // run to entity's position

// AI weapon/animation:
self.actor gun "none"                  // holster weapon
self.actor gun "models/weapons/kar98.tik"

// AI move done radius (stop close enough):
self.actor movedoneradius 64
```

---

## Verified `waitexec` (Blocking External Script with Return)

Like `waitthread` but for external .scr files:

```scr
// Execute an external script file and wait for it to finish, capturing return:
local.result = waitexec global/mines/c4_chuck.scr
local.result = waitexec global/AA/trace.scr local.start local.end self.entnum ( -1 -1 -1 ) ( 1 1 1 ) 1107569441

// vs exec (fire-and-forget, no return)
// vs waitthread (calls a label in same file or another entity's label)
// waitexec = blocking exec of entire external file + returns value
```

---

## Verified Player State Properties

```scr
// Secondary fire button held (bool — 1 while held):
if (self.secfireheld) { ... }

// Current active weapon (returns model path string):
local.wep = self.weapon
if (self.weapon == "models/weapons/thompson.tik") { ... }

// Weapon fire mode (from weaponcommand):
// self.canfire — NOT a standard property; use weaponcommand to query
```

---

## Verified `spectator` / `join_team` (Direct Script Commands)

```scr
// Force player to spectator mode:
self spectator

// Force player to a team (direct command, not via stufftext):
self join_team "allies"
self join_team "axis"
// Note: join_team as direct script cmd vs stufftext "join_team allies" — both work
```

---

## Verified `killent` (Kill Entity by Entnum)

```scr
// Kill/destroy entity by its entnum (for inter-script communication):
killent local.ent.entnum
killent self.entnum

// self.entnum is read-only — assigned by engine on spawn
```

---

## Verified `bool()` Function

```scr
// Convert any value to boolean (0 or 1):
local.enabled = bool ( getcvar "feature_on" )   // "1"->1, "0"->0, ""->0
if (bool(local.val)) { ... }
```

---

## Verified `strtovec` (String to Vector)

```scr
// Parse a string formatted as "X Y Z" into a vector:
local.vec = strtovec "100 200 50"
local.vec = strtovec ( getcvar "spawn_origin" )   // read vector from cvar

// Useful for storing/loading vector positions in cvars
```

---

## Verified Entity Scale

```scr
// Set entity visual scale (affects model size, not collision):
self.scale = 2.0        // double size
self.scale = 0.5        // half size
local.corona.scale = 0.3
```

---

## Verified `spawnflags` (Entity Spawn Flags)

```scr
// Set spawn flags when spawning triggers:
local.trig = spawn trigger_multiple spawnflags 128
local.beam  = spawn func_beam spawnflags 16

// Common flag values (bitfield — add values to combine):
// 1  = start off
// 2  = toggle (trigger_multiple: remains active while touched)
// 128 = various entity-specific uses
```

---

## Verified Trace Content/Surface Flags (from real mods)

Used to interpret `trace` command results (`surfaceFlags` / `contentFlags`):

```scr
// Surface material flags (returned in trace.surfaceFlags):
level.SURF_SKY    = 4       // sky surface
level.SURF_METAL  = 512     // metal surface
level.SURF_GRILL  = 2048    // metal grill
level.SURF_WOOD   = 8192    // wood surface
level.SURF_ROCK   = 16384   // rock/stone
level.SURF_DIRT   = 32768   // dirt/ground
level.SURF_GRASS  = 65536   // grass
level.SURF_PAPER  = 131072  // paper/cardboard

// Content flags (trace.contentFlags):
level.CONTENTS_SOLID       = 1
level.CONTENTS_WATER       = 32
level.CONTENTS_LAVA        = 8
level.CONTENTS_PLAYERCLIP  = 65536
level.CONTENTS_MONSTERCLIP = 131072
level.CONTENTS_FENCE       = 2097152

// Usage:
local.t = trace local.start local.end
if (local.t.fraction < 1.0)
{
    if (local.t.surfaceFlags & level.SURF_METAL)
        self playsound step_metal
}
```

---

## Verified `delete` vs `remove` (Entity Cleanup)

```scr
self.ent remove     // standard removal — defers until safe
self.ent delete     // immediate deletion (used with commanddelay)

// Both achieve the same end result; delete is more immediate
// delete is also the commanddelay keyword:
self.ent commanddelay 0.1 delete
```

---

## Verified `NIL` (Alternate Null Keyword)

```scr
// Some mods use NIL instead of NULL — both are equivalent:
if (local.ent == NIL) { ... }
if (local.ent == NULL) { ... }   // same thing

// NIL appears in older mods; NULL is more common in newer ones
```

---

## Verified `hurt` Full Syntax + Damage Types

```scr
// Simple damage (type only):
self hurt 100 bash
self hurt 100 explosion
self hurt 1   lava
self hurt 100 impale

// With knockback direction vector:
self hurt 100 explosion ( 200 0 200 )

// Confirmed damage type strings:
// bash, explosion, lava, impale, bullet, fire, crush, telefrag, drown, burn, melee
// (some types trigger special hit reactions / sounds client-side)
```

---

## Verified `damage` Command (Full Entity Damage)

More precise than `hurt` — specifies attacker, direction, and flags. Used in landmine/AOE systems:

```scr
// Full signature:
// <target> damage <attacker> <amount> <inflictor> (origin) (direction) (force) <flags> <type> <location> <modelindex>
$player[local.i] damage local.caller local.dmg local.caller \
    ( 0 0 0 ) \
    ( angles_toforward ( angles_pointat local.ent local.ent $player[local.i] ) * -1 ) \
    ( 0 0 0 ) \
    local.dmg 0 9 -1

// Simpler form (most mods use hurt instead):
self damage self 50 self ( 0 0 0 ) ( 0 0 1 ) ( 0 0 0 ) 50 0 0 -1
```

Note: Most mods prefer `hurt` for simplicity. `damage` is for precise attacker tracking (kill credits).

---

## Verified Ammo Types (`ammo` Command)

```scr
// Give specific ammo type to player:
self ammo agrenade 1      // allied grenades
self ammo grenade 1       // (generic grenade alias)
self ammo bullet 30       // rifle bullets
self ammo shotgun 8       // shotgun shells
self ammo rocket 1        // bazooka rockets

// Full syntax:
// <entity> ammo <ammo_type_string> <amount>
```

---

## Verified Spawn Protection Pattern

Complete pattern for temporary invincibility after spawn:

```scr
spawn_protect:                           // call as: self thread spawn_protect
    self notsolid                        // no collision
    self nodamage                        // no damage taken
    self light 0.5 0.5 1.0 100          // blue glow effect
    self.spawnprotected = 1

    local.count = local.duration * 10   // duration in seconds * 10 frames
    while ( self != NULL && self.player_spawned == 1 && local.count > 0 )
    {
        wait 0.1
        local.count--
    }

    self solid
    self takedamage
    self light 0 0 0 0                  // remove glow
    self.spawnprotected = 0
end
```

---

## Verified Trigger Class Comparison

```scr
// trigger_multiple — fires on TOUCH, can fire again after cooldown:
local.t = spawn trigger_multiple origin self.origin
local.t setsize ( -30 -30 0 ) ( 30 30 70 )
local.t setthread do_teleport

// trigger_multipleall — fires on any touch, no cooldown, all entities:
local.t = spawn trigger_multipleall spawnflags 20 origin ( 0 0 0 )
local.t setsize ( -16384 -16384 -16384 ) ( 16384 16384 16384 )
local.t setthread projectile_trigger

// trigger_use — fires when player presses USE key (E):
local.t = spawn trigger_use origin self.origin
local.t setsize ( -64 -64 0 ) ( 64 64 64 )
local.t setthread on_use

// TriggerAll / TriggerBox — entity-class triggers (map-placed):
local.zone = spawn TriggerAll origin level.hill_origin
```

---

## Verified `animate` Entity Class vs `script_model`

```scr
// animate — entity with automatic animation playback:
local.fire = spawn animate model "models/animate/fire.tik" origin local.org targetname "ff_fireent"
// animate entities start their default animation automatically
// call anim commands to change animation state

// script_model — static model, requires explicit anim command:
local.ent = spawn script_model
local.ent model "models/static/barrel.tik"
local.ent anim start   // must call this to start animation
local.ent anim idle    // change animation state

// Both support: origin, angles, scale, hide/show, solid/notsolid, glue/bind
```

---

## Verified `animscript` (Entity Animation Script Path)

```scr
// Set the animation behavior script for an AI actor:
self.actor animscript anim/idle.scr
self.actor animscript anim/run_01.scr

// animscript controls blend trees and animation state machines for AI
// Only applies to Actor/AI entities, not script_model
```

---

## Verified `movedoneradius` (AI Property)

```scr
// Set the radius at which AI considers destination "reached":
self.actor.movedoneradius = 64        // normal precision
self.actor.movedoneradius = level.TC_MOVEDISTANCE * 0.1   // tight precision

// After runto completes:
self.actor runto local.target_ent
self.actor waittill movedone          // fires when within movedoneradius
```

---

## Verified `say` / `sayteam` via stufftext (No waittill say)

MOHAA does NOT have a `waittill say` event. To "say" something as a player from script:

```scr
// Send chat message as the player:
self stufftext "say I have been promoted!"
self stufftext "sayteam Your team needs backup!"

// For server-wide announcements use iprint or huddraw, not say
// say via stufftext will show the player's name as the sender
```

---

## Verified `light` Command on Entities (Dynamic Point Light)

```scr
// Add dynamic colored light to any entity:
local.ent light 1 0 0 300      // red, radius 300
local.ent light 0 0.5 1 200    // cyan, radius 200
self light 0.5 0.5 1.0 100     // blue glow for spawn protection

// Remove / turn off:
self light 0 0 0 0             // black light = effectively off
self lightOff                  // explicit off

// Light follows entity as it moves
```

---

## Verified `isAlive` Function

```scr
// Returns 1 if entity is alive (spawned, not dead, not NULL):
if (isAlive local.player) { ... }
while (isAlive self) { wait 1; ... }

// More thorough check (also handles NULL):
if (local.p != NULL && isAlive local.p) { ... }
```

---

## Verified `healthonly` (Direct Health Set)

Unlike `heal` (which adds), `healthonly` sets health to an exact value without damage calculation:

```scr
self healthonly 100              // set to 100
self healthonly (self.health + 10)  // add 10 (regen pattern)
self healthonly 200              // overheal above max (superhealth)

// vs heal — heal triggers damage events and respects max:
self heal 10    // adds 10, capped at max health
```

---

## Verified `iprintln_noloc` (Debug Print with Variables)

```scr
// Like println but prints to the player's screen AND console, with inline concatenation:
iprintln_noloc "error: " self.error " (dist = " self.dist ")"
iprintln_noloc "rope node " local.i " pos: " local.node.origin

// Unlike iprint, concatenation uses space-separated segments — no "+" operator needed
// Goes to server console and optionally player screen
```

---

## Verified `activate` / `deactivate` (Entity State Toggle)

```scr
local.ent activate      // activate entity (enables its behavior/updates)
local.ent deactivate    // deactivate (pauses updates, entity stays in world)

// Common use: pause a func_beam, disable a trigger, freeze an emitter
// Different from hide/show (which affects visibility)
// Different from triggerable/nottriggerable (which affects trigger firing)
```

---

## Verified `func_beam` Full Property Set

All valid properties for a func_beam entity:

```scr
local.beam = spawn func_beam
local.beam.origin = self.origin
local.beam endpoint   ( 100 200 300 )    // other end of beam
local.beam shader     "textures/common/black"  // visual texture
local.beam color      ( 1 0 0 )          // RGB tint
local.beam alpha      1.0                // opacity
local.beam maxoffset  0.0                // max wave amplitude (0 = straight)
local.beam minoffset  0.0                // min wave amplitude
local.beam numsegments 1                 // how many segments (1 = straight line)
local.beam alwaysdraw                   // render even if origin off-screen
local.beam light 1 0 0 200              // add dynamic light along beam
local.beam activate                      // start drawing
local.beam deactivate                   // stop drawing (entity stays)
local.beam remove                        // destroy completely

// Update beam endpoint each frame (for tracking beams):
while (1)
{
    local.beam endpoint local.target.origin
    waitframe
}
```

---

## Verified `script_origin` Entity Class

Lightweight invisible entity used as position markers and anchors:

```scr
// Spawn a position marker (no model, no collision, not visible):
local.marker = spawn script_origin
local.marker.origin = ( 100 200 50 )
local.marker.angles = ( 0 90 0 )

// Common uses:
// - Reference point for relative positioning
// - Waypoint for AI pathfinding
// - Anchor for bind/glue targets
// - Camera position holder
local.cam = spawn script_origin origin ( X Y Z )
$player glue local.cam    // glue player to invisible point
```

---

## Verified `setplayerusable` (Static Weapon Control)

Controls whether players can man a placed weapon (MG nest, etc.):

```scr
local.mg setplayerusable 1    // players can enter/use this weapon
local.mg setplayerusable 0    // lock — no one can use it

// Used with map-placed weapons or spawned MG entities
// When usable=1, player presses USE key to mount the weapon
```

---

## Verified `yawcenter` / `maxyawoffset` (Weapon Rotation Limits)

For placed/static rotational weapons (MG nests, cannons):

```scr
local.mg yawcenter    local.angle   // set center facing angle (0-360)
local.mg maxyawoffset 52            // max degrees left/right from center
// Total arc = maxyawoffset * 2 (52 = 104° total arc)

// Also: pitchcenter / maxpitchoffset for vertical limits
local.mg pitchcenter    0
local.mg maxpitchoffset 30
```

---

## Verified Entity Rotation Commands (Full Set)

```scr
// Continuous rotation (degrees/second):
local.ent rotatex 50        // spin around X axis at 50 deg/sec
local.ent rotatey local.spinspeed  // spin around Y axis
local.ent rotatez 30        // spin around Z axis (yaw)

// One-shot rotation to target angle:
local.ent rotateto ( 0 90 0 )    // rotate to angles (pitch yaw roll)
local.ent rotatedownto ( X Y Z ) // rotate down to angle
local.ent rotateuptoto ( X Y Z ) // rotate up to angle

// Wait for rotation to complete:
local.ent waitrotate

// Stop all rotation:
local.ent rotatex 0
```

---

## Verified `movedown` / `moveup` / `movenorth` etc. (Directional Movement)

```scr
// Move entity in absolute world direction by distance:
local.door movedown  200      // move down 200 units
local.door moveup    200      // move up 200 units
local.door movenorth 300      // move north (positive Y)
local.door movesouth 300      // move south (negative Y)
local.door moveeast  150      // move east (positive X)
local.door movewest  150      // move west (negative X)

// Then wait for completion:
local.door waitmove

// For elevators — loop pattern:
elevator_loop:
    local.door moveup 256
    local.door waitmove
    wait 3
    local.door movedown 256
    local.door waitmove
    wait 3
    goto elevator_loop
end
```

---

## Verified `weaponcommand dmmovementspeed` (Player Speed Modifier)

Additional weaponcommand subcommand not previously listed:

```scr
// Modify movement speed multiplier (applies while holding this weapon):
self weaponcommand dual  dmmovementspeed 1.10    // 10% faster
self weaponcommand mainhand dmmovementspeed 0.75  // 25% slower (sniper penalty)

// Combined with damage boost for rank system:
self weaponcommand dual dmbulletdamage 120    // 120 damage per bullet (rank bonus)
self weaponcommand dual dmmovementspeed 1.15  // speed bonus at high rank
```

---

## Verified Freeze Tag Pattern (No `freeze` Command Exists)

MOHAA has no built-in `freeze` command. Freeze tag is implemented via model replacement:

```scr
// FREEZE: Kill player, spawn a frozen body at their location
freeze_player local.player:
    local.origin = local.player.origin
    local.angles = local.player.angles
    local.model  = local.player.model

    // Kill the real player (they enter spectator/dead state)
    local.player kill

    // Spawn a frozen body at same location
    local.body = spawn script_model
    local.body model local.model
    local.body.origin = local.origin
    local.body.angles = local.angles
    local.body notsolid
    local.body.frozenfor = local.player     // link body to player

    // Spawn melt trigger on the body (teammates touch to unfreeze)
    local.trig = spawn trigger_multiple
    local.trig setsize ( -30 -30 0 ) ( 30 30 70 )
    local.trig setthread melt_trigger
    local.trig glue local.body
end

// UNFREEZE: Remove body, respawn player
melt_player local.body local.player:
    local.origin = local.body.origin
    local.body remove
    // show melt progress to nearby players:
    self stopwatch 3
    wait 3
    local.player respawn
end
```

---

## Verified Projectile / Physics Object Properties

Properties settable on physics objects (projectiles, grenades, balls):

```scr
// Enable bounce-on-touch behavior:
self.projectile bouncetouch

// Set damage dealt on impact (0 = no damage):
self.projectile hitdamage 0
self.projectile hitdamage 50

// Set explosion visual effect model:
self.projectile explosionmodel "models/fx/paintballdummy.tik"
self.projectile explosionmodel "models/fx/explosion.tik"

// Set velocity directly:
self.projectile.velocity = angles_toforward self.viewangles * 1200

// Extract horizontal component only (for flat-direction checks):
local.flatvel = self.velocity
local.flatvel[2] = 0    // zero out Z — now only XY direction
```

---

## Verified Player Button State Properties

Read-only properties that reflect current button state:

```scr
// Check if player is holding USE key (E):
if (self.useheld) { ... }          // 1 while USE held, 0 when released

// Check if player is holding FIRE button:
if (self.fireheld) { ... }         // 1 while primary fire held
if (self.secfireheld) { ... }      // 1 while secondary fire held

// Pattern for interactive building / charging:
while (self.useheld && self.buildingmapnow)
{
    wait 0.1
    local.progress++
}
```

---

## Verified `jumpto` (Entity Teleport — Not Player)

Different from `tele` (player teleport) — `jumpto` moves a non-player entity instantly:

```scr
// Teleport an entity to a position:
local.flag jumpto local.base.origin

// vs tele — which is for players:
local.player tele local.dest_origin
```

---

## Verified Base Building Pattern (Object Arrays + Player Interaction)

Complete pattern for a mod where players place objects:

```scr
// Global state:
level.build_objects  = makeArray endArray   // empty array
level.objectlimit    = 10
level.objectcount    = 0

// Spawn a buildable object:
place_object local.origin local.model:
    if (level.objectcount >= level.objectlimit)
    {
        self iprint "Object limit reached!" 1
        end
    }

    local.obj = spawn script_model
    local.obj model local.model
    local.obj.origin = local.origin
    local.obj notsolid
    local.obj rotatey 45         // spin while placing

    // Once confirmed:
    local.obj solid
    level.objectcount++
    level.build_objects[level.build_number] = local.obj

    // Interaction trigger:
    local.trig = spawn trigger_multiple
    local.trig setsize ( -64 -64 0 ) ( 64 64 128 )
    local.trig.origin = local.origin
    local.trig setthread on_object_touched
end
```

---

## Verified CTF Core Patterns

CTF is a complex mod pattern — key data structures used in real mods:

```scr
// Flag state stored in level associative arrays:
level.ctf_flags["allies"]    = local.allies_flag_ent
level.ctf_flags["axis"]      = local.axis_flag_ent
level.ctf_flagbase["allies"] = local.allies_base_ent
level.ctf_flagbase["axis"]   = local.axis_base_ent

// Flag pickup:
local.flag.carrier = parm.other           // who picked it up
local.flag glue local.flag.carrier        // flag follows player

// Flag drop (on death):
local.flag unglue
local.flag.origin = local.flag.carrier.origin
local.flag.carrier = NULL

// Flag capture check — player touches their own base while carrying enemy flag:
if (local.player.dmteam == "allies" && local.player.ctf_has_flag == 1)
{
    if (local.zone istouching local.player)
        thread score_capture local.player
}

// Beacon via func_beam to show flag position:
local.beacon = spawn func_beam
local.beacon.origin = local.flag.origin
local.beacon endpoint ( local.flag.origin[0] local.flag.origin[1] local.flag.origin[2] + 512 )
local.beacon color ( 1 0.5 0 )   // orange = allies flag
local.beacon alpha 0.8
local.beacon activate
```

---

## Verified `getactiveweap` (Query Active Weapon Entity)

```scr
// Get the entity handle of the player's current active weapon:
local.weap = self getactiveweap 0    // 0 = primary/main weapon
local.weap = self getactiveweap 1    // 1 = secondary

// Returns entity handle — you can then run weaponcommand or check properties
if (local.weap != NULL)
    local.weap zoom 8
```

---

## Verified `semiauto` (Weapon Fire Mode)

```scr
// Set a weapon to semi-automatic (one shot per trigger pull):
local.weap semiauto 1    // enable semi-auto
local.weap semiauto 0    // disable (return to full-auto)

// Applied to the weapon entity from getactiveweap:
local.weap = self getactiveweap 0
local.weap semiauto 1
```

---

## Verified `freezeplayer` (Freeze Player Input)

```scr
// Lock all player movement and input:
self freezeplayer 1     // freeze — player cannot move, shoot, or look
self freezeplayer 0     // unfreeze — restore full control

// Used in cutscenes, build placement, or spawn protection
// Different from notsolid/nodamage — this blocks the player's INPUT
```

---

## Verified Math Helper Script Library (NOT Built-in)

MOHAA has no built-in `sin`/`cos`/`sqrt`. Real mods include external math scripts.
Pattern (from veersmods `global/AA/math.scr` and MOHAA_PN `global/AA/math.scr`):

```scr
// Call math functions via waitthread on the helper script:
local.result  = waitthread global/AA/math.scr::sin  local.angle_deg
local.result  = waitthread global/AA/math.scr::cos  local.angle_deg
local.result  = waitthread global/AA/math.scr::tan  local.angle_deg
local.result  = waitthread global/AA/math.scr::asin local.value
local.result  = waitthread global/AA/math.scr::acos local.value
local.result  = waitthread global/AA/math.scr::atan local.value
local.result  = waitthread global/AA/math.scr::atan2 local.y local.x
local.result  = waitthread global/AA/math.scr::sqrt local.value

// To use: include math.scr in your pk3 at global/AA/math.scr
// All return float values
```

---

## Verified String Helper Script Library (NOT Built-in)

String manipulation functions in MOHAA are NOT built-in — they come from `global/strings.scr`:

```scr
// All called via waitthread on the helper:
local.pos    = waitthread global/strings.scr::InStr  local.haystack local.needle   // find position, or NIL if not found
local.right  = waitthread global/strings.scr::Right  local.str local.n             // last N chars
local.left   = waitthread global/strings.scr::Left   local.str local.n             // first N chars
local.mid    = waitthread global/strings.scr::Mid    local.str local.start local.n // substring
local.rev    = waitthread global/strings.scr::Reverse local.str
local.lower  = waitthread global/strings.scr::to_lower local.str
local.upper  = waitthread global/strings.scr::to_upper local.str
local.result = waitthread global/strings.scr::Replace local.str local.find local.replacement
local.result = waitthread global/strings.scr::Remove  local.str local.substring

// To use: include strings.scr in your pk3 at global/strings.scr
// .size on a string returns character count
```

---

## Verified `immediateremove` (Instant Entity Deletion)

```scr
// Remove entity immediately (no deferred cleanup):
local.ent immediateremove

// vs remove — deferred (safer but delayed)
// vs delete — also immediate but used in commanddelay context
// Use immediateremove for tracer bullet cleanup, frame-precise removal
```

---

## Verified `gravity` on Players (Player Gravity Scale)

Player gravity can be scaled independently from entity gravity:

```scr
// Scale player gravity (1.0 = normal, lower = lighter):
local.player gravity 0.1     // 10% gravity — floaty/jetpack feel
local.player gravity 0.5     // half gravity
local.player gravity 1.0     // restore normal gravity
self gravity 2.0             // double gravity — heavy feel

// This is a PLAYER command (different from per-entity gravity multiplier on projectiles)
// Persists until changed or player respawns
```

---

## Verified `keyheld` (Raw Key State Polling)

More granular than `useheld`/`fireheld` — can check any key by name:

```scr
// Check if a specific movement key is held:
if (self keyheld "ELORE")   { ... }   // forward key held
if (self keyheld "SETA")    { ... }   // walk/slow key held
if (self keyheld "JUMP")    { ... }   // jump key held
if (self keyheld "CROUCH")  { ... }   // crouch key held
if (self keyheld "LEANLEFT")  { ... } // lean left key
if (self keyheld "LEANRIGHT") { ... } // lean right key

// Used in jetpack, vehicle control, special movement mods
// Key names are Hungarian (ELORE = forward, SETA = walk)
```

---

## Verified `volumedamage` (Volume-Based AOE Damage)

```scr
// Deal damage to entities within a volume:
local.ent volumedamage local.damage

// Applied to an entity whose bounding box defines the damage volume
// Used for car collision damage — the vehicle entity damages players it overlaps
```

---

## Verified `tileshader` (Tiling Texture Shader)

```scr
// Apply a tiling shader to an entity's surface:
local.ent tileshader "textures/effects/ripple.tga"

// Unlike model surface commands, tileshader tiles the texture across the mesh
// Used for water surfaces, force fields, etc.
```

---

## Verified `locationprint` (Location-Based Screen Message)

```scr
// Print a message at a world-position on player's screen:
self locationprint "Spawn Protected" local.origin

// Appears anchored to a world position (not fixed HUD)
// Used for contextual info near objects (mine locations, spawn zones)
// Cleared by calling with empty string:
self locationprint "" local.origin
```

---

## Verified `activatenewweapon` (Force Equip New Weapon)

```scr
// Switch player to the most recently given weapon:
self activatenewweapon

// Call after `give` to force player to equip the new weapon immediately
// Without this, player stays on current weapon after a give command
self give models/weapons/thompson.tik
self activatenewweapon
```

---

## Verified `isadmin` (Admin Status Check)

```scr
// Returns 1 if player has admin status (server-configured):
if (self isadmin) { ... }
if (self isadmin == 1) { self iprint "Admin command granted." 1 }

// Admin status is set by the server's admin plugin/config
// Used to restrict certain mod commands to admins only
```

---

## Verified `ghost` (Intangible Entity Mode)

```scr
// Make entity intangible but still detectable by triggers:
local.ent ghost

// ghost entities:
// - Are NOT visible (like hide)
// - Have NO collision (like notsolid)
// - CAN still fire triggers (unlike hidden entities)
// Used for invisible trigger volumes and phantom projectiles
```

---

## Verified `safeholster` (Holster Without Breaking State)

```scr
// Holster the player's weapon without forcing a specific state:
self safeholster 1    // holster (hide weapon)
self safeholster 0    // unholster (show weapon again)

// Safer than forcelegsstate — doesn't break animation state machine
// Used when temporarily giving control to a vehicle or cutscene
```

---

## Verified `rendereffects` (Entity Visual Effects Flags)

```scr
// Set render effects flags on an entity (bitfield):
local.ent rendereffects 32    // glow effect
local.ent rendereffects 0     // clear all effects

// Common flag values (may vary):
// 1  = environment map
// 2  = refraction
// 32 = fullbright glow
// 64 = mirror/portal surface
```

---

## Verified Entity Targeting via $() with String Variable

```scr
// Get entity by targetname stored in a variable:
local.ent   = $( local.targetname_string )    // variable contains the targetname
local.found = $( self.target )                 // entity's own .target property as name
local.node  = $( "seat_" + local.i )          // dynamic name construction

// Check before use:
if ( $( local.name ) != NULL) { ... }

// All entities with same targetname form an array:
local.all = $mytarget       // if multiple entities share "mytarget", this is an array
local.all.size              // how many entities share that targetname
$mytarget[1]                // first entity with that name
```

---

## Verified `trigger_once` / `trigger_hurt` (More Trigger Classes)

```scr
// Fires exactly once then becomes inactive:
local.t = spawn trigger_once
local.t.origin = local.pos
local.t setsize ( -30 -30 0 ) ( 30 30 70 )
local.t setthread on_first_touch

// Damages any entity that touches it:
local.killzone = spawn trigger_hurt
local.killzone damage 10000            // damage per touch
local.killzone.origin = ( 0 0 -200 )
local.killzone setsize ( -1000 -1000 -120 ) ( 1000 1000 0 )
// trigger_hurt fires continuously while entity is inside
// damage N sets the damage per contact frame
```

---

## Verified `func_rotatingdoor` (Rotating Door Entity)

```scr
// Spawn a rotating door from a brush model:
local.door = spawn func_rotatingdoor model "*2" targetname "door2" wait "-1" origin ( -264 534 456 ) angle ( 180 ) alwaysaway "1"

// Properties:
// model "*N"     = brush model index from map
// wait "-1"      = stay open (no auto-close)
// angle (Y)      = opening angle
// alwaysaway "1" = opens away from touching entity
```

---

## Verified `info_player_start` (Spawn Point Entity)

```scr
// Create a spawn point at runtime:
spawn info_player_start origin "814 -3969 518" angle "90"
spawn info_player_start origin "-1311 -3306 396" angle "143"

// Note: string-quoted args work for all spawn commands
// The engine will parse the string vectors/numbers
// DM modes will use these as random player spawn positions
```

---

## Verified `attachmodel` Full Syntax

```scr
// Full signature (more arguments than basic attach):
// self attachmodel model_path bone_name scale targetname_suffix use_angles pitch yaw roll pitchoffset yawoffset
self attachmodel local.model "Bip01 Head" 1.0 local.helmetname 1 -1 -1 -1 -1

// After spawn, the attached model gets targetname = parent.netname + suffix
// Access it via:
$( local.helmetname ).angles = ( -180 -90 -90 )

// simpler form:
local.p attachmodel "models/emitters/breath_steam_emitter.tik" "Bip01 Head"
```

---

## Verified Level Win/State Properties

```scr
// Set team victory flags (obj maps):
level.allieswin = 1    // trigger allied victory
level.axiswin   = 1    // trigger axis victory

// Round-based check:
if (level.roundbased)
    thread roundbasedthread

// Level time (read-only seconds since map load):
local.start  = level.time
local.elapsed = level.time - local.start

// Custom team tracking (associative):
level.players["allies"] = 0
level.players["axis"]   = 0
level.players[self.dmteam]++     // increment on join
level.players[self.dmteam]--     // decrement on leave
if (level.players["axis"] <= 0 || level.players["allies"] <= 0)
    thread check_win
```

---

## Verified Additional `stufftext` Commands

Full list of useful server→client commands via stufftext:

```scr
// Kick / disconnect:
self stufftext "disconnect"        // disconnect this player
self stufftext "quit"              // force quit client

// Change player appearance:
self stufftext ("set dm_playermodel " + local.model_name)  // change player model
self stufftext ("set dm_playergermanmodel german_army")     // force model (axis)
self stufftext ("set name " + local.new_name)              // change player name

// Client rendering:
self stufftext "r_fastsky 1"       // toggle fast sky rendering
self stufftext "r_fullscreen 0"    // windowed mode (admin abuse, avoid)

// UI:
self stufftext "popmenu"           // close current open menu
self stufftext "showmenu dday1"    // open named menu

// Key binding (for custom key-based mods):
self stufftext "bind F7 keyp 1001"   // bind F7 to keypress command
self stufftext "bind F8 keyp 1002"   // bind F8
// "keyp N" sends a key event readable server-side

// Music:
self stufftext "tmstop"
self stufftext ("tmstop;tmstart " + local.music_path)
```

---

## Verified Readable Entity Properties

Summary of entity properties confirmed readable in real mods:

```scr
self.origin       // (X Y Z) vector — current world position
self.angles       // (pitch yaw roll) — current rotation
self.model        // string — model path, e.g. "models/player/american_army.tik"
self.health       // int — current health (0 = dead)
self.dmteam       // string — "allies", "axis", "spectator", "ffa"
self.entnum       // int — unique entity number (assigned by engine)
self.scale        // float — current visual scale
self.velocity     // (X Y Z) — current velocity
self.forwardvector // (X Y Z) — forward direction unit vector
self.rightvector  // (X Y Z) — right direction unit vector
self.upvector     // (X Y Z) — up direction unit vector
self.viewangles   // (pitch yaw roll) — where the entity is looking
self.target       // string — targetname of linked target entity
self.size         // int (on arrays) — number of elements
self.weapon       // string — current weapon model path

// Confirmed NOT readable (not found in any mod):
// .netname — player's current name string (NOT confirmed)
// .ip      — player IP address (NOT confirmed)
```

---

## Verified `keypress` Callback System (Key Binding → Server Event)

MOHAA has a server-side callback called `keypress` that fires when a player presses a bound key:

```scr
// Step 1 — bind a key on the client to a keyp number:
self stufftext "bind F7 keyp 1001"
self stufftext "bind F8 keyp 1002"
self stufftext "bind G keyp 1003"

// Step 2 — define keypress label in your mod (engine calls it automatically):
keypress local.player local.keynum:
    if (local.player == NULL)
        end

    if (local.keynum == 1001)
        local.player exec global/AA/reward_market.scr

    else if (local.keynum == 1002)
        local.player exec global/AA/reward_store.scr

    else if (local.keynum == 1003)
        local.player thread use_jetpack
end

// keypress is a NAMED ENGINE CALLBACK — like spawn/death/connected
// The engine calls it with (player, keynum) args when keyp fires
// keynum is the number you put in "keyp NNNN" when binding
```

---

## Verified `parm.owner` (Third parm Property)

```scr
// parm.owner — entity that created/spawned this entity
// Most common use: projectiles know who fired them
self.attacker = parm.owner     // get the player who shot this projectile

// Full list of confirmed parm.* properties:
// parm.other          — other entity in trigger/collision event
// parm.previousthread — thread handle returned by waitthread
// parm.owner          — entity that created/owns this entity
```

---

## Verified `keyheld` Key Names (Vehicle/Jetpack Input)

Full list of key name strings for `self.driver.keyheld[KEY]`:

```scr
// Access as array with string key:
if (self.driver.keyheld["ELORE"]  == 1) { ... }    // forward (W)
if (self.driver.keyheld["HATRA"]  == 1) { ... }    // backward (S)
if (self.driver.keyheld["JOBBRA"] == 1) { ... }    // right (D)
if (self.driver.keyheld["BALRA"]  == 1) { ... }    // left (A)
if (self.driver.keyheld["SETA"]   == 1) { ... }    // walk/slow (shift or walk key)
if (self.driver.keyheld["JUMP"]   == 1) { ... }    // jump (space)
if (self.driver.keyheld["CROUCH"] == 1) { ... }    // crouch (C)

// Note: key names are Hungarian
// ELORE = forward, HATRA = backward, JOBBRA = right, BALRA = left, SETA = walk
// Can also use the simpler properties: fireheld, secfireheld, useheld
```

---

## Verified Full Vehicle Entry/Exit Pattern

Complete pattern from real working jeep mod:

```scr
// --- ENTRY CHECK (run in loop) ---
vehicle_check_entry:
while (1)
{
    waitframe
    for (local.i = 1; local.i <= $player.size; local.i++)
    {
        local.player = $player[local.i]
        if (local.player != NULL
            && local.player.dmteam != "spectator"
            && local.player.invehicule != 1
            && local.player.useheld
            && local.player istouching self
            && self.hasdriver != 1)
        {
            self thread playergetin local.player
        }
    }
}
end

// --- ENTER VEHICLE ---
playergetin local.player:
    self.hasdriver = 1
    self.driver    = local.player

    local.player.invehicule = 1
    local.player hide
    local.player notsolid
    local.player nodamage
    local.player glue self
    local.player forcetorsostate STAND
    self attachdriverslot 0 local.player

    // Show custom HUD for vehicle:
    local.player stufftext "showmenu dday2"
end

// --- DRIVE LOOP ---
vehicle_drive:
while (self.driver != NULL)
{
    waitframe

    if (self.driver.keyheld["ELORE"] == 1)
    {
        self.vehiclespeed += 0.04
        if (self.vehiclespeed > self.max_speed)
            self.vehiclespeed = self.max_speed
    }
    else if (self.driver.keyheld["HATRA"] == 1)
        self.vehiclespeed -= 0.03

    if (self.driver.keyheld["JOBBRA"])
        self turnrate  self.max_turnrate
    else if (self.driver.keyheld["BALRA"])
        self turnrate -self.max_turnrate
    else
        self turnrate 0

    // Exit on USE:
    if (self.driver.useheld)
    {
        thread playergetout self.driver
        end
    }
}
end

// --- EXIT VEHICLE ---
playergetout local.player:
    local.player unglue
    self detachdriverslot 0 local.player

    local.player.origin   = self.origin + angles_toleft self.angles * -65 + ( 0 0 32 )
    local.player.viewangles = ( 0 self.angles[1] 0 )

    local.player show
    local.player solid
    local.player takedamage
    local.player rendereffects "+shadow"
    local.player forcetorsostate STAND

    local.player stufftext "ui_removehud dday2"

    wait 1
    local.player.invehicule = 0
    self.driver    = NIL
    self.hasdriver = 0
end
```

---

## Verified Cvar Polling Command Bus Pattern

How mods implement server-wide broadcast commands without chat parsing (no `waittill say` exists):

```scr
// Admin sets a cvar from server console: set !all "give_item"
// Script polls it in a loop:

command_bus:
while (1)
{
    wait 0.5

    local.cmd_all    = getcvar "!all"
    local.cmd_allies = getcvar "!allies"
    local.cmd_axis   = getcvar "!axis"

    if (local.cmd_all != "")
    {
        // Apply to all players via per-player cvar:
        for (local.i = 1; local.i <= $player.size; local.i++)
        {
            local.key = "!" + $player[local.i].entnum
            setcvar local.key local.cmd_all
        }
        setcvar "!all" ""    // clear after reading
    }

    if (local.cmd_allies != "")
    {
        for (local.i = 1; local.i <= $player.size; local.i++)
        {
            if ($player[local.i].dmteam == "allies")
            {
                local.key = "!" + $player[local.i].entnum
                setcvar local.key local.cmd_allies
            }
        }
        setcvar "!allies" ""
    }
}
end

// Player-side: each player script reads its own cvar each frame:
player_cmd_loop:
while (1)
{
    waitframe
    self.cmdvar = getcvar ("!" + self.entnum)
    if (self.cmdvar != "")
    {
        setcvar ("!" + self.entnum) ""
        thread handle_command self.cmdvar
    }
}
end
```

---

## Verified `bind` / `glue` with Extra Property Pairs

Spawn and bind with additional properties in one line:

```scr
// spawn with property pairs after class name:
local.seat = spawn script_origin \
    "targetname" local.seat_name \
    origin ( local.vehicle.origin + ( -40 22 -5 ) ) \
    bind $(local.bindnode_id) \
    "spawnflags" "1" \
    "dmg" "0"

// glue with spawnflags:
local.bindnode glue local.vehicle "spawnflags" "1"

// bind to dynamic entity (variable contains targetname string):
local.obj bind $(local.parent_name)       // $(string) = entity lookup by targetname
```

---

## Verified `rendereffects` Flag Strings

```scr
// Add/remove render effect flags using string modifiers:
self rendereffects "+shadow"     // add shadow (default — restores after vehicle exit)
self rendereffects "-shadow"     // remove shadow
self rendereffects "+invisible"  // make invisible to other players
self rendereffects "-invisible"  // restore visibility

// Numeric form (bitfield):
self rendereffects 32    // specific effect by number
self rendereffects 0     // clear all effects

// stufftext variant (ui):
self stufftext "ui_removehud dday2"   // remove a named HUD element
```

---

## CRITICAL: Engine Callback System (Named Labels)

MOHAA calls specific label names automatically when game events occur.
These are NOT `waittill` — they are LABELS the engine invokes directly.
Define them at the top level of your global script (no `thread` needed).

```scr
// =============================================================
// FULL ENGINE CALLBACK REFERENCE
// =============================================================

// --- PLAYER CONNECTS ---
connected local.player:
    if (local.player == NULL)
        end
    if (local.player.classname != "Player")   // filter non-players
        end
    local.player.isplayer       = 1
    local.player.disable_spawn  = 0
    local.player.invehicule     = 0
    local.player.has_heatseeker = 0
    // Start any per-player loops here
    local.player thread player_cmd_loop
end

// --- PLAYER DISCONNECTS ---
disconnected local.player:
    if (local.player == NULL)
        end
    // Clean up player data, remove owned entities:
    if (local.player.has_heatseeker == 1)
        level.allies_heatseeker--
    // Remove any entities tied to this player
end

// --- PLAYER SPAWNS (fires on EVERY spawn, including respawns) ---
spawn local.player:
    if (local.player == NULL)
        end
    if (local.player.dmteam == "spectator")
        end
    local.player.player_spawned = 1
    local.player thread spawn_protect
    local.player thread give_class_weapons
end

// --- ENTITY RECEIVES DAMAGE ---
// Fires for players, vehicles, and any entity that can take damage
damage local.target local.inflictor local.damage local.position local.direction local.normal local.knockback local.damageflags local.meansofdeath local.location local.entity:
    if (local.entity == NULL)
        end
    if (local.entity.isplayer == 1)
        local.entity thread player_took_damage local.damage local.inflictor
end

// --- PLAYER IS KILLED ---
// Fires only when a player is killed by ANOTHER player
kill local.attacker local.damage local.inflictor local.position local.direction local.normal local.knockback local.damageflags local.meansofdeath local.location local.player:
    if (local.attacker == NULL)
        end
    if (local.player == local.attacker)
        end   // suicide — don't reward
    local.attacker.killcount++
    local.attacker thread check_rank_up
end

// --- PLAYER PRESSES BOUND KEY ---
keypress local.player local.keynum:
    if (local.player == NULL)
        end
    if (local.keynum == 1001)
        local.player exec global/market.scr
    else if (local.keynum == 1002)
        local.player exec global/store.scr
end

// --- MAP/GAME INTERMISSION (round/map end) ---
// local.type: 0 = player intermission screen, 1 = map change, 2 = map restart
intermission local.type:
    level.intermission_started = 1
    if (local.type == 1)
        thread global/save_scores.scr   // save before map change
end

// --- PLAYER RUNS A SERVER COMMAND ---
// Client executes: scmd needmedic  (or via keybind)
servercommand local.player local.command local.args:
    if (local.command == "needmedic")
        local.player thread request_medic
    else if (local.command == "revive")
        local.player thread request_revive
    else if (local.command == "build")
        local.player thread build_object local.args
end
```

### Callback Registration Note

These callbacks must be defined in a script file that the game EXECUTES on every map.
The standard approach — put them in `global/callbacksetup.scr` and exec it from your map script or ubersound override:

```scr
// In your global mod entry script:
main:
    level waittill prespawn
        exec global/callbacksetup.scr    // register all callbacks
    level waittill spawn
        thread mod_main
end
```

---

## Verified Full `level waittill` Event List

```scr
level waittill prespawn      // before any player spawns — register sounds, cache models
level waittill spawn         // all initial spawns done — initialize game state
level waittill roundstart    // round begins — start gameplay threads (every round)
level waittill allieswin     // allies team wins the round
level waittill axiswin       // axis team wins the round

// Note: roundend = doesn't exist separately; use allieswin/axiswin
// Note: allplayerspawned = doesn't exist; use level waittill spawn
```

---

## Verified Full Entity `waittill` Event List

```scr
// On any entity:
self waittill death           // entity/player died
self waittill trigger         // entity was triggered (touch/activate)
self waittill touch           // entity was physically touched
self waittill damage          // entity received damage (fires on any hit)

// On animated entities/actors:
self waittill animdone        // animation sequence completed
self waittill upperanimdone   // upper body animation completed
self waittill flaggedanimdone // animation reached a flagged frame

// On sound:
self waittill sounddone       // playsound finished playing
self waittill saydone         // voice dialog line finished

// On moving entities:
self waittill movedone        // moveto/movedown etc. completed
self waittill drive           // vehicle entered or exited (vehicle entities only)

// On weapons:
self waittill ontarget        // weapon aimed at target (sniper scope etc.)

// Confirm: NO `waittill say`, `waittill use`, `waittill roundend`, `waittill killed`
```

---

## Verified `damage` Callback Full Parameter List

The `damage` callback receives 11 parameters in order:

```scr
damage local.target local.inflictor local.damage local.position local.direction local.normal local.knockback local.damageflags local.meansofdeath local.location local.entity:
// local.target      — entity being damaged (the victim)
// local.inflictor   — entity that caused the damage (weapon/projectile)
// local.damage      — amount of damage (int)
// local.position    — (X Y Z) world position of the hit
// local.direction   — (X Y Z) direction the damage came from
// local.normal      — (X Y Z) surface normal at impact point
// local.knockback   — knockback force applied
// local.damageflags — bitfield of damage flags
// local.meansofdeath — int — damage type code (9 = explosion, etc.)
// local.location    — string — hit location ("head", "torso", "legs", etc.)
// local.entity      — the entity that was damaged (same as target usually)
end
```

---

## Verified `kill` Callback Full Parameter List

```scr
kill local.attacker local.damage local.inflictor local.position local.direction local.normal local.knockback local.damageflags local.meansofdeath local.location local.player:
// local.attacker    — player who made the kill
// local.damage      — damage amount that killed
// local.inflictor   — weapon/projectile used
// local.position    — position of death
// local.direction   — direction of killing shot
// local.normal      — surface normal
// local.knockback   — knockback force
// local.damageflags — damage type flags
// local.meansofdeath — damage type code
// local.location    — hit location string
// local.player      — player who died (the victim)

// Check for suicide:
if (local.player == local.attacker) end

// Check for team kill:
if (local.attacker.dmteam == local.player.dmteam) end
end
```

---

## Verified `trace` Full Return Dictionary

The `trace` command returns a dictionary (object) with these exact fields:

```scr
local.t = trace local.start local.end

local.t.fraction      // 0.0-1.0 — how far along the trace before hitting (1.0 = no hit)
local.t.endPos        // (X Y Z) vector — world position where trace stopped
local.t.entity        // entity hit (NULL if geometry)
local.t.surfaceFlags  // int bitfield — surface material flags
local.t.contents      // int bitfield — content flags (water, solid, etc.)
local.t.entityNum     // int — entnum of entity hit
local.t.allSolid      // 1 if trace started inside solid
local.t.startSolid    // 1 if start point is in solid
local.t.shaderNum     // shader index of surface hit
local.t.location      // hit location string ("head", "torso", "legs", etc.)

// Common pattern:
if (local.t.fraction < 1.0)
{
    local.hit = local.t.endPos
    if (local.t.entity != NULL)
        local.t.entity hurt 50 bullet
}
```

# Medal of Honor Allied Assault — Complete Modding Knowledge Base

> Three games: **AA** = main/, **SH** = mainta/ (Spearhead), **BT** = maintt/ (Breakthrough)
> Scripting language: **Morpheus Script** (.scr files)
> Extension: **SublimeMOHAA** (Package Control → MOHAA) for syntax highlighting, completions, tooltips

---

## 1. Game Versions & Directory Layout

| Short | Full Name         | Folder   | Exe                    | Engine DLL         |
|-------|-------------------|----------|------------------------|--------------------|
| AA    | Allied Assault    | main/    | MOHAA.exe              | system86.dll       |
| SH    | Spearhead         | mainta/  | moh_spearhead.exe      | system86ta.dll     |
| BT    | Breakthrough      | maintt/  | moh_Breakthrough.exe   | system86tt.dll     |

---

## 2. PK3 Priority System

Files are loaded in this order — **higher = wins**:

```
pak0 < pak1 < pak2 < pak3 < pak4 < pak5 < pak6 < pak7 < a_named.pk3 ... < z_named.pk3
```

- A `.pk3` is just a **ZIP file** renamed to `.pk3`
- To override any file, create `z_mymod.pk3` with your replacement inside
- `sv_pure 0` = clients do **NOT** download the server's extra pk3s (required for server-side mods)

---

## 3. Server-Side Mod — The Core Concept

```
sv_pure 0          â† set in server.cfg — clients never download your pk3
```

Your mod lives in `z_mymod.pk3` on the server only.  
Clients connect and play normally with zero downloads.

**What you need per game:**

| Game | Your pk3 goes in | Entry hook |
|------|-----------------|------------|
| AA   | main/           | global/DMprecache.scr |
| SH   | mainta/         | global/DMprecache.scr |
| BT   | maintt/         | global/DMprecache.scr |

---

## 4. Script Execution Flow (Every MP Map)

```
maps/mapname.scr → main:
    level waittill prespawn
    exec global/DMprecache.scr     â† YOUR HOOK — runs on every map, every game type
    exec global/ambient.scr
    level waittill spawn
    level waittill roundstart      â† only for round-based modes (obj, tow, lib)
end
```

`DMprecache.scr` already chains to:
```
exec global/DMSNakesServerPatch.scr
exec global/delator.scr
```

Add your mod at the end of `DMprecache.scr`:
```
exec global/mymod.scr
```

---

## 5. Morpheus Script — Full Language Reference

### 5.1 Variable Scopes

| Scope   | Lifetime        | Example         |
|---------|----------------|-----------------|
| `local` | Current thread | `local.x = 5`  |
| `level` | Current map    | `level.score = 0` |
| `game`  | Across maps    | `game.wins = 1` |
| `parm`  | Thread params  | `parm.value`    |
| `self`  | Current entity | `self.health`   |
| `group` | Thread group   | `group.id`      |

### 5.2 Entity References

```
$targetname          // entity with that targetname
$(local.varname)     // entity from dynamic string
$player              // all players (broadcast)
$player[n]           // specific player slot (1 to sv_maxclients)
$player.size         // total player slots
```

### 5.3 Full Syntax Grammar

```
// Control flow
if (expr) statement
if (expr) statement else statement
while (expr) statement
for (init; condition; step) statement
switch (expr) { case "val": ... break  default: ... break }
try { ... } catch { ... }
break
continue
goto label
end

// Function/label definition
mylabel:
    // code
end

mylabel local.param1 local.param2:
    // code
end

// Thread creation
thread label                        // same group as parent
thread filename::label              // new group
object thread label                 // object becomes self
object thread filename::label       // object becomes self, new group

// Execution
exec global/file.scr                // blocking, runs main:
exec global/file.scr::label         // blocking, runs specific label
waitthread global/file.scr::label   // blocking, waits for return
```

### 5.4 Operators (lowest to highest precedence)

```
||    logical or
&&    logical and
|     bitwise or
^     bitwise xor
&     bitwise and
== != equality / inequality
< > <= >=  comparison
+ -   add / subtract / string concat
* / % multiply / divide / modulus
```

Unary: `!` (not), `-` (negate), `~` (bitwise not)

### 5.5 Arrays

```
// Constant array (immutable, 1-indexed)
local.arr = entry1::entry2::entry3
println local.arr[1]    // "entry1"

// Hash table (dynamic)
local.data[hello][world] = 42
println local.data[hello][world]   // 42

// Targetname array (1-indexed, auto-created when multiple entities share a name)
$player[1]     // first player
$player.size   // count of all player slots

// Vector — access by index 0,1,2
local.v = (10 20 30)
println local.v[0]     // 10
$player.origin += (5 0 0)

// makeArray — multi-column array from block
local.paths = makeArray
node1  100  200
node2  150  250
node3  NIL  100
endArray
println local.paths[1][1]    // "node1"
println local.paths[1][2]    // "100"
```

### 5.6 Timing & Threading

```
wait 2.0           // pause 2 seconds
waitframe          // pause one engine frame
goto label         // infinite loop (no stack overflow)

// Loop pattern:
myloop:
    wait 1.0
    // do stuff
goto myloop
end
```

### 5.7 NULL and NIL

```
NIL    // uninitialized variable
NULL   // non-existent entity

if ($player[n] != NULL)   // player slot is occupied
if (local.x == NIL)       // variable was never set
```

---

## 6. Player Commands

### Reading Players

```
$player[n].dmteam        // "allies" | "axis" | "spectator" | "freeforall"
$player[n].entnum        // client ID number (integer)
$player[n].health        // current health
$player[n].origin        // position vector
$player[n].angles        // facing angles vector
$player.size             // total slots (not online count)
Isalive $player[n]       // 1 if alive, 0 if dead
$player[n] != NULL       // 1 if slot occupied
```

### Controlling Players

```
$player[n] stufftext "command"         // send console command to specific player
$player stufftext "command"            // send to ALL players

$player[n] join_team "allies"          // force team
$player[n] join_team "axis"
$player[n] join_team "spectator"

$player[n] take weapons/bazooka.tik    // remove weapon
$player[n] take weapons/panzerschreck.tik
$player[n] give weapons/m1_garand.tik  // give weapon

$player[n] stopwatch 5.0              // show timer bar (seconds)
$player[n] stopwatch 0                // hide timer bar

// Kill/damage
radiusdamage $player[n].origin 200 512   // radius damage
$player[n] damage 1000                   // direct damage (may vary)
```

### Player Inventory

```
$player item models/items/camera.tik     // give item
$player ammo pistol 30                   // give ammo (pistol/rifle/smg/mg/grenades/shotgun/heavy)
$player take weapons/shotgun.tik         // remove specific weapon
$player takeall                          // remove everything
```

---

## 7. Level Variables (Game Rules)

```
// Round settings
level.dmrespawning         // 1 = respawn on, 0 = round mode
level.dmroundlimit         // round time in minutes
level.clockside            // "axis" | "allies" | "kills" | "draw"

// Bomb settings (Objective mode)
level.bomb_tick_time       // seconds until bomb explodes (default 45)
level.bomb_set_time        // tenths of second to plant (default 50 = 5s)
level.bomb_defuse_time     // tenths of second to defuse (default 60 = 6s)
level.bomb_explosion_radius // quake units (default 1054)
level.bomb_damage          // explosion damage (default 200)
level.bomb_use_distance    // max use distance (default 128)
level.bombusefov           // FOV cone for use (default 30)
level.planting_team        // "allies" or "axis"
level.defusing_team        // opposite team
level.targets_to_destroy   // how many bombs to win
level.targets_destroyed    // current count
level.bombs_planted        // currently live bombs

// Win conditions
teamwin allies
teamwin axis
```

---

## 8. Messages & HUD

### Chat/Print Messages

```
iprintln "message"                    // small print, all players
iprintlnbold_noloc "message"          // bold print, all players
iprint "message"                      // no newline version
$player[n] iprint "message"           // print to specific player
println "debug text"                  // server console only
```

### HUD Drawing (up to 256 elements, index 0–255)

```
huddraw_shader    <index> <shader>
huddraw_align     <index> <h-align> <v-align>   // left/center/right, top/center/bottom
huddraw_rect      <index> <X> <Y> <width> <height>   // upper-left origin, 640x480 virtual
huddraw_virtualsize <index> <0|1>               // 1 = scale with resolution
huddraw_color     <index> <r> <g> <b>           // 0.0 to 1.0
huddraw_alpha     <index> <alpha>               // 0.0 = hidden, 1.0 = solid
huddraw_string    <index> "text"
huddraw_font      <index> <fontname>

// Per-player HUD (prefix with i)
ihuddraw_shader   <index> <shader>
ihuddraw_rect     <index> <X> <Y> <W> <H>
ihuddraw_string   <index> "text"
ihuddraw_alpha    <index> <alpha>

// Example: show score top-center
huddraw_shader    1 "textures/hud/score_bg"
huddraw_rect      1 270 10 100 20
huddraw_virtualsize 1 1
huddraw_alpha     1 0.8
huddraw_string    2 "Round: 1"
huddraw_rect      2 270 10 100 20
huddraw_font      2 "verdana-14"
```

---

## 9. CVars — Read & Set

```
getcvar(varname)             // returns string value
setcvar "varname" "value"    // set any cvar
int(getcvar(varname))        // cast to integer
```

### Most Useful Server CVars for Mods

```
sv_maxclients        // max player slots
sv_fps               // server simulation rate (default 20)
sv_pure              // 0 = allow server-only pk3s
sv_gravity           // world gravity (default 800)
sv_runspeed          // player run speed (default 250, SH=287)
sv_crouchspeedmult   // crouch speed multiplier (default 0.6)
sv_walkspeed         // walk speed (default 150)
sv_friction          // world friction (default 4)
sv_waterfriction     // water friction (default 1)
sv_waterspeed        // water movement speed (default 400)
sv_stopspeed         // deceleration (default 100)
sv_dmspeedmult       // DM speed multiplier (default 1.1)
mapname              // current map name (read-only)
g_gametype           // game type (see below)
g_teamdamage         // 1 = friendly fire on
g_maxplayerhealth    // max player health (default 750 — note: actually player has 100HP, this is a different thing)
g_forcerespawn       // seconds before auto-respawn
g_allowjointime      // seconds to join after round starts
roundlimit           // overall round limit
timelimit            // time limit in minutes
fraglimit            // frag limit
g_inactivekick       // seconds before kicking inactive player
```

### Game Types (g_gametype)

```
0 = Free For All (Deathmatch)
1 = Team Deathmatch
2 = Round-Based
3 = Objective (bomb plant/defuse)
4 = Tug-of-War (SH+)
5 = Capture & Hold (SH+)
6 = Liberation (BT only)
```

---

## 10. Scoreboard & Objective Text

```
setcvar "g_obj_alliedtext1" "Line 1 for allies"
setcvar "g_obj_alliedtext2" "Line 2 for allies"
setcvar "g_obj_alliedtext3" "Line 3 for allies"
setcvar "g_obj_axistext1"   "Line 1 for axis"
setcvar "g_obj_axistext2"   "Line 2 for axis"
setcvar "g_obj_axistext3"   "Line 3 for axis"
setcvar "g_scoreboardpic"   "objdm1"     // scoreboard image (no extension)
setcvar "g_gametypestring"  "My Mode"    // shown in server browser
```

---

## 11. Sound

```
self playsound soundalias              // play from entity position
self loopsound soundalias             // loop until stopped
self stoploopsound                    // stop loop
soundtrack "music/level.mus"          // play music track
forcemusic normal normal              // force music state (normal/aux1-aux6)
```

Sound channels (priority low→high):
- `auto` (0) — background, drops if no hardware channel
- `body` (1) — character body sounds
- `item` (2) — item/reload sounds
- `weaponidle` (3) — weapon hums
- `voice` (4) — speech/pain/death
- `local` (5) — player's own sounds
- `dialog` — mission dialog
- `music` — soundtrack

---

## 12. Entities & Spawning

```
// Spawn a model entity
local.ent = spawn script_model
local.ent.origin = (100 200 300)
local.ent model "models/weapons/m1_garand.tik"
local.ent solid
local.ent show

// Spawn with properties inline
local.ent = spawn script_model model "fx/explosion.tik" targetname "boom"

// Spawn origin (invisible anchor point)
local.anchor = spawn script_origin
local.anchor.origin = $player.origin

// Delete entity
local.ent remove
local.ent hide
local.ent notsolid
```

---

## 13. Weapons List (All Versions)

### AA / SH / BT Base Weapons
| File | Name |
|------|------|
| `weapons/colt45.tik` | Colt .45 Pistol |
| `weapons/p38.tik` | P38 Pistol |
| `weapons/silencedpistol.tik` | Silenced Pistol |
| `weapons/m1_garand.tik` | M1 Garand |
| `weapons/kar98.tik` | Kar98k |
| `weapons/kar98sniper.tik` | Kar98 Sniper |
| `weapons/springfield.tik` | Springfield Sniper |
| `weapons/thompsonsmg.tik` | Thompson SMG |
| `weapons/mp40.tik` | MP40 |
| `weapons/mp44.tik` | MP44 |
| `weapons/bar.tik` | BAR |
| `weapons/bazooka.tik` | Bazooka |
| `weapons/panzerschreck.tik` | Panzerschreck |
| `weapons/shotgun.tik` | Shotgun |
| `weapons/m2frag_grenade.tik` | M2 Frag Grenade |
| `weapons/steilhandgranate.tik` | Stielhandgranate |

### SH / BT Extra Weapons
```
weapons/enfield.tik
weapons/G43.tik
weapons/M18_smoke_grenade.tik
weapons/mg42carryable.tik
weapons/mills_grenade.tik
weapons/Mosin_Nagant_Rifle.tik
weapons/Nagant_revolver.tik
```

---

## 14. Player Models

### Allied
```
allied_airborne, allied_manon, allied_oss, allied_pilot,
american_army, american_ranger, allied_sas (BT only)
```

### German
```
german_afrika_officer, german_afrika_private,
german_elite_gestapo, german_elite_sentry, german_elite_officer (BT),
german_kradshutzen,
german_panzer_grenadier, german_panzer_obershutze, german_panzer_shutze, german_panzer_tankcommander,
german_scientist,
german_waffenss_officer, german_waffenss_shutze,
german_Wehrmacht_officer, german_Wehrmacht_soldier,
german_winter1, german_winter2, german_worker
```

---

## 15. Map Names

### AA — DM Maps
```
dm/mohdm1   Southern France
dm/mohdm2   Destroyed Village
dm/mohdm3   Harbor
dm/mohdm4   Colmar Pocket
dm/mohdm5   Malta
dm/mohdm6   Stalingrad
dm/mohdm7   Gewitter
```

### AA — Objective Maps
```
obj/obj_team1   The Hunt (Flak 88)
obj/obj_team2   V2 Rocket Facility
obj/obj_team3   Omaha Beach
obj/obj_team4   Bridge
```

### SH — DM Maps
```
dm/MP_Bahnhof_DM, dm/MP_Bazaar_DM, dm/MP_Brest_DM,
dm/MP_Gewitter_DM, dm/MP_Holland_DM, dm/MP_Stadt_DM,
dm/MP_Unterseite_DM, dm/MP_Verschneit_DM
```

### SH — TOW/Objective Maps
```
obj/MP_Ardennes_TOW, obj/MP_Berlin_TOW,
obj/MP_Druckkammern_TOW, obj/MP_Flughafen_TOW,
obj/obj_team1, obj/obj_team2, obj/obj_team3, obj/obj_team4
```

### BT — DM Maps (same DM as SH plus)
```
dm/MP_Malta_DM, dm/MP_Palermo_DM
```

### BT — Objective / TOW Maps
```
obj/MP_Bologna_OBJ, obj/mp_castello_obj,
obj/MP_Kasserine_TOW, obj/MP_MonteBattaglia_TOW,
obj/MP_MonteCassino_TOW, obj/MP_Palermo_OBJ,
obj/MP_StreetsOfMessina_TOW
```

### BT — Liberation Maps
```
lib/mp_anzio_lib, lib/mp_bizerteharbor_lib,
lib/mp_tunisia_lib
```

---

## 16. Game Mode Logic Scripts

| Mode | Script | Game |
|------|--------|------|
| Bomb/Objective | `global/obj_dm.scr` | AA, SH, BT |
| Tug of War | `global/tow_dm.scr` | SH, BT |
| Liberation | `global/lib_dm.scr` | BT only |
| Capture & Hold | `global/obj_capture.scr` | SH |
| Ambient/Music | `global/ambient.scr` | All |
| Precache hook | `global/DMprecache.scr` | All |

---

## 17. Objectives System

```
waitthread global/objectives.scr::reset_objectives
waitthread global/objectives.scr::blank_objectives
waitthread global/objectives.scr::add_objectives <idx> <attr> <text>
    // attr: 1=hidden, 2=unchecked, 3=checked
waitthread global/objectives.scr::current_objectives <idx>
```

---

## 18. Camera Control

```
spawn Camera targetname MyCam
cuecamera $MyCam 1.0        // switch to camera (1s blend)
cueplayer 1.0               // return to player view
$MyCam start
$MyCam pause
$MyCam continue
$MyCam stop
$MyCam speed 200
$MyCam fov 90 1.0           // fov, fade time
$MyCam follow $player 1.0
$MyCam orbit $target
$MyCam watch $target 0.5
```

---

## 19. Medals

```
setcvar "g_medal0" "1"     // Infantry Assault
setcvar "g_medal1" "1"
setcvar "g_medal2" "1"
setcvar "g_medal3" "1"
setcvar "g_medal4" "1"
setcvar "g_medal5" "1"
setcvar "g_eogmedal0" "1"  // end-of-game medals
setcvar "g_eogmedal1" "1"
setcvar "g_eogmedal2" "1"
```

---

## 20. Cheat-Protected CVars (Anti-cheat targets)

CVars marked `C` in cvar list = cheat protected. Push safe values to clients:

```
$player stufftext ("setu r_fullbright 0")
$player stufftext ("setu r_lockpvs 0")
$player stufftext ("setu r_novis 0")
$player stufftext ("setu cg_3rd_person 0")
$player stufftext ("setu r_lightmap 0")
$player stufftext ("setu r_showtris 0")
$player stufftext ("setu r_shownormals 0")
$player stufftext ("setu cg_acidtrip 0")
$player stufftext ("setu r_farplane 0")
$player stufftext ("setu r_farplane_nocull 0")
$player stufftext ("setu r_farplane_nofog 0")
$player stufftext ("setu ib_wallhack 0")
$player stufftext ("setu ib_doaim 0")
$player stufftext ("setu g_showbullettrace 0")
```

---

## 21. Level Events You Can Wait For

```
level waittill prespawn        // before entities exist
level waittill spawn           // map fully loaded
level waittill roundstart      // round begins (round-based only)
level waittill allieswin       // allies won the round
level waittill axiswin         // axis won the round
level waittill draw            // round ended in draw
self waittill trigger          // this entity was triggered
self waittill animdone         // animation finished
self waittill death            // entity died
```

---

## 22. Math & String Functions

```
int(value)                  // cast to integer
float(value)                // cast to float
randomfloat N               // random float 0 to N
randomint N                 // random integer 0 to N-1
sqrt(x), sin(x), cos(x)
abs(x), ceil(x), floor(x)
"hello" + " world"          // string concatenation with +

// String character access (0-indexed)
"abc"[0]    // "a"
"abc"[2]    // "c"
```

---

## 23. Debug Commands (via console or stufftext)

```
sv_showentnums 1         // show entity numbers above entities
sv_showbboxes 1          // show bounding boxes
g_entinfo 1              // entity info overlay
g_showbullettrace 1      // show bullet traces
whereami                 // print player coords and yaw
testthread global/myscript.scr::mylabel   // run thread from console
println "message"        // print to server console
dprintln "message"       // print only in developer mode
g_scripttrace 1          // trace script execution
g_scriptdebug 1          // script debug output
developer 1              // enable developer mode
```

---

## 24. Complete Mod Template

### `z_mymod.pk3` structure:
```
z_mymod.pk3
â”œâ”€â”€ global/
â”‚   â”œâ”€â”€ DMprecache.scr    (copy of original + exec global/mymod.scr at end)
â”‚   â””â”€â”€ mymod.scr         (your mod — server only, clients never see this)
```

### `global/mymod.scr`:

```
main:
    // Guard: only run if mod is enabled in server.cfg
    if (getcvar(mymod) != "1")
        end

    level waittill spawn

    // --- Set game rules ---
    level.bomb_tick_time   = 30
    level.bomb_set_time    = 30
    level.bomb_defuse_time = 50
    level.dmroundlimit     = 7

    // --- Scoreboard text ---
    setcvar "g_gametypestring" "My Mod v1.0"

    // --- Start background threads ---
    thread mod_announce
    thread mod_player_rules
    thread mod_anticheat
end


mod_announce:
    wait 15.0
    iprintlnbold_noloc ("Welcome! My Custom Server")
    wait 5.0
    iprintlnbold_noloc ("No bazooka. Fair play.")
    wait 160.0
goto mod_announce
end


mod_player_rules:
    wait 1.0
    if ($player == NULL)
        goto mod_player_rules

    local.maxp   = int(getcvar(sv_maxclients))
    local.allies = 0
    local.axis   = 0

    // Count teams
    for (local.i = 1; local.i <= local.maxp; local.i++) {
        if ($player[local.i] != NULL) {
            if ($player[local.i].dmteam == "allies") local.allies++
            if ($player[local.i].dmteam == "axis")   local.axis++
        }
    }

    // Enforce rules per player
    for (local.i = 1; local.i <= local.maxp; local.i++) {
        if ($player[local.i] != NULL) {

            // Remove bazooka
            $player[local.i] take weapons/bazooka.tik
            $player[local.i] take weapons/panzerschreck.tik

            // Auto-join spectators
            if ($player[local.i].dmteam == "spectator") {
                $player[local.i] stufftext ("primarydmweapon smg")
                wait 0.5
                if (local.axis >= local.allies) {
                    $player[local.i] join_team "allies"
                } else {
                    $player[local.i] join_team "axis"
                }
            }
        }
    }

goto mod_player_rules
end


mod_anticheat:
    wait 5.0
    if ($player != NULL) {
        $player stufftext ("setu r_fullbright 0")
        waitframe
        $player stufftext ("setu r_novis 0")
        waitframe
        $player stufftext ("setu cg_3rd_person 0")
        waitframe
        $player stufftext ("setu r_lightmap 0")
        waitframe
        $player stufftext ("setu ib_wallhack 0;setu ib_doaim 0")
    }
goto mod_anticheat
end
```

### `server.cfg` additions:
```
set mymod "1"
sv_pure "0"
```

---

## 25. PK3 Packaging (Windows)

1. Create folder structure: `global/DMprecache.scr` + `global/mymod.scr`
2. Select both folders → right-click → **Send to → Compressed (zip) folder**
3. Rename the `.zip` to `z_mymod.pk3`
4. Drop into `main/` (AA), `mainta/` (SH), or `maintt/` (BT)

**Tool:** `pakscape.exe` (in tutorials pack Tools/) — GUI pk3 manager

---

## 26. Key Reference Files (this machine)

| File | Location |
|------|----------|
| Script syntax | `MOHAA_TUTORIALS_PACK_V1.4\Tutorials\ModTheater Tuts\Script_Files.txt` |
| SDK cvar list | `MOHAA_TUTORIALS_PACK_V1.4\Tutorials\Lists of Commands, CVARS & Settings\MOHAA - SDK.txt` |
| Game classes | `MOHAA_TUTORIALS_PACK_V1.4\Tutorials\Lists of Commands, CVARS & Settings\Game_Module_Classes\` |
| Script docs | `MOHAA_TUTORIALS_PACK_V1.4\Tutorials\MOH SDK Documents\Server & Game Reference\MOH Miscellaneous Script Documentation.html` |
| AI docs | `MOHAA_TUTORIALS_PACK_V1.4\Tutorials\MOH SDK Documents\Server & Game Reference\MOH_AI_tips.html` |
| Game classes HTML | `MOHAA_TUTORIALS_PACK_V1.4\Tutorials\MOH SDK Documents\Server & Game Reference\MOH_GameClasses.html` |
| HUD scripting | `MOHAA_TUTORIALS_PACK_V1.4\Tutorials\The Rjukan Project\...\Script Commands - huddraw.txt` |
| SublimeMOHAA | https://github.com/eduzappa18/SublimeMOHAA |

---

## 27. SublimeMOHAA Extension

**Language name:** Morpheus Script  
**Install:** Package Control → Install Package → search "MOHAA"  
**File associations:** `.scr`, `.cfg`, `.tik`, `.mus`, `.st`, `.shader`, `.urc`, `.log`

**Features:**
- Syntax highlighting for all 8 file types
- 1,600+ autocompletions for Morpheus commands
- 260+ entity property completions
- 1,287 model path completions
- Hover tooltips with function docs (AA / SH / BT / Reborn versions)
- 15 snippets: if, for, while, switch, for_player_loop, huddraw_*, makearray, if_getcvar

**Level phase completions:**
```
prespawn, spawn, postthink, playerspawn,
roundstart, allieswin, axiswin, draw
```

---

## 28. Important Notes

- Spaces matter in vectors: `( -1 2 3 )` not `(-1 2 3)` — the space after `(` before `-` is required
- `goto` is the proper loop mechanism — not `while(1)` (though both work)
- `$player` without index = broadcast to ALL players
- `$player[n]` index starts at **1**, not 0
- `$player.size` = max slots, not online count — always check `!= NULL`
- Higher pak numbers always win — your `z_mymod.pk3` overrides pak7
- `DMprecache.scr` runs on **every** map load — it is the universal hook
- Scripts run server-side only — clients never execute `.scr` files
- `sv_pure 0` is **mandatory** for server-side mods to work

---

## 29. waitexec — Return Values & Data Files

`exec` fires a script and returns nothing.  
`waitexec` fires a script, **waits for it to finish**, and returns a value.

```
// Call a script that returns a value
local.result = waitexec global/get_game.scr

// Read a .txt file as a data array (each line = element)
local.list = waitexec settings/Mods.txt
// local.list[1] = first line, local.list.size = line count
```

A `.txt` file read by `waitexec` returns a constant array — same as `::` syntax but sourced from a file. This lets you store config outside the pk3 as editable text files.

```
// settings/Mods.txt example:
KillStreaks on
JetPack off
AntiCamper on
DeathCam on

// In script:
local.mods = waitexec settings/Mods.txt
for (local.i = 1; local.i <= local.mods.size; local.i++) {
    // local.mods[local.i] = one line e.g. "KillStreaks on"
}
```

---

## 30. Game Version Detection

Use the `version` cvar — different character positions spell out the game name.

```
// global/get_game.scr pattern (from UBER-MODS):
local.ver = getcvar "version"

// version string examples:
// AA: "Medal of Honor Allied Assault 1.11"
// SH: "Medal of Honor Allied Assault: Spearhead 2.15"
// BT: "Medal of Honor Allied Assault: Breakthrough 2.40b"

// Character at index 15 (or 16 if there is a space) distinguishes them:
// AA → 'A', SH → 'S', BT → 'B'
local.ch = local.ver[15]
if (local.ch == " ")
    local.ch = local.ver[16]

if (local.ch == "A") {
    game.game = "AA"
    setcvar "g_statefile" "global/nagle_aa"
}
else if (local.ch == "S") {
    game.game = "SH"
    setcvar "g_statefile" "global/nagle_sh"
}
else if (local.ch == "B") {
    game.game = "BT"
    setcvar "g_statefile" "global/nagle_bt"
}
```

`game.game` persists across maps. Check it anywhere with `game.game == "AA"`.

---

## 31. String Library (global/strings.scr)

UBER-MODS includes a full string utility library. Call with `waitexec`:

```
// Left(string, count) — first N characters
local.s = waitexec global/strings.scr::Left "Hello World" 5
// → "Hello"

// Right(string, count) — last N characters
local.s = waitexec global/strings.scr::Right "Hello World" 5
// → "World"

// Mid(string, start, count) — substring (0-indexed start)
local.s = waitexec global/strings.scr::Mid "Hello World" 6 5
// → "World"

// InStr(string, search) — position of substring (-1 if not found)
local.pos = waitexec global/strings.scr::InStr "Hello World" "World"
// → 6

// to_lower / to_upper
local.s = waitexec global/strings.scr::to_lower "HELLO"
// → "hello"

// trim — remove leading/trailing spaces
local.s = waitexec global/strings.scr::trim "  hello  "

// replace(string, find, replace_with)
local.s = waitexec global/strings.scr::replace "Hello World" "World" "MOHAA"

// split_string(string, delimiter) — returns array
local.parts = waitexec global/strings.scr::split_string "a,b,c" ","
// local.parts[1]="a", [2]="b", [3]="c"

// team_count — returns axis count :: allies count
local.counts = waitexec global/strings.scr::team_count
local.axis   = int(local.counts[1])
local.allies = int(local.counts[2])
```

---

## 32. Settings / Data-Driven Mod Config

Pattern from UBER-MODS `global/settings.scr`:

```
// settings/Mods.txt (plain text, each line: ModName on|off)
KillStreaks on
JetPack off
AntiCamper on
DeathCam on
RunSpeed off

// In global/settings.scr:
main:
    local.mods = waitexec settings/Mods.txt
    for (local.i = 1; local.i <= local.mods.size; local.i++) {
        local.line  = local.mods[local.i]
        local.name  = waitexec global/strings.scr::Left  local.line (waitexec global/strings.scr::InStr local.line " ")
        local.state = waitexec global/strings.scr::Right local.line 2
        if (local.state == "on")
            level.run[local.name] = 1
        else
            level.run[local.name] = 0
    }
end
```

Check any mod anywhere: `if (level.run["KillStreaks"] == 1)`.

### Cvar-driven override pattern:
```
// on_or_off local.modname:
// reads cvar g_<modname>, falls back to Mods.txt setting
on_or_off local.modname:
    local.cv = getcvar ("g_" + local.modname)
    if (local.cv == "1")
        level.run[local.modname] = 1
    else if (local.cv == "0")
        level.run[local.modname] = 0
    // else leave as Mods.txt value
end
```

### Map filter pattern (run mod only on specific maps):
```
// check_maplist local.modname local.allowed_maps:
// local.allowed_maps = "mohdm1::mohdm2::obj_team1"
check_maplist local.modname local.maps:
    local.current = waitexec global/strings.scr::get_mapstr
    for (local.i = 1; local.i <= local.maps.size; local.i++) {
        if (local.maps[local.i] == local.current) end
    }
    level.run[local.modname] = 0   // disable — map not in list
end
```

---

## 33. Mod Registry & spawn_scripts Pattern

From UBER-MODS advanced architecture:

```
// Register a console command in game.all_commands array
// game.all_commands[local.cmd] = script_path::label
game.all_commands["jetpack"]   = "global/jetpack.scr::give_jetpack"
game.all_commands["killme"]    = "global/admin.scr::kill_player"

// Dispatch command handler
check_command local.cmd:
    if (game.all_commands[local.cmd] != NIL)
        thread waitexec game.all_commands[local.cmd]
end

// spawn_scripts — run a script on player spawn
// game.spawn_scripts is an array of script labels to call after each spawn
game.spawn_scripts[game.spawn_scripts.size + 1] = "global/jetpack.scr::on_spawn"
```

### level.run[] hash (active mod flags):
```
level.run["KillStreaks"] = 1     // mod is active
level.run["JetPack"]     = 0     // mod is disabled
level.run["AntiCamper"]  = 1

// Check anywhere:
if (level.run["KillStreaks"] == 1)
    thread global/killstreaks.scr::main
```

---

## 34. Map Name Variables

```
level.mapname        // full map path e.g. "obj/obj_team2"
level.map_shortname  // short name e.g. "obj_team2"
level.map_specific   // 1 if this map has a specific override script

// Get short name manually:
local.full = getcvar "mapname"
// strip "dm/" or "obj/" prefix using strings.scr:
local.slash = waitexec global/strings.scr::InStr local.full "/"
local.short = waitexec global/strings.scr::Right local.full (local.full.size - local.slash - 1)
```

---

## 35. State Machine Files (.st)

MOHAA supports `.st` state machine files that define player animation/physics states.  
`g_statefile` cvar points to the active state file (no extension).

```
setcvar "g_statefile" "global/nagle_aa"   // use nagle_aa.st
setcvar "g_statefile" "global/nagle_sh"   // SH movement feel
setcvar "g_statefile" "global/nagle_bt"   // BT movement feel
```

UBER-MODS ships separate state files per game version:
```
global/nagle_aa_legs.st   global/nagle_aa_torso.st
global/nagle_sh_legs.st   global/nagle_sh_torso.st
global/nagle_bt_legs.st   global/nagle_bt_torso.st
global/mike.st            global/mike_legs.st    global/mike_torso.st
```

State files control: movement speed profiles, crouch transitions, prone behaviour, animation blend trees. Changing `g_statefile` mid-game takes effect on next spawn.

---

## 36. UBER-MODS Custom CVars

These CVars are added/used by the UBER-MODS system. Useful reference for your own mods:

### Game control
```
g_ubergametype      // extended game type number (UBER-MODS internal)
g_ubermods          // comma-separated list of active uber mods
g_uberhardcode      // hardcoded settings string
g_deathcam          // 1 = enable deathcam after death
g_throwingknives    // 1 = enable throwing knives
```

### Admin commands (server-side console or rcon)
```
addkills    <entnum> <n>     // add N kills to player
adddeaths   <entnum> <n>     // add N deaths to player
hacker_kill <entnum>         // kill player marked as cheater
players                       // list all connected players with entnums
teams                         // show team counts
score                         // show current scores
coord2                        // print player coordinates
entity_pointer <entnum>       // dump entity properties
findent <classname>           // find entities of class
findclass <classname>         // same as findent
```

### Weather system (client-side effect via stufftext)
```
cg_weather          // 0=off 1=rain 2=snow 3=sandstorm
cg_weather_density  // particles per second (default 500)
cg_rain_volume      // rain audio volume (0.0–1.0)
cg_thunder          // 1 = enable thunder sounds

// Push weather to all clients:
$player stufftext ("setu cg_weather 1")
$player stufftext ("setu cg_weather_density 800")
$player stufftext ("setu cg_rain_volume 0.7")
$player stufftext ("setu cg_thunder 1")
```

---

## 37. Advanced Gameplay Systems (from UBER-MODS)

### Kill Streaks (global/killstreaks.scr)

Track kills per player and reward at thresholds:

```
// Pattern:
killstreak_check local.player:
    local.player.streak++
    if (local.player.streak == 3) {
        iprintln (local.player.name + " is on a KILLING SPREE!")
        local.player give weapons/bazooka.tik
    }
    if (local.player.streak == 5) {
        iprintln (local.player.name + " is UNSTOPPABLE!")
        // give ammo or call airstrike
    }
end

// Reset on death:
on_player_death local.player:
    local.player.streak = 0
end
```

### Jetpack (global/jetpack.scr)

```
// Give jetpack to a player:
$player[n] stufftext ("setu cg_jetpack 1")
// Remove:
$player[n] stufftext ("setu cg_jetpack 0")

// Jetpack uses sv_gravity manipulation:
// setcvar "sv_gravity" "200"   â† lighter gravity while active
// Detected server-side by watching vertical velocity changes
```

### Parachute (global/attachparachute.scr / detachparachute.scr)

```
// Attach parachute model to player:
local.chute = spawn script_model
local.chute model "models/parachute.tik"
local.chute.origin = $player[n].origin
local.chute attach $player[n] "Bip01 Spine2"

// Remove parachute:
local.chute detach
local.chute remove

// UBER-MODS also has steerable_chute.scr for directional control
```

### Anti-Camper System (global/anti_camper.scr)

```
// Pattern — detect player not moving for N seconds:
anti_camper_check local.player:
    local.lastpos = local.player.origin
    wait 10.0
    if (local.player.origin == local.lastpos) {
        // Player hasn't moved in 10s — warn then punish
        local.player iprint "Move or be punished!"
        wait 5.0
        if (local.player.origin == local.lastpos) {
            // spawn a camper_turret near them
            local.turret = spawn script_model
            local.turret.origin = local.player.origin + (0 0 50)
            local.turret thread global/camper_turret.scr::fire local.player
        }
    }
end
```

### Death Camera (global/deathcam.scr)

```
// Show killer's perspective after death for N seconds:
on_death local.victim local.killer:
    if (getcvar(g_deathcam) != "1") end
    if (local.killer == NULL) end
    local.victim stufftext ("setu cg_3rd_person 1")
    // camera follows killer for 3 seconds
    wait 3.0
    local.victim stufftext ("setu cg_3rd_person 0")
end
```

### Respawn Fixes (global/respawn_fix.scr / respawn_stuck_fix.scr)

```
// MOHAA bug: players can get stuck in spawn points after round restart
// Fix: brief delay + teleport to valid origin if stuck in solid
respawn_fix local.player:
    wait 0.5
    if (local.player == NULL) end
    // check if player is inside geometry
    if (local.player.groundentity == NULL && !Isalive local.player)
        local.player.origin = local.player.origin + (0 0 10)
end
```

### Throwing Knives

```
// Spawn a knife projectile from player position toward aim direction:
throw_knife local.player:
    local.knife = spawn script_model
    local.knife model "models/weapons/knife.tik"
    local.knife.origin = local.player.origin + (0 0 40)
    local.knife velocity = (local.player.angles[0] * 800)
    local.knife solid
    wait 5.0
    local.knife remove
end
```

---

## 38. Vehicle Scripts (UBER-MODS Vehicles)

Full drivable vehicles implemented entirely in Morpheus Script:

```
// global/playertank.scr   — Panzer tank
// global/playerboat.scr   — Boat
// global/playerflak88.scr — Flak 88 AA gun (static, rotatable)
// global/playernebelwerfer.scr — Rocket launcher
// global/playervehicle.scr    — Generic vehicle base

// Enter vehicle (player walks into trigger):
vehicle_enter local.player:
    local.vehicle.driver = local.player
    local.player stufftext ("setu g_noclip 1")   // temporary, for vehicle motion
    local.player.origin = local.vehicle.origin + (0 0 30)
    thread vehicle_control local.vehicle local.player
end

// Vehicle control loop:
vehicle_control local.vehicle local.player:
    while (local.vehicle.driver != NULL) {
        // read player input direction, move vehicle entity
        local.vehicle.origin += (local.player.angles * local.vehicle.speed)
        waitframe
    }
end
```

---

## 39. HUD Elements in Use (Tracking)

UBER-MODS tracks which HUD element indices are taken to avoid conflicts between mods.

**UBER-MODS HUD index allocation (reference):**
```
0–9    Reserved for game engine
10–19  KillStreaks display
20–29  Weather overlay
30–39  DeathCam timer
40–49  Admin messages
50–59  Jetpack fuel gauge
100+   Free for custom use
```

Use the `ihuddraw_*` variants for per-player HUD to avoid overwriting global HUD:
```
// Per-player (safe for multiple players):
$player[n] ihuddraw_shader   50 "textures/hud/fuel_bg"
$player[n] ihuddraw_rect     50 10 400 100 15
$player[n] ihuddraw_alpha    50 0.7
$player[n] ihuddraw_string   51 "Fuel: 80%"
$player[n] ihuddraw_rect     51 10 400 100 15
$player[n] ihuddraw_font     51 "facfont-20"

// Hide element:
$player[n] ihuddraw_alpha 50 0
```

---

## 40. PK3 Naming — Maximum Priority

To guarantee your mod loads **after** everything else (including other named pk3s):

```
zzzzzzzzzzzzzzz_mymod.pk3    â† wins over z_anything.pk3
```

UBER-MODS uses `zzzzzzzzzzzzzzz_` prefix. A single `z_` prefix wins over pak0–pak7 but loses to `zz_` or longer z-prefixed names if two mods compete.

**Recommended naming strategy:**
```
z_mymod.pk3              // safe for solo modding
zz_mymod.pk3             // beats z_* mods
zzzzzzzzzzzzzzz_mymod.pk3 // maximum — nothing overrides this
```

---

## 41. UBER-MODS Architecture Summary

Understanding the full UBER-MODS v8.00 execution pipeline helps when building complex mods:

```
DMprecache.scr
â””â”€ exec global/settings.scr           â† loads Mods.txt, populates level.run[]
   â”œâ”€ exec global/get_game.scr        â† sets game.game = "AA"/"SH"/"BT"
   â”‚   â””â”€ setcvar g_statefile         â† correct movement state per game
   â”œâ”€ exec global/strings.scr         â† string library (loaded once, called via waitexec)
   â”œâ”€ exec global/math.scr            â† math library
   â””â”€ exec global/mod_inform.scr      â† tells players which mods are active

   Per-mod dispatching (if level.run["ModName"] == 1):
   â”œâ”€ thread global/killstreaks.scr::main
   â”œâ”€ thread global/jetpack.scr::main
   â”œâ”€ thread global/anti_camper.scr::main
   â”œâ”€ thread global/deathcam.scr::main
   â”œâ”€ thread global/weather.scr::main
   â””â”€ thread global/vehicles/playertank.scr::main

   Player spawn hook:
   â””â”€ game.spawn_scripts[] → run for each player spawn
```

**Key design principles used:**
1. **Data outside code** — `settings/Mods.txt` controls which mods run; edit without repackaging
2. **level.run[] as feature flags** — one hash, check anywhere, flip remotely via cvar
3. **game.all_commands registry** — maps console command strings to script labels
4. **waitexec for return values** — enables function-like patterns in Morpheus Script
5. **game.game for portability** — single pk3 works across AA/SH/BT by branching on game version
6. **"zzzzzzzzzzzzzzz_" pk3 prefix** — guaranteed last-to-load, overrides everything

---

## 42. Entity Commands — Transform, Physics, Visuals

### Scale
```
local.object.scale = 2          // double size
$player[n].scale = 0.5          // shrink player (midget)
$player[n].scale = 6            // giant
// Save/restore:
local.player.oldscale = local.player.scale
local.player.scale = 0.5
wait 120
local.player.scale = local.player.oldscale
```

### Dynamic Light on Entity
```
local.object light 0 1 0 65     // green light, radius 65
local.object light 1 0 0 250    // red light, radius 250
local.object light 1 1 1 1      // remove/reset light
$player[n] light 0 1 0 85       // light attached to player
```

### Render Effects (flags)
```
local.object rendereffects "+lensflare"          // add lens flare
local.object rendereffects "-shadow"             // remove shadow
local.object rendereffects "+additivedynamiclight"  // additive dynamic lighting
```

### Entity.svflags (network broadcast)
Dynamically spawned entities are not sent to clients unless forced:
```
local.beam svflags "+broadcast"    // make visible to all players
```

### Angle vs Angles
```
local.object angle 90          // set yaw only (shorthand)
local.object.angles = (0 90 0) // set full pitch yaw roll
```

### Collision & Damage
```
local.ent solid          // enable collision
local.ent notsolid       // disable collision
local.ent nodamage       // immune to damage
local.ent takedamage     // restore damage
```

### Physics
```
local.can physics_off    // freeze (no gravity/collisions)
local.can physics_on     // restore physics
```

### Velocity (instant impulse)
```
local.can.velocity = ( (500 - (randomint(1000))) (500 - (randomint(1000))) (500 + (randomint(100))) )
```

### Instant Rotation (spin object without waiting)
```
local.can rotatex 90     // rotate around X by 90°
local.can rotatey 45
local.can rotatez 180
// These apply a continuous spin rate, not a one-shot rotation
```

### Timed Rotation (for doors)
```
$door time 1.0                // duration in seconds
$door rotateydown 85          // rotate Y axis 85° downward
$door waitmove                // block until done

$door rotateyup 85            // rotate Y axis 85° upward
$door rotatexdown 90          // rotate X axis 90° down

// Shorthand helper label (common pattern):
rotatedown local.amount:
    self rotateydown local.amount
    self waitmove
end
rotateup local.amount:
    self rotateyup local.amount
    self waitmove
end
```

### Timed Movement (entity movers)
```
local.seat time 10                   // movement duration in seconds
local.seat moveto ( x y z )          // target position
local.seat waitmove                  // block thread until arrival
local.seat moveup 3000               // move up by units

// Multi-waypoint path (roller coaster pattern):
local.seat time 10
local.seat moveto ( 5800 -4000 1600 )
local.seat waitmove
local.seat time 2
local.seat moveto ( 5800 2000 1200 )
local.seat waitmove
```

### Waiting for Multiple Entities to Finish Moving
```
// Constant array of targetnames, waitmove waits for ALL:
($bucket8::$bucket5::$bucket2::$bucket7::$bucket6::$bucket4::$bucket3::$bucket1) waitmove
```

### Model Change at Runtime
```
local.player model "player/allied_sas.tik"   // change player's model
local.object model "models/weapons/m1_garand.tik"
```

### Modheight (collision height)
```
local.player modheight stand    // reset to standing height after crouching etc.
```

### Glue / Unglue (parent attachment)
```
local.player glue local.seat    // player follows seat's position/rotation
local.player unglue             // detach player from seat
$fire glue $v2rocket            // attach fire emitter to rocket
```

### Respawn & Health
```
local.player respawn             // force player to respawn immediately
local.player volumedamage -600   // heal 600 HP (negative = heal)
local.player volumedamage 5000   // instant kill / massive damage
```

### Entity dmg Property
```
$ossdoor dmg 0    // set the door's damage output to 0 (won't hurt players)
```

### connect_paths (AI navigation after door opens)
```
$gate connect_paths    // rebuild AI pathfinding after moving blocking entity
```

### removeclass
Remove all entities of a given class from the map (useful at map start):
```
removeclass actor         // remove all AI
removeclass triggeronce   // remove all one-shot triggers
removeclass triggersave   // remove all save triggers
```

---

## 43. Trigger Types & Properties

### trigger_multiple (walk-through)
Fires when a player walks through the volume:
```
local.trig = spawn trigger_multiple
local.trig.origin = ( x y z )
local.trig setsize ( -35 -35 -35 ) ( 35 35 55 )
local.trig setthread myfunction          // run this label when triggered
local.trig wait 0                        // re-arm delay (0 = instant re-arm)
local.trig delay 0                       // initial delay
local.trig message "*** Press E Here! ***"  // hint shown to nearby players
```

### trigger_use (press-E trigger)
Fires only when player presses the Use key (E) while looking at it:
```
local.trig = spawn trigger_use
local.trig.origin = ( x y z )
local.trig setsize ( -85 -55 -35 ) ( 85 55 85 )
local.trig setthread myfunction
local.trig wait 0
local.trig delay 0
```

### Shootable Trigger (spawnflags "128" + health)
```
local.trig = spawn trigger_multiple "spawnflags" "128" "health" "10"
local.trig.origin = local.origin
local.trig setsize ( -8 -8 0 ) ( 8 8 10 )
local.trig glue local.can      // trigger follows the entity
// Fires when the entity receives 10 damage (i.e., is shot)
```
`spawnflags "128"` = trigger can be activated by damage.  
`health "10"` = how much damage before firing.

### Trigger Callback — parm.other
The entity that activated the trigger is available as `parm.other`:
```
myfunction:
    local.player = parm.other     // who walked in / pressed E / shot trigger
    if (local.player.dmteam == "axis") end
    // ...
end
```

### Player Input Detection
```
local.player.useheld   // 1 while player holds Use key (E), 0 otherwise
local.player.fireheld  // 1 while player holds fire button, 0 otherwise

// Wait for player to press E:
while (local.player.useheld == 0)
    waitframe

// Exit vehicle when player presses E:
while ((local.player.dmteam != "spectator") && (local.player.health > 0) && (local.player.useheld == 0))
    waitframe
```

### isTouching (contact detection)
```
if (local.player isTouching $latertruck)
    // player is physically touching the truck entity
```

---

## 44. func_beam (Laser / Beam Effects)

```
local.beam = spawn func_beam origin ( x1 y1 z1 ) endpoint ( x2 y2 z2 )
local.beam targetname "mybeam"
local.beam numsegments 1       // 1 = straight line; higher = zigzag/lightning
local.beam maxoffset 0         // zigzag amplitude in units
local.beam toggledelay 0       // flicker delay (0 = no flicker)
local.beam alpha 0.8           // transparency (0=invisible, 1=solid)
local.beam color (1 0 1)       // RGB color
local.beam scale 8.0           // beam width in units
local.beam activate            // make beam visible
local.beam svflags "+broadcast" // send to all clients (required for dynamic entities)
local.beam shader "textures/general_industrial/cable_wire.jpg"

// Update endpoint every frame (animate beam):
fairylights:
while(1) {
    $mybeam endpoint ( $target.origin )    // track a moving entity
    wait 0.1
}
end
```

---

## 45. Dynamic Sound Aliases (ScriptMaster / aliascache)

To play custom sounds in a map script, register aliases at map start:

```
local.master = spawn ScriptMaster
local.master aliascache myalias sound/path/sound.wav soundparms <vol> <pitch_min> <pitch_max> <pitch_rand> <min_range> <max_range> <channel> <flags> maps "m dm moh obj train"

// Channel:  auto, body, item, weaponidle, voice, local, dialog, music
// Flags:    loaded (preload), streamed, looped
// maps:     which map types this alias applies to

// Full example:
local.master aliascache tractor_run sound/vehicle/veh_tank_run1.wav soundparms 1.0 0.0 1.0 0.0 800 4500 auto streamed maps "m dm moh obj train"
local.master aliascache v2_launch sound/amb/Amb_FireLoop_03.wav soundparms 10.0 0.0 1.0 0.0 1000 6000 item loaded maps "m dm moh obj train"

// Use the alias:
$entity loopsound tractor_run
$entity playsound v2_launch
$entity stoploopsound
```

---

## 46. FX & Emitter Entities

### Particle Emitters
```
local.fire = spawn script_model
local.fire model "emitters/fireandsmoke.tik"   // fire + smoke
local.fire.origin = ( x y z )

local.fire model "emitters/fire.tik"            // fire only
```

### Animated FX (one-shot explosions)
```
local.exp = spawn "animate/fx_explosion_tank.tik"
local.exp.origin = local.groundpos
local.exp.scale = 3
local.exp light 1 0 0 250
local.exp anim start
wait 0.7
local.exp anim stop
local.exp remove

// Common FX paths:
// animate/fx_explosion_mine.tik
// animate/fx_explosion_tank.tik
// animate/fx_mortar_dirt.tik
// fx/scriptbazookaexplosion.tik
```

### Corona / Stars
```
local.stars = spawn "static/corona_orange.tik" targetname "stars"
local.stars.scale = 0.1
local.stars notsolid

// Rapid repositioning trick to fake multiple particles (one entity):
stars:
while(1) {
    $stars.origin = ( (-2100 -5000 1040) + ((randomint(8000)) (randomint(10000)) (0)) )
    waitframe
}
end
```

### Earthquake Effect
```
exec global/earthquake.scr (r g b dur)
// e.g.:
exec global/earthquake.scr (randomfloat(0.999)) (randomfloat(0.999)) (randomfloat(0.999)) (randomfloat(0.999))
waitexec global/earthquake.scr 0.5 0.2 0.1 1.0
```

---

## 47. Trace (Ray Cast)

Cast a ray and get the hit position:

```
local.end       = local.start - (0 0 2096)        // endpoint below start
local.groundpos = trace local.start local.end     // returns hit position or endpoint if no hit

// Optional third parameter (mask): 0 = all solids
local.hit = trace local.start local.end 0
```

### Distance Check (efficient squared distance)
```
// Don't use sqrt — compare squared distances instead:
local.dist   = ( $player[n].origin - local.groundpos )   // vector subtraction
local.sqr    = local.dist * local.dist                    // dot product = squared length
local.radius = 850.0 * 850.0
if (local.sqr <= local.radius) {
    // player is within 850 units of groundpos
}
```

### Additional Math Functions
```
angles_toforward (vector)            // convert angles vector to forward unit vector
vector_scale local.vec local.amount  // multiply vector by scalar
$player[n].forwardvector             // player's forward direction unit vector
```

---

## 48. Camera Sequences & Screen Effects

### Full Camera Sequence Pattern
```
spawn Camera targetname CAM0 origin ( x y z ) angles ( pitch yaw roll )
$CAM0 follow_distance 550      // camera distance from target
$CAM0 orbit_height 250         // height offset when orbiting
$CAM0 speed 1.05               // camera movement speed
waitframe

$CAM0 fov 90 1.0               // set FOV (degrees, blend_time)
$CAM0 fov (randomint(150)+110) (randomint(50)+10)   // random dramatic FOV
cuecamera $CAM0                // switch all players to camera view
$CAM0 follow local.player      // track a specific player
$CAM0 orbit local.player       // orbit around player

wait 5.0

clearletterbox                 // remove letterbox bars
cueplayer                      // return to player view
drawhud 1                      // re-enable HUD
$CAM0 delete                   // remove camera entity
```

### Screen Fade
```
fadeout 2.5 0.20 0.20 0.50 0.5    // duration r g b alpha
fadein  0.5 0.20 0.20 0.50 0.5    // duration r g b alpha

// Black fade out:
fadeout 2.5 0 0 0 1
fadein  1.0 0 0 0 1
```

### Full-screen HUD overlay (win screens)
```
huddraw_virtualsize 19 1
huddraw_alpha 19 0.6
huddraw_rect 19 0 0 640 480         // full screen
huddraw_shader 19 "textures/hud/allieswin"

// Later:
huddraw_alpha 19 0                  // remove overlay
```

---

## 49. $world Entity

Controls global environment settings (visible to all clients):

```
$world farplane 6000                        // draw distance (smaller = more fog)
$world farplane_color ( 0.03 0.05 0.09 )   // fog color (RGB 0.0–1.0)
$world farplane_color ( 0 0 0 )             // black fog = full dark night

// Typical patterns:
$world farplane 16000                       // large open map
$world farplane_color ( .17 .19 .01 )       // greenish dusk
```

Also accessible as level variables:
```
level.farplane = 25000
level.farplanecolor = "0.25 0.15 0.1"
```

### Sky toggle (client-side via stufftext)
```
$player stufftext ("r_fastsky 0")   // enable skybox rendering
$player stufftext ("r_fastsky 1")   // disable skybox (solid color sky)
```

---

## 50. Dynamic Spawn Points

Create spawn points at runtime (MP maps):

```
// Random positions in a zone:
spawn info_player_allied origin ( (-4000 + (randomint(2000))) (-5000 + (randomint(3000))) 1600.13 ) angle (randomint(360))

// Staged spawns with targetname (for mission phases):
spawn info_player_axis  origin "6351 -4473 39" angle 0 targetname "ax_stage_1"
spawn info_player_allied origin "143 2717 -410" angle 35 targetname "al_stage_1"

// Later remove and spawn new stage:
$ax_stage_1 remove
spawn info_player_axis origin "new_x new_y new_z" angle 0 targetname "ax_stage_2"
```

---

## 51. MP3 Playback (Client-Side Music)

```
// Play an MP3 to all clients (path relative to game root):
$player stufftext "playmp3 main/sound/music/mus_09a_action.mp3"

// Stop MP3:
$player stufftext "stopmp3"

// Per-player (only that player hears it):
$player[n] stufftext "playmp3 main/sound/music/mus_10a_action.mp3"
```

---

## 52. HUD Reference — Fonts, Textures, Coordinates

### Available Font Names
```
facfont-20      // military stencil look (large)
verdana-20      // clean sans-serif (large)
verdana-14      // clean sans-serif (medium)
courier-20      // monospace
```

### HUD Coordinate System
```
// Origin: top-left corner of screen
// Virtual resolution: 640 x 480
// Negative Y = measured from bottom of screen (requires align bottom)
// e.g. huddraw_rect 30 40 -140 100 100  = 40px from left, 140px from bottom

huddraw_align 30 left bottom      // anchor: left edge, bottom edge
huddraw_rect  30 40 -140 100 100  // x=40, y=-140 (140px from bottom), w=100, h=100
```

### Common HUD Texture Paths
```
textures/hud/allies         // allied team icon
textures/hud/axis           // axis team icon
textures/hud/allieswin      // full-screen allies win overlay
textures/hud/axiswin        // full-screen axis win overlay
textures/hud/score_bg       // score background
```

### HUD Update Loop Pattern (live counter)
```
display_hud:
while(1) {
    huddraw_align  254 left bottom
    huddraw_font   254 facfont-20
    huddraw_rect   254 10 -215 100 100
    huddraw_color  254 1 1 1
    huddraw_alpha  254 0.7
    huddraw_string 254 ("Can hit: " + level.can_score)
    wait 2
}
end
```

---

## 53. Passenger Slots (Vehicle / Seat System)

Attach a player to a moving entity as a passenger:
```
local.randomslot = (randomint(5) + 1)
local.truck AttachPassengerSlot (local.randomslot) local.player    // seat player
// player rides with truck movement
local.truck DetachPassengerSlot (local.randomslot) local.player    // eject player
```

---

## 54. Full Damage Call (Advanced)

The full form of the `damage` command:
```
entity damage attacker amount attacker origin normal direction flags1 flags2 damagetype flags4

// Example from FunFair rocket:
$player[i] damage local.player 500 local.player $player[i].origin $player[i].forwardvector (0 0 0) 0 0 9 0

// damagetype values:
// 5 = burn
// 7 = fly (knockback)
// 8 = died
// 9 = blown up
```

---

## 55. Common Shared Scripts (Referenced Across Mods)

These helper scripts are commonly included from the `global/` folder:

| Script | Purpose |
|--------|---------|
| `global/ambient.scr mapname` | Ambient music + fog (pass map name to select .mus track) |
| `global/door_locked.scr` | Locked door management system |
| `global/give.scr` | Player loadout handler |
| `global/loadout.scr maps/mapname.scr` | Map-specific loadout |
| `global/_teamz.scr` | Team management (auto-balance, spectator enforcement) |
| `global/punishment.scr` | Player punishment system |
| `global/spotlight.scr` | Spotlight effects |
| `global/exploder.scr` | Explosion/demolition system |
| `global/earthquake.scr r g b dur` | Screen shake effect |
| `server_planes/trigger.scr origin team delay` | Server-side aircraft pass |

---

## 56. Dynamic Sky / Fog System (Admin Cvar Pattern)

A common pattern from map mods: let the server admin change fog/sky mode live by setting a cvar. The `_sky-mapname.scr` script polls the cvar and applies changes.

```
// global/_sky-m1l2a.scr  (loaded with: exec global/_sky-m1l2a.scr)
nightcheck:
setcvar "night" "0"         // default mode (set at map start)

while(1) {
    while((getcvar "night") == "")   // wait until cvar exists
        { wait 1 }

    if (int(getcvar "night") <= 0) {
        $player stufftext ("r_fastsky 0")         // skybox on
        $world farplane 6000
        $world farplane_color ( .03 .05 .09 )     // dark blue/day
        wait 3
    }
    if (int(getcvar "night") == 1) {
        $player stufftext ("r_fastsky 1")         // no skybox
        $world farplane 5323
        $world farplane_color ( 0 0 0 )           // pure black night
        wait 3
    }
    if (int(getcvar "night") == 2) {
        $player stufftext ("r_fastsky 1")
        $world farplane 5500
        $world farplane_color ( .70 .70 .30 )     // golden dust storm
        wait 3
    }
    if (int(getcvar "night") == 3) {
        $player stufftext ("r_fastsky 1")
        $world farplane 6500
        $world farplane_color ( .30 .50 .70 )     // blue dawn
        wait 3
    }
}
end
```

**Usage:** Admin types `set night 2` in console → map switches to golden fog within 3 seconds, no restart needed.

---

## 57. Countdown Timer Pattern

Standard approach for timed game objectives (rescue missions, bomb escorts, etc.):

```
// Initialize (high value = many ticks; divide by 10 for display in seconds):
level.countup = level.start_countup   // e.g. 3000 = 300 seconds

// Main game loop (decrements once per frame, check at waitframe rate):
while ((level.capturedsasagent != 0) && (local.player.iscaptured == 1)) {
    level.countup--

    if (level.countup == 0) {
        iprintln "TIME IS UP !!!"
        // handle timeout
        end
    }

    waitframe
}

// HUD display (divide by 10 for seconds):
huddraw_string 34 ("countdown: " + (level.countup / 10))
```

**Note:** Incrementing/decrementing `level.countup` once per `waitframe` at the default server fps (20) gives roughly 0.05s resolution. Divide by 20 for seconds.

---

## 58. Per-Entity Custom Flags (Lock Pattern)

Use custom properties on entities to prevent re-entry/re-triggering before an action completes:

```
// In trigger handler:
myfunction:
    local.player = parm.other

    // Guard: already processing for this player
    if (local.player.istransport == 1)
        end

    local.player.istransport = 1    // lock

    // ... do stuff ...

    wait 5
    local.player.istransport = 0    // unlock
end
```

This is the universal MOHAA re-entrancy guard. Custom properties (`.isfoo`, `.hasfoo`, `.opendoor`, etc.) persist for the lifetime of the entity.

Global flags work the same way:
```
if (level.hasrocket == 1)
    end                          // only one rocket active at a time

level.hasrocket = 1
// ... launch rocket ...
level.hasrocket = 0
```

---

## 59. Chat Commands (stufftext say / teamsay)

Force a player to send a chat message — useful for immersive feedback:

```
$player[n] stufftext "say I found the health spot!"           // all-chat
$player[n] stufftext "teamsay OH NO!... I'm captured!"       // team-only chat
$player[n] stufftext "say One Hell Of A Rocket Coming Your Way... LOL!!!"

// String concatenation for dynamic messages:
$player[n] stufftext ("say [" + $player[n].entnum + "] reporting in")
```

---

## 60. Spawn with String-Form Origin

`spawn` accepts either vector or quoted-string origin:

```
// Vector form (recommended):
spawn info_player_axis origin ( 6351 -4473 39 ) angle 0

// String form (also valid):
spawn info_player_axis origin "6351 -4473 39" angle 0 "targetname" "ax_stage_1"

// Inline property list (key-value pairs after entity class):
spawn trigger_multiple "spawnflags" "128" "health" "10"

// Multiple inline properties:
local.ent = spawn script_model model "fx/dummy.tik" targetname "bucket_loopsound"
```

---

## 61. level.script Variable

Set to the current map script path. Used by some global scripts to know which map is running:

```
level.script = "maps/m4l0.scr"     // set at start of main:
level.script = "maps/m1l2a.scr"
```

---

## 62. Rotating Carousel (Chained moveto Loop)

Move N entities in a rotating circle — each tick they swap positions:

```
// Eight buckets in a circle. Each frame: advance every bucket one slot.
_bucket_gogo:
while (level.bucketstart == 0)
    wait 1

while(1) {
    // Set speed for all:
    $bucket1 time (level.buckettime)
    $bucket2 time (level.buckettime)
    // ... repeat for all 8 ...
    $bucket8 time (level.buckettime)

    // Each bucket moves to the next bucket's current position:
    $bucket1 moveto $bucket2.origin
    $bucket2 moveto $bucket3.origin
    $bucket3 moveto $bucket4.origin
    $bucket4 moveto $bucket5.origin
    $bucket5 moveto $bucket6.origin
    $bucket6 moveto $bucket7.origin
    $bucket7 moveto $bucket8.origin
    $bucket8 moveto $bucket1.origin       // wrap around

    // Wait for all 8 to arrive before next tick:
    ($bucket8::$bucket5::$bucket2::$bucket7::$bucket6::$bucket4::$bucket3::$bucket1) waitmove
}
end
```

Speed-up trick: decrease `level.buckettime` each entry → they rotate faster as more players board.

---

## 63. Inventory — Complete Weapon Take/Give

```
// Give weapon + switch to it:
local.player give models/weapons/silencedpistol.tik
local.player item "models/weapons/silencedpistol.tik"      // give as item pickup
local.player useweaponclass pistol                          // equip it immediately

// Strip every weapon from a player (useful for captured player scenarios):
local.player take models/weapons/p38.tik
local.player take models/weapons/colt45.tik
local.player take models/weapons/kar98sniper.tik
local.player take models/weapons/kar98.tik
local.player take models/weapons/mp40.tik
local.player take models/weapons/mp44.tik
local.player take models/weapons/steilhandgranate.tik
local.player take models/weapons/panzerschreck.tik
local.player take models/weapons/springfield.tik
local.player take models/weapons/bar.tik
local.player take models/weapons/thompsonsmg.tik
local.player take models/weapons/m1_garand.tik
local.player take models/weapons/m2frag_grenade.tik
local.player take models/weapons/bazooka.tik
local.player take models/weapons/shotgun.tik

// Or use takeall:
local.player takeall

// useweaponclass values:
// pistol, rifle, smg, mg, grenade, shotgun, heavy
```

---

## 64. Complete Real-Mod Patterns (from TheFunFair + RescueMission)

### Pattern A — Player Size Change (midget/giant spot)
```
midget:
    local.player = parm.other
    if (local.player.ismidget == 1) end      // already midget, block re-entry

    local.player.ismidget = 1
    local.player iprint "You Found The Midget Spot !!!"
    local.player.oldscale = local.player.scale
    local.player.scale = 0.5
    wait 120
    local.player.scale = local.player.oldscale
    local.player.ismidget = 0
end
```

### Pattern B — Health Spot (super heal + glow)
```
healty:
    local.player = parm.other
    if (local.player.ishealty == 1) end

    local.player.ishealty = 1
    local.player stufftext "say I Found Incredible Health, Stay The Hell Away From Me...!!!"
    local.player volumedamage -(randomint(1500) + 500)   // heal 500–2000 HP
    local.player light 0 1 0 135                          // green glow
    wait 30
    local.player light 1 1 1 1                            // remove glow
    wait 350
    local.player.ishealty = 0
end
```

### Pattern C — Mover with Player Attached (elevator/ride)
```
transport:
    local.player = parm.other
    if (local.player.istransport1 == 1) end

    local.player.istransport1 = 1
    local.player iprint "Going Up..."
    local.player playsound plantbomb

    local.seat = spawn script_model
    local.seat model "static/static_electricbox1.tik"
    local.seat.origin = ( startX startY startZ )
    local.seat notsolid

    // Color by team:
    if (local.player.dmteam == "allies")
        local.seat light 0 0 1 165
    if (local.player.dmteam == "axis")
        local.seat light 1 0 0 165

    local.player.origin = ( local.seat.origin - (0 0 50) )
    local.player glue local.seat
    local.player notsolid

    local.seat time 10
    local.seat moveto ( endX endY endZ )
    local.seat waitmove

    local.player unglue
    local.seat remove

    wait 5
    local.player solid
    local.player.istransport1 = 0
end
```

### Pattern D — Out-of-Bounds Kill Trigger
```
// Invisible floor trigger covering the entire map:
local.trig = spawn trigger_multiple
local.trig.origin = ( 0 0 -327.88 )
local.trig setsize ( -9999 -9999 -50 ) ( 9999 9999 1 )
local.trig setthread _outofbounds
local.trig message "[ FORBIDDEN AREA! ]"
local.trig wait 0
local.trig delay 0

_outofbounds:
    local.player = parm.other
    if (local.player.ischeats == 1) end

    local.player.ischeats = 1
    wait 1
    local.player respawn
    local.player.ischeats = 0
end
```

### Pattern E — Shootable Target with Physics
```
can1:
    local.origin = ( 5100 -250 573 )
    local.can = spawn script_model
    local.can model "models/static/german_rations_1.tik"
    local.can.origin = local.origin
    local.can angle (randomint(360))
    local.can physics_off

    local.trigger = spawn trigger_multiple "spawnflags" "128" "health" "10"
    local.trigger.origin = local.origin
    local.trigger setsize ( -8 -8 0 ) ( 8 8 10 )
    local.trigger glue local.can         // trigger tracks the can

    local.trigger waittill trigger       // block until shot

    // Physics launch on hit:
    local.can.velocity = ( (500 - (randomint(1000))) (500 - (randomint(1000))) (500 + (randomint(100))) )
    local.can rotatex (500 - (randomint(1000)))
    local.can rotatey (500 - (randomint(1000)))
    local.can rotatez (500 - (randomint(1000)))
    wait 0.2
    local.can physics_on
    wait 0.3
    local.can remove
    wait 5
    thread can1    // respawn after 5 seconds
end

---

## 65. Map-Specific Mod Structure (Script Replacement)

A third delivery method besides overriding `DMprecache.scr`. Replace the map script directly — works only on that specific map, but gives full control with zero interference from other mods.

### PK3 structure:
```
zzzz-m4l0_TheFunFair.pk3
â”œâ”€â”€ global/
â”‚   â””â”€â”€ _sky-m4l0.scr        (custom sky/fog helper)
â””â”€â”€ maps/
    â””â”€â”€ m4l0.scr              (replaces the original map script entirely)
```

The game loads `maps/m4l0.scr` from the pk3 instead of the original. The mod author writes a full `main:` that does everything — set game rules, spawn entities, spawn players, start threads.

### When to use each delivery method:

| Method | Override file | Runs on | Use when |
|--------|--------------|---------|----------|
| Global hook | `global/DMprecache.scr` | Every map | Mod should work on all maps |
| Map script replace | `maps/mapname.scr` | One map only | Deep per-map gameplay, full entity control |
| Both | DMprecache + map script | All maps + special logic per map | Complex mods with global + per-map parts |

### Map-specific mod main: structure
```
main:
    // 1. Remove SP-only entities not needed in MP
    removeclass actor
    removeclass triggeronce
    removeclass triggersave

    // 2. Set game mode
    setcvar "g_gametype" "2"
    setcvar "g_gametypestring" "= My Mod ="
    setcvar "timelimit" "20"
    setcvar "g_obj_alliedtext1" "Allies objective"
    setcvar "g_scoreboardpic" "textures/mohmenu/briefing/..."

    // 3. Spawn player positions (can be randomized)
    spawn info_player_allied origin ( ... ) angle (randomint(360))
    spawn info_player_axis origin "x y z" angle 0 targetname "ax_stage_1"

    // 4. Register sound aliases
    local.master = spawn ScriptMaster
    local.master aliascache mysound sound/path.wav soundparms 1.0 0.0 1.0 0.0 300 2000 auto loaded maps "m dm obj"

    // 5. Initialize state
    level.mygamevar = 0
    level.script = "maps/mapname.scr"

    // 6. Load helper scripts
    exec global/ambient.scr mapname
    exec global/door_locked.scr
    exec global/_sky-mapname.scr

    // 7. Remove unused entities from base map
    $unwanted_entity remove
    $another remove

    level waittill prespawn

    // 8. Spawn interactive world entities (triggers, fx, etc.)
    thread score_display
    thread game_logic

    level waittill spawn

    // 9. Post-spawn entity setup
    $door notsolid
    $something solid
end
```

### Naming convention for map-specific pk3s:
```
zzzz-m4l0_TheFunFair.pk3       // map name + mod name
zzzz-m1l2a_RescueMission.pk3   // "zzzz-" prefix = high priority, map-specific
```
Four z's (`zzzz-`) is enough to beat any default named pk3 while being shorter than UBER-MODS' fifteen z's.

---

## 66. UBER-MODS v8.00 — Complete Architecture

Source: https://github.com/searingwolfe/UBER-MODS-v8.00-MOHAA  
The most complete public MOHAA serverside mod library. Everything below is extracted verbatim or directly from its scripts.

### Repository Layout (NOT_REBORN branch — the active codebase)
```
NOT_REBORN/
â”œâ”€â”€ global/                  â† All server-wide mods (run via dmprecache.scr)
â”‚   â”œâ”€â”€ dmprecache.scr       â† Entry point: execs every global mod
â”‚   â”œâ”€â”€ settings.scr         â† Mod loader: reads settings/Mods.txt, starts each mod
â”‚   â”œâ”€â”€ get_game.scr         â† Detects AA / SH / BT from "version" cvar
â”‚   â”œâ”€â”€ uberversion.scr      â† Sets sv_runspeed, hardcode gametype per map
â”‚   â”œâ”€â”€ mod_inform.scr       â† HUD list of active/inactive mods at map start
â”‚   â”œâ”€â”€ strings.scr          â† Full string library (trim, split, replace, case, etc.)
â”‚   â”œâ”€â”€ math.scr             â† Trig library (sin/cos/asin/acos/atan/sqrt via series)
â”‚   â”œâ”€â”€ nagle.scr            â† Player skin replacement system (.st files)
â”‚   â”œâ”€â”€ jetpack.scr          â† Player jetpack (attach airtank, boost on jump)
â”‚   â”œâ”€â”€ jetpackjump.scr      â† Per-frame jump boost thread
â”‚   â”œâ”€â”€ anti_camper.scr      â† Position-tracking camp detection
â”‚   â”œâ”€â”€ deathcam.scr         â† Death spectate camera (players watch their killer)
â”‚   â”œâ”€â”€ respawn_fix.scr      â† Smart spawn-point selection (furthest from enemies)
â”‚   â”œâ”€â”€ respawn_stuck_fix.scrâ† Auto-respawn players stuck in walls 3+ seconds
â”‚   â”œâ”€â”€ throwingknife.scr    â† USE+fire to throw screwdriver model as knife
â”‚   â”œâ”€â”€ give_players_knives.scr â† Gives all players starting knife on spawn
â”‚   â”œâ”€â”€ playertank.scr       â† Drivable tank with turret, damage, reset
â”‚   â”œâ”€â”€ playerboat.scr       â† Drivable boat (U-boat model)
â”‚   â”œâ”€â”€ playerflak88.scr     â† Drivable Flak 88 cannon
â”‚   â”œâ”€â”€ bomberplane.scr      â† Bomber plane airstrike (spline path + bombs)
â”‚   â”œâ”€â”€ attachparachute.scr  â† Parachute on player (velocity cap + USE to cut)
â”‚   â”œâ”€â”€ steerable_chute.scr  â† Player-steerable parachute variant
â”‚   â”œâ”€â”€ weather.scr          â† Rain/snow/fog environment effects
â”‚   â”œâ”€â”€ rocketfix.scr        â† Fixes backward-facing bazooka projectiles
â”‚   â”œâ”€â”€ sv_maplists.scr      â† Multi-maplist cycling (sv_maplist2/3/4...)
â”‚   â”œâ”€â”€ server_crashed.scr   â† Auto-changelevel to nextmap after crash
â”‚   â”œâ”€â”€ killed.scr           â† Hook for per-player kill events
â”‚   â”œâ”€â”€ get_weapon.scr       â† Get entity reference of player's current weapon
â”‚   â”œâ”€â”€ get_player_weaponclass.scr â† Returns weaponclass string
â”‚   â”œâ”€â”€ loadout.scr          â† SP mission weapon loadouts by map name
â”‚   â”œâ”€â”€ vehicle_tele.scr     â† Teleport vehicles across walls/gates
â”‚   â”œâ”€â”€ files.scr            â† (stub) file utility placeholder
â”‚   â”œâ”€â”€ obj_dm.scr           â† Gametype switching objâ†”dm
â”‚   â”œâ”€â”€ fastsky.scr          â† Rapid sky change helper
â”‚   â”œâ”€â”€ custom_deaths.scr    â† Custom death animations (runs inside deathcam)
â”‚   â”œâ”€â”€ dog.scr / multi_dog.scr â† Spawnable attack dog
â”‚   â”œâ”€â”€ barrel.scr           â† Explosive barrel entity
â”‚   â””â”€â”€ ac/                  â† Admin-Pro system
â”‚       â”œâ”€â”€ admincam.scr     â† Admin spectate-cam a specific player
â”‚       â”œâ”€â”€ check_leanbind.scr â† Detect lean-spam/bind exploits
â”‚       â”œâ”€â”€ cvar_forcer.scr  â† Force player cvars via stufftext
â”‚       â”œâ”€â”€ spawn_protection.scr â† Invulnerability window after spawn
â”‚       â”œâ”€â”€ team_balance.scr â† Auto balance teams
â”‚       â””â”€â”€ command_post/
â”‚           â”œâ”€â”€ player_cmds.scr  â† Admin player punishment dispatch
â”‚           â”œâ”€â”€ punishments.scr  â† rocket / morph punishments
â”‚           â”œâ”€â”€ one_word.scr     â† One-word admin commands
â”‚           â””â”€â”€ console.scr      â† Console command handling
â”œâ”€â”€ killstreaks/
â”‚   â”œâ”€â”€ damagehandler.scr    â† chain_reaction kills nearby killstreak items
â”‚   â”œâ”€â”€ sentry_turret.scr    â† Auto-aiming MG42 turret reward
â”‚   â”œâ”€â”€ claymores.scr        â† Claymore mine reward
â”‚   â””â”€â”€ cluster_mines.scr    â† Cluster mine reward
â”œâ”€â”€ Survivor/                â† Round-based Survivor game mode
â”‚   â”œâ”€â”€ setup.scr            â† Init: lives, warmup, rounds
â”‚   â”œâ”€â”€ spawned.scr          â† Per-player spawn handler
â”‚   â”œâ”€â”€ dead.scr             â† Player death / lives management
â”‚   â”œâ”€â”€ spectator.scr        â† Spectator management
â”‚   â”œâ”€â”€ roundend.scr         â† End of round logic
â”‚   â”œâ”€â”€ camera.scr           â† Deathcam for survivor
â”‚   â””â”€â”€ warm_up.scr          â† Warmup period
â”œâ”€â”€ GuidedMissile/
â”‚   â”œâ”€â”€ Missile.scr          â† Player-guided missile (camera + velocity control)
â”‚   â”œâ”€â”€ SpawnTrigger.scr     â† Trigger to pick up missile launcher
â”‚   â””â”€â”€ trigger.scr          â† Fire trigger
â”œâ”€â”€ HTR/                     â† Hold The Radio mode
â””â”€â”€ cvars/                   â† Developer admin debug tools
    â”œâ”€â”€ cvars.scr            â† Main dev tool loader
    â”œâ”€â”€ findent.scr          â† Find entity by class/model/name
    â”œâ”€â”€ track.scr            â† Track entity positions
    â””â”€â”€ entity_pointer.scr   â† Point laser at entity
```

### Settings Architecture
UBER-MODS uses a data-driven settings system:
- `settings/Mods.txt` — list of enabled mods (one mod name per line)
- Each mod has a `settings/<modname>.txt` — key=value config pairs
- `global/settings.scr` reads Mods.txt, execs each mod's .scr, loads its settings
- `game.all_commands[]` — centralized command registry
- `game.scripts[]` — list of all registered mods with on/off status

---

## 67. UBER-MODS dmprecache.scr — Verbatim

This is the actual entry point that runs on every MP map:

```
main:
    thread globalmods
    thread cache
end

globalmods:
    exec global/sv_maplists.scr         // multi-maplist rotation
    exec global/server_crashed.scr      // auto-changelevel after crash

    exec global/rocketfix.scr           // fixes backward bazooka projectiles

    exec global/deathcam.scr            // death spectate + custom death anims
    //exec global/custom_deaths.scr     // ONLY if NOT running deathcam.scr

    exec global/respawn_stuck_fix.scr   // auto-respawn players stuck 3+ sec in walls
    exec global/respawn_fix.scr         // move respawned players to furthest safe spawn

    exec killstreaks/damagehandler.scr::assisted_suicide   // assisted suicide tracking

    exec global/player_taunts.scr       // USE key x4 within 1 sec = taunt animation

    // Add missing sound aliases to prevent console errors on maps without them:
    level.mapname = getcvar "mapname"
    local.master = spawn scriptmaster
    local.master aliascache manon_pain sound/null.wav soundparms 1.2 0.1 0.9 0.2 320 3200 auto loaded maps level.mapname
    local.master aliascache manon_death sound/null.wav soundparms 1.2 0.1 0.9 0.2 320 3200 auto loaded maps level.mapname
end

cache:
    cache models/animate/hidden_cabinet_a.tik
    cache models/animate/hidden_cabinet_b.tik
    // ... (200+ model caches for all player skins, vehicles, FX)
    // Notable: tigertank and jeep are COMMENTED OUT — they spam the console
    cache models/vehicles/kingtank.tik
    //cache models/vehicles/tigertank.tik  // spams console
    //cache models/vehicles/jeep.tik       // spams console
    cache models/vehicles/shermantank.tik
    cache models/vehicles/sdkfz.tik
    // All bullet holes: bh_carpet/dirt/foliage/glass/grass/metal/mud/paper/sand/snow/stone/water/wood
    // All footstep FX: fs_dirt/grass/heavy_dust/light_dust/mud/puddle/sand/snow
    // All grenade explosions: grenexp_base/carpet/dirt/fireball/foliage/grass/gravel/metal/mud/paper/sand/snow/stone/water/wood
    // All water FX: water_ripple_moving/still, water_splash_drop, water_spray, water_trail_bubble
end
```

**Key insight:** dmprecache.scr uses `thread` for both sections so they run in parallel — globalmods execs scripts while cache preloads assets simultaneously.

---

## 68. get_game.scr — Version Detection (Verbatim)

Detects which game is running by reading the "version" cvar. Character at index 15 (or 16 if there's a space) is the discriminator:

```
getgame:
    local.game = getcvar "version"
    local.i = 15

    if(local.game[local.i] == " ")
    {
        local.i = 16
    }

    switch(local.game[local.i])
    {
    case "A":
        game.game = "AA"
    break
    case "S":
        game.game = "SH"
    break
    case "B":
        game.game = "BT"
    break
    }

end local.cmdwant
```

Usage:
```
waitexec global/get_game.scr::getgame
if(game.game == "AA") { /* Allied Assault logic */ }
if(game.game == "SH") { /* Spearhead logic */ }
if(game.game == "BT") { /* Breakthrough logic */ }
```

---

## 69. respawn_fix.scr — Smart Spawn Selection (Verbatim)

Moves respawned players to the spawn point furthest from all enemies. Supports custom spawn point targetnames as parameters.

```
// Usage: exec global/respawn_fix.scr
// Or with custom names: exec global/respawn_fix.scr "new_allies_spawn" "new_axis_spawn" "new_ffa_spawn"

main local.allies_targetname local.axis_targetname local.ffa_targetname:

    if(local.allies_targetname == NIL) { local.allies_targetname = "allied_spawn" }
    if(local.axis_targetname == NIL) { local.allies_targetname = "axis_spawn" }
    if(local.ffa_targetname == NIL) { local.allies_targetname = "deathmatch_spawn" }

    while(1)
    {
        for(local.i = 1; local.i <= $player.size; local.i++)
        {
            $player[local.i].respawnfix_spawnpoint = NIL
            // detect freshly respawned players (was dead, now alive)
            if((isalive $player[local.i] && $player[local.i].respawnfix_dead == 1 && $player[local.i].dead != 1) || ...)
            {
                if(getcvar("g_gametype") != "1")   // not FFA
                {
                    if($player[local.i].dmteam == "allies") { $player[local.i] waitthread get_new_respawn_point local.allies_targetname }
                    if($player[local.i].dmteam == "axis")   { $player[local.i] waitthread get_new_respawn_point local.axis_targetname }
                }
                else { $player[local.i] waitthread get_new_respawn_point local.ffa_targetname }
            }

            if($player[local.i].respawnfix_spawnpoint != NIL && $player[local.i].respawnfix_spawnpoint != NULL)
            {
                $player[local.i].origin = $player[local.i].respawnfix_spawnpoint.origin
                $player[local.i] face ( 0 $player[local.i].respawnfix_spawnpoint.angles[1] 0 )

                // if still touching any players, just respawn them normally
                for(local.j = 1; local.j <= $player.size; local.j++)
                {
                    if($player[local.i] != $player[local.j] && $player[local.i] istouching $player[local.j]) { $player[local.i] respawn }
                }
            }

            if(!isalive $player[local.i] || $player[local.i].dead == 1) { $player[local.i].respawnfix_dead = 1 }
            else { $player[local.i].respawnfix_dead = 0 }
        }
        waitframe
    }
end

get_new_respawn_point local.targetname:    // self = the player

    if($(local.targetname) == NULL) { end }

    for(local.s = 1; local.s <= $(local.targetname).size; local.s++)
    {
        local.dist_old = 9999999
        for(local.j = 1; local.j <= $player.size; local.j++)
        {
            if($player[local.j] != self && isalive $player[local.j] && ...)
            {
                local.dist_player = vector_length($(local.targetname)[local.s].origin - $player[local.j].origin)
                if(self.dmteam != $player[local.j].dmteam && local.dist_player < local.dist_old)
                {
                    local.dist_array[local.s] = local.dist_player  // shortest enemy distance to this spawn
                }
                if(local.dist_player <= 42.5)
                {
                    local.dist_array[local.s] = 0  // player hitbox diagonal = 42.5 units max
                }
                local.dist_old = local.dist_player
            }
        }
    }

    local.dist = 0
    for(local.s = 1; local.s <= $(local.targetname).size; local.s++)
    {
        if(local.dist_array[local.s] > local.dist)
        {
            local.dist = local.dist_array[local.s]
            self.respawnfix_spawnpoint = $(local.targetname)[local.s]  // pick spawn furthest from enemies
        }
    }
    if(local.dist == 0) { self.respawnfix_spawnpoint = NIL }
end
```

**Key notes:**
- Uses `face (0 angle 0)` instead of `.angles =` to avoid needing an extra waitframe
- Player hitbox diagonal = 42.5 units — any spawn within that radius is disqualified
- Works with `$allied_spawn`, `$axis_spawn`, `$deathmatch_spawn` targetnamed entities

---

## 70. bomberplane.scr — Airstrike System (Key Sections)

Spawns a plane along a spline path that drops bombs. Fully team-aware, respects g_teamdamage.

### Usage
```
// Spawn an airstrike (exec from map script or mod):
exec global/bomberplane.scr "my_plane_path" "axis" 3 30 5 1
//                           path_targetname  team  planes offtime bombs bombswait
```

### Parameters
| Param | Meaning |
|-------|---------|
| `path` | targetname of spline path entity ($path) |
| `team` | "allies" / "axis" / "c47" (uses different plane models) |
| `planes` | how many planes fly in formation |
| `offtime` | seconds between airstrike cycles |
| `bombs` | how many bombs per plane |
| `bombswait` | seconds before first bomb drops after plane enters map |

### Models used
- Allies: `models/vehicles/p47fly.tik`
- Axis: `models/vehicles/fockwulffly.tik`
- C47 transport: `models/vehicles/c47fly.tik`

### How it works (key code):
```
// Plane follows spline:
local.plane followpath $(local.path)
local.plane playsound airplane_flyover
local.plane loopsound airplane_idle
local.plane waitmove
if(local.plane != NULL) { local.plane remove }

// Bomb physics:
local.bomb physics_on
local.bomb gravity level.bomberplane_bombgravity   // default 2
local.bomb.velocity = ( (self.velocity[0] * level.bomberplane_bombspeed) ... )
// level.bomberplane_bombspeed default 0.25

// Bomb damage (team-aware):
$player[local.i] damage local.playerowner 300 local.playerowner (0 0 0) (0 0 0) (0 0 0) 0 9 9 0

// Chain: radiusdamage + visual explosion emitter + sound
radiusdamage local.boom.origin 300 600
```

### Shootable plane trigger
```
local.trigger = spawn trigger_multiple spawnflags 128   // spawnflags 128 = shoots/explosions only
local.trigger setsize ( -300 -300 -100 ) ( 300 300 100 )
local.trigger glue self  // tracks the plane
// health = level.bomberplane_health (default 200)
```

### Water detection
```
level.water_volumes[1][1] = origin_vector
level.water_volumes[1][2] = setsize_mins
level.water_volumes[1][3] = setsize_maxs
// Script manually checks if bomb.origin is inside each water volume box
```

### Configurable defaults
```
level.bomberplane_health = 200        // bullets to shoot down
level.bomberplane_bombspeed = 0.25    // horizontal bomb spread
level.bomberplane_bombgravity = 2     // how fast bombs fall
```

---

## 71. playertank.scr — Drivable Tank (Key Sections)

Spawns a fully drivable VehicleTank with turret, damage smoke, chain reaction explosions.

### Usage
```
exec global/playertank.scr "tankname" "models/vehicles/kingtank.tik" (x y z) (0 180 0) 500 60
//                          name       model                          origin     angles  health resettime
```

### Init sequence
```
main local.name local.model local.origin local.angles local.health local.resettime local.gotout local.groundtarget:

    // Validate model path (prepend "models/" if missing)
    if(local.model[0] != "m" ...) { local.model = "models/" + local.model }

    local.tank = spawn local.model targetname (local.name)
    local.tank.origin = local.origin
    local.tank.angles = local.angles
    local.tank.health = local.health

    if(local.tank.classname != "VehicleTank") { local.tank remove; println("ERROR: not a VehicleTank"); end }

    // Start all threads:
    local.tank thread tank_settings local.gotout
    local.tank thread tankreset local.groundtarget
    local.tank thread tankdamage
    local.tank thread tankdeath
    local.tank thread tanktrigger
    local.tank thread move_stuck_players
    local.tank thread tankdamagesmoke
end
```

### Use trigger (players enter tank via trigger_use)
```
tanktrigger:
    local.trig = spawn trigger_use targetname (self.name + "_trig")
    local.trig.origin = self.origin
    local.trig setsize ( -110 -110 -5 ) ( 110 110 160 )   // KingTank: -150/-150 to 150/150/180
    local.trig.tank = self
    local.trig glue self
    local.trig setthread triggered
end

triggered:
    local.player = parm.other
    // Check: not already driving, not in another vehicle, tank not dead, etc.
    if(self.tank.driver != NIL)
    {
        // Tank already has driver — offer turret slot if available
        self.tank thread turretslot_2nd local.player
    }
    else { self.tank thread playergetin }
end
```

### Turret control
```
tankreset local.groundtarget:
    self.gun = self queryturretslotentity 0    // main cannon (slot 0)
    self.gun2 = self queryturretslotentity 1   // secondary gun (slot 1, jeep_30cal)
    self.gun dmprojectile projectiles/tigercannonshell.tik
    self.gun setaimtarget local.groundtarget   // aim at a ground target script_origin
    self.gun turnspeed 50                      // degrees/sec turret rotation
end
```

### Chain reaction explosions
```
// When a killstreak item is near an exploding tank, it chain-detonates:
level.chainreactors[local.c] = local.tank
// On tank death, all chainreactors within level.sentry_deadradius are killed
```

### Guards against misuse
```
if(local.player.enteringvehicle == 1) { end }      // prevent double-enter
if(local.player.driving == 1) { end }              // already driving
if((local.player getcontrollerangles 0)[2] > 15)   // tilt check
```

---

## 72. attachparachute.scr — Parachute (Verbatim)

Attaches a parachute model to player and caps fall velocity at -200 units/sec.

```
main:
    self.parachute = spawn script_model
    self.parachute model equipment/parachute.tik
    self.parachute.origin = self.origin
    self.parachute.angle = self.angle
    self.parachute notsolid
    self.parachute attach self "bip01 spine2" 0 ( 0 0 0 )

    self.falling = 1

    thread playercancutparachute

    while(self.falling)
    {
        self.velocity = (self.velocity[0] self.velocity[1] -200)   // cap Z velocity

        if!(isalive self)
        {
            self.falling = 0
            self.parachute anim collapse
            wait 5
            self.parachute remove
        }

        waitframe
    }
end

playercancutparachute:
    while(self.useheld)   // wait until USE released first
        waitframe

    while(self.falling)
    {
        if(self.useheld)     // player presses USE to cut parachute
        {
            self.falling = 0
            self.parachute detach
            self.parachute remove
        }
        waitframe
    }
end
```

**Key details:**
- Attached to bone `"bip01 spine2"` — the torso/spine bone
- Model: `equipment/parachute.tik`
- Z velocity is forced to -200 every frame (overrides physics)
- USE key = cut parachute early
- If player dies, plays `collapse` animation then removes after 5s
- Call with: `self exec global/attachparachute.scr` or `$player[local.i] exec global/attachparachute.scr`

---

## 73. sv_maplists.scr — Multi-Maplist Rotation (Verbatim)

Allows more than 256 chars of maps in sv_maplist by chaining multiple cvars.

### server.cfg setup
```
seta sv_maplist  "dm/mohdm1 dm/mohdm2 dm/mohdm3 dm/mohdm4 dm/mohdm5 dm/mohdm6 dm/mohdm7"
seta sv_maplist2 "obj/obj_team1 obj/obj_team2 obj/obj_team3 obj/obj_team4"
seta sv_maplist3 "training m1l1 m1l2a m1l2b m1l3a m1l3b"
seta sv_maplist4 "m5l1a m5l1b m5l2a m5l2b m5l3 m6l1a m6l1b m6l1c"
```

### How it works
```
main local.debug:
    level.mapname = getcvar "mapname"
    if(getcvar "sv_maplist0" == "") { setcvar "sv_maplist0" (getcvar "sv_maplist") }  // save original

    // Loop through all sv_maplist0..sv_maplist999 to find current map
    for(local.c = 0; local.c <= 999; local.c++)
    {
        local.maplist = getcvar ("sv_maplist" + local.c)
        if(local.maplist == "") { break }
        // strstr simulation: scan for current mapname string inside maplist string
        for(local.s = 0; local.s < local.maplist.size; local.s++)
        {
            if(local.maplist[local.s] == level.mapname[0])   // first char match
            {
                local.mapfound = 1
                for(local.v = 0; local.v < level.mapname.size; local.v++)
                {
                    if(local.maplist[local.s + local.v] != level.mapname[local.v]) { local.mapfound = 0; break }
                }
            }
            if(local.mapfound == 1) { break }
        }
        if(local.mapfound == 1) { break }
    }

    // If current map is last in list, advance to next list:
    if(level.mapname == local.lastmap)
    {
        setcvar "sv_maplist" (getcvar ("sv_maplist" + (local.c + 1)))
    }
end
```

**Notes:**
- `sv_maplist0` stores the original list (do not set manually)
- Manually changelevel to a map not in sv_maplist → auto-copies correct list
- Add `exec global/sv_maplists.scr` to dmprecache.scr

---

## 74. killed.scr — Per-Player Kill Event Hook (Verbatim)

Called automatically when a player is killed. Increments a cvar by 1.

```
main local.cvar local.script:

    if(local.script == NIL)
    {
        self stufftext ( "add " + local.cvar + " 1" )  // stufftext to player's console adds to their cvar

        if(local.cvar == "times_killed")
        {
            if(level.killed_scripts != NIL)
            {
                for(local.i = 1; local.i <= level.killed_scripts.size; local.i++)
                {
                    self exec level.killed_scripts[local.i]   // run all registered kill scripts
                }
            }
        }
    }
    else
    {
        // Registration mode: add a script to the kill event queue
        if(level.killed_scripts == NIL) { level.killed_scripts[1] = local.cvar }
        else
        {
            local.i = level.killed_scripts.size
            local.i++
            level.killed_scripts[local.i] = local.cvar
        }
        end
    }
end
```

**Usage:**
```
// Register a script to run on every kill:
exec global/killed.scr "mykillmod" "global/killmod.scr"

// Inside killmod.scr, self = the player who was killed
```

---

## 75. get_weapon.scr — Get Player's Current Weapon Entity (Verbatim)

```
main:
    self weaponcommand dual targetname ("weapon" + self.entnum)
    local.weapon = $("weapon" + self.entnum)

    if(local.weapon != NULL)
    {
        self.weapon = local.weapon.model
        local.weapon targetname ""   // clean up the temporary targetname
    }
    else
    {
        self.weapon = "models/weapons/unarmed.tik"
    }
end
```

**Usage:**
```
$player[local.i] exec global/get_weapon.scr
println $player[local.i].weapon   // e.g. "models/weapons/thompsonsmg.tik"
```

**How it works:** Uses `weaponcommand dual targetname X` to temporarily give the player's held weapon a targetname, then looks it up by that name. The `.model` property gives the .tik path.

---

## 76. jetpackjump.scr — Per-Frame Jetpack Boost (Verbatim)

```
main:
    if(self.pack == 1)
    {
        self playsound jetpack
        self.velocity += self.upvector * 30       // add 30 units/frame upward
        self.jetpack.smoke[1].scale = 1.0
        self.jetpack.smoke[2].scale = 1.0
    }
end
```

Called every frame while the jetpack is active. `self.upvector` is the player's current up direction. The smoke emitter scales are set to 1.0 to show smoke effects.

---

## 77. killstreaks/damagehandler.scr — Chain Reaction (Verbatim)

```
main:
end

chain_reaction:
    local.killstreaks = makeArray
        sentry_turret level.sentry_deadradius
        claymore level.claymore_radius
        cluster_mine level.mines_radius
    endArray

    for(local.k = 1; local.k <= local.killstreaks.size; local.k++)
    {
        for(local.i = 1; local.i <= $(local.killstreaks[local.k][1]).size; local.i++)
        {
            if(self != $(local.killstreaks[local.k][1])[local.i] &&
               vector_length(self.origin - $(local.killstreaks[local.k][1])[local.i].origin) <= local.killstreaks[local.k][2])
            {
                $(local.killstreaks[local.k][1])[local.i].enemy_killer = self.enemy_killer
                killent $(local.killstreaks[local.k][1])[local.i].entnum
            }
        }
    }
end

assisted_suicide:
end
```

**How it works:**
- `makeArray` creates a 2-column matrix of [targetname, radius] pairs
- When any killstreak item explodes, it calls `chain_reaction` on itself
- All nearby items of any killstreak type within their respective radii are `killent`'d
- Propagates `enemy_killer` so the original player gets kill credit

---

## 78. loadout.scr — SP Campaign Weapon Loadouts (Verbatim Key Section)

Provides correct weapon loadout for each SP mission level. Called with the map script path.

```
main local.script:
    if(local.script == NIL) { level.script = "maps/m5l3.scr" }
    else { level.script = local.script }

    level waittill spawn

    if (game.loadout == NIL)
    {
        $player takeall

        // Always give empty grenade weapons:
        $player item weapons/M2frag_grenade_sp_start.tik
        $player item weapons/steilhandgranate_start.tik

        if (level.script == "maps/m1l2a.scr")     // Rescue Mission
        {
            $player item weapons/colt45.tik
            $player item weapons/m1_garand.tik
            $player item weapons/mp40.tik
            $player ammo pistol 200
            $player ammo smg 200
            $player ammo rifle 120
            $player ammo agrenade 4
            $player useweaponclass rifle
        }
        else if (level.script == "maps/m2l1.scr")  // The Sniper's Last Stand
        {
            $player item weapons/silencedpistol.tik
            $player item weapons/Springfield.tik
            $player item weapons/steilhandgranate.tik
            $player ammo pistol 200
            $player ammo smg 200
            $player ammo rifle 120
            $player ammo agrenade 4
            $player useweaponclass rifle
        }
        // ... (all 30+ SP missions covered)
    }
end
```

**Key SP ammo types:**
| Ammo class | Weapons |
|-----------|---------|
| `pistol` | colt45, silencedpistol, p38 |
| `rifle` | m1_garand, kar98, springfield |
| `smg` | thompsonsmg, mp40 |
| `mg` | BAR, mp44 |
| `heavy` | bazooka, panzerschreck |
| `grenade` | steilhandgranate |
| `agrenade` | m2frag_grenade |
| `shotgun` | shotgun |

---

## 79. punishments.scr — Admin Punishment System (Verbatim)

```
main local.words local.actual local.player:
    if(level.punishments == NIL) { level.punishments = waitthread get_menst }

    for(local.i = 1; local.i <= level.punishments.size; local.i++)
    {
        if(local.words[2] == level.punishments[local.i][1])
        {
            thread level.punishments[local.i][1] local.words::local.actual::local.player
            end 1
        }
    }
end

get_menst:
    // Register punishment aliases (sound caches)
    local.master = spawn ScriptMaster
    local.master aliascache rt sound/mechanics/Mec_SteamLoop_01.wav soundparms ...
    local.master aliascache rt1 sound/weapons/explo/Exp_Interior_04.wav soundparms ...
    // ...

    local.punishments = makearray
        "rocket"
        "morph"
    endarray
end local.punishments

rocket local.information:
    local.player = local.information[3]

    local.rocket = spawn script_model
    local.rocket model "models/static/v2.tik"
    local.rocket.origin = local.player.origin
    local.rocket scale 0.2
    local.rocket notsolid

    local.player physics_off
    local.player notsolid
    local.player takeall
    local.player resetstate

    local.origin = spawn script_origin
    local.origin.origin = local.rocket.origin + ( 16 0 0 )
    local.origin bind local.rocket
    local.player glue local.origin    // player rides the rocket

    local.rocket loopsound rt
    local.smoke = spawn script_model model "emitters/linger_smoke.tik"
    local.smoke scale 0.2
    local.smoke glue local.rocket

    wait 2
    local.rocket playsound rt1
    local.rocket time 5
    local.rocket moveup 3500     // shoot up 3500 units over 5 seconds
    local.rocket waitmove

    local.player physics_on
    local.player solid
    local.rocket explode
    local.rocket delete
end

morph local.information:
    local.player = local.information[3]
    local.model = local.information[1][1]
    local.scale = local.information[1][2]

    local.player hide
    local.model = spawn script_model model local.model scale local.scale
    local.model glue local.player    // model attached to player permanently (until disconnect)
end
```

---

## 80. Math Library (global/math.scr) — Summary

All trig functions implemented in pure Morpheus Script (no C builtins):

```
// Sine — Maclaurin series: sin(n) = n - nÂ³/3! + nâµ/5! - nâ·/7! + nâ¹/9! - nÂ¹Â¹/11!
// Cosine — even powers: cos(n) = 1 - nÂ²/2! + nâ´/4! - nâ¶/6! + nâ¸/8! - nÂ¹â°/10!
// Both require degrees between -180 and 180 (auto-constrained)

// Inverse trig — Newton's method, iterates until delta < 0.00000000001
// sqrt — Newton-Raphson method
// factorial — recursive computation

// Speed from velocity vector:
local.speed = sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

// Angles to direction (built-in):
local.fwd = angles_toforward self.angles
local.right = angles_toright self.angles
local.up = angles_toup self.angles
```

**Usage:**
```
local.sin_val = waitexec global/math.scr::sin 45        // returns ~0.7071
local.cos_val = waitexec global/math.scr::cos 45        // returns ~0.7071
local.sqrt_val = waitexec global/math.scr::sqrt 144     // returns 12
local.speed = waitexec global/math.scr::speed self.velocity
```

---

## 81. String Library (global/strings.scr) — Summary

Complete string manipulation library. All functions via `waitexec global/strings.scr::funcname`:

```
// Trim / slice:
waitexec global/strings.scr::trim local.str          // remove leading/trailing spaces
waitexec global/strings.scr::left local.str 3        // first 3 chars
waitexec global/strings.scr::right local.str 3       // last 3 chars
waitexec global/strings.scr::mid local.str 2 5       // chars 2–5

// Search / replace:
waitexec global/strings.scr::InStr local.str "foo"   // position of "foo" (0 if not found)
waitexec global/strings.scr::replace local.str "old" "new"
waitexec global/strings.scr::remove local.str "bad"

// Case:
waitexec global/strings.scr::to_lower local.str
waitexec global/strings.scr::to_upper local.str

// Split:
local.arr = waitexec global/strings.scr::split_string local.str " "  // split by space
local.arr = waitexec global/strings.scr::split_line local.str 1      // split line, returns [words_array, rest]

// Array conversions:
waitexec global/strings.scr::array_to_int local.arr
waitexec global/strings.scr::array_to_str local.arr
waitexec global/strings.scr::array_to_float local.arr
waitexec global/strings.scr::array_to_lower local.arr
waitexec global/strings.scr::Combine local.arr " "   // join array with separator

// Utilities:
waitexec global/strings.scr::reverse local.str
waitexec global/strings.scr::strip_newlines local.str
waitexec global/strings.scr::clean_filename local.str   // remove invalid filename chars
waitexec global/strings.scr::makeline local.str1 local.str2
waitexec global/strings.scr::add_quotes local.str      // wrap in ""

// Game helpers:
waitexec global/strings.scr::team_count "allies"   // number of allied players
waitexec global/strings.scr::light_from_string "1.0 0.5 0.2"  // RGB array from string
waitexec global/strings.scr::random_light          // random non-black RGB array
waitexec global/strings.scr::find_player local.entnum_string  // player entity from entnum string
```

---

## 82. Guided Missile System (GuidedMissile/Missile.scr)

Player-controlled missile with camera view.

### How it works
1. Missile spawns at player origin, player's view is replaced by missile camera
2. Missile velocity = player's viewangles direction Ã— 300 units/sec
3. Fire button fires the missile at 1000 units/sec
4. On collision: explosion + radiusdamage 300 units
5. Player respawns at missile's final location after use

### Key mechanics
```
// Velocity update per frame (guided phase):
local.missile.velocity = angles_toforward local.player.viewangles * 300

// Fire phase (player presses fire again):
local.missile.velocity = angles_toforward local.missile.angles * 1000

// Camera:
local.player cuecamera local.cam
local.cam follow local.missile

// Explosion:
radiusdamage local.missile.origin 300 300
local.missile damage $world 9999 $world (0 0 0) (0 0 0) (0 0 0) 0 0 16 0

// Player respawn at missile position:
local.player.origin = local.missile.origin
local.player respawn
```

### Team awareness
- If `g_teamdamage == 0`: damage only hits enemies
- If `g_gametype == 1` (FFA): hits everyone
- Config: `GMSettings[1]` = flight time, `GMSettings[2]` = max health, `GMSettings[3]` = enable health display

---

## 83. Admin Camera (global/ac/admincam.scr)

Allows an admin player to spectate another player with toggle controls.

```
// Admin becomes invisible and invulnerable:
admin hide
admin nodamage

// Camera positioned 56 units behind target at 24 units elevation:
local.cam.origin = target.origin - angles_toforward(target.angles) * 56 + (0 0 24)

// Controls (checked every 0.2 sec):
// FIRE = toggle between "eye view" (first person) and follow cam
// USE = end admin cam, restore admin's normal state

group.eye = 0   // 0 = follow cam, 1 = eye view

// Cleanup triggers if:
// - target player leaves (NULL)
// - target switches to spectator (dmteam == "spectator")
// → admin takedamage + admin show
```

---

## 84. Vehicle Teleporter (global/vehicle_tele.scr)

Teleports vehicles across walls/gates while maintaining direction.

```
// Spawn a teleport zone:
exec global/vehicle_tele.scr "entrance_trigger_origin" "exit_origin" 0 180
//                             entry_zone_origin         exit_origin  min_angle max_angle

// How it works:
// - Spawns a trigger zone at entry point
// - When a driven vehicle enters the trigger, it teleports to exit_origin
// - Angle constraints (0-180 or 90-270) prevent vehicles from flying off the map
// - Speed is capped at 300 units/sec during teleport
// - Optional laser visual effect changes color on successful teleport

// IMPORTANT: A solid floor entity is required for long-distance teleporters
// to prevent vehicles from blowing up or falling into the void
```

---

## 85. Survivor Game Mode (NOT_REBORN/Survivor/)

Round-based mode where players have limited lives. When all lives on a team are depleted, the other team wins the round.

### Setup (setup.scr)
```
main:
    // Check if Survivor enabled in settings
    if(level.survivor_enabled != 1) { end }

    // Load settings: lives, warmup, round limit
    level.survivor_lives = getsetting "survivor-lives" "3"
    level.survivor_warmup = getsetting "survivor-warmup" "20"
    level.survivor_rounds = getsetting "survivor-rounds" "3"

    level waittill spawn

    thread startround
end

startround:
    // Set objective display
    setcvar "g_obj_alliedtext1" (level.survivor_lives + " lives")
    setcvar "g_obj_axistext1" (level.survivor_lives + " lives")

    // Warmup phase
    thread warm_up
    wait level.survivor_warmup

    // Start actual round
    level.allies_lives = level.survivor_lives
    level.axis_lives = level.survivor_lives
    level.survivor_round_active = 1
end
```

### Files
| File | Purpose |
|------|---------|
| `setup.scr` | Init, round management |
| `spawned.scr` | Player spawn hook |
| `dead.scr` | Decrement lives, check win condition |
| `spectator.scr` | Force dead players to spectate |
| `roundend.scr` | Award round winner, advance rounds |
| `warm_up.scr` | Countdown before round starts |
| `camera.scr` | Deathcam within survivor mode |

---

## 86. Nagle Skin System (.st files)

UBER-MODS uses `.st` (StateMachine) files to replace player model skins without client downloads. One `.st` per body part per game version:

```
nagle_aa_torso.st     // Allied Assault torso replacement
nagle_aa_legs.st      // Allied Assault legs replacement
nagle_sh_torso.st     // Spearhead torso
nagle_sh_legs.st      // Spearhead legs
nagle_bt_torso.st     // Breakthrough torso
nagle_bt_legs.st      // Breakthrough legs
```

These override the player character state machine to replace animations and/or model references. The `.st` extension indicates a StateMachine definition file (not a script).

Anti-camper variant: `nocamp/nocamp_aa_legs.st` etc. — applies a visible "camper" indicator on the player model.

---

## 87. Bomber Plane Cache Requirements

When using `bomberplane.scr`, cache these models in dmprecache.scr or beforehand:
```
cache models/ammo/us_bomb.tik
cache models/emitters/fireandsmoke.tik
cache models/emitters/plane_smoke.tik       // only in UBER-MODS
cache models/emitters/mortar_dirt_nosound.tik
cache models/emitters/mortar_higgins.tik
cache models/vehicles/c47fly.tik
cache models/vehicles/p47fly.tik
cache models/vehicles/fockwulffly.tik
```

Sound aliases needed (registered via ScriptMaster aliascache):
```
explodeplane1-5   // sound/weapons/explo/Explo_MetalMed1-5.wav
leadinmp2         // sound/weapons/explo/Exp_LeadIn_07.wav
artyexp_sand1-4   // sound/weapons/explo/exp_dirt_01-04.wav
artyexp_water1-3  // sound/weapons/explo/exp_water_01-03.wav
airplane_flyover  // (from map/existing alias)
airplane_idle     // (from map/existing alias)
```

---

## 88. Admin Command System (global/ac/)

### Architecture
```
// In dmprecache.scr:
exec global/settings.scr   // loads Mods.txt, starts all enabled mods

// settings.scr registers admin commands in game.all_commands[]
// Player types: "admin_cmd 4 rocket" in console
// → dmprecache dispatches to global/ac/command_post/player_cmds.scr
// → player_cmds.scr finds matching punishment in level.punishments[]
// → calls punishment thread (rocket/morph/etc.)
```

### Command dispatch pattern
```
// game.all_commands usage:
local.cmd = waitexec global/settings.scr::getcmd "mycommand"
// cmd = { enabled, gametype_filter, map_filter, script_path }
waitexec global/settings.scr::setcmd "mycommand" 1   // enable/disable
```

### Available punishment commands
| Command | Effect |
|---------|--------|
| `rocket` | Player rides a V2 rocket into the sky, then explodes |
| `morph` | Replaces player model with a custom model+scale |

### Admin cam usage
```
// Admin types: "admincam <player_entnum>"
// Script execs global/ac/admincam.scr with the target player
// Admin: FIRE = toggle eye/follow, USE = exit cam
```

---

## 89. Complete UBER-MODS Feature Flags

All features are toggled via `level.run[]` in settings.scr or Mods.txt:

| Feature | Script | Notes |
|---------|--------|-------|
| Deathcam | `global/deathcam.scr` | Spectate killer; DO NOT use with custom_deaths.scr simultaneously |
| Respawn Fix | `global/respawn_fix.scr` | Smart spawn; needs `$allied_spawn`/`$axis_spawn` entities |
| Respawn Stuck Fix | `global/respawn_stuck_fix.scr` | Auto-respawn if stuck 3+ sec |
| Rocket Fix | `global/rocketfix.scr` | Fixes backward bazooka projectiles |
| Anti-Camper | `global/anti_camper.scr` | Position tracking, configurable radius+time |
| Jetpack | `global/jetpack.scr` | Airtank model + velocity boost on jump |
| Parachute | `global/attachparachute.scr` | USE to cut; velocity cap -200 Z |
| Throwing Knives | `global/throwingknife.scr` | USE+fire; screwdriver model; 3 max |
| Player Tank | `global/playertank.scr` | Drivable VehicleTank; 2-player (driver+gunner) |
| Player Boat | `global/playerboat.scr` | Drivable U-boat |
| Bomber Plane | `global/bomberplane.scr` | Spline-path + bomb drop; team-aware |
| Guided Missile | `GuidedMissile/Missile.scr` | Player-guided with camera view |
| Sentry Turret | `killstreaks/sentry_turret.scr` | MG42 auto-aiming kill reward |
| Claymore | `killstreaks/claymores.scr` | Proximity mine kill reward |
| Cluster Mines | `killstreaks/cluster_mines.scr` | Area mine kill reward |
| Survivor Mode | `Survivor/setup.scr` | Round-based, limited lives |
| Hold The Radio | `HTR/setup.scr` | HTR game mode |
| Weather | `global/weather.scr` | Rain/snow/fog |
| Multi-Maplist | `global/sv_maplists.scr` | sv_maplist2/3/4 rotation |
| Player Taunts | `global/player_taunts.scr` | USE x4 in 1 sec = taunt |
| Vehicle Teleporter | `global/vehicle_tele.scr` | Teleport vehicles through walls |
| Admin Cam | `global/ac/admincam.scr` | Spectate specific player |
| Spawn Protection | `global/ac/spawn_protection.scr` | Invulnerable window on spawn |
| Team Balance | `global/ac/team_balance.scr` | Auto-equalize team sizes |

---

## 90. Spawn Protection (global/ac/spawn_protection.scr) — Verbatim

Gives a player temporary invulnerability after respawning. Ends early if they fire.

```
main:
    if(self.dmteam == "spectator") { end }
    if(level.run["spawn-protection"] != "1") { end }

    local.team = waitexec global/settings.scr::getcmd "spawn-team"
    if(local.team != "both")
    {
        if(self.dmteam != local.team) { end }
    }

    local.print = waitexec global/settings.scr::getcmd "print-sp"
    if(local.print == "1")
    {
        self stufftext "locationprint 500 60 Spawn-Protect-On 1"
    }

    local.time = int(waitexec global/settings.scr::getcmd "invulnerabletime")

    // Optional: emit a colored light glow on the protected player
    local.lightn = waitexec global/settings.scr::getcmd "spawn-light"
    if(local.lightn == "1")
    {
        local.lightcolour = waitexec global/settings.scr::getcmd "spawn-lightcolour"
        // parse "R G B radius" string into array
        self light local.light[0] local.light[1] local.light[2] local.light[3]
    }

    self nodamage
    for(local.i = 0; local.i <= local.time; local.i = local.i + .1)
    {
        wait .1
        if(self.fireheld == 1 || self.dmteam == "spectator") { break }  // cancel if fires
    }

    if(local.print == "1") { self stufftext "locationprint 500 50 Spawn-Protect-Off 1" }
    self takedamage
    self light 0 0 0 0   // remove the glow
end
```

**Settings keys (in spawn_protection.txt):**
| Key | Value | Meaning |
|-----|-------|---------|
| `spawn-protection` | 1/0 | Enable/disable |
| `spawn-team` | "both"/"allies"/"axis" | Which team gets protection |
| `invulnerabletime` | seconds (float) | Duration |
| `spawn-light` | 1/0 | Show colored glow |
| `spawn-lightcolour` | "R G B radius" | Light color |
| `print-sp` | 1/0 | Show locationprint message |

**Note:** `spawn_protection_setup.scr` disables spawn protection on SH/BT unless `game.run_spawn_protect_on_sh_and_bt = 1`:
```
if(game.game != "AA")
{
    if(game.run_spawn_protect_on_sh_and_bt != 1) { level.run["spawn-protection"] = 0 }
}
```

---

## 91. Team Balance (global/ac/team_balance.scr) — Verbatim

Automatically moves a random dead player from the larger team when imbalance > 1.

```
main:
    if(level.run["team-balance"] != "1") { end }

    while(level.run["team-balance"] == "1")
    {
        local.scantime = waitexec global/settings.scr::getcmd "scan-wait"
        wait local.scantime   // configurable check interval

        if($player.size > 1)
        {
            local.team[allies] = 0
            local.team[axis] = 0

            for(local.i = 1; local.i <= $player.size; local.i++)
            {
                if($player[local.i].dmteam != "spectator")
                {
                    local.team[$player[local.i].dmteam]++
                }
            }

            // Only balance if difference > 1
            if(local.team[allies] - local.team[axis] > 1)
            {
                local.menneske = waitthread pick_random_player "allies"
                local.menneske waitthread swap_team
            }
            else if(local.team[axis] - local.team[allies] > 1)
            {
                local.menneske = waitthread pick_random_player "axis"
                local.menneske waitthread swap_team
            }
        }
    }
end

pick_random_player local.team:
    while(1)
    {
        local.kanskje = randomint($player.size) + 1
        if($player[local.kanskje].dmteam == local.team && !(isalive $player[local.kanskje]))
        {
            end $player[local.kanskje]   // prefer dead players for the swap
        }
        wait 1
    }
end

swap_team:
    local.team = self.dmteam
    self auto_join_team   // game engine auto-assigns to smaller team
    wait 1
    if(self.dmteam != local.team)
    {
        self iprint "You were randomly picked to swap teams to even them out" 1
    }
end
```

---

## 92. Lean Bind Detection (global/ac/check_leanbind.scr) — Verbatim

Checks player key bindings against a list of known lean exploit binds.

```
main:
    if(level.run["check_leanbind"] != "1") { end }

    while(level.run["check_leanbind"] == "1")
    {
        wait 1
        for(local.i = 1; local.i <= $player.size; local.i++)
        {
            $player[local.i] waitthread check_leanbind
            wait 1
        }
    }
end

check_leanbind:   // self = player
    local.possibilities = waitexec settings/lean_binds/lean_binds.txt  // load bind list from file

    for(local.i = 1; local.i <= local.possibilities.size; local.i++)
    {
        local.bind = local.possibilities[local.i][1]

        local.key[1] = getboundkey1 local.bind   // get what keys are bound to this action
        local.key[2] = getboundkey2 local.bind

        if(local.key[1] != "Not Bound" || local.key[2] != "Not Bound")
        {
            self thread using_lb   // flag: player has a lean bind
        }
    }
end

using_lb:
    if(self.lb == NIL) { self.lb = 0 }
    self.lb++
    iprintln ("using lean bind " + self.lb)
end
```

**Key commands:**
- `getboundkey1 "action"` — returns the first key bound to that action (e.g. `"+moveright"`)
- `getboundkey2 "action"` — returns the second key bound to that action
- Returns `"Not Bound"` if action has no binding

---

## 93. CVar Forcer (global/ac/cvar_forcer.scr) — Verbatim

Forces specific cvars on all players every second. Settings loaded from a file.

```
main:
    if(level.run["cvar-forcing"] != "1") { end }

    local.cvars = waitexec game.file["cvar-forcing"]::cvar_force  // load cvar list

    if(!local.cvars.size) { end }

    while(level.run["cvar-forcing"] == "1")
    {
        wait 1
        for(local.i = 1; local.i <= $player.size; local.i++)
        {
            wait 1
            for(local.c = 1; local.c <= local.cvars.size; local.c++)
            {
                wait 1
                $player[local.i] stufftext (local.cvars[local.c][1] + " " + local.cvars[local.c][2])
                // stufftext sends "cvarname value" to the client's console
            }
        }
    }
end
```

**Settings file (cvar_forcing.txt) format:**
```
cvar_force:
    fov 90
    cg_crosshairsize 24
    m_pitch 0.022
end local.cvars
```

---

## 94. One-Word Admin Commands (global/ac/command_post/one_word.scr) — Verbatim

Handles admin commands that are a single word (no player target needed).

```
main local.word:
    switch(local.word)
    {
    case "help":
        exec global/help.scr::help 1
    break
    case "adminscan":
        // Scan all players for admin status by sending a stufftext probe
        local.rcon = getcvar "rconpassword"
        local.text = (local.rcon == "") ? "admin_cmd" : "rcon admin_cmd"
        for(local.i = 1; local.i <= $player.size; local.i++)
        {
            if($player[local.i].admin != 1)
            {
                $player[local.i] stufftext (local.text + " `imadmin_" + $player[local.i].entnum)
            }
            wait 3
        }
    break
    case "hello":
        local.hello = waitexec global/ac/hello_world.scr
        iprintln_noloc "omg serious??? oooook"
        wait 3
        for(local.i = 1; local.i <= local.hello.size; local.i++)
        {
            wait 1
            iprintln_noloc local.hello[local.i][1]
        }
    break
    case "reset":
        exec global/ac/admin_feedback.scr "Admin-Pro Mod Reset"
        exec global/ac/console_feedback.scr "Admin-Pro Mod Reset"
        level.camper_setup = 0
        game.reset = "1"
        exec global/settings.scr   // full mod reload
    break
    case "inputtoggle":
        // Toggle between Windows (space-separated) and Linux (underscore-separated) input parsing
        if(game.input_type == "windows") { game.input_type = "linux" }
        else { game.input_type = "windows" }
    break
    }
end 1
```

---

## 95. exploder_killer.scr — Destructible Walls System

The most complex UBER-MODS utility. Creates destructible walls/buildings that blow up when hit by rockets/projectiles or explosions.

### Overview
```
// Step 1: Run exploder.scr to find all $exploder entities in the map
exec global/exploder.scr

// Step 2: For each destructible wall, run exploder_killer.scr with full parameters
exec global/exploder_killer.scr \
    (damage_origin1)   (damage_origin2)        // 2 radiusdamage positions (both sides of wall)
    (explosion_origin) (debris_origin) angle   // explosion visual + debris flying direction
    (smoke_origin1)    (smoke_origin2)          // 2 sherman smoke emitters
    (trig_setsize1)    (trig_setsize2)          // trigger box mins/maxs
    set_number  damage  radius  smaller
```

### How it works
1. Spawns `trigger_multiple spawnflags 128` (explosion trigger) around the wall
2. Spawns `trigger_multiple spawnflags 20` (projectile trigger) around the wall
3. When a rocket/bazooka/panzerschreck/cannon shell passes through → triggers explosion
4. When a $world radiusdamage (grenade, bomb) hits the explosion trigger → triggers explosion
5. On explosion:
   - Calls `global/exploder.scr::explode set` to toggle wall geometry
   - Spawns `emitters/explosion_tank.tik` + `animate/explosion_bombwall.tik` + smoke
   - Calls `radiusdamage` at 2 positions (both sides of the wall)
   - `exec global/earthquake.scr` for screen shake
   - Optionally resets after `level.exploder_killer_resettime` seconds

### Projectile models detected
```
models/projectiles/bazookashell_dm.tik
models/projectiles/bazookashell.tik
models/projectiles/panzerschreckshell.tik
models/projectiles/tigercannonshell.tik
// Grenades only if: level.exploder_killer_grenades = 1
models/projectiles/m2fgrenade_primary.tik
models/projectiles/steilhandgranate_primary.tik
models/projectiles/panzerivshell.tik
```

### Level flags
```
level.exploder_killer_onlyprojectiles = 1    // no world radiusdamage, rockets only
level.exploder_killer_grenades = 1           // grenades also trigger it
level.exploder_killer_resettime = 60         // reset wall after 60 seconds
level.exploder_killer_nosound = 1            // no explosion sound
level.exploder_killer_noearthquake = 1       // no screen shake
level.exploder_killer_nottriggerable = 1     // manual trigger only (set $exploder.dead = 1)
level.exploder_killer_noprint = 1            // no console messages
```

### Multi-building setups
To blow up multiple connected buildings together: use the same `set` number for all, but set both `trig_setsize` to `(0 0 0)` for secondary buildings. They share the primary's triggers.

### Smoke fade-out pattern
```
local.dec = 0.01   // 0.05 sec per frame / 5 sec duration = 0.01 scale decrement
while(smoke.scale > 0)
{
    smoke.scale -= local.dec
    waitframe
}
smoke remove
```

---

## 96. Earthquake / Screen Shake (global/earthquake.scr)

Used internally by exploder_killer.scr. Produces camera shake at configurable magnitude and duration.

```
// Usage from exploder_killer.scr:
waitexec global/earthquake.scr .35 10 0 0     // (magnitude, duration, x, y)
waitexec global/earthquake.scr .23 6 0 0
waitexec global/earthquake.scr 1 1 0 0
waitexec global/earthquake.scr 1.25 .3 0 1   // last param = 1 means "smaller" shake

// Direct usage:
exec global/earthquake.scr 0.5 3 0 0   // magnitude=0.5, duration=3sec
```

---

## 97. Player Taunts (global/player_taunts.scr) — Summary

USE key Ã— 4 within 1 second triggers a taunt animation.

**Mechanics:**
- Player must press USE 4 times within 1 second (not 5 as docs say — actual code varies)
- Cannot hold FIRE while doing USE
- Player must be alive and not in: spectator, dog, turret, flying, driving states
- Taunt anim: `show_papers` if holding a weapon, `selectionidle` if unarmed
- Duration: 3–6 seconds
- Cooldown: 3 seconds between taunts
- Cancelled if player fires or switches weapons

**Installation requirement:**  
Must comment out 3 "server" lines in `show_papers` animation within `anims_shared.txt`, and add `PLAYER_TAUNT` state to the player torso state machine (`.st` file).

**Not compatible** with mods that have their own `mike_torso.st` without proper integration.

---

## 98. Dog Entity (global/dog.scr) — Summary

Spawns an attack dog that tracks and attacks enemy players.

**Key mechanics:**
- Uses `models/animal/german_shepherd.tik`
- Dog attacks enemy players within its radius (team-aware)
- Can be assigned to a specific player as owner
- On death: plays death animation, then removes
- `multi_dog.scr` variant spawns multiple dogs simultaneously

**Usage:**
```
exec global/dog.scr "dogname" (x y z) 0 "axis"    // name, origin, angle, team
// or from a player:
self exec global/dog.scr                            // spawns dog at player position
```

---

## 99. Doorlocked.scr — Locked Door Sounds

Plays locked door sounds when a player stands near a door and holds USE. No entity spawning in the map editor required.

**Door types and sounds:**
| Type | Sound |
|------|-------|
| `wood` | `sound/mechanics/DoorWood_locked_01.wav` |
| `metal` | `sound/mechanics/DoorMetal_Locked_01.wav` |
| `gateiron` | `sound/mechanics/IronGate_locked_01.wav` |
| `gatelarge` | `sound/mechanics/LargeGate_locked_01.wav` |
| `gatemetal` | `sound/mechanics/MetalGate_locked_01.wav` |
| `garagedoor` | `sound/mechanics/GarageDoor_locked.wav` |
| `vent` | `sound/mechanics/Vent_Locked_01.wav` |

**Usage:**
```
exec global/doorlocked.scr (x y z) "wood" 5    // origin, type, set_number
// set_number links to an $exploder set — door unlocks when that set is destroyed
```

---

## 100. Mines System (global/ac/mines/) — Summary

Players can place mines as a gameplay feature. Managed via `mines_main.scr`.

**Types:**
- `chuck` — thrown proximity mine
- `sticky_chuck` — sticks to surfaces  
- `stickybombs` — explosive charge

**Mechanics:**
```
// Two triggers per mine:
local.trig_shot = spawn trigger_multiple spawnflags 128   // shot/explosion trigger
local.trig_step = spawn trigger_multiple                   // player proximity trigger

// Configurable disarm mechanic:
// Player holds USE within 150 units for configurable seconds to disarm

// Ammo limit:
local.max_mines = waitexec global/settings.scr::getcmd "mines-ammo"

// Team damage:
if(local.player.dmteam == self.owner.dmteam && g_teamdamage != "1") { skip damage }
```

**Settings keys:**
```
mines-ammo      // max mines per player
mines-time      // seconds to arm
mines-disarm    // seconds to disarm (if 0, cannot disarm)
mines-radius    // explosion radius (used in chain_reaction)
```

---

## 101. Settings System — How settings.scr + Mods.txt Works

The UBER-MODS settings system is a data-driven mod loader. Here is the architecture:

### Mods.txt format
```
// settings/Mods.txt
// Each line = mod name. Lines starting with "//" are comments.
deathcam
respawn_fix
anti_camper
jetpack
spawn-protection
team-balance
cvar-forcing
```

### Per-mod settings files
Each enabled mod has `settings/<modname>.txt` with key=value pairs:
```
// settings/anti_camper.txt
camp-time 15        // seconds before camper warning
camp-radius 100     // units radius to check for movement
camp-sound 1        // play sound on detection
```

### settings.scr core functions
```
// Check if mod is enabled for current gametype+map:
on_or_off "modname"
→ returns 1 if: mod in Mods.txt AND gametype matches AND map matches

// Get a setting value:
local.val = waitexec global/settings.scr::getcmd "keyname"

// Set a setting value:
waitexec global/settings.scr::setcmd "keyname" "newvalue"

// Register a cvar from settings:
register "keyname" "cvarname"   // sets getcvar("cvarname") from settings file

// Get current map name formatted for file loading:
waitexec global/settings.scr::get_mapstr
→ returns "dm_mohdm1" from "dm/mohdm1" (slashes → underscores)
```

### level.run[] flag dictionary
```
level.run["deathcam"] = "1"          // mod is active
level.run["respawn_fix"] = "1"
level.run["spawn-protection"] = "1"
level.run["team-balance"] = "1"
level.run["cvar-forcing"] = "1"
level.run["anti_camper"] = "1"
level.run["check_leanbind"] = "1"
// Checking:
if(level.run["mymod"] != "1") { end }
```

### game.all_commands[] registry
```
// Commands are stored as arrays: game.all_commands[cmd_name][param]
// param 1 = enabled (1/0)
// param 2 = gametype filter  
// param 3 = map filter
// param 4 = script path to execute

// Dispatch (from console or admin interface):
local.cmd = waitexec global/settings.scr::getcmd "mycommand"
if(local.cmd != NIL) { exec local.cmd }
```

---

## 102. Multi-Maplist Rotation — Complete Reference

Allows multiple sv_maplist cvars (max 256 chars each) to be chained:

```
// server.cfg:
seta sv_maplist  "dm/mohdm1 dm/mohdm2 dm/mohdm3"
seta sv_maplist2 "obj/obj_team1 obj/obj_team2"
seta sv_maplist3 "m1l1 m1l2a m1l2b m1l3a"

// dmprecache.scr:
exec global/sv_maplists.scr
```

**Rules:**
- `sv_maplist0` is reserved (auto-saved copy of original `sv_maplist`)
- Can use either `sv_maplist1` or `sv_maplist2` as the second list (skips 1 if blank)
- When current map = last map in list → copies next list to `sv_maplist`
- Manually changelevel → auto-copies matching list to `sv_maplist`
- Debug: `exec global/sv_maplists.scr 1` (add parameter 1 to enable debug output)

---

## 103. Player Spotlight (global/player_spotlight.scr)

Spawns an automatic searchlight that follows a spline path and locks onto nearby players.

**Configuration:**
```
exec global/player_spotlight.scr (x y z) 1 0 1 "spotlight1" 300 180 0 0
//                                origin  R G B  name        health angle wall_mount rotate

// Adjustable global vars:
level.autospot_trigdist = 500     // units: distance to lock onto player
level.autospot_movespeed = 1.0    // speed along spline path

// Mount orientations (wall_mount param):
// 0 = floor mount
// 1 = north wall
// 2 = east wall
// 3 = ceiling
```

**Behavior:**
- Follows SplinePath until a player comes within `level.autospot_trigdist`
- Locks onto the player and illuminates with a colored light
- Fire button: player can take manual control (if admin)
- USE button: releases manual control

---

## 104. UBER-MODS Debug/Dev Tools (cvars/)

Located in `NOT_REBORN/cvars/`. Accessed via `admin_cmd` console commands.

| Script | Command | Function |
|--------|---------|----------|
| `cvars.scr` | — | Loads all dev tools at startup |
| `findent.scr` | `findent classname` | Find entity by classname |
| `findmodel.scr` | `findmodel path` | Find entity by model path |
| `findclass.scr` | `findclass X` | Find by class |
| `entitycount.scr` | `entitycount` | Print total entity count |
| `track.scr` | `track name` | Print entity origin each frame |
| `entity_pointer.scr` | `pointer name` | Laser beam to entity origin |
| `coord_pointer.scr` | `coords` | Print player's current coordinates |
| `drawpath.scr` | `drawpath name` | Draw spline path visually |
| `drawsize.scr` | `drawsize name` | Draw entity bounding box |
| `faceto.scr` | `faceto name` | Turn player to face entity |
| `playernames.txt` | — | Player name database |
| `playerspawns.scr` | `playerspawns` | List all spawn point coords |
| `ubergametype.scr` | `gametype X` | Change gametype via console |

**entprint function** (inside cvars.scr):
```
entprint local.ent:
    println ("origin: " + local.ent.origin)
    println ("angles: " + local.ent.angles)
    println ("classname: " + local.ent.classname)
    println ("model: " + local.ent.model)
    println ("health: " + local.ent.health)
    // + targetname, set, team, driver info, etc.
end
```

---

## 105. Countdown Game Mode (NOT_REBORN/countdown/)

Per-map countdown scripts that enforce a time limit and round system. One file per map.

**Template structure:**
```
// countdown/mohdm1.scr
main:
    if(level.run["countdown"] != "1") { end }
    exec countdown/Template.txt   // load countdown settings

    level waittill spawn

    thread countdown_timer
    thread win_condition
end

countdown_timer:
    local.time = waitexec global/settings.scr::getcmd "countdown-time"
    local.time = int(local.time)
    while(local.time > 0)
    {
        wait 1
        local.time--
        // update HUD display
        huddraw_rect ...
        huddraw_string ...
    }
    // Time expired → end round
    thread round_over "time"
end
```

**Supported maps (countdown files exist for):**
```
mohdm1-7, mp_anzio_lib, mp_ardennes_tow, mp_bahnhof_dm, mp_bazaar_dm,
mp_berlin_tow, mp_bizertefort_obj, mp_bizerteharbor_lib, mp_bologna_obj,
mp_brest_dm, mp_castello_obj, mp_druckkammern_tow, mp_flughafen_tow,
mp_gewitter_dm, mp_holland_dm, mp_kasserine_tow, mp_malta_dm,
mp_montebattaglia_tow, mp_montecassino_tow, mp_palermo_dm, mp_palermo_obj,
mp_ship_lib, mp_stadt_dm, mp_tunisia_lib, mp_unterseite_dm,
mp_verschneit_dm, obj_team1-4
```

---

## 106. HTR (Hold The Radio) Game Mode (NOT_REBORN/HTR/)

Radio-capture objective mode.

**Files:**
| File | Purpose |
|------|---------|
| `setup.scr` | Init: radio entity, teams, scoring |
| `radio.scr` | Radio object behavior |
| `player_radio.scr` | Per-player radio interaction |
| `player_scan.scr` | Detect players near radio |
| `camera.scr` | Spectate camera |
| `hud.scr` | Score/time HUD display |
| `coords.scr` | Radio position tracking |

**Gameplay:**
- Radio spawns at a fixed point on the map
- Team that holds the radio earns points over time
- Radio is a physical entity that can be picked up/dropped
- `Countdown non AP 1.5/` subfolder = version without Admin-Pro dependency

---

## 107. UBER-MODS Bip01 Skeleton Reference

From `Bip01 skeleton.txt` in the root of the repo. All bone attachment points:

```
// Root
bip01
bip01 pelvis
bip01 spine           // lower back
bip01 spine1          // mid back
bip01 spine2          // upper back / chest â† PARACHUTE attach point
bip01 neck
bip01 head

// Left arm
bip01 l clavicle
bip01 l upperarm
bip01 l forearm
bip01 l hand
bip01 l finger0       // thumb
bip01 l finger1
bip01 l finger11
bip01 l finger12

// Right arm  
bip01 r clavicle
bip01 r upperarm
bip01 r forearm
bip01 r hand

// Left leg
bip01 l thigh
bip01 l calf
bip01 l foot
bip01 l toe0

// Right leg
bip01 r thigh
bip01 r calf
bip01 r foot
bip01 r toe0
```

**Common attach bones:**
| Bone | Common use |
|------|-----------|
| `bip01 spine2` | Backpack, parachute, airtank |
| `bip01 r hand` | Held item in right hand |
| `bip01 l hand` | Held item in left hand |
| `bip01 head` | Hat, helmet overlay |
| `bip01 pelvis` | Belt items |

---

## 108. Complete Cache List (dmprecache.scr)

All models that UBER-MODS pre-caches for smooth gameplay (no model pop-in):

**Player skins (all cached):**
```
allied_airborne, allied_manon, allied_pilot, allied_sas
american_army, american_ranger
german_afrika_officer, german_afrika_private
german_elite_officer, german_elite_sentry
german_kradshutzen, german_panzer_grenadier
german_panzer_obershutze, german_panzer_shutze
german_panzer_tankcommander, german_scientist
german_waffenss_officer, german_waffenss_shutze
german_Wehrmacht_officer, german_Wehrmacht_soldier
german_winter_1, german_winter_2, german_worker
// NOT cached (missing tiks): allied_oss, german_elite_gestapo
```

**Vehicles:**
```
kingtank (YES), tigertank (NO — spams console), jeep (NO — spams console)
kingtank_all_d, kingtank_d, shermantank, sdkfz
opeltruck, opeltruck_d, jeep_30cal, jeep_30cal_viewmodel
vehiclesoundentity, bmwbike, uboat, stuka_d, shermantank_damaged
fockwulffly, p47fly, stuka_fly
```

**Weapons (all standard MP weapons cached):**
```
colt45, p38, silencedpistol, m1_garand, kar98, kar98sniper
springfield, thompsonsmg, mp40, mp44, bar, bazooka
panzerschreck, shotgun, m2frag_grenade, steilhandgranate
flak88turret, mg42_gun, mg42_gun_fake
```

**FX (complete):**
- All `bh_*` bullet holes (carpet/dirt/foliage/glass/grass/metal/mud/paper/sand/snow/stone/water/wood Ã— hard/lite variants)
- All `fs_*` footstep effects (dirt/grass/heavy_dust/light_dust/mud/puddle/sand/snow)
- All `grenexp_*` grenade explosions (15 surface types)
- All water FX: water_ripple_moving/still, water_splash_drop, water_spray, water_trail_bubble

---

## 109. spectator_jointeam.scr — The "Chose Team But Not Yet Spawned" Edge Case (Verbatim)

A subtle but important helper. When a spectator picks a team but hasn't selected a weapon yet, their `.dmteam` is no longer `"spectator"` but they are still in a limbo state. This can allow mods to trigger on them unintentionally.

```
// Pattern to check if player has FULLY left spectator:
if(self.dmteam != "spectator" && self.spectator_jointeam != 1)

// Pattern to check if player is STILL in any spectator state:
if(self.dmteam == "spectator" || self.spectator_jointeam == 1)
```

**Full implementation:**
```
main:
    if(level.spectator_jointeam_script == 1) { end }  // only run once
    level.spectator_jointeam_script = 1

    while(1)
    {
        for(local.i = 1; local.i <= $player.size; local.i++)
        {
            if($player[local.i].dmteam == "spectator" && $player[local.i].spectator_jointeam == NIL)
            {
                $player[local.i] thread player_fromspectator
                $player[local.i].spectator_jointeam = 1
            }
        }
        waitframe
    }
end

player_fromspectator:
    while(self != NULL && self.dmteam == "spectator") { waitframe }  // wait until team chosen
    while(self != NULL && self.dmteam != "spectator")
    {
        local.weapon = self waitthread check_hand_weapon
        if(local.weapon != NIL && local.weapon != NULL) { break }    // wait until weapon held
        waitframe
    }
    if(self != NULL) { self.spectator_jointeam = NIL }   // now fully in-game
end

check_hand_weapon:
    local.tname = "mefgun" + self.entnum
    local.maxframes = 30
    local.numframes = 0
    local.weapon = NULL
    while(self != NULL && self.dmteam == local.team)
    {
        self weaponcommand dual targetname local.tname
        local.weapon = $(local.tname)
        if(local.weapon != NULL || local.numframes > local.maxframes) { break }
        waitframe
        local.numframes++
    }
    if(local.weapon != NULL) { local.weapon.targetname = NIL }
end local.weapon
```

**Add to your mod:** `exec global/spectator_jointeam.scr` in dmprecache.scr.

---

## 110. modelfix.scr — Anti-Crash FPS Model Filter (Verbatim)

A security check that kicks players trying to use FPS (first-person shooter view model) entities as player models — this would crash the server.

```
main:
    local.in = waitexec global/strings.scr::InStr "fps" self.model

    if(local.in != NIL)
    {
        self noclip
        self physics_off
        self stufftext "say I am trying to crash the server"
        self stufftext "dissconnect"   // intentional misspelling in original
    }
end
```

Checks if `"fps"` appears anywhere in the player's current model path. If so, forces disconnect. Run per player on spawn.

---

## 111. Guided Missile Spawn Trigger (GuidedMissile/SpawnTrigger.scr)

Spawns a pickup trigger that lets players activate a guided missile. Team inventory tracked.

```
// How SpawnTrigger.scr works:
main local.origin local.team_limit_allies local.team_limit_axis:

    // 1. Cache models + load settings from settings/GuidedMissile.txt
    cache models/weapons/bazooka.tik
    local.settings = waitexec settings/GuidedMissile.txt

    // 2. Spawn visible pickup model at origin
    local.pickup = spawn script_model model "models/weapons/bazooka.tik"
    local.pickup.origin = local.origin
    local.pickup notsolid

    // 3. Spawn trigger_use at same origin
    local.trig = spawn trigger_use
    local.trig.origin = local.origin
    local.trig setthread Go

    // 4. Track per-team inventory
    level.gm_stock_allies = local.team_limit_allies
    level.gm_stock_axis = local.team_limit_axis
end

Go:
    local.player = parm.other
    if(local.player.classname != Player || local.player.hasmissile == 1) { end }

    // Check team inventory
    if(local.player.dmteam == "allies" && level.gm_stock_allies <= 0)
    {
        local.player iprint "Out of Stock!"
        end
    }
    if(local.player.dmteam == "axis" && level.gm_stock_axis <= 0)
    {
        local.player iprint "Out of Stock!"
        end
    }

    // Decrement stock
    if(local.player.dmteam == "allies") { level.gm_stock_allies-- }
    if(local.player.dmteam == "axis")   { level.gm_stock_axis-- }

    local.player.hasmissile = 1
    local.player exec GuidedMissile/Missile.scr
end
```

---

## 112. Practical Quick-Reference: UBER-MODS Patterns

### Pattern 1 — Check mod is enabled before running any logic
```
main:
    if(level.run["mymod"] != "1") { end }
    // ... mod code
end
```

### Pattern 2 — Per-player loop with waitframe
```
while(1)
{
    for(local.i = 1; local.i <= $player.size; local.i++)
    {
        if($player[local.i] == NIL || $player[local.i] == NULL) { continue }
        if($player[local.i].dmteam == "spectator") { continue }
        if($player[local.i].spectator_jointeam == 1) { continue }  // add if using spectator_jointeam.scr
        if(!isalive $player[local.i] || $player[local.i].dead == 1) { continue }
        // process player
    }
    waitframe
}
```

### Pattern 3 — Run a script on every player death
```
// In dmprecache.scr or your mod init:
exec global/killed.scr "mykillmod" "global/mymod_onkill.scr"
// mymod_onkill.scr: self = player who died
```

### Pattern 4 — Get player's current weapon model
```
$player[local.i] exec global/get_weapon.scr
local.weapon_model = $player[local.i].weapon
// e.g. "models/weapons/thompsonsmg.tik"
```

### Pattern 5 — stufftext to force a client cvar
```
$player[local.i] stufftext "fov 90"          // set fov
$player[local.i] stufftext "add kills 1"     // increment kills counter
$player[local.i] stufftext "locationprint 400 30 Hello! 1"  // on-screen message
```

### Pattern 6 — spawn trigger_use with thread callback
```
local.trig = spawn trigger_use targetname "my_trigger"
local.trig.origin = ( 100 200 50 )
local.trig setsize ( -32 -32 0 ) ( 32 32 64 )
local.trig setthread on_use     // fires "on_use:" label in this script when triggered
// parm.other = the entity that triggered it (usually a Player)
```

### Pattern 7 — spawn trigger_multiple spawnflags 128 (shootable)
```
local.trig = spawn trigger_multiple spawnflags 128
local.trig.origin = ( x y z )
local.trig setsize ( -8 -8 -8 ) ( 8 8 8 )
local.trig setthread on_shot
// Fires on_shot: when any weapon projectile or explosion hits it
```

### Pattern 8 — glue entity to moving object
```
local.entity glue local.vehicle     // entity moves with vehicle
local.entity unglue                 // detach
local.entity.origin = local.vehicle.origin + ( 0 0 50 )  // reposition before glue
```

### Pattern 9 — Follow a spline path
```
$splineobject followpath $my_path_entity
$splineobject playsound airplane_flyover
$splineobject waitmove   // block until path complete
$splineobject remove
```

### Pattern 10 — Sound alias caching (ScriptMaster aliascache)
```
local.master = spawn scriptmaster
local.master aliascache mysound "sound/path/file.wav" soundparms 1.0 0.0 1.0 0.0 300 3000 auto loaded maps level.mapname
// soundparms: volume_mult pitch_variance volume_variance pitch_mult min_dist max_dist channel loaded_or_streamed
self playsound mysound   // plays the cached alias on self
```

### Pattern 11 — makeArray for multi-column data tables
```
local.table = makeArray
    "key1"  "value1"  100
    "key2"  "value2"  200
    "key3"  "value3"  300
endArray
// Access: local.table[1][1] = "key1", local.table[1][2] = "value1", local.table[1][3] = 100
// local.table.size = 3 (rows)
// local.table[1].size = 3 (columns)
```

### Pattern 12 — Read settings from file (waitexec .txt)
```
local.config = waitexec settings/mymod.txt::mysection
// settings/mymod.txt contents:
//   mysection:
//       option1 value1
//       option2 value2
//   end local.config
// local.config[1][1] = "option1", local.config[1][2] = "value1"
```

---

## 113. All UBER-MODS Sound Aliases Used

Key sound aliases registered via ScriptMaster in various scripts:

| Alias | File | Used in |
|-------|------|---------|
| `manon_pain` | `sound/null.wav` | dmprecache.scr (null = silence for maps without Manon) |
| `manon_death` | `sound/null.wav` | dmprecache.scr |
| `explodeplane1-5` | `sound/weapons/explo/Explo_MetalMed1-5.wav` | bomberplane.scr |
| `leadinmp2` | `sound/weapons/explo/Exp_LeadIn_07.wav` | bomberplane.scr (bomb whistle) |
| `artyexp_sand1-4` | `sound/weapons/explo/exp_dirt_01-04.wav` | bomberplane.scr |
| `artyexp_water1-3` | `sound/weapons/explo/exp_water_01-03.wav` | bomberplane.scr |
| `jetpack` | `sound/...` | jetpackjump.scr |
| `bh` | `sound/characters/gasmask1.wav` | punishments.scr |
| `rt` | `sound/mechanics/Mec_SteamLoop_01.wav` | punishments.scr (rocket loop) |
| `rt1` | `sound/weapons/explo/Exp_Interior_04.wav` | punishments.scr (rocket fire) |
| `pd1` | `sound/mechanics/MOH_Piano3.wav` | punishments.scr |
| `pd` | `sound/weapons/explo/Exp_LeadIn_06.wav` | punishments.scr |
| `explode_building_large` | `sound/...` | exploder_killer.scr |

---

## 114. anti_camper.scr — Anti-Camping Detection System

Detects stationary players and applies configurable punishments. Called per-player from the main loop. Reads all settings via `global/settings.scr`. Integrates with `global/ac/types.scr` for punishment delivery and `global/libmef/mapdesc.scr` for position reporting.

**Invocation:** `self exec global/anti_camper.scr` (once per player per spawn cycle)

**Settings keys read (via settings.scr::getcmd):**
| Key | Purpose |
|-----|---------|
| `camper` | Enable flag — must be `"1"` |
| `time` | Seconds stationary before punishment |
| `radius` | Detection radius (game units) |
| `message` | `iprint` message shown to camper |
| `saysound` | `"1"` = play `streamed_dfr_scripted_M3L1_016a` |
| `weaponscheck` | `"1"` = adjust time per weapon via camper settings |
| `type` | Punishment type string (parsed by `strings.scr::split_line`) |
| `duration` | Punishment duration |
| `counter` | `"1"` = show HUD camp counter |
| `say-pos` | `"1"` = broadcast camper map position |
| `turret-camp` | `"1"` = skip players on turrets |

**Labels:**

### `main`
Guards: skips spectators, jailed/locked players, dead players, and non-DM gametypes. Reads radius + time from settings. Loops with `vector_within` every 1 second; once `camper_time` seconds in-radius, fires punishment via `self exec global/ac/types.scr local.duration local.type 1`. Broadcasts position via `libmef/mapdesc.scr::get_player_position` if enabled.
```
main:
	if(self == NULL || self == NIL) { end }
	if(level.run["camper"]!="1") { ... end }
	if(level.gametype == 0) { level.run["camper"] = 0; end }
	if(self.campinfcheck==1 || self.dmteam=="spectator" || self.mef_spectator==1) { end }
	...
	self.campinfcheck=1
	local.camper_time = waitexec global/settings.scr::getcmd "time"
	if(local.weapons_check=="1") { local.camper_time = waitthread check_weapon self }
	local.inradius = vector_within local.origin self.origin local.camper_radius
	local.camped_for=1
	while(local.inradius && isalive self)
	{
		wait 1
		local.inradius = vector_within local.origin self.origin local.camper_radius
		if(local.camped==0)
		{
			if(local.camped_for==local.camper_time)
			{
				if(local.counter=="1") { level.camps[self.dmteam]++; thread hud 1 }
				if(local.camper_message!="") { self iprint local.camper_message }
				if(local.camper_saysound=="1") { self playsound streamed_dfr_scripted_M3L1_016a }
				self exec global/ac/types.scr local.duration local.type 1
				local.camped=1
			}
			local.camped_for++
		}
	}
	self.campinfcheck=0
end
```

### `check_weapon`
Reads `self.weapon` (via `get_weapon.scr`), looks it up in `game.all_commands` (weapon→time table loaded from camper settings), returns override time.

### `load_weapons`
Switch on `game.game` (AA/SH/BT), calls `waitexec game.file["camper"]::weaponsaa/sh/bt`, appends result to `game.all_commands` via `settings.scr::add_cmds`.

### `getradius`
Simplified version of the main loop used to track radius without punishment logic.

### `hud`
Draws HUD elements 4/5/6/30/31/33 showing "Camp Counter" with team icons and per-team counts `level.camps[allies]` / `level.camps[axis]`.
```
huddraw_rect 5 -105 53 100 73     // background panel
huddraw_string 4 ("Camp Counter")
huddraw_string 6 (level.camps[allies])
huddraw_string 30 (level.camps[axis])
huddraw_shader 31 ("textures/hud/allies")
huddraw_shader 33 ("textures/hud/axis")
```

**Key state variables:**
- `self.campinfcheck` — set to 1 while monitoring, prevents double-entry
- `self.in_radius` — set to 1 while inside radius
- `level.camps[allies/axis]` — team camp counters
- `level.run["camper"]` — global enable flag
- `game.loaded_weapons` — lazy-loaded weapon→time table

---

## 115. elevator.scr — Multi-Floor Elevator System

Spawns a fully functional elevator with up/down switches inside the cab plus per-floor call switches outside. Gates (doors) open/close automatically. Optional roof teleporter for players who fall into the shaft.

**Invocation:** `exec global/elevator.scr array elevator [speed] [flip] [rooftele] [shafttele_origin] [shafttele_destination]`

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `array` | array | Floor data: `[floor][1]` = destination origin, `[2]` = call-switch origin, `[3]` = call-switch angle, `[4]` = gate targetname, `[5]` = 1 if starting floor |
| `elevator` | targetname/entity | The moving brush/model entity |
| `speed` | int | Move speed (default 100) |
| `flip` | 0/1/2 | Switch layout: 0=forward wall, 1=side wall, 2=no interior switches |
| `rooftele` | 0/1 | Spawn shaft-fall teleporter |
| `shafttele_origin` | vector | Secondary tele origin |
| `shafttele_destination` | vector | Secondary tele destination |

**Labels:**

### `main`
Validates all parameters with detailed error messages. Spawns `electrical_switch_nopulse.tik` models for up/down switches bound to elevator. Spawns `trigger_use` for each switch calling `switched`. Calls `spawn_callswitch` + `spawn_callswitchtrig` per floor. Starts `elevator_switches` thread to set initial switch states.
```
main local.array local.elevator local.speed local.flip local.rooftele ...:
	thread scriptmaster
	while(level.time < 1) { waitframe }
	// validation ...
	local.elevator.movespeed = local.speed  // default 100
	// spawn interior switches (up/down)
	local.upswitch = spawn script_model
	local.upswitch model "animate/electrical_switch_nopulse.tik"
	local.upswitch bind local.elevator
	local.upswitchtrig = spawn trigger_use
	local.upswitchtrig setthread switched
	// per-floor call switches
	for(local.a=1;local.a<=local.array.size;local.a++)
	{
		local.elevator waitthread spawn_callswitch local.array[local.a][2] local.array[local.a][3] local.a
		local.elevator waitthread spawn_callswitchtrig local.array[local.a][2] local.a
	}
	local.elevator thread elevator_switches local.array
	if(local.rooftele==1) { local.elevator thread elevatorplayers_fellout ... }
	local.elevator moveto local.array[local.elevator.currentfloor][1]
	local.elevator move
end
```

### `switched`
Triggered by any switch. Determines direction (up/down from interior switches, or target floor from call switches). Calls `movegate "up"` on current floor gate, then `waitthread changefloor`, then `movegate "down"` on new floor gate.
```
switched:
	if(self.elevator.moving==1) { end }
	self.elevator.moving=1
	// determine newfloor ...
	self.elevator waitthread changefloor local.newfloor
	self.elevator waitthread elevator_switches self.elevator.array
	self.elevator.moving=0
end
```

### `changefloor`
Plays `elevatorstart` → loops `elevatormove` → calculates travel time as `dist/speed` → `moveto` → `waitmove` → plays `elevatorstop`.
```
changefloor local.newfloor:
	self playsound elevatorstart
	self loopsound elevatormove
	local.dist = vector_length(self.array[self.currentfloor][1] - self.array[local.newfloor][1])
	self time (local.dist / self.movespeed * 1.000)
	self moveto self.array[local.newfloor][1]
	self waitmove
	self stoploopsound
	self playsound elevatorstop
	self.currentfloor = local.newfloor
end
```

### `elevator_switches`
After 0.5s delay, sets call switches: current floor switch = `nopulse` + nottriggerable (already here); other floors = `pulse` + triggerable. Interior up/down switches: disabled at top/bottom floors, both enabled on middle floors. Opens gate at current floor.

### `movegate`
```
movegate local.direction:
	self playsound elevatorgate
	self time 0.75
	if(local.direction=="up") { self moveup 70 }
	else { self movedown 70 }
	self waitmove
end
```

### `scriptmaster`
Registers sound aliases:
| Alias | File |
|-------|------|
| `elevatormove` | `sound/mechanics/M1_LightTurn.wav` (loop) |
| `elevatorstop` | `sound/mechanics/Mec_GeneratorOff_01.wav` |
| `elevatorgate` | `sound/mechanics/Mec_ElevatorGate_03.wav` |
| `elevatorstart` | `sound/null.wav` |
| `elevatorswitch` | `sound/items/hit_notify.wav` |

### `elevatorplayers_fellout`
Spawns `trigger_use` with red corona at shaft bottom; teleports fallen players to `shafttele_destination`. Trigger follows the elevator as it moves.

**Usage example (map script):**
```
local.floors = makeArray
    ( 0 0 -80 )   ( 0 0 -80 )   270  "gate_floor1"  1
    ( 0 0 80 )    ( 0 0 80 )    270  "gate_floor2"   0
    ( 0 0 240 )   ( 0 0 240 )   270  "gate_floor3"   0
endArray
exec global/elevator.scr local.floors "elev1" 120 0 0
```

---

## 116. ammo_tech.scr — Ammo Technician Role

Players flagged with `self.ammo_tech = 1` can resupply a nearby teammate by holding USE while looking at them. Refills ammo one round at a time with a 30-second cooldown on the recipient.

**Invocation:** `exec global/ammo_tech.scr` (once at level start). Set `$player[i].ammo_tech = 1` to enable a player as ammo tech.

**Labels:**

### `main`
Prevents double-execution via `level.ammo_tech_script`. Loops every frame. For each `$player[i]` with `.ammo_tech = 1` and `useheld`: calls `player_logic` to find a visible teammate within 128 units (30° FOV cone via `cansee`), forces active weapon via `weaponcommand dual targetname`, looks up weapon model in `level.ammo_array`, shows HUD via `ammo_hud`, then counts up ammo 1 per 0.1s while `useheld` is held.
```
if($player[local.i].ammo_tech && $player[local.i].useheld)
{
    local.player = waitthread player_logic $player[local.i]  // find teammate
    local.model = $("Weapon" + local.player.entnum).model
    // look up ammo type in level.ammo_array
    local.player ammo local.ammotype 1    // give 1 round
    local.count++
    $player[local.i] stufftext ("set dmammoammount " + local.count)
    $player[local.i] playsound springfield_snd_reload_single
    // ... up to local.ammount rounds total
}
```

### `do_delay`
Sets `self.ammo_delay = 1` on recipient for 30 seconds or until death/team change.

### `player_logic local.ammo_tech`
Finds the first alive teammate within `cansee 30 128` of the ammo tech. Returns `"bugger all"` if none found.

### `weapon_data`
Returns a `makeArray` lookup table: `[model_path, ammo_type, amount, hud_shader, hud_width]`

Complete weapon→ammo table:
| Weapon model | Ammo type | Amount | HUD shader |
|-------------|-----------|--------|------------|
| `colt45.tik`, `p38.tik`, `nagant_revolver.tik`, `silencedpistol.tik`, `webley_revolver.tik`, `it_w_beretta.tik`, `delisle.tik` | `pistol` | 20 | `clip_pistol` |
| `m1_garand.tik`, `springfield.tik`, `mosin_nagant_rifle.tik`, `kar98.tik`, `kar98sniper.tik`, `enfield.tik`, `fg42.tik`, `g43.tik`, `svt_rifle.tik`, `it_w_carcano.tik`, `uk_w_l42a1.tik` | `rifle` | 30 | `clip_rifle` |
| `thompsonsmg.tik`, `mp40.tik`, `ppsh_smg.tik`, `sten.tik`, `it_w_moschetto.tik` | `smg` | 50 | `clip_pistol` |
| `bar.tik`, `mp44.tik`, `it_w_breda.tik`, `uk_w_vickers.tik` | `mg` | 50 | `clip_rifle` |
| `bazooka.tik`, `panzerschreck.tik`, `uk_w_piat.tik` | `heavy` | 6 | `clip_bazooka/panzerschreck/piat` |
| `shotgun.tik` | `shotgun` | 25 | `clip_shotgun` |
| Frag grenades | `grenade` | 4 | `clip_fraggrenade/steilhandgranate` |
| Smoke grenades | `smokegrenade` | 4 | `clip_cangrenade` |
| Landmines/detectors | `landmine` | 4 | `clip_landmineallies/axis` |

### `ammo_hud local.ammount local.shader local.width`
Uses `globalwidgetcommand` to repurpose existing UI elements (`dday1` menu in AA, `bastogne1` in SH) to show a vertical stat-bar linked to the cvar `dmammoammount`, showing progress of ammo given.
```
self stufftext "globalwidgetcommand june6 statbar vertical 0 local.ammount"
self stufftext "globalwidgetcommand june6 linkcvar dmammoammount"
self stufftext "globalwidgetcommand june6 statbar_tileshader local.shader"
self stufftext "showmenu dday1"  // or bastogne1 for SH
```

---

## 117. barrel.scr — Explosive Barrel System

Manages two barrel types: static explosive barrels and launch barrels that physically fly through the air with rotation physics.

**Entity requirements:**
- `$explosive_barrel` — targetname on standard barrels; health 1 by default; `dmg` and `radius` fields optional
- `$explosive_barrel_launch` — launch barrels; paired with `$explosive_barrel_launch_dummy` via `set` field
- `dmg` default: 250; `radius` default: 256

**Labels:**

### `explosive_barrel`
Iterates `$explosive_barrel` and `$explosive_barrel_launch` arrays, spawning threads for each.
```
explosive_barrel:
	for(local.i=1;local.i<=$explosive_barrel.size;local.i++)
		$explosive_barrel[local.i] thread explosive_barrel_spawn local.i
	for(local.i=1;local.i<=$explosive_barrel_launch.size;local.i++)
		$explosive_barrel_launch[local.i] thread explosive_barrel_launch_spawn local.i
end
```

### `explosive_barrel_spawn local.index`
Waits for barrel `death`, spawns `models/fx/barrel_gas_destroyed` at barrel's origin +32Z, applies proximity screen shake (jitter), waits `level.damage_delay` (0.3s), calls `radiusdamage origin dmg radius`, removes FX after 3-7 seconds.

**Jitter selection by distance:**
| Distance | dmg â‰¤ 150 | dmg > 150 |
|----------|-----------|-----------|
| â‰¤ radiusÃ—1.5 | `jitter_small` | `jitter_normal` |
| â‰¤ radiusÃ—2.5 | `jitter_tiny` | `jitter_small` |

### `explosive_barrel_launch_spawn local.index`
Uses a paired dummy entity for flight. On death: spawns `barrel_gas_destroyed` + `models/emitters/firesmoke` bound to dummy, shows dummy, threads `explosive_barrel_launch_dummy_fly` for physics. Then `radiusdamage` after `level.damage_delay`.

### `explosive_barrel_launch_dummy_fly`
Full physics simulation:
1. Randomizes flight vector: x/y Â±48 units, z = `min_height` to `max_height` (defaults 500–650)
2. Sets angles toward flight vector, applies `physics_velocity`
3. Enables `physics_on 1`
4. Spins barrel via `rotatex` proportional to horizontal distance
5. Each frame: computes velocity delta to detect landing (velocity → 0)
6. On landing: corrects angle to nearest upright/upside-down orientation via incremental `rotatex` + `movedown`

### Jitter functions
```
jitter_normal:    waitexec global/earthquake.scr .4 3 0 0; waitexec global/earthquake.scr .5 1 0 0
jitter_small:     waitexec global/earthquake.scr .3 1.5 0 0; waitexec global/earthquake.scr .35 .75 0 0
jitter_tiny:      waitexec global/earthquake.scr 1 .3 0 0
```
(earthquake.scr parameters: duration, magnitude, no_ramp, no_ramp)

---

## 118. weather.scr — Dynamic Weather System

Adds client-side rain/snow with configurable types, thunder+lightning, per-player interior/exterior sound detection, and water-volume puddle sounds.

**Invocation:** `exec global/weather.scr "type" thunder volume density [spawn_funcrain]`
- `type`: weather type string (see below)
- `thunder`: 1 = enable lightning/thunder
- `volume`: rain sound volume (0.0–1.0); NIL = type default
- `density`: rain density override; NIL = type default
- `spawn_funcrain`: 0 = no `func_rain` entities (map has its own)

**Weather types and cvar presets:**
| Type | Speed | Density | Length | Width | Slant | Sounds |
|------|-------|---------|--------|-------|-------|--------|
| `snow` | 50 | 1 | 3 | 2 | 500 | off |
| `snow_fast` | 150 | 1 | 3 | 2 | 900 | off |
| `blizzard` | 350 | 3 | 4 | 3 | 1500 | on 0.1 |
| `hail` | 1000 | 0.25 | 4 | 3 | 75 | on 0.35 |
| `rain` | 2048 | 1 | 50 | 0.5 | 75 | on 0.8 |
| `drizzle` | 2048 | 0.1 | 50 | 0.5 | 50 | on 0.5 |
| `monsoon` | 2048 | 3 | 50 | 0.5 | 250 | on 1.0 |
| `snow_original` | 32 | 0.2 | 2 | 1 | 250 | off |
| `rain_original` | 2048 | 1 | 90 | 0.4 | 50 | on 1.0 |

Snow types use shader `textures/snow10`; rain types use `textures/rain`.

**Labels:**

### `main`
Spawns up to 9 `func_rain` entities at offsets covering a 8000Ã—8000 area. Creates `script_model` with `rendereffects +viewlensflare` + `light 1 1 1 3000` for lightning flash entity (`weather_thunder`). Sets all `cg_weather*` cvars. Starts threads: `weather`, `weather_init`, `playerweather`, and a cvar polling loop reading `cg_rain_*` into `level.rain_*` fields each frame.

### `funcrain local.origin`
Spawns a `classname "func_rain"` entity at the given origin with setsize `(-20000 -20000 -20000)(20000 20000 20000)`.

### `weather local.string ...`
Switch statement setting all `cg_rain_*` cvars to match the weather type. Default case zeros everything and sets `cg_rain "0"`.

### `weather_init`
Registers sound aliases via scriptmaster:
| Alias | File |
|-------|------|
| `thunderclap1/2/3` | `sound/amb/Amb_Thunder_01/02/03.wav` (range 10000) |
| `rainext` | `sound/amb/Amb_RainExt_01.wav` (range 160–320) |
| `rainpuddle` | `sound/amb/Amb_RainPuddle_01.wav` |
| `rainroof` | `sound/amb/Amb_RainRoof_02.wav` |
| `rainwindow` | `sound/amb/Amb_RainWindow_01.wav` |
| `rainplant` | `sound/amb/Amb_RainPlant_01.wav` |
| `windweak/windstrong` | `sound/amb/wind_weak/strong.wav` (if `$weather_volume_wind` exists) |

Also caches map setsizes into `level.map_setsize1/2` and `level.map_height`. Starts `thunder`, `weatherchanger`/`medicchanger`, `treemovement`, `weatherpattern`, `rainvar`, `rain_inout` threads.

### `thunder`
Random delay between `thundertime` and `2.5Ã—thundertime` (default 20s base). Picks random position within map bounds. Runs one of 3 flash patterns (multiple `thread flash` + `thread unflash` sequences with sub-second delays). Plays one of `thunderclap1/2/3`. Recurses via `thread thunder`.

### `flash` / `unflash`
```
flash:
	if(getcvar("cg_thunder")!="1") { end }
	for all players: stufftext "r_fastsky 1"  // show sky
	$world farplane_color (0.9 0.9 0.9)       // brighten sky
	$weather_thunder show                      // activate lens flare

unflash:
	for all players: stufftext "r_fastsky 0"
	$world farplane_color level.farplane_color
	$weather_thunder hide
```

### `playerweather`
Per-player sound entities: spawns two `script_model` entities per player — one at forward trace position (`rainext` loop sound), one at head position (`rainplant`/`rainpuddle` loop sound). Tracks `weather_soundent` and `weather_soundent2` per player. Calls `playerleft` thread to clean up on disconnect.

### `rain_inout`
Most complex function. Per frame, per player:
1. Checks `level.water_volumes` — switches soundent2 to `rainpuddle` if near water
2. Checks `level.interior_volumes` — if inside a defined volume, plays `rainwindow` (muffled) instead of `rainext`; if volume has flag `[6]=1` (open-roof interior), keeps exterior sounds
3. Roof check: traces upward from head in 5 directions; if all traces hit geometry < 600 units below `level.map_height`, plays `rainroof`
4. For single-player: adjusts `cg_rain_density` to 0 when player is inside (hidden rain), restores when outside
5. For multi-player: locks density at `level.rain_density_init`

**Map setup variables:**
- `level.interior_volumes[n][1]` = volume origin; `[2]` = min corner; `[3]` = max corner; `[4]` = reserved; `[5]` = sound multiplier; `[6]` = 1 if open-roof
- `level.water_volumes[n]` = similar format for water surfaces
- `level.map_setsize1/2` = map world bounds (auto-detected if not set)
- `level.thundertime` = seconds between thunder (default 20)
- `level.shuttertime` = flash duration (default 0.80)

---

## 119. check_team_swap.scr — Team Change Ladder Detach

Called on a player when they swap teams mid-game. If the player changes team or joins spectators, calls `usestuff` + `unattachfromladder` to prevent stuck-on-ladder bugs.

**Invocation:** `self exec global/check_team_swap.scr` or `self exec global/check_team_swap.scr "end"` to cancel.
```
main local.hva:
	if(local.hva == "end") { self.tss = 0; end }
	local.team = self.dmteam
	self.tss = 1
	while(isalive self && self.tss == 1)
	{
		waitframe
		if(self.dmteam != local.team || self.dmteam == "spectator")
		{
			self usestuff
			self unattachfromladder
			self.tss = 0
		}
	}
end
```

---

## 120. camper_turret.scr — Turret-Use Flag Setter

Minimal script called when a player mounts/dismounts a turret. Sets `self.using_turret` so `anti_camper.scr` can skip the player (via `turret-camp` setting).

```
main local.using:
	self.using_turret = local.using
end
```

**Usage:** Called by turret interaction code with `local.using = 1` (mounted) or `0` (dismounted).

---

## 121. throwingknife.scr — Throwable Knife System

Screwdriver models repurposed as throwable knives. Players pick up knives from the map and throw them by pressing USE + SecondaryFire. Max 3 per player.

**Key behaviors:**
- **Pickup trigger:** `trigger_use` near knife; calls `pickup` label
- **Throw detection:** `scan_player` watches `useButtonPressed` + `secondaryfire` combo
- **Flight physics:** `flytimer` applies gravity manually (no engine physics); knife spins via rotating angles each frame
- **Orientation on impact:** `rotate` label corrects knife angle to embed in surface
- **Drop on death:** Knives held at death are dropped at player's position; knives that spawned-with-player are not dropped
- **Reset timer:** Knives reset to original map position after 45 seconds if uncollected
- **Damage:** Uses `impaling` damage type; `radiusdamage` or direct damage; no friendly fire
- **Vehicle targets:** Checks if target is in a vehicle; damages vehicle entity
- **Sound differentiation:** Dirt/ground = dirt impact sound; vehicle/metal = metal clank; player = body impact

**Torso state integration:** Requires `mike_torso.scr` compatibility — documents `nilanim` state file format for mods that override character torso animations.

---

## 122. spectator_music.scr — Per-Map Spectator Music

Plays different music tracks for spectators based on current map. Uses `sendplayercommand playmp3` to stream audio to spectating players only.

**Map→track mapping (abbreviated):**
- `dm/mohdm1` → track 1, `mohdm2` → track 2, ... `mohdm7` → track 7
- `obj/obj_team1` → track 8, ... `obj_team4` → track 11
- Campaign missions `m1l1` through `m6l3e` → specific tracks
- Unrecognized map → random selection from 45 music tracks

**Per-player tracking:**
- Every 0.5s: checks `$player[i].dmteam == "spectator"` or `mef_spectator == 1`
- Spectators receive `sendplayercommand playmp3 <trackpath>`
- Active players receive `sendplayercommand stopmp3`
- Tracks state in `self.MCHECK` to avoid repeat sends

---

## 123. water_wade_sounds.scr — Server-Side Water Movement Sounds

Plays server-side water wading/splash sounds for players inside defined water volumes. Compensates for the missing `ubersound.scr` alias when the game's sound system doesn't cover certain maps.

**Invocation:** `exec global/water_wade_sounds.scr [bigsplash]`
- `bigsplash = 1`: plays heavy splash (`snd_bodyfall_wade`) when falling from > 125 units above water, otherwise uses light landing sound

**Requires:** `level.water_volumes` array defined in map script:
```
level.water_volumes = makeArray
    ( -5047 1768 -195 )  ( 0 0 -1000 )  ( 2423 359 70 )
    // [n][1]=center origin  [n][2]=min corner offset  [n][3]=max corner offset
endArray
```

**Labels:**

### `players_water_sounds local.bigsplash`
Per-frame loop. Per player: computes AABB bounds for each water volume entry. If player is inside, starts `water_temp_ent` thread (sound entity spawner) and detects movement type + falling state.

### `water_temp_ent`
Spawns two `fx/dummy.tik` entities per player (`water_temp_ent` and `water_temp_ent2`) that follow the player via `glue`. Separate entities prevent new `playsound` calls from cutting off earlier sounds.

### `glue local.player`
Copies `local.player.origin` to self each frame until entity or player is removed.

### `water_volumes_runwait` / `water_volumes_runwait2`
Alternating timers (0.375s each) that play `snd_step_wade` on alternating sound entities to simulate left/right footstep wading sounds.

### `water_volumes_falling local.bigsplash`
Waits until player lands (getposition != "offground"), then plays splash sound on `water_temp_ent2`. If `bigsplash == 1` and player fell from > 125 units above water top: `snd_bodyfall_wade`, else `snd_landing_wade`.

### `initialize local.bigsplash`
Registers sound aliases via scriptmaster (skips `m3l1a` which has them built-in):
| Alias | File | Parms |
|-------|------|-------|
| `snd_step_wade1-4` | `sound/characters/body_mvmtwater_01-04.wav` | 0.75 vol, 160–1600 range |
| `snd_landing_wade1` | `sound/characters/fs_water_land_01.wav` | 0.9 vol |
| `snd_bodyfall_wade1/2` | `sound/characters/body_fallwater_01/02.wav` | 1.0 vol, 320–2000 range |
| `snd_gasp` | `sound/null.wav` | silence alias to suppress console errors |

---

## 124. weapon_skin_fix.scr — Nationality-Based Weapon Skin Enforcer

Detects players using incorrect national model skins for their team and forces them to spectator until they select a correct skin.

```
main:
	switch(self.dmteam)
	{
	case "axis":
		switch(self.nationalityprefix)
		{
		case "dfr":      // German-origin but wrong variant
		case "dfrru":    // Russian prefix on German team
		case "dfruk":    // British prefix on German team
			self stufftext "dm_playergermanmodel german_Wehrmacht_soldier"
			self spectator
			self iprint "Please select German or Italian skin."
		break
		}
	break
	case "allies":
		switch(self.nationalityprefix)
		{
		case "den":      // German prefix on allies team
		case "denit":    // Italian prefix on allies team
			self stufftext "dm_playermodel american_army"
			self stufftext " cmd spectator"
			self iprint "Please select an American,British or Russian skin."
		break
		}
	break
	}
end
```
Enforces that Axis players use `dfr`-prefixed models and Allies players use `den`-prefixed models. Incorrect combinations trigger a forced spectator state and a model reset command.

---

## 125. mod_inform.scr — Active Mod HUD Display

Shows active mods list in a bottom-right HUD label (element 80) for all players at level start. Called from `ambient.scr` after `level waittill spawn`, or by `anti_camper.scr` when settings load incorrectly.

**Enable:** `game.show_on_mods = 1`

```
main local.msg:
	if(game.show_on_mods == 1)
	{
		wait 1
		huddraw_align 80 "right" "bottom"
		huddraw_alpha 80 1.0
		huddraw_virtualsize 80 1
		huddraw_rect 80 -115 -15 0 0
		huddraw_color 80 1 0 1         // magenta
		huddraw_font 80 verdana-12

		if(local.msg == NIL)
		{
			// scroll through game.scripts array
			for(local.i=1;local.i<=game.scripts.size;local.i++)
			{
				local.msg = (game.scripts[local.i][1] + " " + (game.scripts[local.i][2]=="1" ? "On" : "Off"))
				huddraw_string 80 local.msg
				wait 1
			}
		}
		else
		{
			huddraw_string 80 local.msg
			wait 1
		}
		huddraw_alpha 80 0    // fade out after display
	}
end
```
`game.scripts` is an array of `[modname, "0"/"1"]` pairs populated by the settings/loading system.

---

## 126. uberversion.scr — Version Init and Run Speed

Entry point called once at level start. Sets `sv_runspeed` and optionally locks `g_ubergametype` per map.

```
main:
	thread runspeed 350    // configurable run speed (default sv_runspeed = 250)

	if(getcvar("g_uberhardcode") == "1")
	{
		level.mapname = getcvar "mapname"
		switch(level.mapname)
		{
			case "dm/mohdm1": setcvar "g_ubergametype" "ft"; break
			case "dm/mohdm2": setcvar "g_ubergametype" "cyb"; break
			case "dm/mohdm3": setcvar "g_ubergametype" "cyb"; break
			case "dm/mohdm4": setcvar "g_ubergametype" "cyb"; break
			case "dm/mohdm5": setcvar "g_ubergametype" "bb"; break
			case "dm/mohdm6": setcvar "g_ubergametype" "ft"; break
			case "dm/mohdm7": setcvar "g_ubergametype" "ft"; break
			case "obj/obj_team1-4": setcvar "g_ubergametype" "snd"; break
			default: setcvar "g_ubergametype" "0"; break
		}
	}

	local.uberversion = "7.987"
end local.uberversion

runspeed local.run_speed:
	level waittill spawn
	setcvar "sv_runspeed" local.run_speed
end
```

**`g_ubergametype` values:**
| Value | Mode |
|-------|------|
| `"0"` | Normal (TDM or FFA based on g_gametype) |
| `"cyb"` | Cyber Attack / Search & Destroy |
| `"snd"` | Search & Destroy (objective maps) |
| `"bb"` | Base Builder |
| `"ft"` | Freeze Tag |

**`g_uberhardcode`:** When set to `"1"`, ignores the `g_ubergametype` cvar and hard-codes game mode per map.

---

## 127. aliascache_triggersounds.scr — Centralized Sound Alias Registry

Master sound alias registration file. Called by other scripts passing a `local.parameter` string to load only the relevant aliases. Uses `level.scriptmaster[local.parameter]` flag to prevent double-registration.

**Invocation:** `exec global/aliascache_triggersounds.scr "parameter"`

**Available parameter groups:**
| Parameter | Sound category |
|-----------|---------------|
| `spotlight` | Searchlight on/off/explosion sounds |
| `training_gate` | Training area gate sounds |
| `bangalore` | Bangalore torpedo explosion |
| `giantbomb` | Large bomb ticking/explosion |
| `lightbomb` | Light bomb sounds |
| `snowball_ammo` | Snowball impact sounds |
| `rocket_ammo` | Rocket ammo sounds |
| `grenade_ammo` | Grenade sounds |
| `led_trap` | LED trap sounds |
| `joint` | Joint/joist creak sounds |
| `health` | Health pickup sounds |
| `track_switch` | Rail switch sounds |
| `alarm_switch` | Alarm switch activate/deactivate |
| `light_switch` | Light switch click |
| `valve_switch` | Valve turn sounds |
| `explode_wood_small` | Small wood explosion |
| `explode_building_small` | Small building explosion |
| `explode_building_large` | Large building explosion |
| `explode_mine_large` | Large mine explosion |
| `pipesteam` | Steam pipe ambient |
| `detonator_switch` | Detonator click |
| `weldingtorch` | Welding torch loop |
| `bonfire` | Campfire crackling loop |
| `radiobomb_walkie` | Radio/walkie-talkie static |
| `bombticker` | Bomb countdown ticking |
| `plantedbomb` | Planted bomb sounds |
| `finalbombticker` | Final countdown ticker |
| `radio_music` / `radio_music2` | Radio music streams |
| `airstrike_radiotrig` | Airstrike radio trigger |
| `airstrikes` | Airstrike explosion sounds |
| `tunnelbase_nazi` | Tunnel base ambient |
| `bathroom` | Bathroom ambient/drips |
| `truck_sounds` | Truck engine/movement |
| `track_sounds` | Train track sounds |
| `slidingobject` | Sliding object sounds |
| `movingobject` | Generic moving object |
| `transformers` | Electrical transformer hum |
| `generator_loop` | Generator ambient loop |
| `fireworks` | Fireworks launch/explosion (used by fworks.scr) |
| `jetpack` | Jetpack thruster sounds |
| `guided_missile` | Guided missile sounds |
| `explode_electrical` | Electrical explosion |
| `arty_exp_sand/water` | Artillery dirt/water impact |
| `arty_leadinmp` | Artillery incoming whistle |
| `cabinet_switch` | Cabinet switch sounds |
| `woodcreak` | Wood creak ambient |
| `wood_doors/gates` | Wooden door/gate open/close |
| `metal_doors_solid` | Solid metal door sounds |
| `metal_doorsgates` | Metal gate sounds |
| `shutters` | Shutter sounds |
| `metal_hatch` | Metal hatch open/close |
| `gates_slide` | Sliding gate sounds |
| `machines_humming` | Machine hum ambient |
| `dog` | Dog bark/attack sounds |

---

## 128. legs_movement.scr — Player Legs State Tracker

Sets boolean flags on `self` (the player) corresponding to the current animation state string. Used by other scripts (e.g., `spawnladder.scr`, `anti_camper.scr`) to query movement without reading animation names.

**Invocation:** `self exec global/legs_movement.scr "STATE_STRING"`

**States and flags set:**
| State string | `runforward` | `runbackward` | `runleft` | `runright` | `walkforward` | `walkbackward` | `walkleft` | `walkright` | `using_ladder` | `ladder_moving` | `getofftop` | `getoffbottom` | `using_turret` |
|-------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `RUN_FORWARD` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `RUN_BACKWARD` | 0 | 1 | 0 | 0 | ... | 0 | 0 | 0 | 0 | 0 | 0 |
| `RUN_LEFT` | 0 | 0 | 1 | 0 | ... |
| `RUN_RIGHT` | 0 | 0 | 0 | 1 | ... |
| `WALK_FORWARD` | 0 | 0 | 0 | 0 | 1 | ... |
| `WALK_BACKWARD` | ... | 0 | 1 | ... |
| `WALK_LEFT` | ... | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| `WALK_RIGHT` | ... | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| `ON_LADDER` | all 0 | ... | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| `LADDER_MOVING` | all 0 | ... | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| `GET_OFF_LADDER_TOP` | all 0 | ... | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| `GET_OFF_LADDER_BOTTOM` | all 0 | ... | 0 | 1 | 1 | 1 | 0 | 0 | 0 |
| `USING_TURRET` | all 0 | ... | 0 | 0 | 0 | 0 | 0 | 1 |
| `STAND` (default) | all 0 |

All flags are on `self.legs_state_*` (e.g., `self.legs_state_runforward`, `self.legs_state_using_ladder`).

---

## 129. player_spotlight.scr — Automated Searchlight System

Full-featured searchlight with floor/wall/ceiling mounting, path-following auto-movement, player-tracking behavior, destructibility, and color-change support.

**Invocation:** `exec global/player_spotlight.scr origin color name health anglestart mountwall orient removeafterdeath spotangles_init path`

**Parameters:**
| Param | Description |
|-------|-------------|
| `origin` | Base position |
| `color` | `(r g b)` beam/flare color |
| `name` | Unique targetname for this spotlight |
| `health` | Spotlight HP (0 = indestructible) |
| `anglestart` | Initial rotation angle |
| `mountwall` | 0=floor, 1=left wall, 2=ceiling, 3=right wall |
| `orient` | 1 = alternate orientation for wall mounts |
| `removeafterdeath` | 1=remove light only, 2=remove base+light |
| `spotangles_init` | Initial beam angles override |
| `path` | Script_origin entity for path auto-movement |

**Entities spawned:**
- `miscobj/searchlightbase.tik` — base model
- `miscobj/searchlightoff.tik` — rotating spotlight head (offset 32 units from base)
- `fx/searchlight.tik` Ã— 3 — light flare, beam glow, path target
- `func_beam` — visible light beam (20 segments, alpha 0.2, scale 50)
- `trigger_multiple` — damage trigger (health-tracked)
- `trigger_multiple` — player proximity trigger

**Key behaviors:**

### Auto-aim (main loop, per frame)
Traces forward from spotlight head 10240 units. Updates base rotation to match beam direction. For wall mounts, adjusts base angle based on which quadrant the player is facing.

### Player detection (aimspot thread)
When beam flare is visible, checks all players within `level.autospot_trigdist` (default 550) units of beam hit point. Calls `map_triggers/led_spotlight.scr::spotted` when a player's feet are directly under the beam (within 50 XY units, < 95 units above ground). Player spotlight follows detected player until out of range.

### Path movement (spotpath/spotmoveauto)
Follows linked `script_origin` path nodes at `level.autospot_movespeed` (default 2 units/s) via `moveto`. When a player is detected, transitions to `spotfollow` mode. On losing the player, calls `spotreset` to return to path.

### Color change
Setting `level.spotlight["name"] = 1` triggers one random color change. Setting `level.spotlight_rainbow["name"] = 1` enables continuous random color cycling. Value `3` enables probability-gated random changes.

### Destruction
When `spotdamage.health <= 0`: spawns `fx/fx_spotlighthit.tik` spark effect, plays `exp_searchlight` sound, removes all spotlight entities.

### Player takeover (replace_spotlight)
When a player uses the `spottrigger` (proximity trigger on base), the spotlight is destroyed and a new one is spawned oriented toward the player's current view angles. Effectively lets players "aim" the spotlight.

---

## 130. trainsequence.scr — Full Scripted Train System

Comprehensive rideable train system with physics, boarding, seating, crash sequences, and projectile response. One of the most complex scripts in UBER-MODS.

**Invocation:** `exec global/trainsequence.scr array speed [options...]`

**Key label groups:**

### Initialization
- `scriptmaster` — pre-caches train sound aliases (engine loops, brakes, crashes)
- `train_init` — spawns train model, binds smoke/sparks, sets up damage triggers
- `spawn_damagetrigs` — creates health-tracked damage triggers for projectile impact detection

### Movement
- `trainsequence` — main path-following loop; reads path node array, calls `trainstop` at stop nodes or `traincrash` at crash nodes
- `moving_train_check` — per-frame collision with players in train's path; damages them proportionally to speed
- `changefloor` equivalent — calculates travel time based on distance/speed

### Passenger system
- `playergetin` — boarding sequence with 3-second cancel window
- `passengers` — manages seated players: follows train, locks movement, processes seat-change and exit inputs
- `seatstuff` — creates `attachmodel` seats for passenger car (matrix layout)
- `seatstuff_cab` — 20 seats in 5Ã—4 grid for cabin car
- `shottrig` / `healthboost` — distributes damage to passengers when train takes damage

### Crash sequence
- `traincrash` — rotates train, plays explosion series, spawns smoke emitters
- `train_rotate` — animation-style rotation with multiple `rotatex`/`rotatey` steps and impact sounds
- `jitter_large` — screen shake via `earthquake.scr`

### Projectile/damage detection
- `trigshot_train` — handles `radiusdamage` impacts; determines crash direction via `angle_between_vectors` + `cross_product_vectors`
- `trigproj_train` — filters projectile types (bazookas only, or all, based on settings)

---

## 131. fworks.scr — Fireworks Launcher

Spawns a player-usable fireworks launch pad. Players press USE on an alarm-switch model to launch a V2-rocket model that flies upward, explodes with corona particles and a truck-explosion FX, and then resets.

**Invocation:** `exec global/fworks.scr roketorg launchorg launchang distance particletime exploscale`
- `roketorg` — rocket model origin (where the rocket sits before launch)
- `launchorg` — launcher switch origin
- `launchang` — angles for the alarm switch model
- `distance` — how far up the rocket travels (game units)
- `particletime` — seconds corona particles stay visible after explosion
- `exploscale` — scale of `fx_truck_explosion.tik`

**Labels:**

### `make_launcher local.origin local.angle`
Spawns `trigger_use` + `animate/alarmswitch.tik` model at given origin. Sets thread `Launch`.

### `make_firework local.origin`
Spawns `static/v2.tik` at origin, sets continuous `rotatey 50` spin, stores `save_origin` for reset.

### `Launch`
Full sequence:
```
Launch:
	self nottriggerable
	// corona blink at rocket base
	local.coron3 = spawn script_model model "fx/corona_red.tik" scale "0.5"
	local.coron3 thread blink
	// smoke trail bound to rocket
	self.rocket.fire = spawn script_model model "projectiles/bazookashell_dm.tik"
	self.rocket.fire bind self.rocket
	self.rocket.fire loopsound fwork_sparks
	// liftoff
	self.rocket playsound fwork_launch
	self.rocket loopsound fwork_steam
	self.rocket moveup self.rocket.distance
	self.rocket waitmove
	// explode
	waitthread explode_rocket self.rocket
	// reset
	self.rocket.origin = self.rocket.save_origin
	wait 3
	self.rocket show; self.rocket rotatey 50
	self triggerable
end
```

### `explode_rocket local.rocket`
Spawns 10 corona particles (`fx/corona_red.tik` or `static/corona_orange.tik`) via `make_fworks`, spawns `fx/fx_truck_explosion.tik`, hides rocket. Then releases all coronas with `physics_on` + random velocity vectors via `firefx`. Random colored light burst (4500 radius). Waits `particletime` then removes all.

### `get_velocity local.fwork`
Returns one of 7 directional velocity vectors spreading coronas in a fan pattern:
```
// velocities: forwardÃ—-300, leftÃ—(-240 to +240), upÃ—(300 to 600)
local.velocity = local.fwork.forwardvector * -300 + local.fwork.leftvector * N + local.fwork.upvector * M
```

### `blink`
Alternates `hide`/`show` every 0.5 seconds indefinitely.

**Sound aliases used (via `aliascache_triggersounds.scr`):**
| Alias | Usage |
|-------|-------|
| `fwork_launch` | rocket launch one-shot |
| `fwork_steam` | rocket ascent loop |
| `fwork_sparks` | trail sparks loop |
| `fwork_explo` | explosion boom |

---

## 132. respawn_stuck_fix.scr — Stuck-in-Wall Auto-Respawn

Detects players stuck inside geometry at spawn (falling but unable to move) and teleports them to a random spawn point after 3 seconds.

**Invocation:** `exec global/respawn_stuck_fix.scr` (once at level start, e.g., from dmprecache.scr)

**Detection logic:**
- Monitors all alive non-spectator players
- `local.c` counts `offground` frames (via `self getposition == "offground"`) per 0.1s tick
- `local.alivetime` counts non-offground (on-ground) frames
- If `local.c >= 30` (3 seconds offground) AND player is not flying/driving/turreting/missile: stuck
- Skips players where `self.wallstuck_fixing == 1`

**Respawn logic:**
```
if(self.dmteam == "allies" && $allied_spawn != NULL)
{
    local.r = randomint($allied_spawn.size - 1) + 1
    self tele ($allied_spawn[local.r].origin + ( 0 0 10 ))
    self.viewangles = $allied_spawn[local.r].angles
}
// axis similarly via $axis_spawn
// fallback if no spawn entities: self respawn
```
Uses `tele` (not `respawn`) to avoid the engine's random spawn-jitter on singleplayer maps.

After resolving, waits 3 seconds then clears `self.respawn_stuck_check = 0` so it can re-arm for the next spawn.
```
main:
	while($player.size >= 1)
	{
		for(local.i=1;local.i<=$player.size;local.i++)
		{
			if(... && $player[local.i].respawn_stuck_check != 1)
				$player[local.i] thread respawn_stuck_check
		}
		waitframe
	}
	thread main
end

respawn_stuck_check:
	self.respawn_stuck_check = 1
	// wait for player to be alive
	local.c = 0
	while(isalive self && local.c < 30 && self.origin == local.origin)
	{
		if(self getposition == "offground") { local.c++ }
		else { local.c = 0; local.alivetime++ }
		wait 0.1
	}
	if(local.c >= 30 && self.flying!=1 && self.driving!=1 ...)
	{
		self iprint "Stuck for 3+ seconds. Respawning..."
		self tele ($allied_spawn[local.r].origin + (0 0 10))
	}
	wait 3
	self.respawn_stuck_check = 0
end
```

---

## 133. under_map.scr — Under-Map Detection and Respawn

Detects players standing on the invisible collision floor below certain maps and respawns them. Credit: mefy (Mark Follett).

**Enable:** `game.undermap = 1` (set before script execution)

**Supported maps with Z-band definitions:**
| Map | Bottom Z | Top Z |
|-----|----------|-------|
| `dm/mohdm2` | -128.125 | -95.875 |
| `obj/obj_team1` | -520.125 | -511.875 |
| `obj/obj_team3` | -728.125 | -719.875 |
| `dm/mohdm3` | -224.125 | -215.875 |
| `dm/mohdm4` / `obj/obj_team4` | -16.125 | 0.125 |
| other | exit (no detection) | |

**Detection method (`check_player local.botz local.topz`):**
Two traces along the Z axis through the player's position:
1. Down from feet: detects the floor the player stands on
2. Up from bottom of map: detects the lowest floor (under-map ceiling)
If both traces land within 0.001 units of the known Z-band: player is under the map.
```
local.down = trace (self.origin+(0 0 10)) local.orglow 1 (-5 -5 0)(5 5 0)
local.up   = trace local.orglow local.orghigh
if((abs(local.down[2]-local.topz)<0.001) && (abs(local.up[2]-local.botz)<0.001))
    end 1
```
On detection: `self respawn; self.forcespawn = 1; self iprint "You are not allowed under the map"`

Checks every 3 seconds + 1 second per player.

---

## 134. fastsky.scr — r_fastsky Manager

Forces or clears `r_fastsky` for all connected players, respecting active thunder (which needs fastsky temporarily).

**Invocation:** `exec global/fastsky.scr [1]` — pass `1` for fastsky on, omit for fastsky off.
```
main local.fastsky:
	while($player.size < 1) { wait 1 }
	while($player.size >= 1)
	{
		for(local.i=1;local.i<=$player.size;local.i++)
		{
			if($player[local.i].fastsky != 1 && level.weather_thundering != 1)
			{
				if(local.fastsky != 1) { stufftext "r_fastsky 0"; $player[local.i].fastsky_value = 0 }
				if(local.fastsky == 1) { stufftext "r_fastsky 1"; $player[local.i].fastsky_value = 1 }
				$player[local.i].fastsky = 1
			}
		}
		wait 3
	}
	thread main local.fastsky
end
```
- `$player[i].fastsky` — set to 1 once the cvar has been pushed, prevents re-sending
- `$player[i].fastsky_value` — stores the current value (0 or 1) for weather.scr's `flash`/`unflash` to reference
- Skips players during `level.weather_thundering == 1` to avoid overriding lightning effect

---

## 135. player_taunts.scr — Taunt Gesture System

Detects rapid USE-key presses (5+ presses within ~2 seconds) and triggers a taunt animation on the player. Guards against use while firing, on turret, flying, dead, or in special states.

**Invocation:** `exec global/player_taunts.scr` (once at level start)

**Detection algorithm (per frame, per player):**
```
if(useheld == 1 && useheld_toggle != 1)  // new press detected
{
    useheld_pressed++
    useheld_toggle = 1
    taunt_starting = 1
}
else { useheld_toggle = 0 }

if(taunt_starting == 1)
{
    if(useheld_count <= 20) { useheld_count++ }
    else { // 20 frames = ~0.33s window expired, reset
        useheld_count = 0; useheld_pressed = 0; taunt_starting = 0
    }
    if(useheld_pressed >= 5)  // 5 presses in window = taunt
    {
        self forcetorsostate PLAYER_TAUNT   // or PLAYER_TAUNT_V if passenger
        self.taunting = 1
        // reset all counters
    }
}
```
- `taunting` state lasts 60 frames (~1 second), then auto-clears
- Guards: `fireheld != 1`, alive, not spectator, not dog, not turret, not missile, not flying

---

## 136. spawnladder.scr — Script-Spawned Ladder

Creates a functional ladder trigger at any arbitrary position without requiring a BSP brush. Optional solid clip geometry and visible laser-beam rungs.

**Invocation:**
```
exec global/spawnladder.scr origin angle height [width] [thickness] [spawn_solidclip] [spawn_laser] [laser_color]
```

**Parameters:**
| Param | Default | Description |
|-------|---------|-------------|
| `origin` | required | Base of ladder |
| `angle` | required | Facing direction (players face this angle while climbing) |
| `height` | required | Ladder height (must be â‰¥ 70) |
| `width` | 13.5 | Half-width of trigger volume |
| `thickness` | 1 | Depth of trigger volume |
| `spawn_solidclip` | 0 | 1 = spawn solid clip brush behind ladder |
| `spawn_laser` | 0 | 1=center beam, 2=two side beams, 3=side beams+rungs |
| `laser_color` | (0 0 1) | RGB color for laser beams |

**Labels:**

### `main`
Traces origin backward from wall to find flush position. Spawns `trigger_multiple` sized to the ladder dimensions. Optionally spawns solid clip and laser beams. Calls `trigger_use` thread for continuous USE detection.

### `ladder`
Entry conditions: player not already climbing, not dead, not at top of ladder looking down. Validates facing angle within 70° of ladder angle. Then:
```
local.player face (viewangles[0]  self.angle  viewangles[2])
local.player forcetorsostate GET_ON_LADDER
local.player.origin = (ladder.origin[0] ladder.origin[1] player.origin[2]) + forwardvector * -offset
local.player.climbing_ladder = 1
local.player thread status_check self
```

### `status_check local.ladder`
Holds player's angle locked to ladder angle while `legs_state_using_ladder == 1`. On exit: clears `climbing_ladder`, nudges origin up 10 units, resets to `STAND` torso state.

### `trigger_use`
Polls every frame for players `istouching` the trigger with `useheld == 1`, then manually calls `ladder` thread.

### `solidclip`
Spawns `script_object` with same setsize as the ladder trigger. `solid` + `nodamage`.

### `spawnlaser local.origin local.endpoint local.color local.scale`
Spawns `func_beam` with `numsegments 1`, `life 0` (permanent), `alwaysdraw`, `alpha 0.4`. Used for both side rails and horizontal rungs.

---

## 137. give_players_knives.scr — Spawn Players with Throwing Knives

Wrapper for `throwingknife.scr` that automatically gives knives to players when they respawn.

**Invocation:** `exec global/give_players_knives.scr [count]` (from map's level start script)
- `count` = number of knives to give (1–3, default 1)

**Configuration:**
- `level.knife_resettime` — seconds before dropped knives reset (default 45)
- `level.knife_velocity` — throw velocity (default 1400)

**Logic:**
```
main local.knivesheld:
	if(level.throwingknife_scriptmaster != 1) { exec global/throwingknife.scr::initialize }
	exec global/spectator_jointeam.scr
	while(1)
	{
		for each player:
			if(alive && knivesheld == NIL)  // newly spawned
				self thread spawn_with_knives local.knivesheld
			if(dead && knivesheld < 1)      // just respawned with no knives
				self thread spawn_with_knives local.knivesheld
		waitframe
	}

spawn_with_knives:
	self.knivesheld = local.knivesheld
	// wait until alive
	self thread global/throwingknife.scr::give_knife NIL NIL NIL
end
```

---

## 138. victory_podium.scr — End-of-Map Camera Podium

Spawns an intermission camera at a configured position when the round timer expires (or at a configurable countdown). Optionally fires fireworks at map end.

**Invocation:**
```
exec global/victory_podium.scr podium_origin podium_angle camera_origin camera_angles [timeduration]
```
- `podium_origin` — origin vector for the podium/focal point
- `podium_angle` — facing angle (used for auto-camera placement)
- `camera_origin` — `"auto"` = computed from podium, or explicit vector
- `camera_angles` — `"auto"` = computed, or explicit angles
- `timeduration` — seconds before map end to trigger podium (default 0 = at time-limit exactly)

**Labels:**

### `countdown`
Polls `timelimit` cvar each second. When `seconds <= timeduration + 1`, calls `map_ended`. Handles timelimit changes mid-game by recursing.

### `time_change`
Waits for timelimit to become non-zero (handles maps with no timelimit), then starts `countdown`.

### `map_ended`
One-shot guard via `level.VP_mapended = 1`. Calls `change_maps`.

### `change_maps`
After `timeduration` seconds:
```
removeclass PlayerIntermission   // remove existing intermission cameras
local.camera = spawn info_player_intermission
// auto-placement: camera behind and above podium using sine/cosine
local.sin = math.scr::sine(podium_angle) * 550
local.cos = math.scr::cosine(podium_angle) * 550
local.camera.origin = podium_origin + (cos  sin  25)
local.camera.angles = (-17  podium_angle+180  0)
// or use explicit camera_origin/camera_angles
```

---

## 139. flickerrotate.scr — Flickering Rotating Light Entity

Attaches to a named map entity, spawning a damage trigger around it. When shot, the entity spins faster and brightens. Creates ambient rotation with flickering light.

**Invocation:** `exec global/flickerrotate.scr entityname r g b radius flicker_amount`
- `flicker_amount` — integer 0–20 (divided by 100 for actual range)

**Behavior:**
- Runs continuous rotation cycle with angles oscillating 3°–10°
- Light flickers by adding/subtracting `flicker_amount / 100` to each RGB channel each frame
- On shot: temporary rotation acceleration + light brightness spike
- On entity destruction: removes trigger, ends

---

## 140. steerable_chute.scr — Player-Controllable Parachute

Manages steerable parachute descent for players who have been ejected (e.g., from aircraft). Works with `attachparachute.scr` for full parachute workflow.

**Labels:**

### `main local.ask`
Called when parachute lands. If `local.ask == "LANDED"` and `self.ejecting != 0`, restores gravity and clears ejecting flag:
```
if(local.ask=="LANDED" && self.ejecting!=0)
{
	self gravity 1
	self.ejecting=0
	self forcelegsstate STAND
}
```

### `parachute local.cobra_para local.chute`
Main parachute descent loop for a given player (`cobra_para`) and chute entity (`chute`):
```
local.cobra_para playsound chute
local.velocity_get = -230   // descent speed
local.cobra_para.ejecting = 1

while(local.cobra_para.ejecting==1)
{
	IPRINTLN ""   // clears center-screen text each frame
	if(local.cobra_para.health > 2)
	{
		// lock Z velocity to -230, allow XY steering from player input
		local.vec[0] = local.cobra_para.velocity[0]
		local.vec[1] = local.cobra_para.velocity[1]
		local.vec[2] = local.velocity_get
		local.cobra_para.velocity = local.vec
	}
	if(local.cobra_para.health < 2)  // player died mid-flight
	{
		local.cobra_para.ejecting = 0
		local.chute speed 205
		local.chute movedown 1500
		local.chute waitmove
		local.chute remove
	}
	if(local.cobra_para.dmteam == "spectator")
	{
		local.cobra_para.ejecting = 0
		local.chute remove
	}
	waitframe
}
// landing sequence
local.cobra_para forcelegsstate CROUCH_IDLE
local.chute detach local.cobra_para
local.chute speed 50
local.chute movedown 500
local.chute anim collapse
local.chute waitmove
wait 5
local.chute remove
```

**Key behaviors:**
- XY movement is player-controlled (keyboard steering); only Z is locked to descent speed
- If player health drops below 2 mid-descent: chute detaches and falls away (dead weight)
- On landing: plays `CROUCH_IDLE` legs state, detaches chute, collapses chute animation over 5 seconds

---

## 141. messagetrig_print.scr — Centered Screen Message with Fade

Displays a formatted text string in the center of the screen with fade-in/out. Prevents message overlap by queueing via `level.message_onscreen`.

```
message local.string local.time:
	if(local.string == NIL) { println "^~^~^ non-valid string passed"; goto message_false_end }
	if(local.time == 0 || local.time == NIL) { local.time = 5 }

	// queue if another message is showing
	while(level.message_onscreen == 1) { level.message_waiting = 1; wait .2 }
	level.message_onscreen = 1
	level.message_waiting = 0

	huddraw_alpha 27 0
	local.formatted_string = waitthread global/string_format.scr::str_format local.string 47

	huddraw_string 27 local.formatted_string
	huddraw_align 27 center center
	huddraw_rect 27 -100 20 0 0

	// fade in (0 → 1, step 0.2 per frame)
	for(local.k = 0; local.k <= 1; local.k += .2)
	{
		huddraw_alpha 27 local.k
		waitframe
	}

	// display for local.time seconds, abort if another message queued
	for(local.i = 1; local.i <= local.time; local.i++)
	{
		wait 1
		if(level.message_waiting == 1) { goto message_abort }
	}

	// fade out (1 → 0)
	for(local.n = 1; local.n >= 0; local.n -= .2)
	{
		huddraw_alpha 27 local.n
		waitframe
	}

message_abort:
	level.message_onscreen = 0
end
```

**Notes:**
- Uses `string_format.scr::str_format` to wrap text at 47 characters
- HUD element 27 is used (same as general message display)
- Default display time is 5 seconds
- No position param — always center/center

---

## 142. sounds.scr — Level-Wide Sound Cache File

Registers commonly needed sound aliases via ScriptMaster. Called from `dmprecache.scr` or `ambient.scr`.

```
main:
	local.master = spawn ScriptMaster

	// Anti-camper
	local.master aliascache streamed_dfr_scripted_M3L1_016a sound/dialogue/m3l1/A/dfr_scripted_M3L1_016a.wav
	    soundparms 1.5 0.0 1.0 0.0 200 1500 dialog streamed subtitle "You stay in one spot, you're a dead man!" maps level.mapname
	local.master aliascache camper_bombtick sound/items/Item_Timer_01.wav soundparms 0.7 0.0 1.0 0.0 200 500 local loaded maps level.mapname
	local.master aliascache camper_final_countdown sound/items/final_countdown.wav soundparms 1.5 0.0 1.0 0.0 200 500 local loaded maps level.mapname

	// Punishments / general
	local.master aliascache alarm_switch sound/mechanics/Mec_Switch_05.wav soundparms 1.5 0.0 1.0 0.0 800 3000 auto loaded maps level.mapname
	local.master aliascache snd_landing_stone1 sound/characters/fs_stone_land_01.wav soundparms 0.9 0.2 0.9 0.2 200 2500 auto loaded maps level.mapname

	// Weather
	local.master aliascache thunder1 sound/amb/Amb_Thunder_01.wav soundparms 1.0 0.0 1.0 0.0 3000 6000 auto streamed maps level.mapname
	local.master aliascache rain_ext sound/amb/Amb_RainExt_01.wav soundparms 1.0 0.0 1.0 0.0 3000 6000 local streamed maps level.mapname
end
```

This file is a starting template — production servers extend it with many more aliases for all active mods.

---

## 143. ambient.scr — Level Ambient / Settings Loader (Entry Point)

The **primary entry point** called every map start. Loads settings, configures music zones, and launches all level-wide services.

**Invocation:** `exec global/ambient.scr [music_track] [print_warnings]`

**Labels:**

### `main local.music local.print`
Full initialization sequence:
```
main:
	// First load: initialize settings system
	if(level.loaded_settings != 1)
	{
		level.loaded_settings = 1
		waitexec global/settings.scr
		if(level.run["camper"]=="1")
		{
			exec global/libmef/mapdesc.scr::setup_map level.map_shortname
			level.camps[allies] = 0
			level.camps[axis] = 0
		}
	}

	if(level.gametype == 0) { exec global/savenames.scr }

	level waittill spawn        // wait for first player to join

	exec global/mod_inform.scr  // show active mods HUD
	exec global/ac/cvarscheck.scr  // verify forced cvars

	if(level.ambient_script_run == 1) { end }  // prevent double-execution

	// Music configuration
	if(local.music != NIL && level.music == NIL) { level.music = local.music }
	if(level.music != NIL)
	{
		soundtrack ("music/" + level.music + ".mus")
		forcemusic normal normal
	}

	// Fog/haze initial state
	level.gamma = 1
	level.hazerange = 0
	level.farplanerate = 0.015

	// Interior/exterior trigger entities
	if($interior != NULL) {
		level.interior = exec global/makearray.scr $interior
		for each: level.interior[i] thread interior
	}
	if($exterior != NULL) {
		level.exterior = exec global/makearray.scr $exterior
		for each: level.exterior[i] thread exterior
		thread musiclevel
	}

	exec global/ambience.scr   // start ambient sound engine
	level.ambient_script_run = 1
end
```

### `interior` / `exterior`
Waits for `waittill trigger` on `$interior`/`$exterior` entities (trigger volumes). On trigger: sets `level.current_music` to `"int<set>"` or `"ext<set>"`. Used for auto-music transitions when players enter/leave buildings.

### `musiclevel`
Polls `level.current_music` every 0.1s. Maps codes to `forcemusic` calls:
| Code | Music call |
|------|-----------|
| `ext1` | `forcemusic aux1 aux1` |
| `ext2` | `forcemusic aux3 aux3` |
| `ext3` | `forcemusic aux5 aux5` |
| `int1` | `forcemusic aux2 aux2` |
| `int2` | `forcemusic aux4 aux4` |
| `int3` | `forcemusic aux6 aux6` |

### `lighten` / `darken`
Animates `$world farplane_color` and `r_farplane_color` cvar smoothly when `level.haze` changes:
- `level.haze = 1` → fade from current color upward (lighten)
- `level.haze = -1` → fade down to 0 (darken)
- Rate: `level.farplanerate = 0.015` per 0.1s tick

**`level.ambient_script_run`:** Guards against double execution if `ambient.scr` is called a second time within the same map.

---

## 144. obj_dm.scr — Bomb Plant/Defuse (Objective DM)

Server-side bomb mechanic for custom Objective-DM maps. Manages planting, defusing, ticking countdown, and explosion.

**Key settings:**
```
level.bomb_set_time    = 50    // tenths of a second (5s to plant)
level.bomb_defuse_time = 60    // tenths of a second (6s to defuse)
level.bomb_tick_time   = 45    // seconds before explosion
level.bomb_explosion_radius = 1054
level.bomb_damage      = 200
level.bomb_use_distance = 128
level.bombusefov       = 30    // degrees cone for cansee check
```

**Labels:**

### `bomb_thinker`
Called once per bomb entity. Sets defaults, prints debug info, calls `bomb_waittill_set`.

### `bomb_waittill_set`
Waits for `self.trigger_name waittill trigger`. Validates player team == `level.planting_team`. If player holds USE and maintains `cansee` within 30°/128 units for `bomb_set_time` tenths of a second: calls `iprintlnbold "A Bomb has been planted!"`, spawns threads for defuse and explode.
```
while(isalive local.player && local.player cansee self bombusefov bomb_use_distance && local.player.useheld == 1)
{
	if(local.counter == 0) { local.player stopwatch (bomb_set_time * .1) }
	local.counter++
	wait .1
	if(local.counter >= level.bomb_set_time)
	{
		iprintlnbold "A Bomb has been planted!"
		thread bomb_waittill_defuse
		thread bomb_waittill_explode
		self.live = 1
		level.bomb_set++
		end
	}
}
```

### `bomb_waittill_defuse`
Mirror of plant: validates enemy team, tracks USE hold for `bomb_defuse_time` tenths. On success: `iprintlnbold "A Bomb has been defused!"`, restarts `bomb_waittill_set`, decrements `level.bomb_set`.

### `bomb_waittill_explode`
```
bomb_waittill_explode:
	self model items/explosive.tik
	self playsound plantbomb
	self loopsound bombtick
	local.start_time = level.time
	while(level.time < (local.start_time + level.bomb_tick_time))
	{
		wait .1
		if(self.live != 1) { self stoploopsound; end }    // defused
		if(level.time == (local.start_time + level.bomb_tick_time - 10))
		{
			self stoploopsound
			self loopsound final_countdown
		}
	}
	thread bomb_explode
end
```

### `bomb_explode`
```
bomb_explode:
	self.trigger_name remove
	thread jitter_large 0
	if(self.exploder_set != NIL) { exec global/exploder.scr::explode self.exploder_set }
	if(self.explosion_fx != NIL) { self thread spawn_fx self.explosion_fx }
	if(self.explosion_sound != NIL) { self playsound self.explosion_sound }
	if(self.target != NIL)
	{
		spawn_damaged self.target.destroyed_model  // swap to destroyed model
		self.target remove
	}
	radiusdamage self.origin level.bomb_damage level.bomb_explosion_radius
	if(self.killarea != NIL) { self.killarea volumedamage 1000 }
	self hide
	self.exploded = 1
	wait 0.5
	level.bomb_set--
end
```

### `jitter_large local.time`
```
waitexec global/earthquake.scr .35 10 0 0
waitexec global/earthquake.scr .23 6  0 0
waitexec global/earthquake.scr 1   1  0 0
waitexec global/earthquake.scr 1.25 .3 0 1
```

**Entity setup (in map script):**
```
$bomb_entity.trigger_name = "bomb_trigger_tname"
$bomb_entity.target = "flak88_entity"    // destructible target
$bomb_entity.exploder_set = 3            // exploder set to trigger
$bomb_entity.explosion_fx = "models/fx/fx_truck_explosion.tik"
$bomb_entity.explosion_sound = "exp_large"
$bomb_entity.killarea = $kill_volume
level.planting_team = "allies"
level.defusing_team = "axis"
exec global/obj_dm.scr::bomb_thinker
```

---

## 145. playerboat.scr — Drivable Boat Vehicle

Full drivable boat system (used for Higgins landing craft, U-boats, etc.). Parallel architecture to `playertank.scr` and `playervehicle.scr`.

**Invocation:** `exec global/playerboat.scr name model origin angles health vehiclespeed resettime scale gotout door_open`

**Key labels and features:**

| Label | Purpose |
|-------|---------|
| `playergetin` | Boarding: face forward, attachment-model seating, block input during animation |
| `passengers local.player local.s` | Per-player passenger loop: views, seat-change inputs, exit input |
| `vehicledamage` | Monitors health per 0.5s, plays damage sounds |
| `vehicledeath` | On death: explosions, fire/smoke FX, rotation sinking sequence, kills all riders |
| `deathrotate` | Animates vehicle rolling/sinking |
| `mainreset` | After resettime seconds, respawns vehicle at original position with full health |
| `projectile local.secondary` | Fires cannon shells or grenades; includes flight physics and impact detection |
| `turret_laser local.name` | Spawns aiming laser for U-boat main gun |
| `display` | HUD widgets for vehicle health bar |
| `keep_at_boat` | Keeps water spray FX following boat each frame |
| `keep_at_door` | Repositions Higgins front ramp collision clip |
| `boatstuck_inwall_fix` | Destroys boat if tilt angle exceeds threshold |
| `wallstuck_fix` | Teleports player to surface after exit if stuck in hull geometry |
| `touching_playerboat` | Tracks players `istouching` any boat; used for boarding detection |
| `scriptmaster local.model` | Registers all sound aliases for the specific boat model |

**Vehicle health display:** Uses `globalwidgetcommand` on existing UI widgets to show a health bar (same pattern as ammo_tech.scr).

**Higgins door:** `keep_at_door` tracks a `script_object` clip entity that moves when the ramp opens. `door_open` flag enables/disables the clip.


---

## 146. exploder.scr — Destructible Structure System

**Source:** `NOT_REBORN/global/exploder.scr`
**Author:** Mackey McCandlish (original), extended by UBER-MODS
**Invocation:** `exec global/exploder.scr` before `level waittill prespawn`

### Overview

Full breakable-building system. Five entity types are tagged with a `#set` integer. On explosion: intact geometry hides, rubble appears, chunks fly out, fire emitters spawn. Supports `#pause` (multi-stage), repeatable destruction, reset, and full removal.

### Entity Types (map editor)

| Targetname | Role |
|---|---|
| `exploder` | Intact structure; hidden while map runs |
| `explodersmashed` | Post-explosion rubble at same position |
| `exploderchunk` | Flying debris; `target` field points to a script_origin (launch origin) |
| `exploderfire` | Explosion/fire emitter tik (saved to matrix, removed from map at load) |
| `explodertrigger` | Trigger that calls `::explode self.set` with 6s cooldown |

All five share the same `#set` integer. Optional `#pause N` delays individual entities. Optional `#nosound 1` silences playsound.

### `main` label

Processes all five entity types at level load:

- **explodersmashed**: hides + notsolid each entity; validates `#set`
- **exploderchunk**: saves `.targetorigin` from the chunk's target script_origin, then removes the target (cuts entity count); stores original `.org`/`.ang` for reset
- **exploderfire**: saves all data to `level.exploderfire[f][1..9]` matrix (model, origin, angles, scale, set, pause, damage, damageradius, fire flag), then removes all `$exploderfire` from map
- **exploder**: notsolid + `thread solidify` (re-solids after `level waittill spawn`); sets `.dead=0`, `.exploded=0`
- **explodertrigger**: starts `thread explodetrigger` on each
- If `getcvar(exploders) == "0"`: calls `thread kill_exploders`

### `explode local.name` label

```
explode local.name:
    if (getcvar(exploders) == "0") end
    level.explodertimer[local.name] = level.time + 6

    // 1. Hide intact model:
    for each exploder with matching set -> thread exploderOFF local.i

    // 2. Show rubble:
    for each explodersmashed with matching set -> thread explodersmashedON local.i

    // 3. Spawn fire emitters from matrix:
    for each level.exploderfire[i] where [i][5] == local.name
    {
        local.exploderfire = spawn level.exploderfire[i][1]  // model
        // set origin, angles, scale, pause, damage, damageradius, fire from matrix
        local.exploderfire thread fire
    }

    // 4. Launch chunks:
    for each exploderchunk with matching set -> thread explodechunk local.exploder

    // Wait for local.exploder.dead == 1 (set by last explodechunk), timeout 200 frames if no chunks
end
```

If `level.exploderrepeat == 1`: after chunks land (10s), hides rubble and restores intact model for re-triggering.

### `explodechunk local.exploder` label

Physics launch away from target origin:

```
explodechunk local.exploder:
    self show; self notsolid
    local.vec = (self.origin - self.targetorigin)       // vector pointing AWAY from target
    local.veclength = vector_length(local.vec)
    local.vec = vector_normalize(local.vec) * -local.veclength  // scaled launch velocity
    local.vec[2] *= 1.5                                 // extra Z for arc

    thread phyvel local.vec                             // physics_on + physics_velocity
    self thread rocksound                               // random stonesmall sound after 1-5s

    // Compute tumble: random anglex/y/z from veclength; dominant axis = veclength * 0.5
    self rotatex local.vec[0]; self rotatey local.vec[1]; self rotatez local.vec[2]

    // Decelerate rotation over 10-25 frames
    for(local.i = 0; local.i < local.inc; local.i++)
    {
        local.vec[0] -= local.x; local.vec[1] -= local.y; local.vec[2] -= local.z
        self rotatex/y/z ...; waitframe
    }

    wait 10
    self notsolid; self hide
    local.exploder.dead = 1   // signals ::explode that chunk sequence is done
end
```

### `phyvel local.vec`

```
phyvel local.vec:
    self physics_velocity(local.vec)
    wait 0.2
    if(self == NULL) end
    self physics_on 1
    self physics_velocity(local.vec)   // re-apply after physics_on to ensure velocity sticks
end
```

### `fire` label (exploderfire emitters)

```
fire:
    if (self.pause != NIL) wait self.pause
    if (self.damage != NIL) radiusdamage self.origin self.damage (self.damageradius ?? 512)
    self notsolid
    self anim start
    if (self.fire != NIL)   // persistent fire (fire=1)
    {
        self lightOn
        self loopsound "sound/environment/fire_small.wav" or "fire_big.wav"
        self thread firelight
    }
    else { wait 6; self remove }
end
```

### `firelight` loop

```
firelight:
    if (self == NULL || self.fire == NIL) end
    self lightRed(0.5 + randomfloat(0.8))
    self lightGreen(0.4 + randomfloat(0.6))
    wait 0.2
    goto firelight
end
```

### Helper labels

| Label | Action |
|---|---|
| `exploderOFF local.i` | Wait `#pause`, play explosion sound, hide + notsolid + `connect_paths` |
| `explodersmashedON local.i` | Wait `#pause`, play `stonecrash0N`, show + solid + `disconnect_paths` |
| `exploderchunkONN local.i` | Wait `#pause`, show chunk |
| `solidify` | `level waittill spawn` then `self solid; disconnect_paths` |
| `explodetrigger` | `self waittill trigger` → `thread explode self.set` with 6s cooldown |
| `rocksound` | Wait 1-5s then `playsound stonesmall0N` |
| `removestuff local.set` | Removes `$mapwall`, `$red_tele`, `$cratesstuff` with matching set |
| `remove_ambiences local.set` | Zeros out `level.interior_volumes[a][1..4]` for matching set index |

### `reset local.set`

Waits for `local.exploder.dead == 1`, then restores chunks to original `.org`/`.ang`, hides smashed, shows intact model with `solid`.

### `remove local.set local.removeall`

Call after `::explode #` to clean up. Waits for all exploders dead, removes trigger/chunk/smashed entities (smashed only if `removeall=1`), then calls `kill_exploders 0 NIL 1`.

### `kill_exploders local.removeall local.array`

Removes all exploder entities. Optional `local.array` = set numbers to **skip**. Without `removeall`: makes smashed entities visible+solid (`show; solid; disconnect_paths`). With `removeall=1`: removes smashed too.

### `level.exploderfire` Matrix Columns

```
[1]=model  [2]=origin  [3]=angles  [4]=scale  [5]=set  [6]=pause  [7]=damage  [8]=damageradius  [9]=fire
```

`fire=1`: persistent looping fire + `firelight`. `fire=0` (default): emitter auto-removes after 6s.

### Usage

```
exec global/exploder.scr                            // at map load, before prespawn
thread global/exploder.scr::explode 101            // trigger set 101
thread global/exploder.scr::remove 101             // cleanup after explosion
thread global/exploder.scr::reset 101              // restore to intact (before remove)
thread global/exploder.scr::kill_exploders         // destroy all, end of map
level.exploderrepeat = 1                            // make exploders repeatable
```

---

## 147. jetpack.scr — Player Jetpack Power-up

**Source:** `NOT_REBORN/global/jetpack.scr`

### Overview

Placeable pickup that gives a player a temporary jetpack. Spawns a visible `static_airtank.tik` at a world origin with `trigger_multiple`. On pickup: attaches dual tank models + steam emitters to spine, reduces gravity to 0.07, shows HUD fuel bar, runs 40-second fuel loop.

### `main local.jetpack` label

```
main local.jetpack:
    local.master = spawn scriptMaster
    local.master aliascache jetpack sound/mechanics/Mec_SteamLoop_01.wav
        soundparms 2.0 0.3 1.0 0.0 320 2200 item loaded maps "m dm obj "

    local.airtank = spawn script_model
    local.airtank model "models/static/static_airtank.tik"
    local.airtank.origin = (local.jetpack) + (0 0 30)
    local.airtank.scale = 0.85
    local.airtank notsolid

    local.trig = spawn trigger_multiple
    local.trig.origin = (local.jetpack)
    local.trig setsize (-50 -50 -50) (50 50 50)
    local.trig setthread jetpack
    local.trig wait .5; local.trig delay 0

    level waittill spawn
    local.airtank.targetname = ("jetpack" + local.airtank.entnum)
    exec global/flickerrotate.scr local.airtank.targetname (.9 .9 0) 150 10 10 5
end
```

### `jetpack` label (trigger handler)

```
jetpack:
    local.player = parm.other
    if(local.player.pack == 1) end   // already equipped

    local.player.pack = 1
    local.team = local.player.dmteam
    local.fuel = 80                  // 0.5s per tick -> 40 seconds total

    // Attach dual tanks to Bip01 Spine:
    local.player attachmodel "models/static/static_airtank.tik" "Bip01 Spine" 0.5
        ("Pairtank" + local.player.entnum) 1 -1 -1 -1 -1 (25 -5 3)
    local.player attachmodel "models/static/static_airtank.tik" "Bip01 Spine" 0.5
        ("Pairtank2" + local.player.entnum) 1 -1 -1 -1 -1 (25 -5 -4)

    // Attach steam emitters to spine:
    local.player attachmodel "emitters/pipe_steam.tik" "Bip01 Spine" 0.1
        ("tankemitter" + local.player.entnum) 1 -1 -1 -1 -1 (0 -10 3)
    local.player attachmodel "emitters/pipe_steam.tik" "Bip01 Spine" 0.1
        ("tankemitter2" + local.player.entnum) 1 -1 -1 -1 -1 (0 -10 -4)

    // Cross-reference smoke on tank entity for cleanup:
    $("Pairtank" + entnum).smoke = (local.smoke :: local.smoke2)
    local.player.jetpack = $("Pairtank" + local.player.entnum)

    local.player gravity .07

    // HUD: vertical fuel bar via globalwidgetcommand
    local.player stufftext "globalwidgetcommand june6 rect 16 420 16 64"
    local.player stufftext "globalwidgetcommand june6 linkcvar fuel"
    local.player stufftext "globalwidgetcommand june6 statbar vertical 0 100"
    local.player stufftext "globalwidgetcommand june6 statbar_shader textures/hud/healthmeter"

    local.player stufftext "globalwidgetcommand charliesector rect 40 470 150 20"
    local.player stufftext "globalwidgetcommand charliesector font facfont-20"
    local.player stufftext ("globalwidgetcommand charliesector title Fuel:" + local.fuel)

    local.player stufftext "showmenu dday1"; local.player stufftext "showmenu dday2"
```

### Fuel loop (inside `jetpack` label)

```
while (1)
{
    local.fuel--
    local.player stufftext ("set fuel " + local.fuel)
    local.player stufftext ("globalwidgetcommand charliesector title Fuel:" + local.fuel)

    // Cleanup: team change, out of fuel, or death
    if(local.player.dmteam != local.team || local.fuel == 0 || local.player.health <= 0)
    {
        local.player stoploopsound
        local.player.jetpack.smoke[1] delete; local.player.jetpack.smoke[2] delete
        local.player.jetpack.twin delete; local.player.jetpack delete
        local.player gravity 1; local.player.pack = 0
        local.player stufftext "hidemenu dday1"; stufftext "hidemenu dday2"
        end
    }

    // Thrust on USE key (E):
    if (local.player.useheld == 1)
    {
        local.player.jetpack.smoke[1].scale = 1.0
        local.player.jetpack.smoke[2].scale = 1.0
        local.player.velocity += local.player.forwardvector * 50
        local.player.velocity += self.upvector * 50
        local.player loopsound jetpack
    }
    else { smoke.scale = 0.2; local.player stoploopsound jetpack }

    wait .5
}
```

### HUD Widgets

| Widget | Role |
|---|---|
| `dday1` / `dday2` | Background menu frames (`townhallwindow` shader) |
| `june6` | Vertical stat bar linked to `fuel` cvar (0–100) |
| `charliesector` | Text label "Fuel:N" in gold (fgcolor 0.70 0.60 0.05) |

### Key Facts

- **Fuel:** 80 units at 1/0.5s = 40 seconds total
- **Gravity:** 0.07 (default 1.0)
- **Thrust:** `forwardvector * 50` + `upvector * 50` per USE tick
- **Guard:** `local.player.pack == 1` prevents double pickup
- **Smoke scale:** 1.0 thrusting, 0.2 idle

---

## 148. playervehicle.scr — Generic Drivable Vehicle

**Source:** `NOT_REBORN/global/playervehicle.scr`

### Overview

Shared driver/passenger/turret system for all `DrivableVehicle`-class tik models (Opel truck, SdKfz, Sherman, etc.). Spawns the vehicle, registers it globally, sets up a `trigger_use` for boarding, and runs concurrent damage/death/reset threads.

### `main` Parameters

```
main local.name local.model local.origin local.angles local.health
     local.vehiclespeed local.resettime local.headlights local.noheadlights local.gotout:
```

Validates: model has `models/` prefix, entity is `DrivableVehicle` class, health > 0.

Initialization:
```
local.vehicle = spawn local.model targetname(local.name)
// set origin, angles, health, vehiclespeed, vehiclespeed_max, resettime, headlights

local.vehicle thread vehicle_settings local.gotout  // per-model: seats, gun tag, outheight, etc.
local.vehicle thread vehiclereset
local.vehicle thread vehicledamage
local.vehicle thread vehicledeath
local.vehicle thread vehicletrigger
local.vehicle thread move_stuck_players

level.vehicle_initorigin[local.name] = local.origin
level.vehicle_initangles[local.name] = local.angles
level.vehicle_inithealth[local.name] = local.health
level.drivable_entities[N] = local.name
level.chainreactors[N] = local.vehicle
```

### Boarding Flow

1. `vehicletrigger` spawns `trigger_use` glued to vehicle (`-105 -105 -5` to `105 105 125`)
2. `triggered` routes player: driver empty → `playergetin`; driver present + gun empty → `turretslot`; driver present + turret full + seats available → `passengers`
3. `playergetin`: 1-second window where FIRE key → turretslot, JUMP+crouch → passengers, else → driver. Guards: enemy in vehicle, tilt > 15°, `bbactive==0`

### Key Entity Properties

| Property | Meaning |
|---|---|
| `self.driver` | Current driver (NIL = empty) |
| `self.passengers[N]` | Passenger in seat N |
| `self.turretplayer` | Turret gunner |
| `self.gun` | Turret entity (NIL = no turret) |
| `self.seats` | Max passenger count |
| `self.flooded` | Vehicle underwater |
| `self.dead` | Destroyed flag |
| `self.shooter` | Last attacker |
| `self.vehiclespeed` / `self.vehiclespeed_max` | Current/max speed |

### `healthboost` label

Per-frame monitor. Vehicle health is restored each frame to `local.health` (effectively invincible hull). When damage is detected, it is distributed proportionally to driver and passengers via `damage` command from `self.shooter`. Dog-biting: if dog's mouth trigger is touching the vehicle, deals 15000 damage to all occupants directly. Tanks (sdkfz, shermantank) do not apply driver damage.

### `vehiclereset` label

Runs `fullstop`, plays `idle`/`idlenolights`/`stop_wheels` anims. If headlights: spawns corona via `deadcorona` + headlight ray via `illuminate "left"/"right"`. Removes `Camera`/`PlayerIntermission` entities.

### `illuminate` / `deadcorona` labels

`illuminate "left"/"right"` spawns a script_model headlight beam bound to the vehicle's headlight tag. `deadcorona` places a static corona at the tag for parked-state visuals.

---

## 149. trainsequence_switch.scr — Train Track Switch

**Source:** `NOT_REBORN/global/trainsequence_switch.scr`

### Overview

Manages interactive rail switches that redirect a moving train's spline path. Works alongside `trainsequence.scr`. Players USE a switch entity to toggle the train onto an alternate path. While the train is actively sequencing (`train_sequencing == 1`), all switches are locked.

### Invocation

```
local.array = thread train_splinepath   // must be its own thread in map .scr
exec global/trainsequence.scr local.array train1 60
exec global/trainsequence_switch.scr train1 trainswitch1 trainswitch1_pulsating NIL NIL leftrail01 rightrail01
exec global/trainsequence_switch.scr train1 trainswitch2 trainswitch2_pulsating NIL NIL leftrail02 rightrail02
```

### `main` Parameters

```
main local.train local.switch local.switchpulse
     local.switchorigin local.switchangles
     local.leftrail local.rightrail
     local.trackslide_origin local.axis:
```

- `local.switch` / `local.switchpulse` — targetnames for `animate/trainswitch.tik` / `animate/trainswitch_pulsating.tik`
- If both are NULL: `local.switchorigin` + `local.switchangles` required; script spawns the models
- `local.leftrail` / `local.rightrail` — optional rail entities that rotate when switched
- `local.axis` — `"x"`, `"y"` (default), or `"z"` for switch rotation axis

### Switch Modes

**trainswitch1_triggered** (map-provided switch entities, two-model toggle):

```
if(self.toggle != 1)   // switch ON
{
    self.switch.switched = 1
    self.train waitthread train_splinepath_change
    self.switch hide; self.switchpulse show
    thread rotate (self.axis + "left")
    waitthread moverail "up" self.leftrail self.rightrail
    self.toggle = 1
}
else { reverse: switched=0, switch show, switchpulse hide, rotate right, moverail down }
```

**trainswitch2_triggered** (script-spawned single model):

Toggles between `idle` and `anim move` states. On second toggle: respawns switch at `angles + (0 180 0)`. Plays `trackswitch` alias.

### `train_splinepath_change` label

Re-reads map's `train_splinepath` thread, removes old `info_splinepath` nodes, rebuilds path via `splinepath_init`. Called via `waitthread` so switch blocks until path is rebuilt.

```
train_splinepath_change local.currentnode:
    local.array = waitthread ("maps/" + getcvar("mapname") + ".scr")::train_splinepath
    for(each node in old array) { if exists -> remove }
    waitthread splinepath_init local.array self local.currentnode
end
```

### `splinepath_init` / `splinenode` labels

Iterates path array, spawning linked `info_splinepath` entities. Column 5 in path array: `1`=stop, `2`=crash, `3`=tram. Stop node gets `speed 0`.

### `rotate` / `moverail` labels

```
rotate local.direction:
    self.switch time 2; self.switchpulse time 2
    // rotateyup/down 180 (or x/z variant)
    self.switch move; self.switchpulse move
    self.switch playsound trackswitch
end

movingrail local.direction local.play:
    self time 2
    if(local.direction == "up") self rotateyup 1
    else self rotateydown 1
    if(local.play == 1) self playsound track_switching
    self waitmove
end
```

### Map Thread Pattern

```
train_splinepath:   // in maps/mapname.scr — must end with "end local.array"
    if($trainswitch1 != NULL && $trainswitch1.switched == 1)
    {
        local.array = makeArray
            trainpath  ((8385 2316 272)+(0 0 7))  (0 180 0)  0.40
            t500       ((7385 2316 272)+(0 0 7))  (0 180 0)  0.40
            t501       ((6908 2316 272)+(0 0 7))  (0 180 0)  0.40  1  (-3650 -1225 0)
        endArray
    }
    else { ... default path ... }
end local.array
```

### Sound Aliases

| Alias | File |
|---|---|
| `trackswitch1` | `sound/mechanics/M4_TrackLever.wav` |
| `trackswitch2` | `sound/mechanics/M1_LeverPull.wav` |
| `track_switching` | `sound/mechanics/M4_TrainTrackSlide.wav` |

### Key Constraints

- `train_sequencing == 1` = train in motion, switches locked
- `trainswitches_switching == 1` set during toggle to prevent concurrent switches
- `$switch` and `$switchpulse` must both exist or both be NULL
- `train_splinepath` thread **must** `end local.array` to return the path array

---

## Section 150 — HUD Draw System (huddraw_*)

The `huddraw_*` commands draw custom HUD elements on all players' screens. Up to **256 elements** are available, indexed **0–255**. All commands broadcast to every connected player.

### Commands

| Command | Syntax | Description |
|---|---|---|
| `huddraw_shader` | `huddraw_shader <idx> <shader>` | Display a shader/image graphic |
| `huddraw_string` | `huddraw_string <idx> <string>` | Display text (font size fixed, color/alpha apply) |
| `huddraw_font` | `huddraw_font <idx> <fontname>` | Set font — filenames from `main/fonts/*.ritualfont` |
| `huddraw_rect` | `huddraw_rect <idx> <X> <Y> <W> <H>` | Position + size. X/Y = upper-left corner, relative to alignment |
| `huddraw_align` | `huddraw_align <idx> <horiz> <vert>` | `left`/`center`/`right` and `top`/`center`/`bottom` |
| `huddraw_virtualsize` | `huddraw_virtualsize <idx> <0|1>` | 1 = treat screen as 640×480 virtual; auto-scales to actual res |
| `huddraw_color` | `huddraw_color <idx> <r> <g> <b>` | RGB each 0.0–1.0 |
| `huddraw_alpha` | `huddraw_alpha <idx> <alpha>` | 0.0–1.0. Set to **0** to hide/remove the element |

### Positioning Notes

- `huddraw_rect` X/Y is relative to the **alignment anchor**, not the screen corner
- Aligned to `right bottom`: use negative X to pull element back onto screen
- Width/height for `huddraw_string` only affects centering math, not font size

### Complete Example — Server Welcome Text

```
game_hud:
    huddraw_font    1  "facfont-20"
    huddraw_align   1  "left" "bottom"
    huddraw_rect    1  5 -15 100 100
    huddraw_string  1  (Welcome to [My clan Server])
    huddraw_color   1  0.400 0.400 1.000
    huddraw_alpha   1  1.000
end
```

Called from `main:` with `thread game_hud`.

### Pattern — Temporary Display Then Hide

```
show_message:
    huddraw_string       10  "Round Starting!"
    huddraw_alpha        10  1.0
    huddraw_align        10  "center" "center"
    huddraw_rect         10  0 0 200 50
    huddraw_color        10  1 1 0
    huddraw_virtualsize  10  1
    wait 5
    huddraw_alpha        10  0          // hide element
end
```

### Index Conventions

- Index 0 is valid but many modders start at 1
- Indexes 0–31 overlap with `globalwidgetcommand` native HUD slots — use 32–255 for safest custom elements
- All `huddraw_*` calls sharing the same index modify the same element

---

## Section 151 — Script Language Formal Syntax

### Statement Types

```scr
identifier event_parameter_list :          // label definition
{ statement_list }                         // compound statement
if prim_expr statement
if prim_expr statement else statement
while prim_expr statement
for ( statement ; expr ; statement_list ) statement
try compound_statement catch compound_statement
switch prim_expr compound_statement
break
continue
identifier event_parameter_list            // command call
object identifier event_parameter_list     // object.command call
object = expr                              // assignment
object += expr
object -= expr
object ++
object --
;                                          // no-op
```

### Operator Precedence (lowest first — evaluated last)

```
||
&&
|
^
&
== !=
< > <= >=
+ -
* / %
```

### Arithmetic Operators

| Op | Description | Output type |
|---|---|---|
| `||` | Logical or | 0 or 1 |
| `&&` | Logical and | 0 or 1 |
| `|` | Bitwise or | integer |
| `^` | Bitwise XOR | integer |
| `&` | Bitwise and | integer |
| `== !=` | Equality / inequality | 0 or 1 |
| `< > <= >=` | Comparison | 0 or 1 |
| `+` | Add (numbers or string concat) | — |
| `- * / %` | Subtract, multiply, divide, modulus | — |

### Vector Literal Syntax

```scr
( 1.1 23.2 -15.5 )    // correct
( -1 2 3 )            // correct — space after ( required before negative
(-1 2 3)              // WRONG — parser bug, leads to error
```

Vectors accessed as array indices 0, 1, 2:

```scr
local.v = (10 -2 60.1)
println local.v[2]    // 60.1
$player.origin += (5 6 7)
```

### Targetname Operator `$`

```scr
$my_targetname        // entity with targetname "my_targetname"
local.t = "target2"
$(local.t)            // entity with targetname from variable
$player               // all players (targetname array when multiple)
```

### String Character Access

```scr
"abc"[0]    // "a"
"abc"[2]    // "c"  — indexing starts at 0
```

### NULL vs NIL

| Value | Meaning |
|---|---|
| `NULL` | Valid null entity — entity does not exist / no entity |
| `NIL` | Uninitialized variable — operations on it cause Script Errors |

```scr
if (local.entity != NULL) { ... }    // safe entity check
if (local.var)                        // truthy check — NIL is falsy
```

---

## Section 152 — Variables and Object Scopes

### Scope Keywords

| Keyword | Description | Lifetime |
|---|---|---|
| `game` | Global game object | Persists **across levels** (primitives only) |
| `level` | Current level object | Duration of level |
| `local` | Current thread | Thread lifetime only |
| `parm` | Parameter-passing object | Used to pass data to spawned threads |
| `self` | Object owning the thread group | Group lifetime |
| `group` | Thread group object | Group lifetime |

### Variable Examples

```scr
game.score = 0           // persists across map changes
level.roundcount = 0     // resets each map
local.i = 0              // local to this thread only
parm.damage = 50         // pass to next thread via parm object
self.health              // entity's own health
$mytarget.origin         // position of named entity
self.enemy.health        // health of self's enemy object
```

### `self` Object Rules

- Auto-started level scripts: `self` = NULL
- `thread label` — new thread inherits same `self` as caller (same group)
- `thread filename::label` — new thread inherits same `self`
- `object thread label` — new thread's `self` = `object`
- Event-triggered thread — `self` = object that received the event

---

## Section 153 — Arrays

### Three Array Types

**1. Constant Array** — `::` operator, read-only, index starts at 1:

```scr
local.n = hello::world::this::is::a::test::123
println local.n[1]    // hello
println local.n[7]    // 123
println local.n[8]    // Script Error: const array index out of range
println local.n[hello]    // Script Error: const array index '0' out of range
```

**2. Hash Table Array** — dynamic, any key, uninitialized = NIL:

```scr
local.n[1][3] = 10
local.n["mykey"] = "value"
local.n[hello][world][5] = 23
local.a = local.n[hello]
local.b = local.a[world]
println local.b[5]    // 23
```

**3. Targetname Array** — `$name` when multiple entities share a targetname, index starts at 1:

```scr
$player[1].origin    // first player's position
$player[2].origin    // second player's position
$player.size         // total connected player count
```

### `.size` Property

```scr
local.arr.size    // element count of array
$player.size      // number of players connected
```

### makeArray Block

```scr
local.Path1 = makeArray
t1 300 10 200
t2
t7 NIL 10 200
t14 0 10 200
endArray

// Access: row index (1-based), column index (1-based)
println local.Path1[1][1]    // t1
println local.Path1[1][2]    // 300
println local.Path1[7][2]    // NIL
println local.Path1[14][1]   // t14
println local.Path1[15][1]   // NIL (beyond rows)
```

### Iterating Over Players Safely

```scr
for (local.i = 1; local.i <= $player.size; local.i++)
{
    if ($player[local.i] != NULL)
    {
        $player[local.i] stufftext ("set r_lightmap 0")
    }
}
```

---

## Section 154 — Animation Commands

### moveanim — Animated Props (ScriptModel)

Makes a ScriptModel play a named animation AND physically move through the world:

```scr
while (1)
{
    $truck moveanim drive_and_crash
    $truck waittill animdone
}
```

Requires the animation to exist in the model's `.tik` file.

### anim_attached — Animated Actor on a Bone

For actors attached to another object's bone:

```scr
actorthread:
    self attach $plane "seat01" 1 ( 0 0 0 )
    self exec global/disable_ai.scr
    self anim_attached idle
    self waittill animdone
    self anim_attached standup
    self waittill animdone
    self anim_attached walk
    self waittill animdone
end
```

Start it with: `$dude script actorthread`

### Model Surface Control

```scr
$target surface +nodraw    // hide surface
$target surface -nodraw    // show surface
$target surface +skin1     // switch to skin1 shader offset
$target surface -skin1     // reset skin1
$target surface +skin2     // switch to skin2 shader offset
```

Multiple skins must be defined in the model's `.tik` file.

---

## Section 155 — PlayerSpawn Command

Spawns a model near the player with distance and FOV filtering:

```scr
playerspawn <model> [range] [vector_offset] [inFOV] [speed]
```

| Param | Default | Description |
|---|---|---|
| `model` | required | Path to .tik file |
| `range` | 480 | Max distance from player to trigger spawn |
| `vector_offset` | `(0 0 0)` | Spawn offset relative to player orientation |
| `inFOV` | `0` | `1`=only when in FOV, `-1`=only outside FOV, `0`=always |
| `speed` | `960` | Simulated travel speed. Delay = distance / speed. `0`=instant |

```scr
// Spawn explosion effect near player, travelling at 960 u/s
playerspawn models/fx/grenexp_base.tik 480 (0 0 0) 0 960
```

---

## Section 156 — Camera System

### Spawning a Camera

```scr
spawn Camera targetname MyCamera
```

Or place `func_camera` entity in Radiant with desired spawnflags.

### Switching Views

```scr
cuecamera $cam           // switch to camera (smooth if not already in camera view)
cuecamera $cam 2.0       // switch with 2-second transition
cueplayer                // return to player view
cueplayer 1.0            // return to player view with 1s transition
```

### Camera Script Commands (prefixed with camera's targetname)

```scr
$cam start                          // begin moving/watching
$cam stop                           // stop everything
$cam pause                          // pause on path
$cam continue                       // resume
$cam speed 200                      // movement speed
$cam fov 75                         // set FOV instantly
$cam fov 75 2.0                     // transition FOV over 2s
$cam cut                            // snap immediately, no fade
$cam fadetime 0.5                   // default fade time for all transitions

$cam watch "$player" 0              // watch player instantly
$cam watch "$entity" 2              // watch entity, 2s fade
$cam watchpath                      // look along movement direction
$cam watchnode                      // use path node stored orientation
$cam nowatch                        // stop tracking, static orientation
$cam lookat $entity                 // snap look at entity immediately
$cam turnto (0 90 0)                // snap to angle vector
$cam moveto $entity                 // snap position to entity origin
$cam movetopos (100 200 50)         // snap position to world coords

$cam follow "$player"               // follow player
$cam follow "$player" "$enemy"      // follow player, watch enemy
$cam follow_distance 200
$cam follow_yaw 45
$cam follow_yaw_absolute
$cam follow_yaw_relative

$cam orbit $entity                  // orbit entity
$cam orbit $entity "$watch"         // orbit entity, watch second entity
$cam orbit_height 128
```

### Camera Example Script

```scr
local.pos = $player.origin + (0 0 64)
$watch_camera movetopos local.pos
$watch_camera watch "$player" 0
$watch_camera cut
setcvar cg_3rd_person 1       // make player model visible
cuecamera $watch_camera

wait 6

$watch_camera watch "$plane" 2    // smoothly track plane over 2s
wait 8

setcvar cg_3rd_person 0
cueplayer
```

### func_camera Spawnflags

| Flag | Effect |
|---|---|
| `ORBIT` | Circle target or loop a spline path |
| `START_ON` | Moving immediately on spawn |
| `AUTOMATIC` | Auto-activates when player enters `auto_radius` |
| `NO_TRACE` | Skip line-of-sight trace for auto activation |
| `NO_WATCH` | In automatic mode, don't auto-watch player |
| `LEVEL_EXIT` | Set level exit state while active |

### Cinematic Player Control

```scr
freezeplayer        // freeze player in place
releaseplayer       // unfreeze
$player physics_off // disable physics (briefings, cutscenes)
```

---

## Section 157 — Scripting Objectives

### Objective Components

| Component | Values | Description |
|---|---|---|
| `idx` | integer > 0 | Display order — lower = higher on list |
| `attr` | `1`/`2`/`3` | `1`=hidden, `2`=shown unchecked, `3`=shown checked |
| `text` | string | Display text |
| `loc` | entity.origin | Optional world position for HUD compass |

### Commands

```scr
// Add/update objective
waitthread global/objectives.scr::add_objectives <idx> <attr> <text> [<loc>]

// Set current objective (shown in yellow)
waitthread global/objectives.scr::current_objectives <idx>
```

Initial `attr` must be 1 or 2 — cannot add a pre-completed objective.

### Full Objective Example

```scr
main:
    waitthread global/objectives.scr::add_objectives 1 2 "Destroy the cannon." $cannon.origin
    waitthread global/objectives.scr::add_objectives 2 2 "Escape the area." $exit.origin
    waitthread global/objectives.scr::current_objectives 1
    thread wait_obj1
end

wait_obj1:
    $cannon waittill death
    waitthread global/objectives.scr::add_objectives 1 3    // mark complete
    waitthread global/objectives.scr::current_objectives 2
    thread wait_obj2
end

wait_obj2:
    $exit waittill trigger
    waitthread global/objectives.scr::add_objectives 2 3
    exec global/missioncomplete.scr nextmap bsp2bsp
end
```

---

## Section 158 — Mission Briefing System

Briefing = a special map level where the game displays menu slideshow before a mission.

### Setup

```scr
start:
    level waittill prespawn
    drawhud 0                       // hide HUD
    level waittill spawn
    exec global/briefing_save.scr

    thread briefingskip             // fire-button skip handler
    $player physics_off             // prevent movement
    thread freezeplayerview

    $player playsound mb5_music

    // Slide 1
    $player playsound slide_advance
    showmenu briefing5a 1
    $player playsound mb_501
    wait 10

    // Slide 2
    $player playsound slide_advance
    showmenu briefing5a2 1
    hidemenu briefing5a 1
    wait 8

    // Wait for narration
    $player playsound mb_502 wait
    $player waittill sounddone

    goto endbriefing
end

endbriefing:
    $player stufftext "spmap m5l1a"    // load first mission map
end

briefingskip:
    if ($player.fireheld)
    {
        goto endbriefing
    }
    wait 0.01
    goto briefingskip
end

freezeplayerview:
    $player.viewangles = (0 0 0)
    wait 0.01
    goto freezeplayerview
end
```

### Menu Commands

```scr
showmenu briefing5a 1     // display named menu overlay
hidemenu briefing5a 1     // hide named menu overlay
drawhud 0                 // hide entire game HUD
```

### Sound Modes

```scr
$player playsound alias_name          // play, continue immediately
$player playsound alias_name wait     // play, block until done
$player waittill sounddone            // wait for current sound to end
```

---

## Section 159 — Medals

```scr
// Award medal directly
setcvar g_medal0 "1"      // up to g_medal5

// Award based on difficulty
level.skill = getcvar (skill)
if (level.skill == "0")
{
    setcvar "g_eogmedal2" "1"    // Bronze Star
}
else if (level.skill == "1")
{
    setcvar "g_eogmedal1" "1"    // Silver Star
}
else if (level.skill == "2")
{
    setcvar "g_eogmedal0" "1"    // Distinguished Service Cross
}
```

---

## Section 160 — Player Inventory (Give / Take)

### Give Items or Weapons

```scr
$player item items/bratwurst.tik 1      // give 1 bratwurst food item
$player item weapons/colt45.tik 1       // give a Colt 45 pistol
```

Path is relative to `models/` folder.

### Give Ammo

```scr
$player ammo pistol   30
$player ammo rifle    100
$player ammo smg      64
$player ammo mg       250
$player ammo grenades 4
$player ammo shotgun  12
$player ammo heavy    3
```

### Take Items / Weapons / Ammo

```scr
$player take items/bratwurst.tik    // take all of this item
$player take weapons/colt45.tik     // remove weapon
$player take pistol                 // remove all pistol ammo
$player take grenades               // remove all grenades
$player takeall                     // remove everything (items, weapons, ammo)
```

---

## Section 161 — Gun Turrets

Fixed-position guns usable by AI, players, or pure script control. In Radiant: right-click → **turret**.

### Placement

Origin point = rotation axis. Place origin directly over attachment point to the surface/object.

### Script Commands

```scr
$turret setPlayerUsable 1       // allow player mounting (0 = deny)
$turret setAimTarget $target    // auto-aim at entity
$turret clearAimTarget          // stop aiming at entity
$turret startFiring             // start firing (overridden when user mounts)
$turret stopFiring              // stop script firing

$turret TurnSpeed 180           // turn speed in degrees/sec for both pitch+yaw
$turret pitchCaps -45 45        // max up (negative) / max down (positive)
$turret yawCenter 90            // center yaw angle
$turret maxYawOffset 90         // arc around center (default 180 = full 360)

// Burst fire: minFireTime maxFireTime minDelay maxDelay (all in seconds)
$turret burstFireSettings 0.5 1.5 1.0 2.5
$turret burstFireSettings 0 0 0 0    // disable burst mode

$turret firetype "bullet"       // "bullet" or "fakebullet" (no damage)
$turret firedelay 0.1           // seconds between shots
$turret bulletdamage 50         // >40 = rifle round, <=40 = pistol round
$turret tracerfrequency 5       // 1 tracer per N bullets
```

### AI-Controlled Turret Example

```scr
setup_turret:
    $machinegun setPlayerUsable 0
    $machinegun setAimTarget $patrol_point
    $machinegun burstFireSettings 0.3 0.8 0.5 1.2
    $machinegun firedelay 0.05
    $machinegun bulletdamage 25
    $machinegun tracerfrequency 5
    $machinegun TurnSpeed 90
    $machinegun pitchCaps -30 30
    $machinegun startFiring
end
```

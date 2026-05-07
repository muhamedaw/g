# MOHAA Config Files & CVars Reference

## .cfg Files

Config files are plain-text lists of console commands, executed on startup or map load.

Common config files:
```
main/server.cfg          server startup config
main/autoexec.cfg        auto-executed on game start
main/pure.cfg            pure server settings
```

## setcvar / getcvar in Script

```scr
setcvar "varname" "value"           // set a cvar
local.val = getcvar (varname)       // read a cvar (no quotes around name)
```

## Key Game CVars

### Server Config
| CVar | Values | Description |
|---|---|---|
| `sv_maxclients` | int | Max players |
| `g_gametype` | `0`–`5` | Game mode |
| `g_gametypestring` | string | Displayed game mode name |
| `sv_hostname` | string | Server name |
| `fraglimit` | int | Frag limit for DM |
| `timelimit` | int | Time limit in minutes |
| `roundlimit` | int | Round limit for obj |

### Anti-Cheat
| CVar | Value | Effect |
|---|---|---|
| `cheats` | `"0"` | Disable cheat codes |
| `thereisnomonkey` | `"0"` | Disable monkey cheat |
| `r_lightmap` | `"0"` | Force lightmap off (anti-wallhack) |
| `developer` | `"0"` | Disable developer mode |
| `ui_console` | `"0"` | Hide console |

### Objective Map Text (shown on scoreboard)
```scr
setcvar "g_obj_alliedtext1" "Primary objective line 1"
setcvar "g_obj_alliedtext2" "Line 2"
setcvar "g_obj_alliedtext3" "Line 3"
setcvar "g_obj_axistext1"   "Axis objective line 1"
setcvar "g_obj_axistext2"   "Line 2"
setcvar "g_obj_axistext3"   "Line 3"
setcvar "g_scoreboardpic"   "objdm1"   // scoreboard background image
```

### Weather/Visuals
| CVar | Description |
|---|---|
| `cg_rain` | `"1"` enables rain |
| `r_fastsky` | `"1"` fast sky rendering |
| `night` | Custom — used with nightcheck |

## stufftext — Send Commands to Clients

```scr
// Send to ALL players
$player stufftext ("set r_lightmap 0")
$player stufftext ("developer 0")
$player stufftext ("spmap obj/obj_team2")   // change map
$player stufftext ("say Server: Round Over!")

// Send to specific player
$player[1] stufftext ("set r_lightmap 0")

// ALWAYS guard with NULL check
if ($player != NULL)
{
    $player stufftext ("set r_lightmap 0")
}
```

## server.cfg Template

```cfg
seta sv_hostname        "My MOHAA Server"
seta sv_maxclients      "20"
seta g_gametype         "2"
seta g_gametypestring   "Objective"
seta timelimit          "20"
seta roundlimit         "5"
seta cheats             "0"
seta developer          "0"
seta sv_pure            "1"
exec mapcycle.cfg
```

## Physics & World CVars

| CVar | Default | Description |
|---|---|---|
| `sv_gravity` | `800` | World gravity |
| `sv_friction` | `4` | Ground friction |
| `sv_waterspeed` | `400` | Move speed in water |
| `sv_waterfriction` | `1` | Water friction |
| `sv_stopspeed` | `100` | Deceleration rate |
| `sv_maxvelocity` | (engine) | Velocity cap |
| `sv_fps` | `20` | Server tick rate |

## Audio CVars

| CVar | Default | Description |
|---|---|---|
| `s_volume` | — | Master volume |
| `s_musicvolume` | `0.55` | Music volume |
| `s_reverb` | — | Enable reverb |
| `s_khz` | `22` | Mixing rate (kHz) |

## mapcycle.cfg Template

```cfg
set d1 "map obj/obj_team1 ; set nextmap vstr d2"
set d2 "map obj/obj_team2 ; set nextmap vstr d3"
set d3 "map obj/obj_team4 ; set nextmap vstr d1"
vstr d1
```

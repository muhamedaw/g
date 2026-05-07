# MOHAA Map Script Template

## Script File Load Behavior

| File | When loaded |
|---|---|
| `maps/mapname.scr` | First map load only (NOT from saved games) |
| `maps/mapname_precache.scr` | Every load including saved games — use for asset precaching |
| `anim/*.scr` | AI state machine scripts — triggered by AI system |

## Complete Boilerplate — maps/obj/obj_teamN.scr

```scr
// ─── MAP NAME ─────────────────────────────────────────────────────────────────
// MAP: obj_team1 (The Hunt)
// MOD: My Christmas Mod v1.0
// BY:  YourName

main:

// ── Scoreboard text ───────────────────────────────────────────────────────────
setcvar "g_obj_alliedtext1" "Destroy the cannon"
setcvar "g_obj_alliedtext2" "Welcome To"
setcvar "g_obj_alliedtext3" "My Server"
setcvar "g_obj_axistext1"   "Defend the cannon"
setcvar "g_obj_axistext2"   "Modded By"
setcvar "g_obj_axistext3"   "YourName"
setcvar "g_scoreboardpic"   "objdm1"

// ── Sound aliases (before prespawn) ───────────────────────────────────────────
local.master = spawn ScriptMaster
local.master aliascache my_sound sound/items/example.wav soundparms 1.0 0.0 1.0 0.0 400 3000 item loaded maps "dm obj"

// ── External script precache ──────────────────────────────────────────────────
// exec global/myfeature.scr::prepare

level waittill prespawn

// ── Background threads (spawn BEFORE other inits) ─────────────────────────────
thread cheats
thread nocheats

// ── Mod features ──────────────────────────────────────────────────────────────
exec global/g2message.scr           // scrolling HUD ticker
exec global/g2music.scr             // custom music
exec global/g2teams.scr             // team balance HUD
thread my_hud                       // custom HUD elements
thread nightcheck                   // day/night cycle

// ── Map-specific setup ────────────────────────────────────────────────────────
exec global/DMprecache.scr
level.script = maps/obj/obj_team1.scr
exec global/ambient.scr obj_team1

end


// ─── ANTI-CHEAT THREADS ───────────────────────────────────────────────────────

cheats:
setcvar "cheats" "0"
setcvar "thereisnomonkey" "0"
if ($player != NULL)
{
    $player stufftext ("set r_lightmap 0")
}
wait 1
goto cheats
end

nocheats:
if ($player != NULL)
{
    $player stufftext ("developer 0")
}
wait 1
goto nocheats
end


// ─── CUSTOM HUD ───────────────────────────────────────────────────────────────

my_hud:
    huddraw_virtualsize  50  1
    huddraw_font         50  "facfont-20"
    huddraw_align        50  "left" "bottom"
    huddraw_rect         50  5 -5 300 20
    huddraw_color        50  0.4 0.4 1.0
    huddraw_alpha        50  1.0
    huddraw_string       50  "Welcome to My Server"
end


// ─── NIGHT CHECK ──────────────────────────────────────────────────────────────

nightcheck:
setcvar "night" "0"
while (1)
{
    local.hour = level.time
    if (local.hour >= 22 || local.hour < 6)
    {
        setcvar "night" "1"
    }
    else { setcvar "night" "0" }
    wait 60
}
end
```

## Standard Global Script Pattern — global/myfeature.scr

```scr
// global/myfeature.scr

prepare:
    // Register sound aliases here (called before prespawn)
    local.master = spawn ScriptMaster
    local.master aliascache feature_snd sound/items/example.wav soundparms 1.0 0.0 1.0 0.0 300 2000 item loaded maps "dm obj"
end

main:
    // Main feature logic — called with: exec global/myfeature.scr
    // or: thread global/myfeature.scr::main
    local.i = 1
    while (local.i <= 10)
    {
        // do stuff
        local.i++
        wait 1
    }
end
```

## Trigger-Based Event Pattern

```scr
// Wait for bomb plant → trigger victory
bomb_planted_watcher:
    level waittill ObjectiveDestroyed
    exec global/fworks.scr          // launch fireworks
    $player stufftext ("say Allies Win!")
    wait 5
    $player stufftext ("spmap obj/obj_team2")
end
```

## Animated Light Loop (Christmas)

```scr
lights:
    local.colors = (1 0 0)::(0 1 0)::(0 0 1)::(1 1 0)::(1 0 1)::(0 1 1)::(1 1 1)
    local.lvl = 1
    while (1)
    {
        if (local.lvl > 7) { local.lvl = 1 }
        $xmas_light lightStyle local.lvl
        local.lvl++
        wait 0.5
    }
end
```

## FX Spawner Loop

```scr
spark_loop:
    while (1)
    {
        local.spark = spawn StaticModelEntity model models/fx/generic_spark.tik
        local.spark origin self.origin
        wait 0.2
        local.spark remove
        wait 1
    }
end
```

## Objective Map Full Template (Bomb Plant)

```scr
// maps/obj/obj_custom.scr

main:
setcvar "g_obj_alliedtext1" "Destroy the panel"
setcvar "g_obj_alliedtext2" ""
setcvar "g_obj_alliedtext3" ""
setcvar "g_obj_axistext1"   "Defend the panel"
setcvar "g_obj_axistext2"   ""
setcvar "g_obj_axistext3"   ""
setcvar "g_scoreboardpic"   "none"

level waittill prespawn

exec global/DMprecache.scr
level.script = maps/obj/obj_custom.scr
exec global/ambient.scr obj_custom

thread global/exploder.scr::main

level waittill spawn

level.defusing_team    = "axis"
level.planting_team    = "allies"
level.targets_to_destroy = 1
level.bomb_damage        = 200
level.bomb_explosion_radius = 2048
level.dmrespawning       = 0
level.dmroundlimit       = 5
level.clockside          = axis

$panel_bomb thread global/obj_dm.scr::bomb_thinker
thread allies_win_bomb
$panel_bomb thread axis_win_timer

end

allies_win_bomb:
while (level.targets_destroyed < level.targets_to_destroy)
    waitframe
teamwin allies
end

axis_win_timer:
level waittill axiswin
end
```

## Moving Gate / Door Template

```scr
// global/doors.scr — generic door controller

main:
    level waittill spawn

    // Set up open and close triggers
    $trigger_door_open  setthread door_open
    $trigger_door_close setthread door_close
end

door_open:
    local.ent = parm.other
    $trigger_door_open nottriggerable
    $door waitthread movedoor $door_open_pos 200
    iprintlnbold "Door opened"
    $trigger_door_close triggerable
end

door_close:
    local.ent = parm.other
    $trigger_door_close nottriggerable
    $door loopsound mec_slam
    $door waitthread movedoor $door_close_pos 200
    $door stoploopsound mec_slam
    iprintlnbold "Door closed"
    $trigger_door_open triggerable
end

movedoor local.dest local.spd:
    if (local.spd == NIL)
        local.spd = 200
    self speed local.spd
    self moveto local.dest.origin
    self waitmove
end
```

## Ambient Sound Object (Barking Dog / NPC) Template

```scr
// global/ambient_barks.scr

prepare:
    local.master = spawn ScriptMaster
    local.master aliascache bark_1 sound/characters/dog_bark_1.wav soundparms 1.5 0.0 0.8 0.4 160 4000 voice loaded maps "dm obj"
    local.master aliascache bark_2 sound/characters/dog_bark_2.wav soundparms 1.5 0.0 0.8 0.4 160 4000 voice loaded maps "dm obj"
    local.master aliascache bark_3 sound/characters/dog_bark_3.wav soundparms 1.5 0.0 0.8 0.4 160 4000 voice loaded maps "dm obj"
end

main:
    level waittill spawn
    thread ambient_bark
end

ambient_bark:
while (1)
{
    local.times = randomint 5 + 1
    wait (randomint 30 + 20)
    for (local.i = 1; local.i <= local.times; local.i++)
    {
        $bark_origin playsound ("bark_" + (randomint 3 + 1))
        wait (randomfloat 1 + 0.4)
    }
}
end
```

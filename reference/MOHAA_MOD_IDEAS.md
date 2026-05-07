# MOHAA Mod Ideas & Quick-Start Templates

## Mod Idea Categories

### Advanced / Complex Mods (discovered from tested mods)
- **Jetpack**: Player gets airtank model + velocity applied on USE key; fuel HUD via `globalwidgetcommand`
- **Guided Missile**: Player launches missile, camera binds to it, player steers by view direction
- **Artillery Strike**: Trace from binoculars to target → delay → explosions at location
- **Anti-Camper**: Detect player staying within `vector_within` radius → warn/punish
- **Domination** (multi-flag): 3–5 capture points, `useheld` + `isTouching` + countdown to capture
- **Medic/Revive**: Medic class gets heal tool, proximity revive with stopwatch countdown
- **Drivable Tanks/Vehicles**: `VehicleTank` spawn, player enters via trigger_use, turret aims at enemies
- **Freeze Tag**: Players freeze on death, teammates melt them with proximity; func_beam frozen indicator
- **Steal the Beer / Carry Object**: Model attached to player head via `attachmodel`, score while carrying
- **Jail System**: Players "jailed" in spawn area, must escape; used on objective maps

### Seasonal / Event Mods
- Christmas: trees, snow, festive HUD, holiday music, fireworks on win
- Halloween: dark atmosphere, lightning, spooky sounds, fog
- New Year: countdown timer HUD, fireworks at 00:00
- Summer: beach sounds, bright lighting

### Gameplay Mods
- **Team Balance**: auto-move players to keep teams even
- **VIP Mode**: one VIP player per team, protect/kill them
- **Last Man Standing**: no respawn, last player wins
- **Boss Mode**: one player has 500 HP and special weapons
- **Juggernaut**: kill leader to become the new leader

### Server Enhancement Mods
- **Welcome HUD**: server name + rules displayed on join
- **Kill Announcer**: `say` message when player gets kill streak
- **Anti-Cheat**: force r_lightmap 0, developer 0, cheats 0 every second
- **Auto-Balance**: move overflow players at round start
- **Stats Ticker**: scrolling HUD with player count, map name, time

### Visual Mods
- **Night Mode**: dark sky, reduced visibility, flashlight effect
- **Weather**: rain, thunder, lightning strikes on players
- **Hologram Turrets**: fake turret models that spin and light up
- **Animated Flags**: corona-lit flags on bases

### Fun / Mini-game Mods
- **Ferris Wheel / Ride**: rotating platform players can ride
- **Cannon Ride**: player gets launched by script
- **Jet Pack**: vertical velocity applied to player on key press
- **Treasure Hunt**: hidden objects with HUD clue system

---

## Quick-Start: Kill Streak Announcer

```scr
// global/killstreak.scr
// exec from map script: thread global/killstreak.scr::main

main:
    level.ks = makeArray
    // track per-player streaks using $player[i] targetname as key
    while (1)
    {
        wait 0.5
    }
end

// Called when player gets a kill:
// $killer notify killevent
check_streak:
    level.streak++
    if (level.streak == 3)
    {
        $player stufftext ("say " + self.netname + " is on a KILLING SPREE!")
    }
    else if (level.streak == 5)
    {
        $player stufftext ("say " + self.netname + " IS UNSTOPPABLE!")
    }
    $player notify killed
end
```

## Quick-Start: Welcome Message on Player Join

```scr
// global/welcome.scr
// thread global/welcome.scr::main from map init

main:
    while (1)
    {
        level waittill player_spawned
        local.newplayer = parm.other
        wait 1     // let client fully load
        if (local.newplayer != NULL)
        {
            local.newplayer stufftext ("say Welcome to GF Server, " + local.newplayer.netname + "!")
            // HUD welcome
            huddraw_virtualsize  200  1
            huddraw_font         200  "facfont-20"
            huddraw_align        200  "center" "center"
            huddraw_rect         200  0 -60 400 30
            huddraw_color        200  1.0 1.0 0.0
            huddraw_alpha        200  1.0
            huddraw_string       200  ("Welcome, " + local.newplayer.netname + "!")
            wait 5
            huddraw_alpha        200  0
        }
    }
end
```

## Quick-Start: Countdown Timer HUD

```scr
// global/countdown.scr
// thread global/countdown.scr::start from map init

start:
    local.time = 300   // 5 minutes
    huddraw_virtualsize  100  1
    huddraw_align        100  "center" "top"
    huddraw_rect         100  0 10 200 25
    huddraw_font         100  "facfont-20"
    huddraw_color        100  1.0 1.0 1.0
    huddraw_alpha        100  1.0

    while (local.time > 0)
    {
        local.mins = int(local.time / 60)
        local.secs = local.time % 60
        huddraw_string 100 ("Time: " + local.mins + ":" + local.secs)
        wait 1
        local.time--
    }
    huddraw_string 100 "TIME'S UP!"
    huddraw_color  100 1.0 0.0 0.0
    wait 3
    huddraw_alpha  100 0
end
```

## Quick-Start: Fireworks on Round Win

```scr
// global/win_fireworks.scr
// thread global/win_fireworks.scr::on_win

on_win:
    local.positions = makeArray
    (500 500 -400)
    (600 400 -400)
    (400 600 -400)
    endArray

    for (local.i = 1; local.i <= 3; local.i++)
    {
        local.fw = spawn StaticModelEntity model models/fx/bazookaexp_base.tik
        local.fw.origin = local.positions[local.i][1]
        wait 0.8
        local.fw remove
    }
end
```

## Quick-Start: Ambient Dog Barks (any map)

```scr
// global/dogbarks.scr
// In map script: exec global/dogbarks.scr::prepare (before prespawn)
//                thread global/dogbarks.scr::main

prepare:
    local.master = spawn ScriptMaster
    local.master aliascache bark_1 sound/characters/dog_bark_1.wav soundparms 1.5 0.0 0.8 0.4 160 4000 voice loaded maps "dm obj"
    local.master aliascache bark_2 sound/characters/dog_bark_2.wav soundparms 1.5 0.0 0.8 0.4 160 4000 voice loaded maps "dm obj"
    local.master aliascache bark_3 sound/characters/dog_bark_3.wav soundparms 1.5 0.0 0.8 0.4 160 4000 voice loaded maps "dm obj"
end

main:
    level waittill spawn
    thread bark_loop
end

bark_loop:
while (1)
{
    local.times = randomint 8 + 2
    wait (randomint 40 + 20)
    for (local.i = 1; local.i <= local.times; local.i++)
    {
        $bark_origin playsound ("bark_" + (randomint 3 + 1))
        wait (randomfloat 1.0 + 0.4)
    }
}
end
```

## Quick-Start: Moving Door / Gate

```scr
// global/gates.scr
// In map: thread global/gates.scr::main

main:
    level waittill spawn
    $trigger_gate_open  setthread gate_open
    $trigger_gate_close setthread gate_close
end

gate_open:
    $trigger_gate_open nottriggerable
    $gate loopsound mec_slam
    $gate waitthread movegate $gate_open_pos 200
    $gate stoploopsound mec_slam
    iprintlnbold "Gate Opened"
    $trigger_gate_close triggerable
end

gate_close:
    $trigger_gate_close nottriggerable
    $gate waitthread movegate $gate_close_pos 200
    iprintlnbold "Gate Closed"
    $trigger_gate_open triggerable
end

movegate local.dest local.spd:
    if (local.spd == NIL)
        local.spd = 200
    self speed local.spd
    self moveto local.dest.origin
    self waitmove
end
```

## Quick-Start: Self-Heal While Crouching (from selfhealv2)

```scr
// global/selfheal.scr — thread this from map init
// Requires cvar: setcvar "self_heal" "1"

main:
    level waittill spawn
    while (1)
    {
        level waittill player_spawned
        local.p = parm.other
        local.p thread player_heal_watch
    }
end

player_heal_watch:
    while (isAlive self)
    {
        // Wait until crouching + standing still + not shooting + not using
        while (isAlive self &&
               ((self getposition)[0] != "c" ||
                (self getmovement)[0] != "s" ||
                self.fireheld == 1 ||
                self.useheld == 1))
            waitframe
        // Count 1.75 seconds of valid crouch
        local.t = 0
        while (isAlive self && local.t < 1.75 &&
               (self getposition)[0] == "c" &&
               (self getmovement)[0] == "s" &&
               self.fireheld != 1 && self.useheld != 1)
        {
            self loopsound snd_breath
            waitframe
            local.t += 0.05
        }
        self stoploopsound snd_breath
        if (local.t >= 1.75 && isAlive self)
            self heal 10
    }
end
```

## Quick-Start: King of the Hill (from gametypekoth)

```scr
// global/koth.scr — thread from map init

main:
    level waittill spawn
    level.koth_allies = 0
    level.koth_axis   = 0
    level.koth_win    = 5       // captures to win
    thread koth_hud
    thread koth_loop
end

koth_loop:
    // Randomly pick a hill position each round
    local.positions = makeArray
    (100 200 -500)
    (500 400 -500)
    (-200 300 -500)
    endArray
    local.hill_pos = local.positions[randomint 3 + 1]

    local.hill = spawn trigger_multiple targetname koth_hill
    local.hill.origin = local.hill_pos
    local.hill setsize (-100 -100 -50) (100 100 100)

    // Spawn corona indicator
    local.light = spawn StaticModelEntity model models/static/corona_reg.tik
    local.light.origin = local.hill_pos + (0 0 60)
    local.light setscale 1.0
    local.light.color = (1 1 1)

    local.count = 0
    local.holder_team = NIL
    local.capture_time = 15

    while (local.count < local.capture_time)
    {
        waitframe
        // Count players per team in zone
        local.a = 0
        local.x = 0
        for (local.i = 1; local.i <= $player.size; local.i++)
        {
            if ($player[local.i] != NULL && isAlive $player[local.i] &&
                $player[local.i] isTouching $koth_hill)
            {
                if ($player[local.i].dmteam == "allies") local.a++
                else local.x++
            }
        }
        if (local.a > 0 && local.x == 0)
        {
            local.holder_team = "allies"
            local.light.color = (0 0 1)
            local.count++
        }
        else if (local.x > 0 && local.a == 0)
        {
            local.holder_team = "axis"
            local.light.color = (1 0 0)
            local.count++
        }
        else { local.count = 0 }
    }

    // Captured
    if (local.holder_team == "allies") { level.koth_allies++ }
    else                               { level.koth_axis++ }
    iprintlnbold (local.holder_team + " captured the hill!")

    local.hill remove
    local.light remove

    if (level.koth_allies >= level.koth_win) { teamwin allies }
    else if (level.koth_axis >= level.koth_win) { teamwin axis }
    else { goto koth_loop }
end

koth_hud:
    huddraw_virtualsize 80 1
    huddraw_align 80 "left" "top"
    huddraw_rect 80 5 5 250 20
    huddraw_font 80 "facfont-20"
    huddraw_color 80 1 1 1
    huddraw_alpha 80 1
    while (1)
    {
        huddraw_string 80 ("Allies: " + level.koth_allies + "  Axis: " + level.koth_axis)
        wait 1
    }
end
```

## Quick-Start: Carry Object Mode (from capture_the_toilet)

```scr
// global/carryobject.scr — thread from map init

main:
    level waittill spawn
    thread spawn_object
end

spawn_object:
    // Spawn pickup trigger
    local.trigger = spawn trigger_use targetname obj_pickup
    local.trigger.origin = (200 300 -500)
    local.trigger setsize (-40 -40 -40) (40 40 40)
    local.trigger setthread on_pickup

    // Visual marker beam
    local.beam = spawn func_beam targetname obj_beam
    local.beam.origin = local.trigger.origin + (0 0 10)
    local.beam endpoint (local.beam.origin + (0 0 60))
    local.beam color (1 1 0)
    local.beam scale 2
    local.beam numsegments 1
    local.beam alpha 0.8
    local.beam activate
end

on_pickup:
    local.p = parm.other
    if (local.p == NIL || !isAlive local.p) { end }
    $obj_pickup nottriggerable
    $obj_beam deactivate

    // Attach object model to player's head
    local.p attachmodel "models/static/barrel.tik" "Bip01 Head" 1.0 "obj_visual" 1

    // Score while carrying
    local.score_thread = thread score_while_carrying local.p
    level waittill obj_dropped
    local.p detachall
    local.score_thread remove
    thread spawn_object
end

score_while_carrying local.p:
    while (isAlive local.p)
    {
        wait 1
        if (local.p.dmteam == "allies") level.allies_score++
        else                            level.axis_score++
    }
    level notify obj_dropped
end
```

## Mod Generation Checklist

When generating a new mod from scratch:
1. Which maps does it cover? (obj_team1/2/4)
2. What feature(s) does it add?
3. Are there new sounds? → aliascache in main: before prespawn
4. Are there HUD elements? → thread game_hud, huddraw_* commands
5. Are there background loops? → thread labelname at call site, goto inside loop
6. Does it reference $player? → always NULL guard
7. Are there new models? → cache in _precache.scr
8. Does it need sound precache? → exec myscript.scr::prepare before prespawn
9. Package as zzz-modname-v1.0.pk3

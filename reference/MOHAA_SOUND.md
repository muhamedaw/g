# MOHAA Sound System Reference

## aliascache — Register Sound Alias

```scr
local.master = spawn ScriptMaster
local.master aliascache <alias_name> <sound_file> soundparms <vol> <pitch_min> <pitch_max> <cone_inner> <min_dist> <max_dist> <channel> <load_type> maps "<gamemodes>"
```

### soundparms Fields

| Position | Name | Typical Value | Description |
|---|---|---|---|
| 1 | volume | `1.0` | Base volume 0.0–2.0+ |
| 2 | pitch_random | `0.0` | Random pitch offset |
| 3 | pitch | `1.0` | Base pitch multiplier |
| 4 | cone_offset | `0.0` | Directional cone offset |
| 5 | min_dist | `300` | Full volume radius (units) |
| 6 | max_dist | `3000` | Silence radius (units) |
| 7 | channel | `item` | Playback channel (see below) |
| 8 | load_type | `loaded` | `loaded` or `streamed` |
| 9 | maps | `"dm obj"` | Applicable game modes |

### Valid Channels

| Channel | Use |
|---|---|
| `item` | Pickups, mechanics |
| `auto` | Ambient loops |
| `local` | UI / non-positional |
| `body` | Character sounds |
| `dialog` | Voice lines / subtitles |

**NOT valid:** `class` (causes parse error)

### Load Types

| Type | Use |
|---|---|
| `loaded` | Short sounds — loaded into memory |
| `streamed` | Long music/ambient — streamed from disk |

### Quick Examples

```scr
// Short mechanical click — loaded
local.master aliascache door_click sound/mechanics/click.wav soundparms 1.0 0.0 1.0 0.0 300 2000 item loaded maps "dm obj"

// Looping ambient wind — streamed
local.master aliascache wind_loop sound/amb/wind.wav soundparms 0.8 0.0 1.0 0.0 500 4000 auto streamed maps "dm obj"

// Music — local channel, long range
local.master aliascache xmas_music sound/music/xmas.mp3 soundparms 1.3 0.0 1.0 0.0 10000 10000 local loaded maps "obj"

// Voice line with subtitle
local.master aliascache soldier_shout sound/dialogue/shout.wav soundparms 1.0 0.0 1.0 0.0 400 2000 dialog streamed subtitle "Enemy spotted!" maps "dm obj"
```

## Playing Sounds

```scr
$entity playsound alias_name            // play from entity position
$entity playsound alias_name wait       // play and block
$entity waittill sounddone              // wait for sound to finish
$entity loopsound alias_name            // start looping sound (defined in ubersound or aliascache)
$entity stopallsounds                   // stop all sounds on entity
```

## Sound File Paths

Common paths in MOHAA:
```
sound/amb/Amb_*.wav          ambient
sound/mechanics/Mec_*.wav    doors, machinery
sound/dialogue/*/            voice lines
sound/weapons/*/             weapon sounds
sound/items/                 pickups
sound/music/                 background music
sound/characters/            body/movement sounds
```

## Duplicate Alias Warning

If the same alias name appears in both `ubersound.scr` and a mod script:
```
DUPLICATE ALIASES: myalias and myalias
```
This is harmless — mod alias takes priority if loaded later.

## Loop Sound Control

```scr
$entity loopsound alias_name        // start looping sound on entity
$entity stoploopsound alias_name    // stop specific looping sound
$entity stopallsounds               // stop ALL sounds on entity
```

Pattern — loop while player holds USE:
```scr
$flag loopsound tick_pulley
while (local.player.useheld == 1)
{
    // ... do work each frame ...
    $flag waitmove
}
$flag stoploopsound tick_pulley
```

## Random Sound Playback Pattern

```scr
// Play a random sound from a set
local.num = randomint 5 + 1           // random 1–5
local.alias = "b_" + local.num        // builds "b_1" through "b_5"
$bark_origin playsound local.alias

// Full barking-dog pattern:
dog_bark:
while (1)
{
    local.bark_times = randomint 10 + 1
    wait (randomint 21 + 30)          // 30–50 second silence gap
    for (local.i = 1; local.i <= local.bark_times; local.i++)
    {
        local.num = randomint 5 + 1
        $bark_origin playsound ("b_" + local.num)
        wait (randomfloat 1 + 0.5)    // 0.5–1.5 between barks
    }
}
end
```

## voice Channel

`voice` is also a valid channel (used by character/NPC barks and ambient creature sounds):
```scr
local.master aliascache b_1 sound/characters/dog_bark_1.wav soundparms 1.5 0.0 0.8 0.4 160 4000 voice loaded maps "dm "
```

Full valid channel list: `item` `auto` `local` `body` `dialog` `voice`

## exec ::prepare Pattern

To register aliases before the map spawns:
```scr
exec global/fworks.scr::prepare    // call ::prepare label to load aliases early

// In fworks.scr:
prepare:
    local.master = spawn ScriptMaster
    local.master aliascache fworks_boom sound/...
end
```

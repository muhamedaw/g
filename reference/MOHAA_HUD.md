# MOHAA HUD System Reference

## huddraw_* Commands

All commands broadcast to ALL players. Up to 256 elements (index 0–255).
Safest range for custom mods: **32–255** (0–31 overlap with native HUD).

| Command | Syntax |
|---|---|
| `huddraw_shader` | `huddraw_shader <idx> <shader_path>` |
| `huddraw_string` | `huddraw_string <idx> <text>` |
| `huddraw_font` | `huddraw_font <idx> <fontname>` |
| `huddraw_rect` | `huddraw_rect <idx> <X> <Y> <width> <height>` |
| `huddraw_align` | `huddraw_align <idx> <horiz> <vert>` |
| `huddraw_virtualsize` | `huddraw_virtualsize <idx> <1|0>` |
| `huddraw_color` | `huddraw_color <idx> <R> <G> <B>` |
| `huddraw_alpha` | `huddraw_alpha <idx> <0.0–1.0>` |

**Hide element:** `huddraw_alpha <idx> 0`

## Alignment Values

| horiz | vert |
|---|---|
| `left` | `top` |
| `center` | `center` |
| `right` | `bottom` |

X/Y in `huddraw_rect` is offset FROM the alignment anchor.
- `right bottom` + X=-5, Y=-15 → 5 from right, 15 from bottom.

## virtualsize

`huddraw_virtualsize <idx> 1` → coordinates based on 640×480 virtual screen.
Recommended for text and icons that should scale with resolution.

## Fonts (from main/fonts/*.ritualfont)

Common names:
- `facfont-20` — standard game font
- `verdana-12`, `verdana-14`, `verdana-16`

## Templates

### Bottom-left server text
```scr
setup_hud:
    huddraw_virtualsize  50  1
    huddraw_font         50  "facfont-20"
    huddraw_align        50  "left" "bottom"
    huddraw_rect         50  5 -5 300 20
    huddraw_color        50  0.4 0.4 1.0
    huddraw_alpha        50  1.0
    huddraw_string       50  "Welcome to GF Server"
end
```

### Center-screen announcement (auto-hides after 5s)
```scr
announce_hud:
    huddraw_virtualsize  60  1
    huddraw_font         60  "facfont-20"
    huddraw_align        60  "center" "center"
    huddraw_rect         60  0 -80 400 30
    huddraw_color        60  1.0 1.0 0.0
    huddraw_alpha        60  1.0
    huddraw_string       60  "Round Starting!"
    wait 5
    huddraw_alpha        60  0
end
```

### Team score display
```scr
show_teams:
    // Allied count — top right
    huddraw_virtualsize  70  1
    huddraw_align        70  "right" "top"
    huddraw_rect         70  -10 10 200 20
    huddraw_color        70  0.3 0.5 1.0
    huddraw_alpha        70  1.0
    huddraw_font         70  "facfont-20"

    // Axis count — below allies
    huddraw_virtualsize  71  1
    huddraw_align        71  "right" "top"
    huddraw_rect         71  -10 30 200 20
    huddraw_color        71  1.0 0.3 0.3
    huddraw_alpha        71  1.0
    huddraw_font         71  "facfont-20"
end

update_teams:
    local.allied = 0
    local.axis = 0
    for (local.i = 1; local.i <= $player.size; local.i++)
    {
        if ($player[local.i] != NULL)
        {
            if ($player[local.i].dmteam == "allies") { local.allied++ }
            else { local.axis++ }
        }
    }
    huddraw_string  70  ("Allies: " + local.allied)
    huddraw_string  71  ("Axis:   " + local.axis)
    wait 2
    goto update_teams
end
```

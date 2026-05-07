#!/usr/bin/env python3
"""MOHAA Mod Workshop v3  |  run: python app.py"""

# ── Auto-install deps ─────────────────────────────────────────────────────────
import subprocess, sys

def _install(pkg):
    print(f"Installing {pkg}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg], stdout=subprocess.DEVNULL)

try:
    from flask import Flask, request, jsonify, send_file
except ImportError:
    _install("flask")
    from flask import Flask, request, jsonify, send_file

try:
    import anthropic as _ant
except ImportError:
    _install("anthropic")
    import anthropic as _ant

try:
    import requests as _req
except ImportError:
    _install("requests")
    import requests as _req

import re, json, os, io, zipfile, webbrowser, threading

app = Flask(__name__)
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
REF_DIR     = r"C:\Users\Muhammed\Desktop\mods\reference"

# ═══════════════════════════════════════════════════════════════════════════════
#  PROVIDERS
# ═══════════════════════════════════════════════════════════════════════════════

PROVIDERS = {
    "groq": {
        "name":      "Groq (Free – Llama)",
        "base_url":  "https://api.groq.com/openai/v1",
        "models":    ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile",
                      "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        "free":      True,
        "key_hint":  "gsk_...",
        "key_link":  "https://console.groq.com/keys",
        "key_label": "Groq API key — free at console.groq.com:",
    },
    "grok": {
        "name":      "Grok (xAI)",
        "base_url":  "https://api.x.ai/v1",
        "models":    ["grok-3-mini", "grok-beta", "grok-2-1212"],
        "free":      False,
        "key_hint":  "xai-...",
        "key_link":  "https://console.x.ai",
        "key_label": "xAI API key:",
    },
    "anthropic": {
        "name":      "Claude (Anthropic)",
        "base_url":  None,
        "models":    ["claude-sonnet-4-6", "claude-haiku-4-5-20251001", "claude-opus-4-7"],
        "free":      False,
        "key_hint":  "sk-ant-...",
        "key_link":  "https://console.anthropic.com",
        "key_label": "Anthropic API key:",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIG MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def _load_cfg():
    try:
        with open(CONFIG_PATH) as f: return json.load(f)
    except Exception: return {}

def _save_cfg(cfg):
    with open(CONFIG_PATH, "w") as f: json.dump(cfg, f, indent=2)

def get_provider(): return _load_cfg().get("provider", "groq")
def get_model():
    cfg = _load_cfg()
    prov = cfg.get("provider", "groq")
    return cfg.get("model", PROVIDERS[prov]["models"][0])

def get_key(provider=None):
    if provider is None: provider = get_provider()
    env_map = {"anthropic": "ANTHROPIC_API_KEY", "groq": "GROQ_API_KEY", "grok": "XAI_API_KEY"}
    if env_map.get(provider) and os.environ.get(env_map[provider]):
        return os.environ[env_map[provider]]
    cfg = _load_cfg()
    if provider == "anthropic":
        k = cfg.get("api_key", "")  # legacy field
        if k: return k
    return cfg.get("keys", {}).get(provider, "")

def set_key(provider, key):
    cfg = _load_cfg()
    cfg.setdefault("keys", {})[provider] = key
    if provider == "anthropic": cfg["api_key"] = key  # keep legacy field
    _save_cfg(cfg)

def set_provider_cfg(provider, model=None):
    cfg = _load_cfg()
    cfg["provider"] = provider
    if model: cfg["model"] = model
    _save_cfg(cfg)

# ═══════════════════════════════════════════════════════════════════════════════
#  REFERENCE DOCS → ENHANCED SYSTEM PROMPT
# ═══════════════════════════════════════════════════════════════════════════════

def _load_refs():
    # Priority order — most useful for code generation
    files = ["MOHAA_SCR.md", "MOHAA_MAP_TEMPLATE.md", "MOHAA_MOD_IDEAS.md",
             "MOHAA_HUD.md", "MOHAA_SOUND.md", "MOHAA_PKG.md",
             "MOHAA_CFG.md", "MOHAA_TIK.md", "MOHAA_ENTITIES.md"]
    MAX_CHARS = 30_000  # stay well under Groq's HTTP body limit
    parts, total = [], 0
    for fn in files:
        try:
            text = open(os.path.join(REF_DIR, fn), encoding="utf-8").read()
            remaining = MAX_CHARS - total
            if remaining <= 0:
                break
            if len(text) > remaining:
                text = text[:remaining] + "\n... [truncated]"
            parts.append(f"### {fn}\n{text}")
            total += len(text)
        except Exception:
            pass
    return "\n\n---\n\n".join(parts)

MOHAA_REFS = _load_refs()

# ═══════════════════════════════════════════════════════════════════════════════
#  SYSTEM PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

MOHAA_SYSTEM = """You are an expert MOHAA (Medal of Honor: Allied Assault) server-side modder.
All code you generate must use ONLY paths, entity classes, sound aliases, and patterns verified
from the real game pak files (Pak0–Pak7). Never invent paths or aliases.

## CRITICAL RULES — NEVER BREAK:
1. `thread label` at call sites; `goto label` INSIDE loops — NEVER `thread` inside a loop
2. Always `if ($player != NULL) { ... }` before ANY `$player stufftext` call
3. aliascache valid channels: item, auto, local, body, dialog, voice — NOT class
4. Duplicate label names crash the ENTIRE .scr file — nothing runs
5. `exec script::prepare` MUST come BEFORE `level waittill prespawn`
6. Vector negatives need space: `( -1 0 0 )` not `(-1 0 0)`
7. After `spawn VehicleTank` always `waitframe` before accessing properties

## FILE STRUCTURE (verified):
- pk3 = renamed ZIP → MOHAA/main/ folder, `zzz-` prefix = highest priority
- Map scripts: `maps/obj/obj_teamN.scr`  |  Global scripts: `global/featurename.scr`
- Game dirs: main=AA, mainta=SH, maintt=BT

## EXECUTION MODEL:
- `thread label`           → background thread, caller continues immediately
- `goto label`             → jump in SAME thread (use inside loops, not at call sites)
- `exec file.scr::label`   → blocking call
- `thread file.scr::label` → background thread in another file
- `level waittill prespawn` → before entity spawn (register sound aliases here)
- `level waittill spawn`    → after entity spawn (set level vars here)
- `level waittill roundstart` → after spawn vars, BEFORE starting bomb threads (REQUIRED in obj maps)

## VARIABLE SCOPES:
- `local.x` — current thread only | `level.x` — entire map | `game.x` — across maps
- `self.x`  — entity data        | `parm.x`  — passed to thread

## VERIFIED OBJECTIVE MAP BOILERPLATE (from real Pak5 scripts):
```
main:
setcvar "g_obj_alliedtext1" "Allied objective"
setcvar "g_obj_axistext1"   "Axis objective"
setcvar "g_scoreboardpic"   "objdm1"

level waittill prespawn
    exec global/DMprecache.scr
    level.script = maps/obj/obj_team1.scr
    exec global/ambient.scr obj_team1

level waittill spawn
    level.defusing_team = "axis"
    level.planting_team = "allies"
    level.targets_to_destroy = 1
    level.bomb_damage = 200
    level.bomb_explosion_radius = 2048
    level.dmrespawning = 0
    level.dmroundlimit = 5
    level.clockside = axis

level waittill roundstart      // ← ALWAYS REQUIRED before bomb threads

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

cheats:
setcvar "cheats" "0"
if ($player != NULL) { $player stufftext ("set r_lightmap 0") }
wait 1
goto cheats
end

nocheats:
if ($player != NULL) { $player stufftext ("developer 0") }
wait 1
goto nocheats
end
```

## VERIFIED BOMB SYSTEM (from real global/obj_dm.scr):
- bomb_thinker sets: defuse=6s, plant=5s, tick=45s, fov=30, dist=128
- Override in map script (after spawn, before roundstart): `level.bomb_tick_time = 30`
- Real bomb models: `items/pulse_explosive.tik` (unplanted), `items/explosive.tik` (planted)
- Real bomb sounds (built-in, no aliascache): `plantbomb`, `bombtick`, `final_countdown`
- Team sounds: `dfr_objective_o` / `den_objective_o` (planted), `dfr_diffused_d` / `den_diffused_d` (defused)
- `level.targets_destroyed` increments on each bomb explosion
- `level.bombs_planted` tracks armed bombs
- `$(self.trigger_name)` dereferences a string as entity reference

## VERIFIED WEAPON PATHS (from DMprecache.scr):
models/weapons/colt45.tik, p38.tik, silencedpistol.tik, m1_garand.tik, kar98.tik,
kar98sniper.tik, springfield.tik, thompsonsmg.tik, mp40.tik, mp44.tik, bar.tik,
bazooka.tik, panzerschreck.tik, shotgun.tik, m2frag_grenade.tik, steilhandgranate.tik

## VERIFIED PLAYER MODEL PATHS (from DMprecache.scr):
Allied: allied_airborne, allied_manon, allied_oss, allied_pilot, american_army, american_ranger
Axis: german_afrika_officer, german_afrika_private, german_elite_gestapo, german_elite_sentry,
      german_kradshutzen, german_panzer_grenadier, german_panzer_obershutze, german_panzer_shutze,
      german_panzer_tankcommander, german_scientist, german_waffenss_officer, german_waffenss_shutze,
      german_Wehrmacht_officer, german_Wehrmacht_soldier, german_winter1, german_winter2, german_worker
All under models/player/<name>.tik (and <name>_fps.tik for first-person)

## VERIFIED GLOBAL SCRIPTS (from Pak0 global/):
- exec global/DMprecache.scr         — cache all MP weapons/players
- exec global/ambient.scr MAPNAME    — ambient music/sound zones
- thread global/exploder.scr::main   — destructible objects system
- thread global/minefield.scr::minefield_setup — mines in BSP
- exec global/door_locked.scr::lock  — lock all BSP door_locked entities
- exec global/bomber.scr             — flyby bomber precache
- thread global/bomber.scr::bomb N   — trigger bomber pass (N=waypoint 1-7)
- waitexec global/earthquake.scr DUR MAG X END — screen shake

## VERIFIED WEATHER SYSTEM (from global/weather.scr):
- Requires BSP entities: weatherF, weatherR, weatherI, weatherW, wind (by targetname)
- `exec global/weather.scr` (before prespawn)
- `level.weatherpattern = N` (0=none, 1=light, 2=moderate, 3=heavy)
- Built-in sounds: rain_ext, rain_puddle, rain_int, rain_roof, rain_window, thunder
- Lightning: `setcvar "r_fastsky" "1"` (flash) / `"0"` (normal)

## BACKGROUND LOOP PATTERN:
```
thread myloop          // call site: always thread
myloop:
    // work here
    wait 1
    goto myloop        // loop: always goto, never thread
end
```

## HUD PATTERN:
```
huddraw_virtualsize 50 1
huddraw_font        50 "facfont-20"
huddraw_align       50 "left" "bottom"
huddraw_rect        50 5 -5 300 20
huddraw_color       50 0.8 0.7 0.2
huddraw_alpha       50 1.0
huddraw_string      50 "My Server"
```

## SOUND ALIAS PATTERN (before prespawn only):
```
local.master = spawn ScriptMaster
local.master aliascache mysound sound/path.wav soundparms 1.0 0.0 1.0 0.0 300 3000 item loaded maps "dm obj"
```

## SCOREBOARD PIC VALUES: objdm1(Hunt) objdm2(V2) objdm4(Bridge) objdm5(Omaha)

When generating a mod: produce complete .scr files using ONLY verified paths and patterns above.
When fixing a script: return the complete corrected script only, no explanation, no markdown fences.
When the user asks about game paths/sounds/models: only cite verified values from this prompt."""

# Enhanced version includes full reference docs (used for Groq/Grok which have no built-in MOHAA knowledge)
MOHAA_ENHANCED = MOHAA_SYSTEM + "\n\n# COMPLETE MOHAA REFERENCE DOCUMENTATION\n\n" + MOHAA_REFS

# ═══════════════════════════════════════════════════════════════════════════════
#  AI DISPATCH
# ═══════════════════════════════════════════════════════════════════════════════

def _chat_oai(base_url, api_key, model, messages, system, timeout=120):
    """Call any OpenAI-compatible endpoint (Groq, Grok, etc.)."""
    resp = _req.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "max_tokens": 4096,
              "messages": [{"role": "system", "content": system}] + messages},
        timeout=timeout
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def ai_chat(messages):
    provider = get_provider()
    model    = get_model()
    key      = get_key(provider)
    if not key: raise ValueError("no_key")

    if provider == "anthropic":
        client = _ant.Anthropic(api_key=key)
        msg = client.messages.create(
            model=model, max_tokens=4096,
            system=MOHAA_SYSTEM, messages=messages
        )
        return msg.content[0].text
    else:
        info = PROVIDERS[provider]
        return _chat_oai(info["base_url"], key, model, messages, MOHAA_SYSTEM)

# ═══════════════════════════════════════════════════════════════════════════════
#  BUG CHECKER ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

KEYWORDS = {"if","else","while","for","switch","case","default","try","catch","end","break","continue"}
LABEL_RE  = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)(\s+local\.\w+)*\s*:\s*(?://.*)?$')

def chk_duplicate_labels(lines):
    issues, seen = [], {}
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("//"): continue
        m = LABEL_RE.match(s)
        if m:
            name = m.group(1)
            if name in KEYWORDS: continue
            if name in seen:
                issues.append(dict(line=i+1, severity="critical", rule="Duplicate Label",
                    message=f'Label <code>{name}</code> already defined at line {seen[name]}. '
                            f'MOHAA rejects the <em>entire file</em> — no script runs at all.',
                    code=line.rstrip()))
            else:
                seen[name] = i+1
    return issues

def chk_null_stufftext(lines):
    issues = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not re.search(r'\$player\s+stufftext', s): continue
        ctx = "\n".join(lines[max(0,i-20):i+1])
        if not re.search(r'if\s*\(\s*\$player\s*!=\s*NULL', ctx):
            issues.append(dict(line=i+1, severity="critical", rule="Missing NULL Guard",
                message='<code>$player stufftext</code> without <code>if ($player != NULL)</code> guard. '
                        'Crashes with "command applied to NULL listener" at map load before any player connects.',
                code=line.rstrip()))
    return issues

def chk_bad_sound_channel(lines):
    issues = []
    for i, line in enumerate(lines):
        s = line.strip()
        if "soundparms" not in s: continue
        if re.search(r'\bclass\b', s):
            issues.append(dict(line=i+1, severity="critical", rule="Invalid Sound Channel",
                message='<code>class</code> is not a valid aliascache channel. '
                        'Valid channels: <code>item</code> <code>auto</code> <code>local</code> <code>body</code> <code>dialog</code> <code>voice</code>',
                code=line.rstrip()))
    return issues

def chk_prepare_after_prespawn(lines):
    issues, prespawn_at = [], None
    for i, line in enumerate(lines):
        s = line.strip()
        if "level waittill prespawn" in s: prespawn_at = i+1
        if prespawn_at and re.search(r'exec\s+\S+::prepare', s) and i+1 > prespawn_at:
            issues.append(dict(line=i+1, severity="critical", rule="prepare After prespawn",
                message=f'<code>exec ::prepare</code> at line {i+1} comes AFTER <code>level waittill prespawn</code> (line {prespawn_at}). '
                        'Sound aliases won\'t register. Move all <code>::prepare</code> calls before prespawn.',
                code=line.rstrip()))
    return issues

def chk_vector_negative(lines):
    issues = []
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("//"): continue
        if re.search(r'\(-[0-9]', s):
            issues.append(dict(line=i+1, severity="warning", rule="Vector Negative Space",
                message='Negative first vector component needs a space after <code>(</code>. '
                        'Write <code>( -1 0 0 )</code> not <code>(-1 0 0)</code>.',
                code=line.rstrip()))
    return issues

def chk_goto_in_main(lines):
    issues, in_main, depth = [], False, 0
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("//"): continue
        if re.match(r'^main\s*:', s): in_main = True; depth = 0; continue
        if in_main:
            depth += s.count("{") - s.count("}")
            if s == "end" and depth <= 0: in_main = False; continue
            m = re.match(r'^goto\s+(\w+)\s*$', s)
            if m and depth == 0:
                lbl = m.group(1)
                issues.append(dict(line=i+1, severity="warning", rule="goto at Call Site",
                    message=f'<code>goto {lbl}</code> in <code>main:</code> is a jump, not a thread. '
                            f'All code after this line is dead. Use <code>thread {lbl}</code> to run it as a background loop.',
                    code=line.rstrip()))
    return issues

def chk_thread_leak(lines):
    issues, cur = [], None
    label_bodies = {}
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("//"): continue
        m = LABEL_RE.match(s)
        if m:
            name = m.group(1)
            if name not in KEYWORDS:
                cur = name
                label_bodies[name] = {"is_loop": False, "lines": []}
        if cur:
            label_bodies[cur]["lines"].append((i, line))
            if re.match(rf'^goto\s+{re.escape(cur)}\s*$', s):
                label_bodies[cur]["is_loop"] = True
    for lname, info in label_bodies.items():
        if not info["is_loop"]: continue
        for (i, line) in info["lines"]:
            if re.match(rf'^thread\s+{re.escape(lname)}\s*$', line.strip()):
                issues.append(dict(line=i+1, severity="critical", rule="Thread Leak in Loop",
                    message=f'<code>thread {lname}</code> INSIDE loop <code>{lname}:</code>. '
                            f'Every iteration spawns a new thread → exponential leak → server crash. '
                            f'Use <code>goto {lname}</code> to stay in the same thread.',
                    code=line.rstrip()))
    return issues

def chk_vehicle_waitframe(lines):
    issues = []
    for i, line in enumerate(lines):
        if "spawn VehicleTank" in line:
            nxt = [lines[j].strip() for j in range(i+1, min(i+4, len(lines)))]
            if not any("waitframe" in l for l in nxt):
                issues.append(dict(line=i+1, severity="warning", rule="VehicleTank Missing waitframe",
                    message='<code>spawn VehicleTank</code> must be followed by <code>waitframe</code> '
                            'before accessing turret or speed properties.',
                    code=line.rstrip()))
    return issues

def chk_player_index_null(lines):
    issues = []
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("//"): continue
        if re.search(r'\$player\[\w+\]', s) and ".size" not in s:
            ctx = "\n".join(lines[max(0,i-15):i+1])
            if not (re.search(r'\$player\[\w+\]\s*!=\s*NULL', ctx) or re.search(r'isAlive\s+\$player', ctx)):
                issues.append(dict(line=i+1, severity="warning", rule="Player Index Without NULL Check",
                    message='<code>$player[i]</code> without <code>!= NULL</code> check. '
                            'Disconnected players leave NULL slots — accessing their properties crashes.',
                    code=line.rstrip()))
    return issues

def chk_missing_end(lines):
    issues = []
    labels = [l for l in lines if LABEL_RE.match(l.strip()) and l.strip().split()[0] not in KEYWORDS
              and not l.strip().startswith("//")]
    ends = sum(1 for l in lines if l.strip() == "end")
    if labels and ends < len(labels):
        diff = len(labels) - ends
        issues.append(dict(line=0, severity="warning", rule="Possible Missing end",
            message=f'Found {len(labels)} labels but only {ends} <code>end</code> statements — '
                    f'~{diff} may be missing. Unterminated labels cause parse errors.',
            code="(whole-file check)"))
    return issues

def chk_nil_direct(lines):
    issues = []
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("//"): continue
        if re.search(r'\bNIL\b', s) and "== NIL" not in s and "!= NIL" not in s:
            issues.append(dict(line=i+1, severity="info", rule="NIL Value Used Directly",
                message='<code>NIL</code> means uninitialized. Using it in operations (not just comparing with <code>== NIL</code>) causes a Script Error.',
                code=line.rstrip()))
    return issues

ALL_CHECKS = [
    chk_duplicate_labels, chk_null_stufftext, chk_bad_sound_channel,
    chk_prepare_after_prespawn, chk_vector_negative, chk_goto_in_main,
    chk_thread_leak, chk_vehicle_waitframe, chk_player_index_null,
    chk_missing_end, chk_nil_direct,
]

def analyze(code):
    lines = code.splitlines()
    issues = []
    for fn in ALL_CHECKS:
        try: issues.extend(fn(lines))
        except Exception: pass
    issues.sort(key=lambda x: x["line"])
    return {"issues": issues,
            "critical": sum(1 for x in issues if x["severity"]=="critical"),
            "warnings": sum(1 for x in issues if x["severity"]=="warning"),
            "info":     sum(1 for x in issues if x["severity"]=="info")}

# ═══════════════════════════════════════════════════════════════════════════════
#  MOD BUILDER ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def _w(L, *args): L.extend(args)

def build_map_script(map_name, cfg):
    F, author = cfg.get("features",[]), cfg.get("author","Author")
    mod, ver  = cfg.get("mod_name","mymod"), cfg.get("version","1.0")
    srv       = cfg.get("server_name","My Server")
    allied    = cfg.get("allied_text","Complete the objective")
    axis_t    = cfg.get("axis_text","Stop the Allies")
    L = []
    _w(L,
       f"// ── {map_name.upper()} ─────────────────────────────────────────────────────────────",
       f"// MOD: {mod} v{ver}",  f"// BY:  {author}", "",
       "main:", "",
       f'setcvar "g_obj_alliedtext1" "{allied}"',
        'setcvar "g_obj_alliedtext2" ""',
       f'setcvar "g_obj_alliedtext3" "Welcome to {srv}"',
       f'setcvar "g_obj_axistext1"   "{axis_t}"',
        'setcvar "g_obj_axistext2"   "Modded by"',
       f'setcvar "g_obj_axistext3"   "{author}"', "",
    )
    if "custom_music" in F and cfg.get("music_path"):
        _w(L, f'setcvar "forcemusic" "{cfg["music_path"]}"', "")
    if "welcome" in F:
        _w(L, "local.master = spawn ScriptMaster",
           'local.master aliascache welcome_ding sound/items/lt_pickup_health.wav soundparms 1.0 0.0 1.0 0.0 10000 10000 local loaded maps "obj"', "")
    _w(L, "level waittill prespawn", "")
    if "anticheat" in F: _w(L, "thread cheats", "thread nocheats", "")
    if "server_hud"  in F: _w(L, "thread server_hud")
    if "team_hud"    in F: _w(L, "thread team_hud")
    if "killstreak"  in F: _w(L, "thread global/killstreak.scr::main")
    if "welcome"     in F: _w(L, "thread global/welcome.scr::main")
    if "selfheal"    in F: _w(L, "thread global/selfheal.scr::main")
    if "koth"        in F: _w(L, "thread global/koth.scr::main")
    _w(L, "", "exec global/DMprecache.scr",
       f"level.script = maps/obj/{map_name}.scr",
       f"exec global/ambient.scr {map_name}", "", "end")
    if "anticheat" in F:
        _w(L, "", "",
           "// ─── ANTI-CHEAT ─────────────────────────────────────────────────────────────",
           "", "cheats:",
           'setcvar "cheats" "0"', 'setcvar "thereisnomonkey" "0"',
           "if ($player != NULL)", "{",
           '    $player stufftext ("set r_lightmap 0")', "}",
           "wait 1", "goto cheats", "end", "",
           "nocheats:", "if ($player != NULL)", "{",
           '    $player stufftext ("developer 0")', "}",
           "wait 1", "goto nocheats", "end")
    if "server_hud" in F:
        _w(L, "", "",
           "// ─── SERVER HUD ─────────────────────────────────────────────────────────────",
           "", "server_hud:",
           "    huddraw_virtualsize  50  1", '    huddraw_font         50  "facfont-20"',
           '    huddraw_align        50  "left" "bottom"', "    huddraw_rect         50  5 -5 300 20",
           "    huddraw_color        50  0.8 0.7 0.2", "    huddraw_alpha        50  1.0",
           f'    huddraw_string       50  "{srv}"', "end")
    if "team_hud" in F:
        _w(L, "", "",
           "// ─── TEAM HUD ───────────────────────────────────────────────────────────────",
           "", "team_hud:",
           "    huddraw_virtualsize  70  1", '    huddraw_align        70  "right" "top"',
           "    huddraw_rect         70  -10 10 200 20", '    huddraw_font         70  "facfont-20"',
           "    huddraw_color        70  0.3 0.5 1.0", "    huddraw_alpha        70  1.0",
           "    huddraw_virtualsize  71  1", '    huddraw_align        71  "right" "top"',
           "    huddraw_rect         71  -10 30 200 20", '    huddraw_font         71  "facfont-20"',
           "    huddraw_color        71  1.0 0.3 0.3", "    huddraw_alpha        71  1.0",
           "    while (1)", "    {",
           "        local.a = 0", "        local.x = 0",
           "        for (local.i = 1; local.i <= $player.size; local.i++)", "        {",
           "            if ($player[local.i] != NULL)", "            {",
           '                if ($player[local.i].dmteam == "allies") { local.a++ }',
           "                else { local.x++ }", "            }", "        }",
           '        huddraw_string  70  ("Allies: " + local.a)',
           '        huddraw_string  71  ("Axis:   " + local.x)',
           "        wait 2", "    }", "end")
    return "\n".join(L)

def build_welcome_scr(cfg):
    srv = cfg.get("server_name","My Server")
    return "\n".join([
        "// global/welcome.scr", f"// Welcome message — {srv}", "",
        "main:", "    while (1)", "    {",
        "        level waittill player_spawned",
        "        local.p = parm.other", "        wait 1",
        "        if (local.p != NULL)", "        {",
        f'            local.p stufftext ("say Welcome to {srv}, " + local.p.netname + "!")',
        "            huddraw_virtualsize  200  1", '            huddraw_font         200  "facfont-20"',
        '            huddraw_align        200  "center" "center"',
        "            huddraw_rect         200  0 -60 400 30",
        "            huddraw_color        200  1.0 1.0 0.0", "            huddraw_alpha        200  1.0",
        f'            huddraw_string       200  ("Welcome, " + local.p.netname + "!")',
        "            wait 5", "            huddraw_alpha        200  0",
        "        }", "    }", "end",
    ])

def build_killstreak_scr(cfg):
    return "\n".join([
        "// global/killstreak.scr", "// Kill streak announcer",
        "", "main:", "    level waittill spawn",
        "    for (local.i = 1; local.i <= $player.size; local.i++)", "    {",
        "        if ($player[local.i] != NULL)",
        "        {", '            setcvar ("ks_" + $player[local.i].entnum) "0"', "        }",
        "    }", "    while (1)", "    {", "        wait 1",
        "        for (local.i = 1; local.i <= $player.size; local.i++)", "        {",
        "            if ($player[local.i] != NULL && isAlive $player[local.i])", "            {",
        "                local.p   = $player[local.i]",
        '                local.cur = int(getcvar ("ks_" + local.p.entnum))',
        "                if (local.cur == 3)", "                {",
        '                    iprintlnbold (local.p.netname + " is on a KILLING SPREE!")',
        "                }", "                else if (local.cur == 5)", "                {",
        '                    iprintlnbold (local.p.netname + " IS UNSTOPPABLE!")',
        "                }", "                else if (local.cur == 7)", "                {",
        '                    iprintlnbold (local.p.netname + " IS GODLIKE!")',
        "                }", "            }", "        }", "    }", "end",
    ])

def build_selfheal_scr(cfg):
    return "\n".join([
        "// global/selfheal.scr", "// Crouch still 1.75s → +10 HP", "",
        "main:", "    level waittill spawn", "    while (1)", "    {",
        "        level waittill player_spawned",
        "        local.p = parm.other", "        local.p thread heal_watch", "    }", "end", "",
        "heal_watch:", "    while (isAlive self)", "    {",
        "        while (isAlive self &&",
        '               ((self getposition)[0] != "c" ||',
        '                (self getmovement)[0] != "s" ||',
        "                self.fireheld == 1 || self.useheld == 1))",
        "            waitframe",
        "        local.t = 0",
        "        while (isAlive self && local.t < 1.75 &&",
        '               (self getposition)[0] == "c" &&',
        '               (self getmovement)[0] == "s" &&',
        "               self.fireheld != 1 && self.useheld != 1)",
        "        {", "            waitframe", "            local.t += 0.05", "        }",
        "        if (local.t >= 1.75 && isAlive self)", "            self heal 10",
        "    }", "end",
    ])

def build_koth_scr(cfg):
    return "\n".join([
        "// global/koth.scr", "// King of the Hill — first team to capture 5 times wins", "",
        "main:", "    level waittill spawn",
        "    level.koth_allies = 0", "    level.koth_axis   = 0", "    level.koth_win    = 5",
        "    thread koth_hud", "    thread koth_loop", "end", "",
        "koth_hud:", "    huddraw_virtualsize  80  1", '    huddraw_align        80  "left" "top"',
        "    huddraw_rect         80  5 5 250 20", '    huddraw_font         80  "facfont-20"',
        "    huddraw_color        80  1.0 1.0 1.0", "    huddraw_alpha        80  1.0",
        "    while (1)", "    {",
        '        huddraw_string 80 ("Hill — Allies: " + level.koth_allies + "  Axis: " + level.koth_axis)',
        "        wait 1", "    }", "end", "",
        "koth_loop:", "    local.positions = makeArray",
        "    (0 0 -500)", "    (500 500 -500)", "    ( -500 500 -500)", "    endArray",
        "    local.hill_pos = local.positions[randomint 3 + 1]",
        "    local.hill = spawn trigger_multiple targetname koth_hill",
        "    local.hill.origin = local.hill_pos",
        "    local.hill setsize (-100 -100 -50) (100 100 100)",
        "    local.light = spawn StaticModelEntity model models/static/corona_reg.tik",
        "    local.light.origin = local.hill_pos + (0 0 60)",
        "    local.count = 0",
        "    while (local.count < 15)", "    {", "        waitframe",
        "        local.a = 0", "        local.x = 0",
        "        for (local.i = 1; local.i <= $player.size; local.i++)", "        {",
        "            if ($player[local.i] != NULL && isAlive $player[local.i] &&",
        "                $player[local.i] isTouching $koth_hill)", "            {",
        '                if ($player[local.i].dmteam == "allies") { local.a++ }',
        "                else { local.x++ }", "            }", "        }",
        "        if (local.a > 0 && local.x == 0)",
        '        { local.holder = "allies" ; local.light.color = (0 0 1) ; local.count++ }',
        "        else if (local.x > 0 && local.a == 0)",
        '        { local.holder = "axis"   ; local.light.color = (1 0 0) ; local.count++ }',
        "        else { local.count = 0 }", "    }",
        "    iprintlnbold (local.holder + \" captured the hill!\")",
        "    local.hill remove", "    local.light remove",
        '    if (local.holder == "allies") { level.koth_allies++ }',
        "    else                          { level.koth_axis++ }",
        "    if (level.koth_allies >= level.koth_win) { teamwin allies }",
        "    else if (level.koth_axis >= level.koth_win) { teamwin axis }",
        "    else { goto koth_loop }", "end",
    ])

def build_mod(cfg):
    F    = cfg.get("features", [])
    maps = cfg.get("maps", ["obj_team1"])
    mod  = cfg.get("mod_name",  "mymod")
    author = cfg.get("author",  "Author")
    ver  = cfg.get("version",   "1.0")
    files = {}
    for m in maps:
        files[f"maps/obj/{m}.scr"] = build_map_script(m, cfg)
    if "welcome"    in F: files["global/welcome.scr"]    = build_welcome_scr(cfg)
    if "killstreak" in F: files["global/killstreak.scr"] = build_killstreak_scr(cfg)
    if "selfheal"   in F: files["global/selfheal.scr"]   = build_selfheal_scr(cfg)
    if "koth"       in F: files["global/koth.scr"]       = build_koth_scr(cfg)
    pkg_name = f"zzz-{author.lower().replace(' ','-')}-{mod}-v{ver}.pk3"
    return {"files": files, "pkg_name": pkg_name}

def build_pk3_bytes(cfg):
    result = build_mod(cfg)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, content in result["files"].items():
            zf.writestr(path, content.encode("utf-8"))
    buf.seek(0)
    return buf, result["pkg_name"]

# ═══════════════════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index(): return HTML_TEMPLATE

@app.route("/api/providers")
def api_providers():
    prov = get_provider()
    mdl  = get_model()
    data = {}
    for k, v in PROVIDERS.items():
        data[k] = {**v, "has_key": bool(get_key(k))}
    return jsonify({"providers": data, "active_provider": prov, "active_model": mdl})

@app.route("/api/set-provider", methods=["POST"])
def api_set_provider():
    d = request.get_json(force=True)
    set_provider_cfg(d.get("provider","groq"), d.get("model"))
    return jsonify({"ok": True})

@app.route("/api/set-key", methods=["POST"])
def api_set_key():
    d = request.get_json(force=True)
    provider = d.get("provider", get_provider())
    set_key(provider, d.get("key",""))
    return jsonify({"ok": True})

@app.route("/api/key-status")
def api_key_status():
    provider = request.args.get("provider", get_provider())
    return jsonify({"has_key": bool(get_key(provider)), "provider": provider})

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(force=True)
    return jsonify(analyze(data.get("code", "")))

@app.route("/api/autofix", methods=["POST"])
def api_autofix():
    data   = request.get_json(force=True)
    code   = data.get("code", "")
    issues = data.get("issues", [])
    issue_lines = "\n".join(
        f"Line {i['line']}: [{i['severity'].upper()}] {i['rule']} — {re.sub('<[^>]+>','',i['message'])}"
        for i in issues
    )
    prompt = (f"Fix ALL bugs listed below in this MOHAA Morpheus Script.\n"
              f"Return ONLY the corrected script — no explanation, no markdown fences.\n\n"
              f"BUGS:\n{issue_lines}\n\nSCRIPT:\n{code}")
    try:
        text = ai_chat([{"role": "user", "content": prompt}])
        return jsonify({"fixed": text})
    except ValueError as e:
        if str(e) == "no_key": return jsonify({"error": "no_key"}), 401
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/build", methods=["POST"])
def api_build():
    data = request.get_json(force=True)
    return jsonify(build_mod(data))

@app.route("/api/pk3", methods=["POST"])
def api_pk3():
    data = request.get_json(force=True)
    buf, name = build_pk3_bytes(data)
    return send_file(buf, mimetype="application/zip",
                     as_attachment=True, download_name=name)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data     = request.get_json(force=True)
    messages = data.get("messages", [])[-20:]
    try:
        text = ai_chat(messages)
        return jsonify({"text": text})
    except ValueError as e:
        if str(e) == "no_key": return jsonify({"error": "no_key"}), 401
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════
#  HTML TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════════

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>MOHAA Mod Workshop</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d0d0d;--card:#161616;--card2:#1e1e1e;
  --gold:#c8a84b;--gold2:#a08030;
  --red:#e74c3c;--orange:#e67e22;--blue:#3498db;--green:#2ecc71;
  --text:#d8d8d8;--muted:#777;--border:#2a2a2a;
  --code:#0a0a0a;--mono:'Consolas','Courier New',monospace;
}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',sans-serif;font-size:14px;height:100vh;display:flex;flex-direction:column;overflow:hidden}

/* HEADER */
header{background:linear-gradient(90deg,#0d0d0d,#1a1500,#0d0d0d);border-bottom:2px solid var(--gold2);padding:10px 20px;display:flex;align-items:center;gap:12px;flex-shrink:0}
header h1{font-size:1.1rem;font-weight:700;color:var(--gold);letter-spacing:1px;white-space:nowrap}
header span.sub{color:var(--muted);font-size:.75rem;white-space:nowrap}
.hdr-right{margin-left:auto;display:flex;align-items:center;gap:8px}
.prov-label{font-size:.72rem;color:var(--muted);white-space:nowrap}
select.hsel{background:#111;color:var(--gold);border:1px solid var(--gold2);padding:4px 8px;border-radius:4px;font-size:.78rem;cursor:pointer;outline:none}
select.hsel:focus{border-color:var(--gold)}
select.hsel.mdl{color:var(--text);border-color:var(--border)}
.free-badge{background:#0a2a0a;color:var(--green);border:1px solid #27ae60;border-radius:10px;padding:2px 7px;font-size:.65rem;font-weight:700}

/* KEY BANNER */
#key-banner{background:#1a1000;border-bottom:1px solid var(--gold2);padding:9px 20px;display:flex;align-items:center;gap:10px;flex-shrink:0;flex-wrap:wrap}
#key-label{color:#b8920a;font-size:.82rem;white-space:nowrap}
#key-input{background:#0d0d0d;border:1px solid var(--gold2);color:var(--text);padding:5px 10px;border-radius:4px;font-size:.82rem;width:300px;font-family:var(--mono)}
#key-input:focus{outline:none;border-color:var(--gold)}
#key-link{color:var(--green);font-size:.78rem;text-decoration:none;white-space:nowrap}
#key-link:hover{text-decoration:underline}

/* TABS */
nav{display:flex;gap:2px;padding:10px 20px 0;background:#111;border-bottom:1px solid var(--border);flex-shrink:0}
.tab{padding:8px 18px;cursor:pointer;border:1px solid transparent;border-bottom:none;border-radius:5px 5px 0 0;font-size:.85rem;font-weight:600;color:var(--muted);transition:.15s;background:none}
.tab:hover{color:var(--text);background:var(--card)}
.tab.active{color:var(--gold);background:var(--card);border-color:var(--border)}

/* PANELS */
.panel{display:none;flex:1;overflow:hidden}
.panel.active{display:flex;flex-direction:column}

/* BUTTONS */
.btn{padding:7px 16px;border:none;border-radius:5px;cursor:pointer;font-size:.82rem;font-weight:700;letter-spacing:.3px;transition:.15s}
.btn-gold{background:var(--gold);color:#111}.btn-gold:hover{background:#dbb95e}
.btn-red{background:#c0392b;color:#fff}.btn-red:hover{background:var(--red)}
.btn-dim{background:#2a2a2a;color:var(--text)}.btn-dim:hover{background:#333}
.btn-green{background:#27ae60;color:#fff}.btn-green:hover{background:var(--green);color:#111}
.btn-blue{background:#2471a3;color:#fff}.btn-blue:hover{background:var(--blue)}
.spinner{display:none;width:14px;height:14px;border:2px solid #555;border-top-color:var(--gold);border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.loading .spinner{display:inline-block}.loading .btn-text{display:none}

/* ══ CHECKER TAB ══ */
.checker-wrap{display:flex;flex:1;gap:0;overflow:hidden}
.checker-left{display:flex;flex-direction:column;width:50%;border-right:1px solid var(--border)}
.checker-right{display:flex;flex-direction:column;width:50%}
.pane-hdr{padding:8px 14px;background:var(--card2);border-bottom:1px solid var(--border);font-size:.75rem;font-weight:700;color:var(--gold);text-transform:uppercase;letter-spacing:.5px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
textarea.code{flex:1;background:var(--code);color:#a8c8a8;font-family:var(--mono);font-size:13px;padding:12px;border:none;outline:none;resize:none;line-height:1.6}
textarea.code::placeholder{color:#333}
.pane-footer{padding:8px 14px;background:var(--card2);border-top:1px solid var(--border);display:flex;gap:8px;align-items:center;flex-shrink:0}
#results{flex:1;overflow-y:auto;padding:12px}

/* Issue cards */
.summary{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap}
.badge{padding:4px 10px;border-radius:20px;font-size:.75rem;font-weight:700}
.b-ok{background:#0d2a0d;color:var(--green);border:1px solid var(--green)}
.b-red{background:#2a0d0d;color:var(--red);border:1px solid var(--red)}
.b-orange{background:#2a1a00;color:var(--orange);border:1px solid var(--orange)}
.b-blue{background:#0d1a2a;color:var(--blue);border:1px solid var(--blue)}
.b-dim{background:#111;color:var(--muted);border:1px solid var(--border)}
.issue{margin-bottom:8px;border-radius:5px;overflow:hidden;border:1px solid var(--border)}
.issue-hdr{padding:7px 12px;display:flex;align-items:center;gap:8px;cursor:pointer}
.issue-hdr:hover{filter:brightness(1.1)}
.issue.critical .issue-hdr{background:#241010}
.issue.warning  .issue-hdr{background:#241a08}
.issue.info     .issue-hdr{background:#08182a}
.sev{font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:10px;text-transform:uppercase}
.sev.critical{background:var(--red);color:#fff}
.sev.warning{background:var(--orange);color:#000}
.sev.info{background:var(--blue);color:#fff}
.issue-rule{font-weight:700;font-size:.82rem}
.issue-ln{margin-left:auto;color:var(--muted);font-size:.75rem;font-family:var(--mono)}
.issue-body{padding:10px 12px;background:var(--code);border-top:1px solid var(--border);display:none}
.issue-body.open{display:block}
.issue-msg{margin-bottom:7px;line-height:1.6;font-size:.82rem}
.issue-msg code{background:#1e1e1e;padding:1px 5px;border-radius:3px;font-family:var(--mono);font-size:.8em;color:#8dcc8d}
.issue-code{font-family:var(--mono);font-size:.78rem;background:#111;padding:7px 10px;border-radius:4px;color:#f0c070;overflow-x:auto;white-space:pre}
.ok-msg{text-align:center;padding:40px;color:var(--green)}
.placeholder-msg{text-align:center;padding:40px;color:var(--muted)}

/* Auto-fix section */
#autofix-section{flex-shrink:0;border-top:1px solid var(--border);background:var(--card)}
#autofix-section .section-hdr{padding:8px 14px;display:flex;align-items:center;gap:10px;background:#101a10}
#fixed-area{display:none;flex-direction:column}
#fixed-code{flex:1;background:#060f06;color:#a8c8a8;font-family:var(--mono);font-size:13px;padding:12px;border:none;outline:none;resize:none;line-height:1.6;height:200px}
#fixed-footer{padding:8px 14px;background:var(--card2);border-top:1px solid var(--border);display:flex;gap:8px;align-items:center}

/* ══ BUILDER TAB ══ */
.builder-wrap{display:flex;flex:1;overflow:hidden}
.builder-form-col{width:330px;overflow-y:auto;border-right:1px solid var(--border);flex-shrink:0}
.builder-out-col{flex:1;display:flex;flex-direction:column;overflow:hidden}
.form-section{padding:12px 14px;border-bottom:1px solid var(--border)}
.form-section h3{font-size:.7rem;font-weight:700;color:var(--gold);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}
.field{margin-bottom:8px}
.field label{display:block;font-size:.75rem;color:var(--muted);margin-bottom:3px}
.field input[type=text]{width:100%;background:#0d0d0d;color:var(--text);border:1px solid var(--border);padding:6px 9px;border-radius:4px;font-size:.82rem;outline:none}
.field input:focus{border-color:var(--gold2)}
.check-grid{display:grid;grid-template-columns:1fr 1fr;gap:3px}
.chk{display:flex;align-items:flex-start;gap:6px;padding:4px 0;cursor:pointer}
.chk input{width:14px;height:14px;margin-top:2px;accent-color:var(--gold);cursor:pointer;flex-shrink:0}
.chk .cl{font-size:.8rem;line-height:1.3}.chk .cd{font-size:.7rem;color:var(--muted)}
.map-chk{display:flex;align-items:center;gap:6px;padding:3px 0;cursor:pointer}
.map-chk input{accent-color:var(--gold)}
.map-chk span{font-size:.82rem;font-family:var(--mono)}
.build-actions{padding:10px 14px;border-bottom:1px solid var(--border);display:flex;gap:8px}
.build-actions .btn{flex:1;padding:9px}
.file-tabs{display:flex;flex-wrap:wrap;gap:3px;padding:8px 12px;background:var(--card2);border-bottom:1px solid var(--border);flex-shrink:0}
.ftab{padding:3px 10px;border-radius:3px;cursor:pointer;font-size:.75rem;font-family:var(--mono);background:#111;color:var(--muted);border:1px solid var(--border)}
.ftab:hover{color:var(--text)}.ftab.active{background:var(--gold);color:#111;font-weight:700}
.file-view{flex:1;position:relative;overflow:hidden}
.file-view pre{height:100%;overflow:auto;background:var(--code);color:#a8c8a8;font-family:var(--mono);font-size:12.5px;padding:14px;line-height:1.6;margin:0}
.copy-btn{position:absolute;top:8px;right:12px;background:#333;color:var(--text);border:none;padding:3px 10px;border-radius:3px;cursor:pointer;font-size:.72rem;z-index:10;transition:.15s}
.copy-btn:hover{background:#555}.copy-btn.copied{background:var(--green);color:#000}
.out-placeholder{flex:1;display:flex;align-items:center;justify-content:center;color:var(--muted);flex-direction:column;gap:10px}

/* ══ CHAT TAB ══ */
.chat-wrap{display:flex;flex:1;flex-direction:column;overflow:hidden}
.chat-messages{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:82%;padding:10px 14px;border-radius:10px;line-height:1.6;font-size:.85rem;word-break:break-word}
.msg.user{align-self:flex-end;background:#1e1a08;border:1px solid var(--gold2);color:var(--text)}
.msg.assistant{align-self:flex-start;background:var(--card);border:1px solid var(--border);color:var(--text)}
.msg.assistant code{background:#111;padding:1px 5px;border-radius:3px;font-family:var(--mono);font-size:.82em;color:#8dcc8d}
.msg.assistant strong{color:var(--gold)}
.code-block{position:relative;margin:8px 0}
.code-block pre{background:#060606;color:#a8c8a8;font-family:var(--mono);font-size:.8rem;padding:12px;border-radius:5px;overflow-x:auto;line-height:1.5;border:1px solid #222;margin:0}
.code-block .cbtn{position:absolute;top:5px;right:6px;background:#2a2a2a;color:var(--muted);border:none;padding:2px 8px;border-radius:3px;cursor:pointer;font-size:.7rem}
.code-block .cbtn:hover{background:#444;color:var(--text)}
.code-block .cbtn.done{background:#1a3a1a;color:var(--green)}
.typing-dot{display:inline-block;width:6px;height:6px;background:var(--gold);border-radius:50%;animation:dot .8s infinite;margin:0 2px}
.typing-dot:nth-child(2){animation-delay:.2s}.typing-dot:nth-child(3){animation-delay:.4s}
@keyframes dot{0%,80%,100%{opacity:.2}40%{opacity:1}}
.chat-input-row{padding:12px 16px;border-top:1px solid var(--border);background:var(--card2);display:flex;gap:8px;align-items:flex-end;flex-shrink:0}
#chat-input{flex:1;background:#0d0d0d;color:var(--text);border:1px solid var(--border);padding:8px 12px;border-radius:6px;font-size:.85rem;resize:none;outline:none;font-family:inherit;max-height:120px;line-height:1.5}
#chat-input:focus{border-color:var(--gold2)}
.chat-actions{display:flex;flex-direction:column;gap:4px}
.prov-info{padding:6px 16px;background:#111;border-top:1px solid var(--border);font-size:.72rem;color:var(--muted);flex-shrink:0}
</style>
</head>
<body>

<header>
  <div>
    <h1>&#9876; MOHAA Mod Workshop</h1>
    <span class="sub">Bug Checker &middot; Auto Fix &middot; Mod Builder &middot; AI Chat</span>
  </div>
  <div class="hdr-right">
    <span class="prov-label">AI Provider:</span>
    <select id="prov-sel" class="hsel" onchange="onProviderChange()">
      <option value="groq">&#128994; Groq (Free)</option>
      <option value="grok">Grok (xAI)</option>
      <option value="anthropic">Claude</option>
    </select>
    <select id="mdl-sel" class="hsel mdl" onchange="onModelChange()"></select>
    <span id="free-badge" class="free-badge">FREE</span>
  </div>
</header>

<!-- API Key Banner -->
<div id="key-banner" style="display:none">
  <span id="key-label">&#128273; API key:</span>
  <input type="password" id="key-input" placeholder="gsk_...">
  <button class="btn btn-gold" onclick="saveKey()">Save Key</button>
  <button class="btn btn-dim" onclick="document.getElementById('key-banner').style.display='none'">Dismiss</button>
  <a id="key-link" href="#" target="_blank">Get free key &#8599;</a>
</div>

<nav>
  <button class="tab active" onclick="switchTab('checker',this)">&#128269; Bug Checker</button>
  <button class="tab" onclick="switchTab('builder',this)">&#128230; Mod Builder</button>
  <button class="tab" onclick="switchTab('chat',this)">&#129302; AI Chat</button>
</nav>

<!-- ═══════════════════ BUG CHECKER ═══════════════════ -->
<div id="panel-checker" class="panel active">
  <div class="checker-wrap">
    <div class="checker-left">
      <div class="pane-hdr">
        Paste your .scr script
        <button class="btn btn-dim" onclick="clearCode()" style="font-size:.7rem;padding:2px 8px">Clear</button>
      </div>
      <textarea id="code-input" class="code" placeholder="// Paste your Morpheus Script here..."></textarea>
      <div class="pane-footer">
        <button class="btn btn-gold" id="analyze-btn" onclick="analyzeCode()">
          <span class="btn-text">&#128269; Analyze</span>
          <div class="spinner"></div>
        </button>
        <span id="line-count" style="color:var(--muted);font-size:.78rem"></span>
      </div>
    </div>
    <div class="checker-right">
      <div class="pane-hdr">Analysis Results</div>
      <div id="results" style="flex:1;overflow-y:auto;padding:12px">
        <div class="placeholder-msg">
          <div style="font-size:2rem;margin-bottom:8px">&#128196;</div>
          <div>Paste a script and click <strong>Analyze</strong></div>
          <div style="margin-top:6px;font-size:.78rem;color:var(--muted)">Checks 11 common Morpheus Script bugs</div>
        </div>
      </div>
      <div id="autofix-section" style="display:none">
        <div class="section-hdr">
          <button class="btn btn-green" id="fix-btn" onclick="autoFix()">
            <span class="btn-text">&#129302; Auto Fix with AI</span>
            <div class="spinner"></div>
          </button>
          <span id="fix-status" style="font-size:.78rem;color:var(--muted)"></span>
        </div>
        <div id="fixed-area">
          <div class="pane-hdr" style="background:#060f06;color:#5a9a5a">
            Fixed Script
            <span id="fix-diff" style="color:var(--muted);font-weight:400;font-size:.72rem"></span>
          </div>
          <textarea id="fixed-code" readonly></textarea>
          <div id="fixed-footer">
            <button class="btn btn-gold" onclick="applyFix()">Apply Fix → Editor</button>
            <button class="btn btn-dim" onclick="reAnalyze()">Re-Analyze</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ═══════════════════ MOD BUILDER ═══════════════════ -->
<div id="panel-builder" class="panel">
  <div class="builder-wrap">
    <div class="builder-form-col">
      <div class="form-section">
        <h3>&#127942; Identity</h3>
        <div class="field"><label>Mod name (no spaces)</label><input type="text" id="b-mod" value="my-server-mod"></div>
        <div class="field"><label>Author</label><input type="text" id="b-author" value="Author"></div>
        <div class="field"><label>Version</label><input type="text" id="b-ver" value="1.0"></div>
        <div class="field"><label>Server name</label><input type="text" id="b-srv" value="GF Server"></div>
        <div class="field"><label>Allied objective text</label><input type="text" id="b-allied" value="Complete the objective"></div>
        <div class="field"><label>Axis objective text</label><input type="text" id="b-axis" value="Stop the Allies"></div>
      </div>
      <div class="form-section">
        <h3>&#128506; Maps</h3>
        <label class="map-chk"><input type="checkbox" id="map-obj1" checked><span>obj_team1 (The Hunt)</span></label>
        <label class="map-chk"><input type="checkbox" id="map-obj2"><span>obj_team2 (V2 Facility)</span></label>
        <label class="map-chk"><input type="checkbox" id="map-obj4"><span>obj_team4 (Pipeline)</span></label>
      </div>
      <div class="form-section">
        <h3>&#9881; Features</h3>
        <div class="check-grid">
          <label class="chk"><input type="checkbox" id="f-anticheat" checked><div><div class="cl">Anti-Cheat</div><div class="cd">Blocks wallhack cvars</div></div></label>
          <label class="chk"><input type="checkbox" id="f-server_hud" checked><div><div class="cl">Server HUD</div><div class="cd">Name bottom-left</div></div></label>
          <label class="chk"><input type="checkbox" id="f-team_hud"><div><div class="cl">Team Count HUD</div><div class="cd">Live count top-right</div></div></label>
          <label class="chk"><input type="checkbox" id="f-welcome"><div><div class="cl">Welcome Message</div><div class="cd">Greet on join</div></div></label>
          <label class="chk"><input type="checkbox" id="f-killstreak"><div><div class="cl">Kill Streak</div><div class="cd">3/5/7 kill announce</div></div></label>
          <label class="chk"><input type="checkbox" id="f-selfheal"><div><div class="cl">Self Heal</div><div class="cd">Crouch still = +HP</div></div></label>
          <label class="chk"><input type="checkbox" id="f-koth"><div><div class="cl">King of the Hill</div><div class="cd">Capture zone mode</div></div></label>
          <label class="chk"><input type="checkbox" id="f-custom_music"><div><div class="cl">Custom Music</div><div class="cd">Force music track</div></div></label>
        </div>
      </div>
      <div class="form-section" id="music-row" style="display:none">
        <h3>&#127925; Music path</h3>
        <div class="field"><input type="text" id="b-music" value="sound/music/mus_MainTheme.mp3"></div>
      </div>
      <div class="build-actions">
        <button class="btn btn-dim" id="preview-btn" onclick="previewMod()">
          <span class="btn-text">&#128065; Preview Scripts</span><div class="spinner"></div>
        </button>
        <button class="btn btn-green" id="dl-btn" onclick="downloadPk3()">
          <span class="btn-text">&#11015; Download .pk3</span><div class="spinner"></div>
        </button>
      </div>
    </div>
    <div class="builder-out-col">
      <div id="builder-output" style="flex:1;display:flex;flex-direction:column;overflow:hidden">
        <div class="out-placeholder">
          <div style="font-size:2.5rem">&#128230;</div>
          <div>Configure your mod and click <strong>Preview</strong> or <strong>Download</strong></div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ═══════════════════ AI CHAT ═══════════════════ -->
<div id="panel-chat" class="panel">
  <div class="chat-wrap">
    <div id="chat-messages" class="chat-messages">
      <div class="msg assistant">
        <strong>MOHAA AI Assistant ready.</strong><br><br>
        I know everything about Morpheus Script and MOHAA server-side modding. Ask me to:<br>
        &bull; Generate a complete mod from description<br>
        &bull; Explain how any script feature works<br>
        &bull; Fix or improve your scripts<br>
        &bull; Suggest ideas for your server<br><br>
        <em style="color:var(--muted)">Tip: I have the full MOHAA reference docs loaded — I generate complete, working .scr files.</em>
      </div>
    </div>
    <div class="prov-info" id="prov-info">Provider: Groq &middot; Model: llama-3.3-70b-versatile</div>
    <div class="chat-input-row">
      <textarea id="chat-input" rows="2" placeholder="Ask anything about MOHAA modding... (Enter to send, Shift+Enter for new line)"></textarea>
      <div class="chat-actions">
        <button class="btn btn-gold" id="send-btn" onclick="sendChat()">&#9658; Send</button>
        <button class="btn btn-dim" onclick="clearChat()" style="font-size:.72rem;padding:5px 10px">Clear</button>
      </div>
    </div>
  </div>
</div>

<script>
// ── State ─────────────────────────────────────────────────────────────────────
let chatHistory = [];
let currentIssues = [];
let currentCode = '';
let builtFiles = {};

const PROV_DATA = {
  groq:      {models:["llama-3.3-70b-versatile","llama-3.1-70b-versatile","llama-3.1-8b-instant","mixtral-8x7b-32768"], free:true,  keyLink:"https://console.groq.com/keys",  keyLabel:"Groq API key — free at console.groq.com:", hint:"gsk_..."},
  grok:      {models:["grok-3-mini","grok-beta","grok-2-1212"],                                                          free:false, keyLink:"https://console.x.ai",           keyLabel:"xAI API key:",                             hint:"xai-..."},
  anthropic: {models:["claude-sonnet-4-6","claude-haiku-4-5-20251001","claude-opus-4-7"],                               free:false, keyLink:"https://console.anthropic.com",  keyLabel:"Anthropic API key:",                       hint:"sk-ant-..."}
};

let activeProv  = 'groq';
let activeModel = 'llama-3.3-70b-versatile';

// ── Init ──────────────────────────────────────────────────────────────────────
window.addEventListener('load', async () => {
  const r = await fetch('/api/providers');
  const d = await r.json();
  activeProv  = d.active_provider || 'groq';
  activeModel = d.active_model   || PROV_DATA[activeProv].models[0];

  // Set provider dropdown
  document.getElementById('prov-sel').value = activeProv;
  populateModels(activeProv, activeModel);
  updateFreeBadge();
  updateProvInfo();

  // Check key
  checkKeyStatus(activeProv);
});

function populateModels(prov, selectedModel) {
  const sel = document.getElementById('mdl-sel');
  sel.innerHTML = PROV_DATA[prov].models.map(m =>
    `<option value="${m}" ${m===selectedModel?'selected':''}>${m}</option>`
  ).join('');
}

function updateFreeBadge() {
  const badge = document.getElementById('free-badge');
  badge.style.display = PROV_DATA[activeProv].free ? '' : 'none';
}

function updateProvInfo() {
  document.getElementById('prov-info').textContent =
    `Provider: ${activeProv.charAt(0).toUpperCase()+activeProv.slice(1)} · Model: ${activeModel}`;
}

async function onProviderChange() {
  activeProv  = document.getElementById('prov-sel').value;
  activeModel = PROV_DATA[activeProv].models[0];
  populateModels(activeProv, activeModel);
  updateFreeBadge();
  updateProvInfo();
  await fetch('/api/set-provider', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({provider: activeProv, model: activeModel})});
  checkKeyStatus(activeProv);
}

async function onModelChange() {
  activeModel = document.getElementById('mdl-sel').value;
  updateProvInfo();
  await fetch('/api/set-provider', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({provider: activeProv, model: activeModel})});
}

async function checkKeyStatus(prov) {
  const r = await fetch('/api/key-status?provider=' + prov);
  const d = await r.json();
  const banner = document.getElementById('key-banner');
  if (!d.has_key) {
    const pd = PROV_DATA[prov];
    document.getElementById('key-label').textContent = '🔑 ' + pd.keyLabel;
    document.getElementById('key-input').placeholder  = pd.hint;
    document.getElementById('key-link').href           = pd.keyLink;
    document.getElementById('key-link').textContent    = 'Get key ↗';
    banner.style.display = 'flex';
  } else {
    banner.style.display = 'none';
  }
}

async function saveKey() {
  const key = document.getElementById('key-input').value.trim();
  if (!key) return;
  await fetch('/api/set-key', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({provider: activeProv, key})});
  document.getElementById('key-banner').style.display = 'none';
}

// ── Tabs ──────────────────────────────────────────────────────────────────────
function switchTab(id, btn) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('panel-' + id).classList.add('active');
  btn.classList.add('active');
}

// ── Utils ─────────────────────────────────────────────────────────────────────
function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function renderMD(text) {
  text = text.replace(/```(?:scr|script|)?\n([\s\S]*?)```/g, (_, code) =>
    `<div class="code-block"><button class="cbtn" onclick="copyCB(this)">Copy</button><pre>${esc(code)}</pre></div>`);
  text = text.replace(/`([^`\n]+)`/g, '<code>$1</code>');
  text = text.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
  text = text.replace(/\n/g, '<br>');
  return text;
}

function copyCB(btn) {
  const code = btn.nextElementSibling.textContent;
  navigator.clipboard.writeText(code).then(() => {
    btn.textContent = 'Copied!'; btn.classList.add('done');
    setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('done'); }, 1500);
  });
}

// ── Bug Checker ───────────────────────────────────────────────────────────────
document.getElementById('code-input').addEventListener('input', function(){
  document.getElementById('line-count').textContent = this.value.split('\n').length + ' lines';
});

function clearCode() {
  document.getElementById('code-input').value = '';
  document.getElementById('line-count').textContent = '';
  document.getElementById('results').innerHTML = '<div class="placeholder-msg"><div style="font-size:2rem;margin-bottom:8px">&#128196;</div><div>Paste a script and click <strong>Analyze</strong></div></div>';
  document.getElementById('autofix-section').style.display = 'none';
  document.getElementById('fixed-area').style.display = 'none';
}

async function analyzeCode() {
  currentCode = document.getElementById('code-input').value.trim();
  if (!currentCode) return;
  const btn = document.getElementById('analyze-btn');
  btn.classList.add('loading');
  try {
    const r = await fetch('/api/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({code: currentCode})});
    const data = await r.json();
    currentIssues = data.issues;
    renderResults(data);
    document.getElementById('fixed-area').style.display = 'none';
    document.getElementById('fix-status').textContent = '';
    document.getElementById('autofix-section').style.display = data.issues.length > 0 ? 'block' : 'none';
  } finally { btn.classList.remove('loading'); }
}

function renderResults(data) {
  const el = document.getElementById('results');
  if (data.issues.length === 0) {
    el.innerHTML = `<div class="ok-msg"><div style="font-size:2.5rem">&#10003;</div><div style="font-size:1rem;font-weight:700;margin-top:8px">No issues found</div><div style="margin-top:4px;color:var(--muted);font-size:.8rem">Script passed all 11 checks</div></div>`;
    return;
  }
  let html = `<div class="summary">
    <span class="badge ${data.critical>0?'b-red':'b-ok'}">${data.critical} Critical</span>
    <span class="badge ${data.warnings>0?'b-orange':'b-ok'}">${data.warnings} Warnings</span>
    <span class="badge ${data.info>0?'b-blue':'b-ok'}">${data.info} Info</span>
    <span class="badge b-dim">${data.issues.length} total</span></div>`;
  data.issues.forEach((issue, idx) => {
    const ln = issue.line > 0 ? `Line ${issue.line}` : 'File';
    html += `<div class="issue ${issue.severity}" onclick="toggleIssue(${idx})">
      <div class="issue-hdr">
        <span class="sev ${issue.severity}">${issue.severity}</span>
        <span class="issue-rule">${issue.rule}</span>
        <span class="issue-ln">${ln}</span>
      </div>
      <div class="issue-body" id="ib-${idx}">
        <div class="issue-msg">${issue.message}</div>
        ${issue.code !== '(whole-file check)' ? `<div class="issue-code">${esc(issue.code)}</div>` : ''}
      </div></div>`;
  });
  el.innerHTML = html;
  data.issues.forEach((issue, idx) => {
    if (issue.severity === 'critical') document.getElementById('ib-'+idx)?.classList.add('open');
  });
}

function toggleIssue(idx) { document.getElementById('ib-'+idx)?.classList.toggle('open'); }

// ── Auto Fix ──────────────────────────────────────────────────────────────────
async function autoFix() {
  const btn = document.getElementById('fix-btn');
  btn.classList.add('loading');
  document.getElementById('fix-status').textContent = 'Asking AI...';
  try {
    const r = await fetch('/api/autofix', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({code: currentCode, issues: currentIssues})
    });
    if (r.status === 401) {
      checkKeyStatus(activeProv);
      document.getElementById('fix-status').textContent = 'API key required';
      return;
    }
    const data = await r.json();
    if (data.error) { document.getElementById('fix-status').textContent = 'Error: ' + data.error; return; }
    document.getElementById('fixed-code').value = data.fixed;
    const origLines = currentCode.split('\n').length;
    const fixedLines = data.fixed.split('\n').length;
    document.getElementById('fix-diff').textContent = `${origLines} → ${fixedLines} lines`;
    document.getElementById('fixed-area').style.display = 'flex';
    document.getElementById('fix-status').textContent = '✓ Fixed script ready';
  } finally { btn.classList.remove('loading'); }
}

function applyFix() {
  const fixed = document.getElementById('fixed-code').value;
  document.getElementById('code-input').value = fixed;
  currentCode = fixed;
  document.getElementById('line-count').textContent = fixed.split('\n').length + ' lines';
  document.getElementById('fixed-area').style.display = 'none';
  document.getElementById('fix-status').textContent = '✓ Applied to editor';
}

async function reAnalyze() {
  currentCode = document.getElementById('fixed-code').value;
  document.getElementById('code-input').value = currentCode;
  await analyzeCode();
}

// ── Mod Builder ───────────────────────────────────────────────────────────────
document.getElementById('f-custom_music').addEventListener('change', function(){
  document.getElementById('music-row').style.display = this.checked ? '' : 'none';
});

function getBuilderCfg() {
  const maps = [
    document.getElementById('map-obj1').checked ? 'obj_team1' : null,
    document.getElementById('map-obj2').checked ? 'obj_team2' : null,
    document.getElementById('map-obj4').checked ? 'obj_team4' : null,
  ].filter(Boolean);
  const features = ['anticheat','server_hud','team_hud','welcome','killstreak','selfheal','koth','custom_music']
    .filter(f => document.getElementById('f-'+f).checked);
  return {
    mod_name:    document.getElementById('b-mod').value.trim()||'mymod',
    author:      document.getElementById('b-author').value.trim()||'Author',
    version:     document.getElementById('b-ver').value.trim()||'1.0',
    server_name: document.getElementById('b-srv').value.trim()||'My Server',
    allied_text: document.getElementById('b-allied').value.trim(),
    axis_text:   document.getElementById('b-axis').value.trim(),
    music_path:  document.getElementById('b-music').value.trim(),
    maps, features
  };
}

async function previewMod() {
  const cfg = getBuilderCfg();
  if (!cfg.maps.length) { alert('Select at least one map.'); return; }
  const btn = document.getElementById('preview-btn');
  btn.classList.add('loading');
  try {
    const r = await fetch('/api/build', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(cfg)});
    const data = await r.json();
    builtFiles = data.files;
    renderFileViewer(data);
  } finally { btn.classList.remove('loading'); }
}

async function downloadPk3() {
  const cfg = getBuilderCfg();
  if (!cfg.maps.length) { alert('Select at least one map.'); return; }
  const btn = document.getElementById('dl-btn');
  btn.classList.add('loading');
  try {
    const r = await fetch('/api/pk3', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(cfg)});
    if (!r.ok) { alert('Build failed.'); return; }
    const cd   = r.headers.get('Content-Disposition') || '';
    const name = (cd.match(/filename="?([^";\n]+)"?/) || [])[1] || 'mod.pk3';
    const blob = await r.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = name; a.click();
    URL.revokeObjectURL(url);
    const pr = await fetch('/api/build', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(cfg)});
    const pdata = await pr.json();
    builtFiles = pdata.files;
    renderFileViewer(pdata, true);
  } finally { btn.classList.remove('loading'); }
}

function renderFileViewer(data, downloaded=false) {
  const names = Object.keys(data.files);
  const badge = downloaded
    ? `<span style="color:var(--green);font-size:.75rem">&#11015; Downloaded: ${data.pkg_name}</span>`
    : `<span style="color:var(--gold);font-size:.75rem">${data.pkg_name}</span>`;
  let tabs = names.map((f,i) =>
    `<button class="ftab ${i===0?'active':''}" onclick="showFile('${CSS.escape(f)}',this)">${f.split('/').pop()}</button>`
  ).join('');
  let views = names.map((f,i) => `
    <div id="fv-${CSS.escape(f)}" class="file-view" style="${i===0?'':'display:none'}">
      <button class="copy-btn" onclick="copyFileContent('${CSS.escape(f)}')">Copy</button>
      <pre id="fc-${CSS.escape(f)}">${esc(data.files[f])}</pre>
    </div>`).join('');
  document.getElementById('builder-output').innerHTML = `
    <div class="pane-hdr">${badge}<span style="color:var(--muted);font-size:.72rem;margin-left:6px">${names.length} file(s)</span></div>
    <div class="file-tabs">${tabs}</div>
    ${views}`;
}

function showFile(name, btn) {
  document.querySelectorAll('.file-view').forEach(el => el.style.display='none');
  document.querySelectorAll('.ftab').forEach(t => t.classList.remove('active'));
  const fv = document.getElementById('fv-'+name);
  if (fv) fv.style.display = '';
  btn.classList.add('active');
}

function copyFileContent(name) {
  const el = document.getElementById('fc-'+name);
  if (!el) return;
  navigator.clipboard.writeText(el.textContent).then(() => {
    const btn = el.parentElement.querySelector('.copy-btn');
    btn.textContent='Copied!'; btn.classList.add('copied');
    setTimeout(()=>{btn.textContent='Copy';btn.classList.remove('copied');},1500);
  });
}

// ── Chat ──────────────────────────────────────────────────────────────────────
document.getElementById('chat-input').addEventListener('keydown', e => {
  if (e.key==='Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); }
});

function addMsg(role, html) {
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  div.innerHTML = html;
  document.getElementById('chat-messages').appendChild(div);
  div.scrollIntoView({behavior:'smooth'});
  return div;
}

function clearChat() {
  chatHistory = [];
  document.getElementById('chat-messages').innerHTML =
    `<div class="msg assistant"><strong>Chat cleared.</strong> Ask me anything about MOHAA modding.</div>`;
}

async function sendChat() {
  const input = document.getElementById('chat-input');
  const text  = input.value.trim();
  if (!text) return;
  input.value = '';
  input.style.height = '';

  chatHistory.push({role:'user', content: text});
  addMsg('user', esc(text).replace(/\n/g,'<br>'));

  const typingEl = addMsg('assistant',
    '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>');
  const btn = document.getElementById('send-btn');
  btn.disabled = true;

  try {
    const r = await fetch('/api/chat', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({messages: chatHistory})
    });
    if (r.status === 401) {
      typingEl.innerHTML = '<em style="color:var(--red)">API key required.</em>';
      checkKeyStatus(activeProv);
      chatHistory.pop();
      return;
    }
    const data = await r.json();
    if (data.error) {
      typingEl.innerHTML = `<em style="color:var(--red)">Error: ${esc(data.error)}</em>`;
      chatHistory.pop();
    } else {
      typingEl.innerHTML = renderMD(data.text);
      typingEl.scrollIntoView({behavior:'smooth'});
      chatHistory.push({role:'assistant', content: data.text});
    }
  } catch(e) {
    typingEl.innerHTML = `<em style="color:var(--red)">Network error: ${e.message}</em>`;
    chatHistory.pop();
  } finally {
    btn.disabled = false;
  }
}
</script>
</body>
</html>"""

# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = 5055
    url  = f"http://localhost:{port}"
    prov = get_provider()
    key  = get_key(prov)
    ref_kb = len(MOHAA_REFS) // 1024
    print(f"\n  MOHAA Mod Workshop v3")
    print(f"  Open: {url}")
    print(f"  Active provider: {PROVIDERS[prov]['name']} / {get_model()}")
    print(f"  API key ({prov}): {'OK' if key else 'NOT SET'}")
    print(f"  Reference docs loaded: {ref_kb} KB\n")
    threading.Timer(0.9, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)

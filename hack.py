#!/usr/bin/env python3
"""
I'm a hacker, mommy!  --  a Hollywood hacking console for Omarchy.

Reads the colours of whatever Omarchy theme is currently active and uses them
to do absolutely nothing of value in the most cinematic way possible.

    ./hack.py            full-speed drama
    ./hack.py --fast     same drama, less waiting
    ./hack.py --theme ~/.config/omarchy/themes/cyberdelia/colors.toml

Every command looks plausible right up until it finishes.
"""

import os
import random
import re
import shutil
import signal
import sys
import time
from pathlib import Path

try:
    import readline  # noqa: F401  (history + line editing at the prompt)
except ImportError:
    pass

# --------------------------------------------------------------------------
# palette
# --------------------------------------------------------------------------

THEME_PATH = Path.home() / ".local/state/omarchy/current/theme/colors.toml"

FALLBACK = {
    "accent": "#7fd7a3", "foreground": "#d0d0d0", "dark_foreground": "#8a8a8a",
    "bright_foreground": "#ffffff", "muted": "#555555", "background": "#000000",
    "red": "#ff5f5f", "yellow": "#ffd75f", "green": "#5fff87", "cyan": "#5fd7ff",
    "blue": "#5f87ff", "magenta": "#d787ff", "orange": "#ffaf5f",
    "bright_red": "#ff8787", "bright_green": "#87ffaf", "bright_cyan": "#87ffff",
    "bright_yellow": "#ffff87",
}

SPEED = 1.0
PALETTE = dict(FALLBACK)
THEME_NAME = "fallback"


def load_theme(path: Path) -> None:
    global THEME_NAME
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        m = re.match(r'\s*([a-z_]+)\s*=\s*"(#[0-9a-fA-F]{6})"', line)
        if m:
            PALETTE[m.group(1)] = m.group(2)
    first = text.lstrip().splitlines()[0] if text.strip() else ""
    if first.startswith("#"):
        THEME_NAME = first.lstrip("# ").strip()


def rgb(key: str):
    h = PALETTE.get(key, FALLBACK.get(key, "#ffffff")).lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def c(key: str, s: str, bold: bool = False) -> str:
    r, g, b = rgb(key)
    pre = "\x1b[1m" if bold else ""
    return f"{pre}\x1b[38;2;{r};{g};{b}m{s}\x1b[0m"


def cols() -> int:
    return max(60, shutil.get_terminal_size((80, 24)).columns)


# --------------------------------------------------------------------------
# timing + output helpers
# --------------------------------------------------------------------------

def nap(seconds: float) -> None:
    time.sleep(seconds * SPEED)


def out(s: str = "", delay: float = 0.0) -> None:
    print(s, flush=True)
    if delay:
        nap(delay)


def typewrite(s: str, key: str = "foreground", per_char: float = 0.012, end: str = "\n") -> None:
    for ch in s:
        sys.stdout.write(c(key, ch))
        sys.stdout.flush()
        nap(per_char * random.uniform(0.4, 1.6))
    sys.stdout.write(end)
    sys.stdout.flush()


def bar(label: str, seconds: float = 2.0, key: str = "accent", stall: bool = True) -> None:
    """A filling bar. Occasionally stalls at 99% for dramatic tension."""
    width = min(44, cols() - 40)
    steps = 60
    tick = seconds / steps
    label = label[:26].ljust(26)
    for i in range(steps + 1):
        pct = i / steps
        if stall and i == steps - 1 and random.random() < 0.6:
            nap(tick * 12)
        filled = int(width * pct)
        fill = c(key, "█" * filled) + c("muted", "░" * (width - filled))
        rate = f"{random.uniform(0.9, 9.9):.1f} {random.choice(['TB/s', 'GB/s', 'PB/s'])}"
        sys.stdout.write(f"\r  {c('dark_foreground', label)} {fill} {int(pct * 100):3d}%  {c('muted', rate)}")
        sys.stdout.flush()
        nap(tick * random.uniform(0.3, 1.7))
    sys.stdout.write("\r" + " " * (cols() - 1) + "\r")
    print(f"  {c('dark_foreground', label)} {c(key, '█' * width)} {c('green', '100%  OK')}", flush=True)


def spinner(label: str, seconds: float = 1.5) -> None:
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    end = time.monotonic() + seconds * SPEED
    i = 0
    while time.monotonic() < end:
        sys.stdout.write(f"\r  {c('accent', frames[i % len(frames)])} {c('foreground', label)}")
        sys.stdout.flush()
        time.sleep(0.07)
        i += 1
    sys.stdout.write("\r" + " " * (cols() - 1) + "\r")
    sys.stdout.flush()


# --------------------------------------------------------------------------
# convincing-looking nonsense
# --------------------------------------------------------------------------

def ip(dodgy: float = 0.15) -> str:
    """Mostly valid private addresses; sometimes an octet quietly overflows."""
    kind = random.choice(["10", "172", "192", "pub", "pub"])
    if kind == "10":
        parts = [10, random.randint(0, 255), random.randint(0, 255), random.randint(1, 254)]
    elif kind == "172":
        parts = [172, random.randint(16, 31), random.randint(0, 255), random.randint(1, 254)]
    elif kind == "192":
        parts = [192, 168, random.randint(0, 255), random.randint(1, 254)]
    else:
        parts = [random.choice([23, 45, 66, 91, 104, 141, 185, 203]), random.randint(0, 255),
                 random.randint(0, 255), random.randint(1, 254)]
    if random.random() < dodgy:
        parts[random.randint(1, 3)] = random.choice([256, 300, 512, 999])
    return ".".join(map(str, parts))


def cidr() -> str:
    return f"{ip(0.05)}/{random.choice([8, 16, 24, 24, 24, 27, 33, 42])}"


def port() -> str:
    return str(random.choice([21, 22, 23, 25, 53, 80, 110, 139, 443, 445, 1337, 3306, 3389,
                              4444, 8080, 8443, 31337, 65535, 65536, 70000]))


def mac() -> str:
    return ":".join(f"{random.randint(0, 255):02X}" for _ in range(6))


def hexword() -> str:
    return f"0x{random.getrandbits(32):08X}"


def hexdump_line() -> str:
    off = f"{random.randint(0x7F0000000000, 0x7FFFFFFFFFFF):012x}"
    data = [random.randint(0, 255) for _ in range(16)]
    hx = " ".join(f"{b:02x}" for b in data)
    asc = "".join(chr(b) if 32 <= b < 127 else "." for b in data)
    frag = random.choice(["", "", "", "PASSWD=", "root:x:0", "BEGIN RSA", "hunter2", "TODO fix", "SELECT *",
                          "pls no", "lol", "N0TAVIRUS"])
    if frag:
        asc = frag[:16].ljust(16, ".")
    return f"{c('muted', off)}  {c('dark_foreground', hx)}  {c('foreground', asc)}"


def hex_storm(lines: int = 12, per_line: float = 0.03) -> None:
    for _ in range(lines):
        out(hexdump_line())
        nap(per_line)


def matrix_rain(seconds: float = 1.2) -> None:
    glyphs = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄ0123456789ABCDEF<>/\\|=+*#@$%"
    end = time.monotonic() + seconds * SPEED
    w = cols() - 2
    while time.monotonic() < end:
        line = "".join(random.choice(glyphs) if random.random() < 0.35 else " " for _ in range(w))
        out(c(random.choice(["green", "bright_green", "accent", "muted"]), line))
        time.sleep(0.04)


NODE_NAMES = [
    "MAINFRAME-01", "CORE-ROUTER", "DMZ-GATEWAY", "AUTH-SRV-7", "VAULT", "BACKUP-NAS",
    "ICE-WALL", "SATLINK-UPLINK", "PROXY-CHAIN-3", "ORACLE-DB",
    # ...and then it falls apart
    "printer-that-jams", "smart-kettle", "Dans-iPhone", "LIVING-ROOM-TV", "roomba",
    "NOT-A-HONEYPOT", "steam-deck", "lightbulb-3", "old-laptop-dont-touch", "framework-13",
]

HOPS = [
    "Reykjavík, IS", "Lagos, NG", "Kuala Lumpur, MY", "Ulaanbaatar, MN", "Nuuk, GL",
    "Tristan da Cunha", "Svalbard, SJ", "Gallowgate, Glasgow", "a Tesco car park",
    "the ISS (transit)", "Slough, UK", "Milton Keynes roundabout 4", "an undersea cable, probably",
]

PASSWORDS = ["hunter2", "password1", "letmein", "Passw0rd!", "correcthorse", "admin", "qwerty123",
             "iloveyou", "changeme", "Summer2019"]

PLAINTEXTS = [
    ["milk", "eggs", "bread (the good one)", "cat food", "batteries AA", "ring mum"],
    ["Ingredients: 1 haggis, 1 neep, 3 tatties, butter (much)", "Boil neep + tatties, mash, add butter",
     "Heat haggis per packet. Do NOT pierce bag. Again.", "Serve with whisky and regret"],
    ["Reminder: the wifi password is on the fridge", "Reminder: the fridge password is on the wifi",
     "Reminder: stop writing reminders in encrypted files"],
    ["Q3 SECRET PLAN", "1. Have plan", "2. ???", "3. Profit", "4. Buy a nicer chair"],
]

FACE = [
    "  .-----.  ",
    " /  o o  \\ ",
    "|    ^    |",
    " \\  \\_/  / ",
    "  '-----'  ",
]


# --------------------------------------------------------------------------
# boot sequence
# --------------------------------------------------------------------------

BANNER = r"""
 ____  _        _    ____ _  __     ___ ____ _____
| __ )| |      / \  / ___| |/ /    |_ _/ ___| ____|
|  _ \| |     / _ \| |   | ' /_____ | | |   |  _|
| |_) | |___ / ___ \ |___| . \_____|| | |___| |___
|____/|_____/_/   \_\____|_|\_\    |___\____|_____|
"""


def boot() -> None:
    os.system("clear")
    for line in BANNER.splitlines():
        out(c("accent", line, bold=True))
        nap(0.04)
    out(c("dark_foreground", f"  intrusion suite v4.0.4-omarchy   theme: {THEME_NAME}   uid: {os.getlogin() if hasattr(os, 'getlogin') else 'root'}"))
    out()
    typewrite("> initialising black-ice runtime ...", "foreground")
    nap(0.3)
    for mod in ["quantum entropy pool", "ghost protocol stack", "zero-day cache", "ice breaker heuristics",
                "satellite handshake table", "neural packet sniffer"]:
        spinner(f"loading {mod}", random.uniform(0.3, 0.7))
        out(f"  {c('green', '✔')} {c('foreground', mod)}  {c('muted', hexword())}")
    out()
    bar("uplink handshake", 1.6, "cyan")
    bar("spoofing MAC " + mac(), 1.2, "yellow")
    bar("tunnelling via " + cidr(), 2.0, "accent")
    out()
    typewrite("> sweeping local segment for targets", "foreground")
    for _ in range(6):
        out(f"  {c('cyan', ip().ljust(17))} {c('muted', mac())}  {c('foreground', random.choice(NODE_NAMES).ljust(22))} "
            f"{c('dark_foreground', 'port ' + port())}")
        nap(0.12)
    out()
    out(c("green", "  CONNECTION ESTABLISHED.", bold=True) + c("dark_foreground", "  we are in.  (we were always in. this is your laptop.)"))
    out(c("muted", "  type 'help' for a list of commands that will not help."))
    out()


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------

def cmd_help(_args):
    rows = [
        ("scan [subnet]", "enumerate hosts on a target segment"),
        ("trace <ip>", "route-trace a target across the globe"),
        ("crack <target>", "brute-force credentials, one character at a time (as is tradition)"),
        ("decrypt <file>", "break military-grade encryption"),
        ("mainframe", "establish a backdoor into the mainframe"),
        ("firewall", "bypass the firewall"),
        ("satellite", "acquire a satellite"),
        ("enhance", "enhance"),
        ("gui", "build a GUI interface in Visual Basic"),
        ("override", "override"),
        ("ls / cat / whoami / sudo", "unix commands, allegedly"),
        ("exit", "wipe traces and disconnect"),
    ]
    out()
    for k, v in rows:
        out(f"  {c('accent', k.ljust(26))} {c('dark_foreground', v)}")
    out()


def cmd_scan(args):
    subnet = args[0] if args else cidr()
    typewrite(f"> scanning {subnet} ...", "foreground")
    bar("host discovery", 1.4, "cyan")
    bar("service fingerprint", 1.8, "cyan")
    out()
    found = random.sample(NODE_NAMES[:10], 4) + random.sample(NODE_NAMES[10:], 4)
    random.shuffle(found)
    for name in found:
        vuln = random.choice(["CRITICAL", "HIGH", "MEDIUM", "LOW", "none", "vibes"])
        key = {"CRITICAL": "red", "HIGH": "orange", "MEDIUM": "yellow"}.get(vuln, "muted")
        out(f"  {c('cyan', ip().ljust(17))} {c('foreground', name.ljust(24))} {c('dark_foreground', ('tcp/' + port()).ljust(11))} {c(key, vuln)}")
        nap(0.18)
    out()
    out(c("green", f"  {len(found)} hosts found.") + c("dark_foreground", "  8 of them are in this house. one of them is the kettle."))
    out()


def cmd_trace(args):
    target = args[0] if args else ip()
    typewrite(f"> tracing route to {target}, 30 hops max", "foreground")
    out()
    hops = random.sample(HOPS, 7)
    latency = 2.0
    for i, place in enumerate(hops, 1):
        latency *= random.uniform(1.4, 2.6)
        out(f"  {c('dark_foreground', f'{i:2d}')}  {c('cyan', ip(0.2).ljust(17))} {c('foreground', place.ljust(28))} {c('muted', f'{latency:8.1f} ms')}")
        nap(0.35)
    out(f"  {c('dark_foreground', f'{len(hops)+1:2d}')}  {c('yellow', '* * *'.ljust(17))} {c('muted', 'request timed out (someone unplugged it)')}")
    nap(0.6)
    out(f"  {c('dark_foreground', f'{len(hops)+2:2d}')}  {c('green', '127.0.0.1'.ljust(17))} {c('foreground', 'this laptop, this chair'.ljust(28))} {c('muted', '   0.001 ms')}")
    out()
    out(c("accent", "  TRACE COMPLETE. ") + c("dark_foreground", "the call is coming from inside the house. it was always going to be."))
    out()


def cmd_crack(args):
    target = args[0] if args else "AUTH-SRV-7"
    pw = random.choice(PASSWORDS)
    typewrite(f"> brute-forcing credentials on {target}", "foreground")
    bar("loading rainbow tables", 1.2, "magenta")
    out()
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%"
    locked = ""
    tries = 0
    for i in range(len(pw)):
        for _ in range(random.randint(8, 16)):
            tries += random.randint(90_000, 900_000)
            noise = "".join(random.choice(charset) for _ in range(len(pw) - i))
            sys.stdout.write(f"\r  {c('dark_foreground', 'key:')} {c('green', locked, bold=True)}{c('muted', noise)}   "
                             f"{c('dark_foreground', f'{tries:,} attempts')}")
            sys.stdout.flush()
            nap(0.04)
        locked += pw[i]
    sys.stdout.write("\r" + " " * (cols() - 1) + "\r")
    out(f"  {c('dark_foreground', 'key:')} {c('green', pw, bold=True)}   {c('dark_foreground', f'{tries:,} attempts')}")
    out()
    out(c("green", "  ACCESS GRANTED.", bold=True))
    nap(0.5)
    out(c("dark_foreground", "  note: password was also on a post-it under the keyboard. we checked that second."))
    out()


def cmd_decrypt(args):
    fname = args[0] if args else "classified.bin"
    lines = random.choice(PLAINTEXTS)
    typewrite(f"> decrypting {fname}  (AES-4096-QUANTUM, allegedly)", "foreground")
    bar("deriving key schedule", 1.0, "magenta")
    bar("collapsing waveforms", 1.6, "magenta")
    out()
    glyphs = "!@#$%^&*()_+-=[]{}|;:,.<>?/~0123456789ABCDEF"
    for text in lines:
        width = len(text)
        for step in range(width + 1):
            shown = text[:step] + "".join(random.choice(glyphs) for _ in range(width - step))
            sys.stdout.write(f"\r  {c('green', shown[:step])}{c('muted', shown[step:])}")
            sys.stdout.flush()
            nap(0.025)
        sys.stdout.write("\n")
        sys.stdout.flush()
    out()
    out(c("accent", "  PLAINTEXT RECOVERED. ") + c("dark_foreground", "it is not clear why this was encrypted."))
    out()


def cmd_mainframe(_args):
    typewrite("> establishing backdoor into MAINFRAME-01", "foreground")
    hex_storm(8)
    bar("negotiating ICE", 1.4, "red")
    bar("escalating privileges", 1.2, "orange")
    bar("root shell", 0.9, "green", stall=False)
    out()
    out(c("green", "  MAINFRAME ACCESS: GRANTED", bold=True))
    nap(0.6)
    out(c("dark_foreground", "  identifying hardware ..."))
    nap(0.8)
    out(f"  {c('foreground', 'model:')}    {c('cyan', 'Raspberry Pi 3 Model B+')}")
    out(f"  {c('foreground', 'role:')}     {c('cyan', 'Pi-hole + that one cron job nobody remembers writing')}")
    out(f"  {c('foreground', 'uptime:')}   {c('cyan', '412 days')}")
    out(f"  {c('foreground', 'sticker:')}  {c('cyan', chr(34) + 'DO NOT TOUCH' + chr(34) + ' (in Sharpie)')}")
    out()
    out(c("yellow", "  the mainframe is respectfully asking you to leave."))
    out()


def cmd_firewall(_args):
    typewrite("> probing perimeter firewall", "foreground")
    for _ in range(5):
        out(f"  {c('muted', 'SYN')} → {c('cyan', ip())}:{c('yellow', port())}   {c('red', random.choice(['DROP', 'REJECT', 'DROP', 'FILTERED']))}")
        nap(0.2)
    bar("fragmenting packets", 1.2, "yellow")
    bar("tunnelling over DNS", 1.4, "yellow")
    bar("asking nicely", 0.8, "green", stall=False)
    out()
    out(c("green", "  FIREWALL BYPASSED.", bold=True))
    nap(0.5)
    out(c("dark_foreground", "  post-mortem: it was ufw with zero rules. it was bypassed by walking through it."))
    out()


def cmd_satellite(_args):
    typewrite("> acquiring satellite uplink", "foreground")
    for name in ["KH-11 KEYHOLE", "NROL-39", "SENTINEL-2B", "GLONASS-K2"]:
        spinner(f"hailing {name}", random.uniform(0.5, 0.9))
        out(f"  {c('red', '✘')} {c('foreground', name)}  {c('muted', 'no response')}")
    spinner("hailing ISS", 0.9)
    out(f"  {c('green', '✔')} {c('foreground', 'ISS')}  {c('muted', 'responded')}")
    bar("satellite lock", 1.2, "cyan")
    out()
    out(c("green", "  SATELLITE ACQUIRED.", bold=True))
    nap(0.5)
    out(c("dark_foreground", "  incoming message: ") + c("foreground", "\"hi. please stop. we are trying to sleep up here.\""))
    out()


def cmd_enhance(_args):
    scale = getattr(cmd_enhance, "scale", 1) + 1
    cmd_enhance.scale = min(scale, 4)
    typewrite("> ENHANCE", "accent")
    spinner("upsampling", 0.8)
    for row in FACE:
        big = "".join(ch * cmd_enhance.scale for ch in row)
        for _ in range(cmd_enhance.scale):
            out("    " + c("cyan", big))
    out()
    out(c("dark_foreground", f"  resolution: unchanged.  size: {cmd_enhance.scale}x.  confidence: 100%.  face: still a face."))
    if cmd_enhance.scale == 4:
        out(c("yellow", "  maximum enhancement reached. the pixels have feelings too."))
    out()


def cmd_gui(_args):
    typewrite("> building GUI interface in Visual Basic to track the killer's IP", "foreground")
    bar("drawing buttons", 1.0, "blue")
    bar("adding a globe", 1.2, "blue")
    bar("making it spin", 0.9, "blue")
    out()
    out(f"  {c('foreground', 'killer IP:')}  {c('red', '127.0.0.1', bold=True)}")
    nap(0.5)
    out(c("dark_foreground", "  it's you. you're the killer. of productivity, specifically."))
    out()


def cmd_override(_args):
    typewrite("> OVERRIDE", "red")
    matrix_rain(1.0)
    out()
    out(c("green", "  OVERRIDE ACCEPTED.", bold=True))
    nap(0.4)
    out(c("dark_foreground", "  nothing was overridden. there was nothing to override. it felt good though."))
    out()


def cmd_ls(_args):
    files = [
        ("passwords.txt", "0 B"), ("passwords_FINAL.txt", "0 B"), ("passwords_FINAL_v2.txt", "1 B"),
        ("do_not_open.exe", "4.2 MB"), ("definitely_not_a_honeypot/", "-"), ("launch_codes.pdf", "corrupt"),
        ("todo.md", "88 KB"), ("core", "14 GB"),
    ]
    out()
    for name, size in files:
        key = "cyan" if name.endswith("/") else "foreground"
        out(f"  {c('muted', '-rw-r--r--')}  {c('dark_foreground', size.rjust(7))}  {c(key, name)}")
    out()


def cmd_cat(args):
    if not args:
        out(c("dark_foreground", "  cat: which file, exactly"))
        return
    name = args[0]
    if name.startswith("passwords"):
        nap(0.4)
        out(c("dark_foreground", "  (file is empty. it has always been empty. the passwords were inside us all along.)"))
    elif name.startswith("launch"):
        out(c("red", "  cat: launch_codes.pdf: input/output error (good)"))
    elif name.startswith("todo"):
        for line in ["- [ ] hack the planet", "- [x] hack the kettle", "- [ ] stop hacking the kettle", "- [ ] buy milk"]:
            out("  " + c("foreground", line))
    else:
        out(c("red", f"  cat: {name}: no such file or directory (it never existed. neither did we.)"))
    out()


def cmd_whoami(_args):
    nap(0.5)
    typewrite("  you are the one.", "accent")
    nap(0.3)
    out(c("dark_foreground", f"  ({os.environ.get('USER', 'root')}, apparently)"))
    out()


def cmd_sudo(_args):
    nap(0.4)
    out(c("yellow", "  we are already root. we have always been root. root is a state of mind."))
    out()


def cmd_rm(args):
    if "-rf" in args and "/" in args:
        out(c("red", "  nice try. deleting the internet requires the other laptop."))
    else:
        out(c("dark_foreground", "  rm: refusing to delete in this economy"))
    out()


def cmd_exit(_args):
    out()
    typewrite("> disconnecting", "foreground")
    bar("wiping traces", 1.0, "red", stall=False)
    bar("burning logs", 0.8, "red", stall=False)
    bar("forgetting everything", 0.6, "red", stall=False)
    out()
    out(c("dark_foreground", "  traces wiped. (your bash history is fine. so is your browser history. we didn't look.)"))
    out(c("accent", "  hack the planet.", bold=True))
    out()
    sys.exit(0)


COMMANDS = {
    "help": cmd_help, "?": cmd_help,
    "scan": cmd_scan, "nmap": cmd_scan,
    "trace": cmd_trace, "traceroute": cmd_trace,
    "crack": cmd_crack, "brute": cmd_crack,
    "decrypt": cmd_decrypt,
    "mainframe": cmd_mainframe,
    "firewall": cmd_firewall,
    "satellite": cmd_satellite, "uplink": cmd_satellite,
    "enhance": cmd_enhance,
    "gui": cmd_gui,
    "override": cmd_override,
    "ls": cmd_ls, "dir": cmd_ls,
    "cat": cmd_cat,
    "whoami": cmd_whoami,
    "sudo": cmd_sudo, "su": cmd_sudo,
    "rm": cmd_rm,
    "exit": cmd_exit, "quit": cmd_exit, "logout": cmd_exit,
}


def access_denied(word: str) -> None:
    for _ in range(3):
        sys.stdout.write("\r  " + c("red", "ACCESS DENIED", bold=True))
        sys.stdout.flush()
        nap(0.15)
        sys.stdout.write("\r" + " " * 20 + "\r")
        sys.stdout.flush()
        nap(0.1)
    out("  " + c("red", "ACCESS DENIED", bold=True) + c("dark_foreground", f"   ('{word}' isn't a thing. try 'help'.)"))
    out()


def counter_hack() -> None:
    """Someone is hacking us back. Classic. Two people, one keyboard."""
    out()
    for _ in range(4):
        out(c("red", "  ⚠  INTRUSION DETECTED  ⚠   INBOUND FROM " + ip(0.4), bold=True))
        nap(0.12)
    hex_storm(6, 0.02)
    out()
    out(c("yellow", "  they're in the system. two people need to type on this keyboard at once."))
    out(c("dark_foreground", "  (press enter when both of you are ready)"))
    try:
        input(c("red", "  >> "))
    except EOFError:
        pass
    bar("counter-intrusion", 1.2, "red", stall=False)
    out()
    out(c("green", "  THREAT NEUTRALISED.", bold=True))
    nap(0.4)
    out(c("dark_foreground", "  it was a Windows Update notification from the laptop in the other room."))
    out()


# --------------------------------------------------------------------------
# main loop
# --------------------------------------------------------------------------

def on_sigint(_sig, _frame):
    out()
    out(c("red", "  SIGINT intercepted. they're onto us. pulling the plug."))
    out()
    sys.exit(130)


def main() -> None:
    global SPEED
    args = sys.argv[1:]
    if "--fast" in args:
        SPEED = 0.2
    if "--theme" in args:
        load_theme(Path(args[args.index("--theme") + 1]).expanduser())
    else:
        load_theme(THEME_PATH)
    signal.signal(signal.SIGINT, on_sigint)

    boot()
    n = 0
    while True:
        try:
            line = input(c("accent", "black-ice", bold=True) + c("muted", " ▸ "))
        except EOFError:
            cmd_exit([])
        parts = line.strip().split()
        if not parts:
            continue
        n += 1
        word, rest = parts[0].lower(), parts[1:]
        fn = COMMANDS.get(word)
        if fn:
            fn(rest)
        else:
            access_denied(word)
        if n == 4 or (n > 4 and random.random() < 0.08):
            counter_hack()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import sys
import json
import os
import subprocess
import threading

PID_FILE = os.path.expanduser("~/.config/i3/sleep-inhibit.pid")

# Catppuccin Mocha, as in ~/.config/i3/config.
MANTLE, SURFACE0, TEXT = "#181825", "#313244", "#cdd6f4"
PEACH, OVERLAY0 = "#fab387", "#6c7086"

# Nerd Font glyphs: the rounded powerline caps, the two sleep-mode icons, then a keyboard.
# Their spans name ICON_FONT, so they keep its metrics while the value uses the bar's font.
ICON_FONT = "Hack Nerd Font"
# The caps are sized to the line height Noto Sans sets, as explained in ~/.config/i3status/config.
CAP_SIZE = "size='15000' rise='-250' line_height='0.5'"
LEFT_CAP, RIGHT_CAP = "", ""
COFFEE, SLEEP = "\U000f0176", "\U000f04b2"
KEYBOARD = "\U000f030c"

# The keyboard block runs this report. It reads the keyboard's state from the kernel and resets the
# keyboard driver, so it runs as root through a sudoers rule that needs no password.
KBD_STUCK_REPORT = ["sudo", "-n", "/usr/local/sbin/kbd-stuck-report"]

# Every write to stdout holds this lock, because a click redraws the bar from the click thread.
output_lock = threading.Lock()
last_blocks = None
kbd_report_running = False


def pill(color, icon, value):
    """Render a block the way ~/.config/i3status/config does: a colored icon cap, then the value."""
    return (
        f"<span font_family='{ICON_FONT}' {CAP_SIZE} foreground='{color}'>{LEFT_CAP}</span>"
        f"<span font_family='{ICON_FONT}' background='{color}' foreground='{MANTLE}'>{icon} </span>"
        f"<span background='{SURFACE0}' foreground='{TEXT}'> {value}</span>"
        f"<span font_family='{ICON_FONT}' {CAP_SIZE} foreground='{SURFACE0}'>{RIGHT_CAP}</span>"
    )


def sleep_block():
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        inhibited = True
    except (FileNotFoundError, ProcessLookupError, ValueError, OSError):
        inhibited = False

    if inhibited:
        text = pill(PEACH, COFFEE, "Insomniac")
    else:
        text = pill(OVERLAY0, SLEEP, "Circadian")

    return {"name": "sleep_mode", "markup": "pango", "full_text": text}


def kbd_block():
    if kbd_report_running:
        text = pill(PEACH, KEYBOARD, "Unsticking")
    else:
        text = pill(OVERLAY0, KEYBOARD, "Unstick")
    return {"name": "kbd_stuck", "markup": "pango", "full_text": text}


def write_blocks(blocks, prefix):
    """Write one status line to i3bar, with the wrapper's own blocks before the last one."""
    blocks = blocks[:-1] + [kbd_block(), sleep_block()] + blocks[-1:]
    # The pills' rounded caps already separate the blocks, so i3bar draws no separator line.
    for block in blocks:
        block["separator"] = False
        block["separator_block_width"] = 6
    sys.stdout.write(f"{prefix}{json.dumps(blocks)}\n")
    sys.stdout.flush()


def redraw():
    """Write the last status line again, so a change to the wrapper's blocks shows at once."""
    with output_lock:
        if last_blocks is not None:
            write_blocks(last_blocks, ",")


def notify(body):
    subprocess.run(["notify-send", "Stuck keyboard", body])


def run_kbd_report():
    global kbd_report_running
    kbd_report_running = True
    redraw()
    notify("Press keys and push the red TrackPoint nub for 5 seconds")
    result = subprocess.run(KBD_STUCK_REPORT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode == 0:
        notify("Report done: journalctl -t kbd-stuck-report")
    else:
        notify(f"The report failed with exit code {result.returncode}: journalctl -t kbd-stuck-report")
    kbd_report_running = False
    redraw()


def read_clicks():
    """Read the click events i3bar writes to stdin: a `[`, then one JSON object per line."""
    for line in sys.stdin:
        stripped = line.strip().lstrip(",")
        if not stripped.startswith("{"):
            continue
        click = json.loads(stripped)
        # A second click while the report runs would only restart the 5 s sample, so it is ignored.
        if click.get("name") == "kbd_stuck" and not kbd_report_running:
            threading.Thread(target=run_kbd_report, daemon=True).start()


def main():
    global last_blocks
    # i3status gets no stdin, so the click events reach only this wrapper.
    i3status = subprocess.Popen(["i3status"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, text=True)

    # Ask i3bar for click events in the version header, then pass the opening bracket through.
    header = json.loads(next(i3status.stdout))
    header["click_events"] = True
    sys.stdout.write(json.dumps(header) + "\n")
    sys.stdout.write(next(i3status.stdout))
    sys.stdout.flush()

    threading.Thread(target=read_clicks, daemon=True).start()

    for line in i3status.stdout:
        stripped = line.strip()
        if not stripped:
            continue
        prefix = "," if stripped.startswith(",") else ""
        with output_lock:
            last_blocks = json.loads(stripped.lstrip(","))
            write_blocks(last_blocks, prefix)


main()

#!/usr/bin/python3
"""Rebuild the project workspaces after a restart.

For each project, starts a Ghostty running `zellij attach --create SESSION` in the project's
directory. zellij resurrects a saved session of that name or creates a new one. zellij puts the
session name at the start of the window title, which is how this script finds the window and
moves it to the project's workspace.

A LibreWolf window whose title starts with `[LABEL]`, as the Window Titler extension sets it, is
moved to the workspace whose name ends in LABEL. That workspace is a project's or one of
BROWSER_WORKSPACES.

Each workspace gets the layout it has by hand: the Ghostty in one tab, and every LibreWolf window
on the workspace side by side in a second tab.
"""

import json
import os
import subprocess
import time
from pathlib import Path

HOME = Path.home()

# workspace, session, directory
PROJECTS = [
    ("2: OCPI Tariffs", "ocpi-tariffs", HOME / "projects/ds/ocpi-tariffs"),
    ("3: Thus", "thus-spoke-claude", HOME / "projects/ds/thus-spoke-claude"),
    ("4: Tan", "tandemdrive", HOME / "projects/ds/tandemdrive"),
    ("5: Tuig", "tuig", HOME / "projects/ds/tuig"),
]

# Workspaces that hold only LibreWolf windows, with no zellij session.
BROWSER_WORKSPACES = ["1: Office"]

TERMINAL_CLASS = "com.mitchellh.ghostty"
# The test run puts other windows in the browser's place.
BROWSER_CLASS = os.environ.get("RESTORE_BROWSER_CLASS", "librewolf")

# Windows appear over several seconds, and LibreWolf restores its windows late.
SECONDS_TO_WAIT = 30


def i3(*command):
    subprocess.run(["i3-msg", "-q", *command], check=False)


def tree():
    output = subprocess.run(
        ["i3-msg", "-t", "get_tree"], capture_output=True, text=True, check=True
    ).stdout
    return json.loads(output)


def windows(node, workspace=None, parent=None):
    """Yields (window, workspace name, parent container) for every window in the tree."""
    if node.get("type") == "workspace":
        workspace = node["name"]
    if node.get("window") is not None:
        yield node, workspace, parent
    for child in node.get("nodes", []) + node.get("floating_nodes", []):
        yield from windows(child, workspace, node)


def window_class(window):
    return (window.get("window_properties") or {}).get("class")


def running_sessions():
    output = subprocess.run(
        ["zellij", "list-sessions", "--no-formatting"], capture_output=True, text=True
    ).stdout
    return {line.split()[0] for line in output.splitlines() if line and "EXITED" not in line}


def target_workspace(window):
    """The workspace a window belongs on, or None when the script leaves it where it is."""
    title = window.get("name") or ""
    if window_class(window) == TERMINAL_CLASS:
        for workspace, session, _ in PROJECTS:
            # zellij writes only the session name until a pane sets a title of its own.
            if title == session or title.startswith(f"{session} "):
                return workspace
    if window_class(window) == BROWSER_CLASS:
        for workspace in browser_workspaces():
            label = workspace.split(": ", 1)[1]
            if title.startswith(f"[{label}]"):
                return workspace
    return None


def browser_workspaces():
    return [workspace for workspace, _, _ in PROJECTS] + BROWSER_WORKSPACES


def name_numbered_workspaces():
    """Renames a workspace named only by its number, such as the `1` i3 opens at login, to the
    full name of the workspace with that number. Otherwise `$mod+1` would go to the bare `1`
    rather than to `1: Office`."""
    output = subprocess.run(
        ["i3-msg", "-t", "get_workspaces"], capture_output=True, text=True, check=True
    ).stdout
    existing = {workspace["name"] for workspace in json.loads(output)}
    for workspace in browser_workspaces():
        number = workspace.split(": ", 1)[0]
        if number in existing and workspace not in existing:
            i3(f'rename workspace "{number}" to "{workspace}"')


def move_windows():
    for window, workspace, _ in windows(tree()):
        target = target_workspace(window)
        if target is None or target == workspace:
            continue
        i3(f'[con_id={window["id"]}] move to workspace "{target}"')


def put_browsers_side_by_side(workspace):
    """Puts every browser window on the workspace in one horizontal split, in one tab."""
    browsers = [
        (window, parent)
        for window, window_workspace, parent in windows(tree())
        if window_workspace == workspace and window_class(window) == BROWSER_CLASS
    ]
    if len(browsers) < 2:
        return

    # A browser window already in a split is the anchor the others join, so a second run of the
    # script leaves the layout as it is.
    in_a_split = [b for b in browsers if b[1]["layout"] in ("splith", "splitv")]
    anchor, anchor_parent = in_a_split[0] if in_a_split else browsers[0]
    if not in_a_split:
        i3(f"[con_id={anchor['id']}] split h")

    mark = f"restore_{anchor['id']}"
    i3(f"[con_id={anchor['id']}] mark {mark}")
    for window, parent in browsers:
        if window is anchor or (in_a_split and parent["id"] == anchor_parent["id"]):
            continue
        i3(f"[con_id={window['id']}] move to mark {mark}")
    i3(f"[con_id={anchor['id']}] unmark {mark}")


def main():
    if subprocess.run(["pgrep", "-x", "librewolf"], capture_output=True).returncode != 0:
        subprocess.Popen(["librewolf"], start_new_session=True)

    running = running_sessions()
    for _, session, directory in PROJECTS:
        # A running session presumably has a window already, so a second run opens none.
        if session in running:
            continue
        subprocess.Popen(
            ["ghostty", f"--working-directory={directory}", "-e", "zellij", "attach", "--create", session],
            start_new_session=True,
        )

    for _ in range(SECONDS_TO_WAIT):
        time.sleep(1)
        name_numbered_workspaces()
        move_windows()
        for workspace in browser_workspaces():
            put_browsers_side_by_side(workspace)


if __name__ == "__main__":
    main()

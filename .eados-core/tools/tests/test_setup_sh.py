#!/usr/bin/env python3
"""Behavioral smoke for setup.sh + install.command — the M9.2 guided (interactive) installer.

setup.sh is the Q&A wrapper around the 9.1 engine (install.sh); install.command is the macOS
double-click shim that delegates to it. Driven through a POSIX shell (`sh`, falling back to
`bash`) with prompts fed on stdin, this asserts the interactive logic: new-vs-existing routing,
the required-name re-prompt, the confirm/abort gate, that the plan is shown via the engine, and —
end to end and OFFLINE via the engine's `--from` seam — that a NEW repo is extracted AND
git-inited while an EXISTING one is only extracted (no git init). No network is touched.

    python .eados-core/tools/tests/test_setup_sh.py
"""

import hashlib
import io
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(os.path.dirname(TOOLS))
INSTALL_DIR = os.path.join(REPO_ROOT, "install")
SETUP_SH = os.path.join(INSTALL_DIR, "setup.sh")
COMMAND = os.path.join(INSTALL_DIR, "install.command")

SHELL = shutil.which("sh") or shutil.which("bash")
HAVE_GIT = shutil.which("git") is not None


def check(label, cond, failures):
    if not cond:
        failures.append(label)


def run(script, *args, cwd=None, stdin=""):
    """Run a script via the POSIX shell with `stdin` fed to its prompts; return (rc, out, err).
    The filesystem cases pass cwd + RELATIVE paths so they work on POSIX and Git Bash alike (a
    drive path like C:/x trips GNU tar)."""
    proc = subprocess.run([SHELL, script.replace("\\", "/"), *args],
                          capture_output=True, text=True, cwd=cwd, input=stdin)
    return proc.returncode, proc.stdout, proc.stderr


def make_bundle(path):
    """Write a tiny prefix-less .tar.gz fixture (the agent contract + a factory file)."""
    with tarfile.open(path, "w:gz") as tar:
        for name, body in (("AGENTS.md", b"# agent contract\n"),
                           (".eados-core/tools/render.py", b"# render\n")):
            entry = tarfile.TarInfo(name)
            entry.size = len(body)
            tar.addfile(entry, io.BytesIO(body))


def main():
    failures = []

    if SHELL is None:
        print("test-setup-sh: SKIP — no POSIX shell (sh / bash) on PATH")
        return 0
    for needed in (SETUP_SH, COMMAND):
        if not os.path.exists(needed):
            print(f"test-setup-sh: FAIL — not found: {needed}")
            return 1

    # --help
    rc, out, _ = run(SETUP_SH, "--help")
    check("setup.sh --help exits 0", rc == 0, failures)
    check("…shows usage + flags", "USAGE" in out and "--dry-run" in out and "--no-gh" in out,
          failures)

    # install.command delegates to setup.sh (the double-click shim)
    rc, out, _ = run(COMMAND, "--help")
    check("install.command --help delegates to setup.sh", rc == 0 and "USAGE" in out, failures)

    # dry-run, existing: routes to existing mode + the chosen path, shows the plan, no writes
    rc, out, err = run(SETUP_SH, "--dry-run", stdin="2\n/srv/myrepo\ny\n")
    blob = out + err
    check("dry-run existing exits 0", rc == 0, failures)
    check("…resolves existing mode + path (via the engine plan)",
          "existing" in blob and "/srv/myrepo" in blob, failures)
    check("…and only reports a dry-run (no real run)", "dry-run" in blob.lower(), failures)

    # dry-run, new: routes to new mode + <parent>/<name>
    rc, out, err = run(SETUP_SH, "--dry-run", stdin="1\n/opt\nproj\ny\n")
    blob = out + err
    check("dry-run new exits 0", rc == 0, failures)
    check("…resolves new mode + <parent>/<name> target", "/opt/proj" in blob, failures)
    check("…would git-init the new target", "git" in blob.lower() and "/opt/proj" in blob, failures)

    # a new repo requires a non-empty name (the re-prompt loop)
    rc, out, err = run(SETUP_SH, "--dry-run", stdin="1\n.\n\ncoolproj\ny\n")
    blob = out + err
    check("an empty new-repo name re-prompts, then accepts a name", rc == 0 and "coolproj" in blob,
          failures)

    # confirm gate: answering no aborts and writes nothing
    rc, out, err = run(SETUP_SH, "--dry-run", stdin="2\n.\nn\n")
    check("answering 'n' at the confirm aborts (exit 0)", rc == 0, failures)
    check("…with an 'aborted' message", "abort" in (out + err).lower(), failures)

    with tempfile.TemporaryDirectory() as tmp:
        make_bundle(os.path.join(tmp, "bundle.tar.gz"))  # relative "bundle.tar.gz" under cwd=tmp

        # end-to-end NEW (offline via --from): the engine extracts AND setup git-inits the target
        rc, out, err = run(SETUP_SH, "--no-gh", "--", "--from", "bundle.tar.gz", "--no-verify",
                           cwd=tmp, stdin="1\nparent\nproj\ny\n")
        target = os.path.join(tmp, "parent", "proj")
        check("e2e new install exits 0", rc == 0, failures)
        check("…extracted the bundle into <parent>/<name>",
              os.path.exists(os.path.join(target, "AGENTS.md")), failures)
        if HAVE_GIT:
            check("…and git-inited the new repo", os.path.isdir(os.path.join(target, ".git")),
                  failures)

        # end-to-end EXISTING (offline): extracts into the existing dir, does NOT git init
        os.mkdir(os.path.join(tmp, "ex"))
        rc, out, err = run(SETUP_SH, "--", "--from", "bundle.tar.gz", "--no-verify",
                           cwd=tmp, stdin="2\nex\ny\n")
        check("e2e existing install exits 0", rc == 0, failures)
        check("…extracted the bundle into the existing dir",
              os.path.exists(os.path.join(tmp, "ex", "AGENTS.md")), failures)
        check("…and did NOT git-init an existing repo",
              not os.path.isdir(os.path.join(tmp, "ex", ".git")), failures)

    if failures:
        print("test-setup-sh: FAIL\n")
        for f in failures:
            print(f"  {f}")
        print(f"\n{len(failures)} expectation(s) failed.")
        return 1
    print("test-setup-sh: OK — new/existing routing, required-name re-prompt, the confirm/abort "
          "gate, and offline e2e (new=extract+git-init, existing=extract-only) all hold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

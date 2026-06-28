#!/usr/bin/env python3
"""Behavioral smoke for install.sh — the M9.1 guided-installer core (POSIX engine).

Drives the script through a POSIX shell (`sh`, falling back to `bash`) and asserts the PURE CORE:
plan resolution (`--print-plan`: the URL + target, no network / disk), argument validation,
fail-closed checksum verification, and ADDITIVE extraction (it refuses to overwrite an existing
file) — all offline via the `--from <local bundle>` seam, so CI never touches the network. The
shellcheck static-analysis gate and the PowerShell (`.ps1`) equivalent land in M9.5 / M9.3.

    python .eados-core/tools/tests/test_install_sh.py
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
INSTALL_SH = os.path.join(REPO_ROOT, "install", "install.sh")

SHELL = shutil.which("sh") or shutil.which("bash")


def check(label, cond, failures):
    if not cond:
        failures.append(label)


def run(*args, cwd=None):
    """Run install.sh with args; return (returncode, stdout, stderr). The filesystem cases pass
    `cwd` + RELATIVE paths so they work identically on POSIX and Git Bash — a drive path like
    C:/x trips GNU tar (it reads the colon as a `host:path` remote spec). Only the script path is
    forward-slashed (it loads fine on both)."""
    proc = subprocess.run([SHELL, INSTALL_SH.replace("\\", "/"), *args],
                          capture_output=True, text=True, cwd=cwd)
    return proc.returncode, proc.stdout, proc.stderr


def make_bundle(path):
    """Write a tiny prefix-less .tar.gz fixture (the agent contract + a factory file) and return
    its sha256 hex — shaped like the real bundle (contents at the top level)."""
    with tarfile.open(path, "w:gz") as tar:
        for name, body in (("AGENTS.md", b"# agent contract\n"),
                           (".eados-core/tools/render.py", b"# render\n")):
            entry = tarfile.TarInfo(name)
            entry.size = len(body)
            tar.addfile(entry, io.BytesIO(body))
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    failures = []

    if SHELL is None:
        print("test-install-sh: SKIP — no POSIX shell (sh / bash) on PATH")
        return 0
    if not os.path.exists(INSTALL_SH):
        print(f"test-install-sh: FAIL — install.sh not found at {INSTALL_SH}")
        return 1

    # --help
    rc, out, _ = run("--help")
    check("--help exits 0", rc == 0, failures)
    check("--help shows usage + key flags",
          "USAGE" in out and "--mode" in out and "--print-plan" in out, failures)

    # plan: latest -> the stable /latest/download/ URL, no network / disk
    rc, out, _ = run("--print-plan")
    check("--print-plan exits 0", rc == 0, failures)
    check("plan (default) uses the latest-download URL",
          "releases/latest/download/pgs-eados-bundle.tar.gz" in out, failures)
    check("plan (default) is mode existing, target .",
          "existing" in out and "target:" in out, failures)
    check("plan (default) repo is danielPoloWork/pgs-eados",
          "danielPoloWork/pgs-eados" in out, failures)

    # plan: pinned --ref -> the tagged download URL
    rc, out, _ = run("--print-plan", "--ref", "v2.2.0")
    check("plan --ref uses the tagged download URL",
          "releases/download/v2.2.0/pgs-eados-bundle.tar.gz" in out, failures)

    # plan: --mode new -> target is <path>/<repo-name>
    rc, out, _ = run("--print-plan", "--mode", "new", "--path", "/tmp/x", "--repo-name", "proj")
    check("plan --mode new resolves target <path>/<name>", "/tmp/x/proj" in out, failures)

    # plan: --repo override flows into the URL
    rc, out, _ = run("--print-plan", "--repo", "octo/fork")
    check("plan --repo override flows into the URL", "github.com/octo/fork/" in out, failures)

    # --mode new without --repo-name -> a clear error
    rc, out, err = run("--mode", "new")
    check("--mode new without --repo-name fails", rc != 0, failures)
    check("…with a message naming repo-name", "repo-name" in (err + out), failures)

    # an invalid --mode -> error
    rc, _, _ = run("--mode", "sideways", "--print-plan")
    check("an invalid --mode fails", rc != 0, failures)

    with tempfile.TemporaryDirectory() as tmp:
        good_sha = make_bundle(os.path.join(tmp, "bundle.tar.gz"))  # relative "bundle.tar.gz" under tmp
        seq = [0]

        def fresh_target():
            """Make an empty target dir under tmp; return its relative name (resolved against cwd=tmp)."""
            seq[0] += 1
            name = f"t{seq[0]}"
            os.mkdir(os.path.join(tmp, name))
            return name

        # additive success: empty target, checksum pinned
        tgt = fresh_target()
        rc, _, _ = run("--from", "bundle.tar.gz", "--sha256", good_sha,
                       "--mode", "existing", "--path", tgt, cwd=tmp)
        check("additive install into an empty target succeeds", rc == 0, failures)
        check("…extracted the agent contract",
              os.path.exists(os.path.join(tmp, tgt, "AGENTS.md")), failures)
        check("…extracted the factory file",
              os.path.exists(os.path.join(tmp, tgt, ".eados-core", "tools", "render.py")), failures)

        # additive refusal: a pre-existing file is never clobbered (and nothing partial is written)
        tgt = fresh_target()
        with open(os.path.join(tmp, tgt, "AGENTS.md"), "w", encoding="utf-8") as fh:
            fh.write("ORIGINAL")
        rc, out, err = run("--from", "bundle.tar.gz", "--no-verify",
                           "--mode", "existing", "--path", tgt, cwd=tmp)
        check("install refuses to overwrite an existing file", rc != 0, failures)
        check("…names the conflicting file", "AGENTS.md" in (err + out), failures)
        with open(os.path.join(tmp, tgt, "AGENTS.md"), encoding="utf-8") as fh:
            kept = fh.read() == "ORIGINAL"
        check("…leaves the existing file untouched", kept, failures)
        check("…and extracts nothing (no partial write)",
              not os.path.exists(os.path.join(tmp, tgt, ".eados-core", "tools", "render.py")), failures)

        # checksum verification: a wrong --sha256 fails
        tgt = fresh_target()
        rc, out, err = run("--from", "bundle.tar.gz", "--sha256", "deadbeef",
                           "--mode", "existing", "--path", tgt, cwd=tmp)
        check("a wrong --sha256 fails (checksum mismatch)", rc != 0, failures)
        check("…with a 'mismatch' message", "mismatch" in (err + out).lower(), failures)

        # fail-closed: no checksum source and no --no-verify -> refuse, extract nothing
        tgt = fresh_target()
        rc, out, err = run("--from", "bundle.tar.gz", "--mode", "existing", "--path", tgt, cwd=tmp)
        check("fail-closed: refuses to extract unverified", rc != 0, failures)
        check("…extracts nothing when unverified",
              not os.path.exists(os.path.join(tmp, tgt, "AGENTS.md")), failures)

        # a missing local bundle -> a clean error, no crash
        tgt = fresh_target()
        rc, out, err = run("--from", "nope.tar.gz", "--no-verify",
                           "--mode", "existing", "--path", tgt, cwd=tmp)
        check("a missing --from bundle fails cleanly", rc != 0, failures)
        check("…with a 'not found' message", "not found" in (err + out).lower(), failures)

        # existing mode requires the target dir to already exist
        rc, _, _ = run("--from", "bundle.tar.gz", "--no-verify",
                       "--mode", "existing", "--path", "absent-dir", cwd=tmp)
        check("existing mode requires the target dir to exist", rc != 0, failures)

        # --- M9.4: verify against a SHA256SUMS file, in the format release.yml publishes ---
        # The release attaches a `sha256sum` SHA256SUMS over every asset; --sums-file verifies the
        # bundle against it offline. The bundle must be named pgs-eados-bundle.tar.gz (the name the
        # installer looks up). The file written below is exactly `sha256sum`'s text output.
        real = "pgs-eados-bundle.tar.gz"
        real_sha = make_bundle(os.path.join(tmp, real))
        with open(os.path.join(tmp, "SHA256SUMS"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(f"{real_sha}  {real}\n")
            fh.write(f"{'0' * 64} *pgs-eados-bundle.zip\n")   # '*' (binary) form must be stripped
            fh.write(f"{'1' * 64}  install.sh\n")

        tgt = fresh_target()
        rc, out, err = run("--from", real, "--sums-file", "SHA256SUMS",
                           "--mode", "existing", "--path", tgt, cwd=tmp)
        check("verify via --sums-file succeeds (picks the bundle line)", rc == 0, failures)
        check("…extracted the bundle", os.path.exists(os.path.join(tmp, tgt, "AGENTS.md")), failures)

        with open(os.path.join(tmp, "BAD_SUMS"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(f"{'a' * 64}  {real}\n")
        tgt = fresh_target()
        rc, out, err = run("--from", real, "--sums-file", "BAD_SUMS",
                           "--mode", "existing", "--path", tgt, cwd=tmp)
        check("a tampered --sums-file fails (mismatch)",
              rc != 0 and "mismatch" in (out + err).lower(), failures)

        with open(os.path.join(tmp, "NOENTRY"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(f"{'b' * 64}  some-other-file.txt\n")
        tgt = fresh_target()
        rc, out, err = run("--from", real, "--sums-file", "NOENTRY",
                           "--mode", "existing", "--path", tgt, cwd=tmp)
        check("a --sums-file lacking the bundle entry fails ('no entry')",
              rc != 0 and "no entry" in (out + err).lower(), failures)

        tgt = fresh_target()
        rc, out, err = run("--from", real, "--sums-file", "missing-sums",
                           "--mode", "existing", "--path", tgt, cwd=tmp)
        check("a missing --sums-file fails cleanly",
              rc != 0 and "not found" in (out + err).lower(), failures)

    if failures:
        print("test-install-sh: FAIL\n")
        for f in failures:
            print(f"  {f}")
        print(f"\n{len(failures)} expectation(s) failed.")
        return 1
    print("test-install-sh: OK — plan resolution, arg validation, fail-closed checksum, and "
          "additive (no-clobber) extraction all hold; offline via --from.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

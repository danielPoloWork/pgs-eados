#!/bin/sh
# install.sh — guided-installer CORE (POSIX): download the EADOS factory bundle and place it
# additively at a target repo root.  Milestone 9 (guided installer), item 9.1.
#
# SCOPE.  "install" = bundle download + placement only (the consumer step of USAGE §6) — NOT the
# agentic-OS init (interview / generate).  This is the NON-INTERACTIVE engine: the interactive Q&A
# wrapper (new-vs-existing repo, git init) and the double-clickable macOS `.command` land in 9.2;
# the PowerShell equivalent in 9.3.
#
# WHAT IT DOES.  Downloads `pgs-eados-bundle.tar.gz` from a GitHub release, VERIFIES its SHA256
# (fail-closed — it refuses to extract an unverified bundle unless `--no-verify`), and extracts it
# ADDITIVELY: it refuses to overwrite any existing file (the ADR-0007 no-clobber principle).  A
# side-effect-free `--print-plan` (resolve the URL + target without touching the network or disk)
# and a `--from <file>` local-bundle seam keep the core testable and let it degrade cleanly offline
# (the derive_links.py pattern).
#
# Strict POSIX sh — no bashisms — so it runs under dash / ash / bash and the double-click wrappers.

set -eu

PROG=install.sh
BUNDLE_NAME=pgs-eados-bundle.tar.gz
SUMS_NAME=SHA256SUMS
DEFAULT_REPO=danielPoloWork/pgs-eados

# --- output helpers --------------------------------------------------------
fail()    { _code=$1; shift; printf '%s: error: %s\n' "$PROG" "$*" >&2; exit "$_code"; }
die()     { fail 1 "$@"; }                # user / safety error
offline() { fail 2 "$@"; }                # environmental: offline / asset unavailable
warn()    { printf '%s: warning: %s\n' "$PROG" "$*" >&2; }
info()    { printf '%s\n' "$*"; }

usage() {
  cat <<'EOF'
install.sh — download the EADOS factory bundle into a repo (download + placement only).

USAGE
  install.sh [options]

WHERE TO INSTALL
  --mode new|existing   install into a new repo dir or an existing one      (default: existing)
  --path DIR            target repo root (existing), or parent dir (new)    (default: .)
  --repo-name NAME      name of the new repo dir under --path               (required for --mode new)

WHICH BUNDLE
  --ref REF             release tag to install, e.g. v2.2.0                 (default: latest)
  --repo OWNER/REPO     source GitHub repo                                  (default: danielPoloWork/pgs-eados)
  --from FILE           install from a local bundle file (skip download; air-gapped / testing)
  --bundle-url URL      download the bundle from this exact URL (overrides --ref / --repo)

INTEGRITY (fail-closed: refuses to extract an unverified bundle)
  --sha256 HEX          expected SHA256 of the bundle (else read from the release SHA256SUMS)
  --sums-file FILE      verify against a local SHA256SUMS file (skip the download; air-gapped)
  --no-verify           skip checksum verification (loudly; not recommended)

OTHER
  --print-plan          print the resolved plan and exit (no download, no writes)
  -h, --help            this help

The bundle is extracted ADDITIVELY at the target root: it refuses to overwrite any existing file.
EOF
}

# --- side-effecting helpers ------------------------------------------------
download() {  # $1 url  $2 dest ; non-zero on failure (caller decides)
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$1" -o "$2"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$2" "$1"
  else
    die "need curl or wget to download (or use --from <file>)"
  fi
}

sha256_of() {  # $1 file ; prints the bare hex on stdout, non-zero if no tool is available
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1; exit}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1; exit}'
  elif command -v openssl >/dev/null 2>&1; then
    openssl dgst -sha256 "$1" | awk '{print $NF; exit}'
  else
    return 3
  fi
}

# --- defaults --------------------------------------------------------------
mode=existing
path=.
repo_name=
ref=latest
repo=$DEFAULT_REPO
from=
bundle_url_override=
expected_sha=
sums_file=
no_verify=0
print_plan=0

# --- parse args (space-form flags only; POSIX) -----------------------------
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help)     usage; exit 0 ;;
    --mode)        shift; [ $# -ge 1 ] || die "--mode requires a value";        mode=$1;                shift ;;
    --path)        shift; [ $# -ge 1 ] || die "--path requires a value";        path=$1;                shift ;;
    --repo-name)   shift; [ $# -ge 1 ] || die "--repo-name requires a value";   repo_name=$1;           shift ;;
    --ref)         shift; [ $# -ge 1 ] || die "--ref requires a value";         ref=$1;                 shift ;;
    --repo)        shift; [ $# -ge 1 ] || die "--repo requires a value";        repo=$1;                shift ;;
    --from)        shift; [ $# -ge 1 ] || die "--from requires a value";        from=$1;                shift ;;
    --bundle-url)  shift; [ $# -ge 1 ] || die "--bundle-url requires a value";  bundle_url_override=$1; shift ;;
    --sha256)      shift; [ $# -ge 1 ] || die "--sha256 requires a value";      expected_sha=$1;        shift ;;
    --sums-file)   shift; [ $# -ge 1 ] || die "--sums-file requires a value";   sums_file=$1;           shift ;;
    --no-verify)   no_verify=1; shift ;;
    --print-plan)  print_plan=1; shift ;;
    --)            shift; break ;;
    -*)            die "unknown option: $1 (try --help)" ;;
    *)             die "unexpected argument: $1 (try --help)" ;;
  esac
done

# --- validate (pure: argument shape only, no filesystem / network) ---------
case "$mode" in
  new|existing) ;;
  *) die "--mode must be 'new' or 'existing' (got: $mode)" ;;
esac
if [ "$mode" = new ] && [ -z "$repo_name" ]; then
  die "--mode new requires --repo-name"
fi

# --- resolve the plan (pure) ----------------------------------------------
if [ "$mode" = new ]; then
  target=$path/$repo_name
else
  target=$path
fi

if [ -n "$bundle_url_override" ]; then
  bundle_url=$bundle_url_override
  sums_url=
  source_desc=$bundle_url
elif [ -n "$from" ]; then
  bundle_url=
  sums_url=
  source_desc="(local file) $from"
elif [ "$ref" = latest ]; then
  bundle_url="https://github.com/$repo/releases/latest/download/$BUNDLE_NAME"
  sums_url="https://github.com/$repo/releases/latest/download/$SUMS_NAME"
  source_desc=$bundle_url
else
  bundle_url="https://github.com/$repo/releases/download/$ref/$BUNDLE_NAME"
  sums_url="https://github.com/$repo/releases/download/$ref/$SUMS_NAME"
  source_desc=$bundle_url
fi

if [ "$no_verify" = 1 ]; then
  verify_desc="DISABLED (--no-verify)"
elif [ -n "$expected_sha" ]; then
  verify_desc="pinned $expected_sha"
elif [ -n "$sums_file" ]; then
  verify_desc="$SUMS_NAME file ($sums_file)"
elif [ -n "$sums_url" ]; then
  verify_desc="$SUMS_NAME from the release"
else
  verify_desc="REQUIRED but no source (pass --sha256, --sums-file, or --no-verify)"
fi

if [ "$print_plan" = 1 ]; then
  info "install plan:"
  info "  mode:       $mode"
  info "  target:     $target"
  info "  source:     $source_desc"
  if [ -z "$from" ] && [ -z "$bundle_url_override" ]; then
    info "  repo:       $repo"
    info "  ref:        $ref"
  fi
  info "  checksum:   $verify_desc"
  info "  extract:    additive (refuses to overwrite an existing file)"
  exit 0
fi

# --- run -------------------------------------------------------------------
tmpdir=$(mktemp -d 2>/dev/null) || die "could not create a temp dir"
trap 'rm -rf "$tmpdir"' EXIT INT TERM

# Resolve the target on disk.
if [ "$mode" = new ]; then
  if [ -e "$target" ] && [ -n "$(ls -A "$target" 2>/dev/null)" ]; then
    die "target already exists and is not empty: $target (use --mode existing to add to it)"
  fi
  mkdir -p "$target" || die "could not create target dir: $target"
else
  [ -d "$target" ] || die "target repo dir does not exist: $target (create it, or use --mode new)"
fi

# Obtain the bundle.
if [ -n "$from" ]; then
  [ -f "$from" ] || die "bundle file not found: $from"
  bundle=$from
else
  bundle=$tmpdir/$BUNDLE_NAME
  info "downloading $source_desc"
  download "$bundle_url" "$bundle" || offline "download failed: $bundle_url (offline? wrong --ref / --repo?)"
fi

# It must be a readable gzip tarball; capture the listing once for the safety checks.
listing=$tmpdir/bundle.list
tar tzf "$bundle" > "$listing" 2>/dev/null || die "not a readable .tar.gz bundle: $bundle"

# Verify integrity (fail-closed).
if [ "$no_verify" = 1 ]; then
  warn "checksum verification DISABLED (--no-verify) — the bundle's provenance is NOT checked"
else
  if [ -z "$expected_sha" ]; then
    if [ -n "$sums_file" ]; then
      [ -f "$sums_file" ] || die "$SUMS_NAME file not found: $sums_file"
      sums_src=$sums_file
    elif [ -n "$sums_url" ]; then
      download "$sums_url" "$tmpdir/$SUMS_NAME" || offline "could not fetch $SUMS_NAME ($sums_url); pass --sha256, --sums-file, or --no-verify"
      sums_src=$tmpdir/$SUMS_NAME
    else
      die "cannot verify integrity (no $SUMS_NAME source for --from / --bundle-url); pass --sha256, --sums-file, or --no-verify"
    fi
    expected_sha=$(awk -v n="$BUNDLE_NAME" '{ f=$2; sub(/^[*]/,"",f); sub(/^\.\//,"",f); if (f==n) { print $1; exit } }' "$sums_src")
    [ -n "$expected_sha" ] || die "$SUMS_NAME ($sums_src) has no entry for $BUNDLE_NAME; pass --sha256 or --no-verify"
  fi
  actual=$(sha256_of "$bundle") || die "no checksum tool (sha256sum / shasum / openssl) found; install one or use --no-verify"
  if [ "$actual" != "$expected_sha" ]; then
    die "checksum mismatch: expected $expected_sha, got $actual"
  fi
  info "checksum OK ($actual)"
fi

# Defense in depth: refuse an archive whose paths escape the target root.
unsafe=$(awk '/^\// { print; next } $0 ~ /(^|\/)\.\.(\/|$)/ { print }' "$listing")
if [ -n "$unsafe" ]; then
  die "refusing to extract — the archive has unsafe paths:
$unsafe"
fi

# Additive: refuse to overwrite any existing FILE (directories may coexist).
clobber=
while IFS= read -r entry; do
  case "$entry" in */) continue ;; esac        # skip directory entries
  if [ -e "$target/$entry" ] && [ ! -d "$target/$entry" ]; then
    clobber="$clobber  $entry
"
  fi
done < "$listing"
if [ -n "$clobber" ]; then
  die "refusing to overwrite existing files under $target (install is additive):
$clobber"
fi

# Place it.
tar xzf "$bundle" -C "$target" || die "extraction failed"

info ""
info "EADOS installed into: $target"
info "  next:  cd \"$target\" && ls .eados-core      # orchestrator/ templates/ tools/ …"
info "  then:  open the repo with an AI agent (it auto-loads AGENTS.md), or render deterministically:"
info "         python .eados-core/tools/render.py .eados-core/orchestrator/project.yaml --in-place"
info "  see .eados-core/README.md for the bundle entry-point instructions."

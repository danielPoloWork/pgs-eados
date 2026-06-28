#!/bin/sh
# setup.sh — guided EADOS installer (POSIX). Downloads the factory bundle, VERIFIES its SHA256
# (fail-closed), and extracts it ADDITIVELY (refuses to overwrite any existing file — the ADR-0007
# no-clobber principle) into a target repo root. Scriptable via flags; INTERACTIVE when run bare
# (or --interactive), prompting for where to install. Double-clickable on macOS via setup.command.
#
# SCOPE: "install" = bundle download + placement only (the consumer step of USAGE §6), not the
# agentic-OS init. The installer lives OUTSIDE .eados-core/ because it *delivers* it, and is
# export-ignored from the bundle. POSIX sh only (no bashisms); mirror of setup.ps1.

set -eu

PROG=setup.sh
BUNDLE_NAME=pgs-eados-bundle.tar.gz
SUMS_NAME=SHA256SUMS
DEFAULT_REPO=danielPoloWork/pgs-eados
CR=$(printf '\r')   # strip a trailing CR off answers so CRLF-piped input works everywhere

# --- output helpers --------------------------------------------------------
fail()    { _code=$1; shift; printf '%s: error: %s\n' "$PROG" "$*" >&2; exit "$_code"; }
die()     { fail 1 "$@"; }                # user / safety error
offline() { fail 2 "$@"; }                # environmental: offline / asset unavailable
warn()    { printf '%s: warning: %s\n' "$PROG" "$*" >&2; }
info()    { printf '%s\n' "$*"; }
prompt()  { printf '%s' "$*" >&2; }       # prompts go to stderr; stdout stays clean for the plan

usage() {
  cat <<'EOF'
setup.sh — download the EADOS factory bundle into a repo (download + placement only).

USAGE
  setup.sh                         # bare / double-click (via setup.command) => interactive prompts
  setup.sh [options]               # scriptable (flags below); add --interactive to force prompts

WHERE TO INSTALL
  --mode new|existing   install into a new repo dir or an existing one      (default: existing)
  --path DIR            target repo root (existing), or parent dir (new)     (default: .)
  --repo-name NAME      name of the new repo dir under --path                (required for --mode new)

WHICH BUNDLE
  --ref REF             release tag to install, e.g. v2.2.0                  (default: latest)
  --repo OWNER/REPO     source GitHub repo                                   (default: danielPoloWork/pgs-eados)
  --from FILE           install from a local bundle file (skip download; air-gapped / testing)
  --bundle-url URL      download the bundle from this exact URL (overrides --ref / --repo)

INTEGRITY (fail-closed: refuses to extract an unverified bundle)
  --sha256 HEX          expected SHA256 of the bundle (else read from the release SHA256SUMS)
  --sums-file FILE      verify against a local SHA256SUMS file (skip the download; air-gapped)
  --no-verify           skip checksum verification (loudly; not recommended)

OTHER
  --interactive         force the prompts even when flags are given
  --non-interactive     never prompt (use flags / defaults)
  --no-gh               do not offer to create a GitHub repo with gh (new-repo mode)
  --dry-run             prompt + show the plan, but do not download / write / git-init
  --print-plan          print the resolved plan and exit (no download, no writes)
  -h, --help            this help

The bundle is extracted ADDITIVELY: it refuses to overwrite any existing file. On a NEW repo it
also runs `git init` (and offers `gh repo create` when gh is present).
EOF
}

ask() {  # $1 prompt  $2 default ; sets ANSWER (falls back to the default on empty / EOF)
  if [ -n "${2:-}" ]; then prompt "$1 [$2]: "; else prompt "$1: "; fi
  if IFS= read -r ANSWER; then :; else ANSWER=; printf '\n' >&2; fi
  ANSWER=${ANSWER%"$CR"}
  [ -n "$ANSWER" ] || ANSWER=${2:-}
}

confirm() {  # $1 prompt ; 0 if the answer is yes
  prompt "$1 [y/N]: "
  if IFS= read -r _reply; then :; else _reply=; printf '\n' >&2; fi
  case "${_reply%"$CR"}" in [yY]|[yY][eE][sS]) return 0 ;; *) return 1 ;; esac
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
dry_run=0
no_gh=0
interactive=0
non_interactive=0

argc=$#   # capture before parsing: bare invocation (no args) implies interactive

# --- parse args (space-form flags only; POSIX) -----------------------------
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help)        usage; exit 0 ;;
    --mode)           shift; [ $# -ge 1 ] || die "--mode requires a value";        mode=$1;                shift ;;
    --path)           shift; [ $# -ge 1 ] || die "--path requires a value";        path=$1;                shift ;;
    --repo-name)      shift; [ $# -ge 1 ] || die "--repo-name requires a value";   repo_name=$1;           shift ;;
    --ref)            shift; [ $# -ge 1 ] || die "--ref requires a value";         ref=$1;                 shift ;;
    --repo)           shift; [ $# -ge 1 ] || die "--repo requires a value";        repo=$1;                shift ;;
    --from)           shift; [ $# -ge 1 ] || die "--from requires a value";        from=$1;                shift ;;
    --bundle-url)     shift; [ $# -ge 1 ] || die "--bundle-url requires a value";  bundle_url_override=$1; shift ;;
    --sha256)         shift; [ $# -ge 1 ] || die "--sha256 requires a value";      expected_sha=$1;        shift ;;
    --sums-file)      shift; [ $# -ge 1 ] || die "--sums-file requires a value";   sums_file=$1;           shift ;;
    --no-verify)      no_verify=1; shift ;;
    --interactive)    interactive=1; shift ;;
    --non-interactive) non_interactive=1; shift ;;
    --no-gh)          no_gh=1; shift ;;
    --dry-run)        dry_run=1; shift ;;
    --print-plan)     print_plan=1; shift ;;
    --)               shift; break ;;
    -*)               die "unknown option: $1 (try --help)" ;;
    *)                die "unexpected argument: $1 (try --help)" ;;
  esac
done

# Interactive when run bare (double-click) or asked for; never when --non-interactive / --print-plan.
want_interactive=0
if [ "$non_interactive" = 0 ] && [ "$print_plan" = 0 ]; then
  if [ "$interactive" = 1 ] || [ "$argc" = 0 ]; then want_interactive=1; fi
fi

if [ "$want_interactive" = 1 ]; then
  info "EADOS guided installer — downloads the factory bundle into a repo (no agent init)."
  info ""
  ask "Install into a (1) new repo or (2) existing repo?" "2"
  case "$ANSWER" in
    1|new|n|N)      mode=new ;;
    2|existing|e|E) mode=existing ;;
    *) die "please answer 1 (new) or 2 (existing)" ;;
  esac
  if [ "$mode" = new ]; then
    ask "Parent directory for the new repo" "."
    path=$ANSWER
    repo_name=
    while [ -z "$repo_name" ]; do
      ask "New repo name" ""
      repo_name=$ANSWER
      [ -n "$repo_name" ] || info "  (a name is required for a new repo)"
    done
  else
    ask "Path to the existing repo" "."
    path=$ANSWER
  fi
fi

# --- validate (argument shape only) ----------------------------------------
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

print_the_plan() {
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
  if [ "$mode" = new ]; then info "  git init:   $target (a fresh repository)"; fi
}

if [ "$print_plan" = 1 ]; then
  print_the_plan
  exit 0
fi

if [ "$want_interactive" = 1 ]; then
  info ""
  print_the_plan
  info ""
  confirm "Proceed?" || { info "Aborted — nothing was written."; exit 0; }
fi

if [ "$dry_run" = 1 ]; then
  info "[dry-run] would install into $target (mode $mode); nothing written."
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

# git init for a new repo (the lifecycle the engine defers to the interactive layer).
if [ "$mode" = new ]; then
  if command -v git >/dev/null 2>&1; then
    if ( CDPATH= cd -- "$target" && git init -q ); then
      info "git: initialised an empty repository in $target"
    else
      info "note: 'git init' did not complete for $target — you can run it yourself"
    fi
  else
    info "note: git not found — skipped 'git init' for $target (install git, then run it there)"
  fi
  if [ "$no_gh" = 0 ] && command -v gh >/dev/null 2>&1; then
    if confirm "Create a GitHub repo for it now with gh?"; then
      ( CDPATH= cd -- "$target" && gh repo create "$repo_name" --private --source=. --remote=origin ) \
        || info "note: 'gh repo create' did not complete — you can run it later"
    fi
  fi
fi

info ""
info "Done. EADOS installed into: $target"
info "  next:  cd \"$target\" && ls .eados-core      # orchestrator/ templates/ tools/ …"
info "  then:  open the repo with an AI agent (it auto-loads AGENTS.md), or render deterministically:"
info "         python .eados-core/tools/render.py .eados-core/orchestrator/project.yaml --in-place"
info "  see .eados-core/README.md for the bundle entry-point instructions."

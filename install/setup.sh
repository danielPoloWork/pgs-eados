#!/bin/sh
# setup.sh — guided (interactive) EADOS installer (M9 9.2): the Q&A wrapper around the
# NON-interactive engine install.sh (9.1). It asks *where* to install (new vs existing repo, the
# path, and the repo name), shows the plan, confirms, then runs install.sh to download + verify +
# place the bundle. On a NEW repo it also `git init`s the target (and offers `gh repo create` when
# gh is present).
#
# It adds NO new install logic — provenance, SHA256 verification, and the additive no-clobber
# guarantee all live in install.sh, which this only drives. Strict POSIX sh; double-clickable on
# macOS via install.command. For a fully non-interactive install, call install.sh directly.

set -eu

PROG=setup.sh
SELF_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ENGINE=$SELF_DIR/install.sh
CR=$(printf '\r')   # strip a trailing CR off answers so CRLF-piped input works everywhere

die()    { printf '%s: error: %s\n' "$PROG" "$*" >&2; exit 1; }
info()   { printf '%s\n' "$*"; }
prompt() { printf '%s' "$*" >&2; }      # prompts go to stderr; stdout stays clean for the plan

usage() {
  cat <<'EOF'
setup.sh — guided installer for EADOS: answer a few prompts and it downloads the factory bundle
and places it in a repo. It wraps install.sh — the actual download / verify / extract lives there.

USAGE
  setup.sh [--no-gh] [--dry-run] [-- <install.sh options>]

  --no-gh      do not offer to create a GitHub repo with gh (new-repo mode)
  --dry-run    prompt + show the plan, but do not download / write / git-init
  -h, --help   this help
  --           pass the remaining options straight to install.sh (e.g. --ref, --from, --no-verify)

Prompts: new vs existing repo, the path, and (for a new repo) the repo name. You confirm before
anything is written.
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

# --- parse this script's own flags; everything after `--` is for install.sh -----------------
no_gh=0
dry_run=0
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --no-gh)   no_gh=1; shift ;;
    --dry-run) dry_run=1; shift ;;
    --)        shift; break ;;
    -*)        die "unknown option: $1 (try --help)" ;;
    *)         die "unexpected argument: $1 (use -- to pass install.sh options)" ;;
  esac
done
# "$@" now holds the passthrough options for install.sh.

[ -f "$ENGINE" ] || die "install.sh not found next to this script ($ENGINE) — keep them together"

info "EADOS guided installer — downloads the factory bundle into a repo (no agent init)."
info ""

# Q1: new vs existing repo
ask "Install into a (1) new repo or (2) existing repo?" "2"
case "$ANSWER" in
  1|new|n|N)      mode=new ;;
  2|existing|e|E) mode=existing ;;
  *) die "please answer 1 (new) or 2 (existing)" ;;
esac

# Q2: where
if [ "$mode" = new ]; then
  ask "Parent directory for the new repo" "."
  path=$ANSWER
  repo_name=
  while [ -z "$repo_name" ]; do
    ask "New repo name" ""
    repo_name=$ANSWER
    [ -n "$repo_name" ] || info "  (a name is required for a new repo)"
  done
  target=$path/$repo_name
else
  ask "Path to the existing repo" "."
  path=$ANSWER
  target=$path
fi

# Build the engine argv: the resolved flags first, then the passthrough.
if [ "$mode" = new ]; then
  set -- --mode new --path "$path" --repo-name "$repo_name" "$@"
else
  set -- --mode existing --path "$path" "$@"
fi

info ""
info "Plan:"
sh "$ENGINE" --print-plan "$@" || die "could not resolve the install plan"
[ "$mode" = new ] && info "  git init:   $target (a fresh repository)"
info ""

confirm "Proceed?" || { info "Aborted — nothing was written."; exit 0; }

if [ "$dry_run" = 1 ]; then
  info "[dry-run] would run:  install.sh $*"
  [ "$mode" = new ] && info "[dry-run] would git init:  $target"
  exit 0
fi

sh "$ENGINE" "$@" || die "install failed (see the message above)"

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
info "Done. Next:"
info "  cd \"$target\""
info "  open the repo with an AI agent (it auto-loads AGENTS.md), or render deterministically:"
info "  python .eados-core/tools/render.py .eados-core/orchestrator/project.yaml --in-place"

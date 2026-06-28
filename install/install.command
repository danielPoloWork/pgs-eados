#!/bin/sh
# install.command — macOS double-click entry for the guided EADOS installer (M9 9.2).
#
# Double-clicking this in Finder opens Terminal and runs it; it simply delegates to setup.sh next
# to it (the interactive Q&A wrapper around install.sh). Kept as a thin shim so all the install
# logic lives in one place. On Linux just run setup.sh from a terminal.

dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
sh "$dir/setup.sh" "$@"
status=$?

# When launched by double-click (a real terminal), pause so the window does not vanish before the
# output can be read. Skipped under a pipe (e.g. tests / scripted use).
if [ -t 0 ] && [ -t 1 ]; then
  printf '\nPress Return to close…'
  read -r _ || true
fi

exit "$status"

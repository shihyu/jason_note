#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MAIN_SRC="$ROOT/tests/godebug_runtime_debug/main.go"
CGO_SRC="$ROOT/tests/godebug_runtime_debug/cgocheck/main.go"
MAIN_BIN="/tmp/godebug-demo"
CGO_BIN="/tmp/godebug-cgocheck"

go build -o "$MAIN_BIN" "$MAIN_SRC"
go build -o "$CGO_BIN" "$CGO_SRC"

run() {
  printf '\n== %s ==\n' "$1"
  shift
  "$@"
}

run "gctrace" env GODEBUG=gctrace=1 "$MAIN_BIN" gc
run "gcpacertrace" env GODEBUG=gcpacertrace=1 "$MAIN_BIN" gc
run "gcshrinkstackoff=0" "$MAIN_BIN" stack
run "gcshrinkstackoff=1" env GODEBUG=gcshrinkstackoff=1 "$MAIN_BIN" stack
run "schedtrace" env GODEBUG=schedtrace=500 "$MAIN_BIN" sched
run "scheddetail" env GODEBUG=schedtrace=500,scheddetail=1 "$MAIN_BIN" sched
run "tracebackancestors" bash -lc "set +e; GODEBUG=tracebackancestors=5 '$MAIN_BIN' traceback; exit 0"
run "asyncpreempt default" "$MAIN_BIN" asyncpreempt
run "asyncpreemptoff=1" env GODEBUG=asyncpreemptoff=1 "$MAIN_BIN" asyncpreempt
run "cgocheck default" bash -lc "set +e; '$CGO_BIN'; exit 0"
run "cgocheck=0" env GODEBUG=cgocheck=0 "$CGO_BIN"
run "invalidptr default" bash -lc "set +e; '$MAIN_BIN' invalidptr; exit 0"
run "invalidptr=0" env GODEBUG=invalidptr=0 "$MAIN_BIN" invalidptr
run "scavtrace" env GODEBUG=scavtrace=1 "$MAIN_BIN" rss
run "madvdontneed=0" env GODEBUG=madvdontneed=0 "$MAIN_BIN" rss
run "madvdontneed=1" env GODEBUG=madvdontneed=1 "$MAIN_BIN" rss
run "sbrk=1" env GODEBUG=sbrk=1 "$MAIN_BIN" rss
run "gcstoptheworld=1" env GODEBUG=gcstoptheworld=1,gctrace=1 "$MAIN_BIN" gc
run "gcstoptheworld=2" bash -lc "set +e; GODEBUG=gcstoptheworld=2,gctrace=1 '$MAIN_BIN' gc; exit 0"
run "gccheckmark=1" env GODEBUG=gccheckmark=1 "$MAIN_BIN" gc
run "efence=1" env GODEBUG=efence=1 "$MAIN_BIN" addr
run "allocfreetrace=1 (head)" bash -lc "GODEBUG=allocfreetrace=1 '$MAIN_BIN' gc 2>&1 | sed -n '1,14p'"
run "clobberfree=1" env GODEBUG=clobberfree=1 "$MAIN_BIN" clobber
run "runtime doc scavenge lookup" bash -lc "go doc runtime | rg -n 'scavtrace|scavenge'"

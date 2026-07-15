#!/usr/bin/env bash
# Bootstrap and verify LoopPilot on WSL/Linux.
#
# Usage:
#   bash scripts/deploy_wsl.sh
#   bash scripts/deploy_wsl.sh --repo-dir "$HOME/LoopPilot"
#
# From a fresh WSL shell after this script is published:
#   curl -fsSL https://raw.githubusercontent.com/bosprimigenious/LoopPilot/main/scripts/deploy_wsl.sh | bash

set -Eeuo pipefail

REPO_URL="${LOOPPILOT_REPO_URL:-https://github.com/bosprimigenious/LoopPilot.git}"
REPO_DIR="${LOOPPILOT_REPO_DIR:-$HOME/LoopPilot}"
SKIP_FULL_TESTS="${LOOPPILOT_SKIP_FULL_TESTS:-0}"
SKIP_ACCEPTANCE="${LOOPPILOT_SKIP_ACCEPTANCE:-0}"
SKIP_API_SMOKE="${LOOPPILOT_SKIP_API_SMOKE:-0}"
NO_PULL="${LOOPPILOT_NO_PULL:-0}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
API_SMOKE_PORT="${LOOPPILOT_API_SMOKE_PORT:-17860}"

usage() {
  cat <<'USAGE'
Usage: deploy_wsl.sh [options]

Options:
  --repo-dir PATH       Repository directory to use or clone into.
  --repo-url URL        Git repository URL. Defaults to LoopPilot origin.
  --skip-full-tests     Skip full pytest and run only smoke/acceptance commands.
  --skip-acceptance     Skip version acceptance scripts.
  --skip-api-smoke      Skip local read-only API bridge smoke check.
  --no-pull             Do not pull when --repo-dir already exists.
  -h, --help            Show this help.

Environment:
  LOOPPILOT_REPO_DIR
  LOOPPILOT_REPO_URL
  LOOPPILOT_SKIP_FULL_TESTS=1
  LOOPPILOT_SKIP_ACCEPTANCE=1
  LOOPPILOT_SKIP_API_SMOKE=1
  LOOPPILOT_API_SMOKE_PORT=17860
  LOOPPILOT_NO_PULL=1
  PYTHON_BIN=python3.11
USAGE
}

log() {
  printf '\n==> %s\n' "$*"
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-dir)
      [[ $# -ge 2 ]] || die "--repo-dir requires a path"
      REPO_DIR="$2"
      shift 2
      ;;
    --repo-url)
      [[ $# -ge 2 ]] || die "--repo-url requires a URL"
      REPO_URL="$2"
      shift 2
      ;;
    --skip-full-tests)
      SKIP_FULL_TESTS=1
      shift
      ;;
    --skip-acceptance)
      SKIP_ACCEPTANCE=1
      shift
      ;;
    --skip-api-smoke)
      SKIP_API_SMOKE=1
      shift
      ;;
    --no-pull)
      NO_PULL=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
done

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

require_command() {
  if ! command_exists "$1"; then
    apt_hint
    die "missing command: $1. Install it in WSL, then rerun this script."
  fi
}

apt_hint() {
  if command_exists apt-get; then
    printf 'Hint: sudo apt-get update && sudo apt-get install -y git python3 python3-venv python3-pip\n' >&2
  fi
}

run() {
  printf '+'
  printf ' %q' "$@"
  printf '\n'
  "$@"
}

check_python() {
  "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' || {
    "$PYTHON_BIN" --version >&2 || true
    die "LoopPilot requires Python >= 3.11"
  }
  "$PYTHON_BIN" -m venv --help >/dev/null 2>&1 || {
    apt_hint
    die "Python venv module is missing"
  }
}

api_bridge_smoke() {
  local api_log="$LOG_DIR/api-bridge-smoke.log"
  local api_pid

  log "Running read-only API bridge smoke on port $API_SMOKE_PORT"
  loop-pilot api serve --host 127.0.0.1 --port "$API_SMOKE_PORT" >"$api_log" 2>&1 &
  api_pid=$!

  for _ in $(seq 1 30); do
    if python -c 'import json, sys, urllib.request; port=sys.argv[1]; data=json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=1)); methods=data.get("allowedMethods", []); ok=data.get("status") == "ok" and data.get("readOnly") is True and data.get("mutationsEnabled") is False and methods == ["GET", "OPTIONS"] and "POST" not in methods and data.get("corsPreflight") is True and "/api/reviews/{run_id}" in data.get("endpoints", []); raise SystemExit(0 if ok else 1)' "$API_SMOKE_PORT" 2>/dev/null; then
      kill "$api_pid" 2>/dev/null || true
      wait "$api_pid" 2>/dev/null || true
      printf 'API bridge smoke: OK\n'
      return 0
    fi
    if ! kill -0 "$api_pid" 2>/dev/null; then
      printf 'API bridge exited before smoke completed.\n' >&2
      sed -n '1,80p' "$api_log" >&2 || true
      return 1
    fi
    sleep 0.25
  done

  kill "$api_pid" 2>/dev/null || true
  wait "$api_pid" 2>/dev/null || true
  sed -n '1,80p' "$api_log" >&2 || true
  die "API bridge smoke failed on port $API_SMOKE_PORT"
}

ensure_repo() {
  if [[ -f "pyproject.toml" && -d "src/loop_pilot" ]]; then
    REPO_DIR="$(pwd)"
    log "Using current repository: $REPO_DIR"
    return
  fi

  if [[ -d "$REPO_DIR/.git" ]]; then
    log "Using existing repository: $REPO_DIR"
    cd "$REPO_DIR"
    if [[ "$NO_PULL" == "1" ]]; then
      log "Skipping git pull (--no-pull)"
    else
      run git fetch --prune origin
      run git pull --ff-only
    fi
    return
  fi

  log "Cloning repository into $REPO_DIR"
  mkdir -p "$(dirname "$REPO_DIR")"
  run git clone "$REPO_URL" "$REPO_DIR"
  cd "$REPO_DIR"
}

main() {
  log "Checking WSL/Linux prerequisites"
  case "$(uname -s)" in
    Linux) ;;
    *) die "this script is intended for WSL/Linux; current system is $(uname -s)" ;;
  esac
  require_command git
  require_command "$PYTHON_BIN"
  check_python

  ensure_repo

  LOG_DIR="var/logs"
  mkdir -p "$LOG_DIR"
  LOG_FILE="$LOG_DIR/wsl-deploy-$(date -u +%Y%m%dT%H%M%SZ).log"
  log "Writing deployment log to $LOG_FILE"
  exec > >(tee -a "$LOG_FILE") 2>&1

  log "Creating Python virtual environment"
  run "$PYTHON_BIN" -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate

  log "Installing LoopPilot with dev dependencies"
  run python -m pip install --upgrade pip
  run python -m pip install -e ".[dev]"

  log "Preparing local state directories and config"
  run python scripts/bootstrap_local.py

  log "Running health checks"
  run loop-pilot doctor
  run loop-pilot adapters doctor

  log "Running static checks"
  run ruff check .
  run python scripts/verify_wsl_deploy_static.py
  run python scripts/verify_api_bridge_contract.py
  run python scripts/verify_wechat_miniprogram_static.py

  if [[ "$SKIP_FULL_TESTS" == "1" ]]; then
    log "Skipping full pytest by request"
    run python -m pytest -q tests/integration/test_mini_acceptance.py
    run python -m pytest -q tests/integration/test_v1_cli.py
  else
    log "Running full pytest"
    run python -m pytest -q
  fi

  if [[ "$SKIP_ACCEPTANCE" == "1" ]]; then
    log "Skipping acceptance gates by request"
  else
    log "Running acceptance gates"
    run python scripts/verify_0_3_acceptance.py
    run python scripts/verify_0_4_acceptance.py
    run python scripts/verify_0_5_prep.py
  fi

  log "Running CLI smoke workflow"
  run loop-pilot run all --fixture-set mini --dry-run
  run loop-pilot status
  if [[ "$SKIP_API_SMOKE" == "1" ]]; then
    log "Skipping API bridge smoke by request"
  else
    api_bridge_smoke
  fi

  log "LoopPilot WSL deployment verified"
  printf '\nRepository: %s\n' "$(pwd)"
  printf 'Activate:   source %s/.venv/bin/activate\n' "$(pwd)"
  printf 'Log file:   %s/%s\n' "$(pwd)" "$LOG_FILE"
}

main "$@"

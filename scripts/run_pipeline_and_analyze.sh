#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

MODE="${1:-}"
case "${MODE}" in
  qwen)
    RUN_SCRIPT="${SCRIPT_DIR}/run_qwen.py"
    ;;
  qwen_base)
    RUN_SCRIPT="${SCRIPT_DIR}/run_qwen_base.py"
    ;;
  openai)
    RUN_SCRIPT="${SCRIPT_DIR}/run_openai.py"
    ;;
  dry|simple)
    RUN_SCRIPT="${SCRIPT_DIR}/dry_run_pipeline.py"
    ;;
  *)
    echo "Usage: $0 {qwen|qwen_base|openai|dry|simple}" >&2
    exit 1
    ;;
esac

VENV_DIR="${VENV_DIR:-${REPO_ROOT}/.venv}"
if [[ ! -d "${VENV_DIR}" ]]; then
  echo "ERROR: virtual environment not found at ${VENV_DIR}" >&2
  exit 1
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.env"
  set +a
fi

LOG_FILE="$(mktemp)"
trap 'rm -f "${LOG_FILE}"' EXIT

echo "Starting ${MODE} pipeline (streaming; this can take a long time for many role cards)..." >&2
python -u "${RUN_SCRIPT}" 2>&1 | tee "${LOG_FILE}"

RUN_ID=""
while IFS= read -r line; do
  [[ "${line}" == Run\ directory:* ]] || continue
  RUN_ID="$(basename "${line#Run directory: }")"
done < "${LOG_FILE}"

if [[ -z "${RUN_ID}" ]]; then
  echo "ERROR: could not parse run id from pipeline output (expected a 'Run directory:' line)" >&2
  exit 1
fi

export PIPELINE_RUN_ID="${RUN_ID}"
echo "Analyzing ${RUN_ID}..." >&2
python -u "${SCRIPT_DIR}/analyze_run.py"

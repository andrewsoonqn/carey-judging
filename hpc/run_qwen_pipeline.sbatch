#!/bin/bash
#SBATCH --job-name=qwen-pipeline
#SBATCH --partition=gpu-long
#SBATCH --gpus=a100-40:1
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --time=48:00:00
#SBATCH --chdir=/home/a/andrewsq/dev/judging
#SBATCH --output=/home/a/andrewsq/dev/judging/logs/slurm_%j.out
#SBATCH --error=/home/a/andrewsq/dev/judging/logs/slurm_%j.err

set -euo pipefail

START_TIME="$(date +%s)"

finish() {
  local exit_code=$?
  local end_time duration
  end_time="$(date +%s)"
  duration="$((end_time - START_TIME))"

  echo
  echo "===== Job Summary ====="
  echo "Exit code: ${exit_code}"
  echo "Duration: ${duration}s"

  if command -v nvidia-smi >/dev/null 2>&1; then
    echo
    echo "===== Final GPU State ====="
    nvidia-smi || true
  fi
}

trap finish EXIT

PROJECT_DIR="${PROJECT_DIR:-/home/a/andrewsq/dev/judging}"
LOG_DIR="${LOG_DIR:-${PROJECT_DIR}/logs}"
VENV_DIR="${VENV_DIR:-${PROJECT_DIR}/.venv}"
PIPELINE_CMD="${PIPELINE_CMD:-python -u dry_run_qwen.py}"

# Optional module names. Override at submit time if your cluster uses modules.
CUDA_MODULE="${CUDA_MODULE:-}"
CUDNN_MODULE="${CUDNN_MODULE:-}"
PYTHON_MODULE="${PYTHON_MODULE:-}"

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export PYTHONUNBUFFERED=1

echo "===== SLURM Job Info ====="
echo "Job ID: ${SLURM_JOB_ID:-unknown}"
echo "Job Name: ${SLURM_JOB_NAME:-unknown}"
echo "Partition: ${SLURM_JOB_PARTITION:-unknown}"
echo "Node: ${SLURMD_NODENAME:-unknown}"
echo "Submit Dir: ${SLURM_SUBMIT_DIR:-unknown}"
echo "Project Dir: ${PROJECT_DIR}"
echo "Started At: $(date)"

mkdir -p "${LOG_DIR}"
cd "${PROJECT_DIR}"

if [[ -f "${PROJECT_DIR}/.env" ]]; then
  echo "Loading environment from ${PROJECT_DIR}/.env"
  set -a
  # shellcheck disable=SC1091
  source "${PROJECT_DIR}/.env"
  set +a
fi

if [[ -f /etc/profile.d/modules.sh ]]; then
  # shellcheck disable=SC1091
  source /etc/profile.d/modules.sh
fi

if type module >/dev/null 2>&1; then
  module purge || true

  for module_name in "${CUDA_MODULE}" "${CUDNN_MODULE}" "${PYTHON_MODULE}"; do
    if [[ -n "${module_name}" ]]; then
      echo "Loading module: ${module_name}"
      module load "${module_name}" || echo "Warning: failed to load module ${module_name}" >&2
    fi
  done
else
  echo "Module system not available; skipping module load"
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "ERROR: virtual environment not found at ${VENV_DIR}" >&2
  exit 1
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "ERROR: OPENAI_API_KEY is not set. dry_run_qwen.py uses OpenAI victim and tagger components." >&2
  exit 1
fi

QWEN_MODEL_DIR="${QWEN_MODEL_DIR:-${PROJECT_DIR}/qwen-caregiver-model}"
if [[ ! -f "${QWEN_MODEL_DIR}/adapter_config.json" ]]; then
  echo "Warning: adapter_config.json not found at ${QWEN_MODEL_DIR}" >&2
  echo "The job will rely on pipeline/qwen_friend.py path resolution." >&2
fi

echo
echo "===== Environment Check ====="
echo "Python: $(command -v python)"
python --version
python -c "import torch; print('torch', torch.__version__)"
python -c "import transformers; print('transformers', transformers.__version__)"
python -c "import peft; print('peft', peft.__version__)"
python -c "import torch; print('cuda_available', torch.cuda.is_available()); print('cuda_device_count', torch.cuda.device_count())"

if command -v nvidia-smi >/dev/null 2>&1; then
  echo
  echo "===== GPU Status ====="
  nvidia-smi
fi

RUN_LOG="${LOG_DIR}/qwen_pipeline_${SLURM_JOB_ID:-manual}.log"

echo
echo "===== Command ====="
echo "${PIPELINE_CMD}"
echo "Run log: ${RUN_LOG}"

set +e
bash -lc "${PIPELINE_CMD}" 2>&1 | tee "${RUN_LOG}"
CMD_EXIT=${PIPESTATUS[0]}
set -e

exit "${CMD_EXIT}"

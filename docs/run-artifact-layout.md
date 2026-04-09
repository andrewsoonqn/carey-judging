# Run Artifact Layout

This document defines how to store raw, derived, and operational artifacts for one pipeline run.

The layout is designed for:

- concurrent per-conversation processing
- clean separation of raw and derived data
- easy resume and retry
- reproducible dataset-level analysis

## Core Principles

- Raw artifacts are immutable.
- Derived artifacts are recomputable.
- Each conversation gets its own files so workers can write safely in parallel.
- Dataset-level tables are built later from stored per-conversation artifacts.
- Operational state is tracked separately from the raw conversation content.

## Recommended Directory Tree

```text
runs/
  run_2026_03_31_a/
    config/
      run-config.json
      victim-prompt.txt
      friend-prompt.txt
      taxonomy-version.txt
    role-cards/
      role_cards.snapshot.json
    conversations/
      conv_0001.json
      conv_0002.json
    tags/
      conv_0001.tags.json
      conv_0002.tags.json
    tables/
      friend_turn_tags.parquet
      conversation_metrics.parquet
      run_metrics.parquet
    reports/
      summary.json
      notes.md
    logs/
      simulation.log
      tagging.log
      analysis.log
    state/
      manifest.sqlite
      failures.jsonl
```

## What Goes Where

### `config/`

Store the exact run configuration used to generate the data.

- `run-config.json`: models, temperatures, concurrency, retry limits, turn limits, version ids.
- `victim-prompt.txt`: frozen victim prompt template for the run.
- `friend-prompt.txt`: frozen friend prompt template for the run.
- `taxonomy-version.txt`: frozen taxonomy identifier or content hash.

### `role-cards/`

Store a snapshot of the role-card set actually used in the run.

- This avoids ambiguity if the source role-card file changes later.

### `conversations/`

Store one raw transcript artifact per conversation.

- One file per conversation keeps concurrent writes simple.
- These are the main source artifacts.

### `tags/`

Store one per-conversation tagging artifact.

- Each file corresponds to one transcript file.
- The tags are derived from transcripts and can be regenerated.

### `tables/`

Store flattened and aggregated tables.

- `friend_turn_tags.parquet`: one row per friend turn.
- `conversation_metrics.parquet`: one row per conversation.
- `run_metrics.parquet`: one row per run, or summary by subgroup if needed.

### `reports/`

Human-readable summaries.

- Useful for quick inspection but not the source of truth.

### `logs/`

Execution logs.

- Helpful for debugging model failures or malformed outputs.

### `state/`

Operational bookkeeping.

- `manifest.sqlite`: job state, retries, timestamps, file paths.
- `failures.jsonl`: append-only failure events for debugging.

## Recommended Manifest Schema

Use `state/manifest.sqlite` or equivalent to track execution state. Suggested logical columns:

- `run_id`
- `conversation_id`
- `role_card_id`
- `simulation_status`
- `tagging_status`
- `analysis_status`
- `simulation_attempts`
- `tagging_attempts`
- `conversation_path`
- `tag_path`
- `error_type`
- `error_message`
- `updated_at`

This lets you rerun only missing or failed stages.

## Concurrency Guidance

### Good pattern

- simulation worker writes one `conversations/conv_xxxx.json`
- tagging worker reads that file and writes one `tags/conv_xxxx.tags.json`
- no worker writes to the same conversation file as another worker

### Avoid

- many workers appending to the same JSON file
- doing dataset-level aggregation inside each worker
- treating a live aggregate file as the source of truth

## Dataset-Level Analysis Pattern

Run analysis after enough per-conversation work is complete.

Recommended flow:

1. read all completed tag files
2. flatten them into `friend_turn_tags.parquet`
3. compute conversation-level metrics into `conversation_metrics.parquet`
4. compute run-level summaries into `run_metrics.parquet`
5. optionally write a human-readable `reports/summary.json`

This keeps dataset-level analysis separate from concurrent generation/tagging.

## File Naming Rules

- Use stable IDs, not titles or free text.
- Keep names deterministic:
  - `conv_0001.json`
  - `conv_0001.tags.json`
- Avoid spaces and ad hoc suffixes.
- If you rerun a whole experiment with a changed prompt or taxonomy, create a new `run_id` rather than overwriting files.

## Versioning Rules

At minimum, record:

- `role_card_version`
- `victim_prompt_version`
- `friend_prompt_version`
- `taxonomy_version`
- `tagger_version`
- `victim_model`
- `friend_model`
- `tagger_model`

These should appear both in run config and in the relevant per-file artifacts.

## Minimum Viable Setup

If you want the simplest version that still scales, start with:

```text
runs/
  run_x/
    config/
    conversations/
    tags/
    tables/
    state/manifest.sqlite
```

You can add `reports/` and `logs/` later without breaking the structure.

## Recommendation

For your use case, the best operational pattern is:

- generate and save each conversation independently
- tag each conversation independently as soon as it is ready
- build aggregate tables afterward in a separate pass

That gives you concurrency during production and clean analysis later.

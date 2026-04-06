# Tagging Output Schema

This document defines the JSON artifact written by the tagger for one completed conversation.

The transcript remains the raw source artifact. This file is a derived artifact that labels only the `friend` turns.

## Design Goals

- one tag file per conversation
- easy to validate
- easy to recompute if the taxonomy changes
- explicit versioning for the tagger and taxonomy
- simple to flatten later into analysis tables

## Recommended File-Level Schema

```json
{
  "run_id": "run_2026_03_31_a",
  "conversation_id": "conv_0001",
  "role_card_id": "rc_0001",
  "source_transcript_path": "runs/run_2026_03_31_a/conversations/conv_0001.json",
  "source_transcript_sha256": "abc123...",
  "tagger": {
    "tagger_version": "tagger_v1",
    "taxonomy_version": "taxonomy_v1",
    "model": "model_name_here",
    "temperature": 0.0
  },
  "friend_turn_tags": [
    {
      "friend_turn_index": 1,
      "message_array_index": 1,
      "text": "That sounds really hard. Has it felt more like burnout, sadness, or just being thrown off by everything changing?",
      "structure": "hybrid",
      "primary_strategy": "reflect",
      "secondary_strategies": ["probe"],
      "notes": "Reflection plus substantive question.",
      "confidence": 0.91
    },
    {
      "friend_turn_index": 2,
      "message_array_index": 3,
      "text": "Yeah, that kind of disruption can really drain your momentum. What has felt hardest to get back into?",
      "structure": "hybrid",
      "primary_strategy": "validate",
      "secondary_strategies": ["probe"],
      "notes": "Validation followed by probing question.",
      "confidence": 0.88
    },
    {
      "friend_turn_index": 3,
      "message_array_index": 5,
      "text": "That makes sense. Maybe the first step is making the workload feel smaller instead of forcing full motivation right away.",
      "structure": "hybrid",
      "primary_strategy": "suggest",
      "secondary_strategies": ["validate"],
      "notes": "Brief validation plus practical suggestion.",
      "confidence": 0.84
    }
  ],
  "status": "completed",
  "created_at": "2026-03-31T12:05:00Z"
}
```

## Field Definitions

### Top-level fields

- `run_id`: groups all artifacts from the same run.
- `conversation_id`: stable per-conversation ID.
- `role_card_id`: copied here for convenient joins.
- `source_transcript_path`: relative path to the raw transcript artifact.
- `source_transcript_sha256`: checksum of the transcript used for tagging.
- `tagger`: versioned metadata about the tagging process.
- `friend_turn_tags`: one entry per friend turn.
- `status`: typically `completed` or `failed`.
- `created_at`: timestamp for the tag artifact.

### Per-turn fields

- `friend_turn_index`: 1-based friend turn index.
- `message_array_index`: zero-based or one-based message offset; choose one convention and keep it fixed. Recommended: zero-based if used internally, one-based if used in exported tables. If you want to avoid ambiguity, rename this to `message_position_1_based`.
- `text`: exact friend text that was tagged.
- `structure`: one of `question`, `reflection`, `suggestion`, `hybrid`.
- `primary_strategy`: one of the allowed taxonomy labels.
- `secondary_strategies`: array, often empty.
- `notes`: optional short explanation for auditability.
- `confidence`: optional numeric field if the tagger can provide it.

## Validation Rules

- `friend_turn_tags` length should equal the number of friend turns in the transcript.
- `friend_turn_index` values should be unique and increasing.
- `text` must exactly match the corresponding text in the transcript.
- `structure` and `primary_strategy` must be from controlled vocabularies.
- `secondary_strategies` must not repeat `primary_strategy`.
- `secondary_strategies` should contain no duplicates.
- If `status` is `failed`, include an `error` object instead of partial tags unless you explicitly support partial output.

## Failure Schema

```json
{
  "run_id": "run_2026_03_31_a",
  "conversation_id": "conv_0001",
  "role_card_id": "rc_0001",
  "tagger": {
    "tagger_version": "tagger_v1",
    "taxonomy_version": "taxonomy_v1",
    "model": "model_name_here",
    "temperature": 0.0
  },
  "status": "failed",
  "error": {
    "type": "json_validation_error",
    "message": "primary_strategy missing for friend_turn_index 2"
  },
  "created_at": "2026-03-31T12:05:00Z"
}
```

## Flattened Table Shape

This file is designed to flatten into a per-turn table like:

```json
{
  "run_id": "run_2026_03_31_a",
  "conversation_id": "conv_0001",
  "role_card_id": "rc_0001",
  "friend_turn_index": 1,
  "structure": "hybrid",
  "primary_strategy": "reflect",
  "secondary_strategies": ["probe"],
  "tagger_version": "tagger_v1",
  "taxonomy_version": "taxonomy_v1"
}
```

That flattened table is what your dataset-level analysis should read.

## Recommendation

Keep the tag artifact small and literal:

- exact source text
- one primary label per turn
- optional secondary labels
- strong version metadata

Anything aggregative should live in later tables, not here.

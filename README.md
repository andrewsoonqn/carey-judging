# Friend Evaluation Pipeline

This repo is a lightweight scaffold for evaluating how a `friend` responds to different simulated `victims`.

Right now it uses simple deterministic stub components instead of AI calls, but the code is organized so you can swap in model-backed implementations later without changing the overall flow.

## What This Repo Does

- stores structured role cards
- simulates short 3-turn victim/friend conversations
- saves raw transcripts as JSON
- tags only the friend turns with structure and strategy labels
- writes per-conversation tag JSON artifacts

The current setup is intentionally simple so you can validate the pipeline shape before adding model APIs.

## Current Flow

```text
role card
  -> runner generates transcript
  -> transcript saved to conversations/conv_xxxx.json
  -> tagger reads transcript
  -> tag file saved to tags/conv_xxxx.tags.json
```

## Key Files

- `README.md` - this guide
- `foundation-spec.md` - design decisions for role cards, prompts, stop rules, and transcript schema
- `tagging-taxonomy.md` - structure/strategy label definitions
- `tagging-output-schema.md` - schema for tag artifacts
- `run-artifact-layout.md` - recommended run directory layout
- `sample_role_cards.json` - 5 example role cards in the new schema
- `dry_run_pipeline.py` - simplest end-to-end demo script
- `pipeline/interfaces.py` - swap points for victim, friend, and tagger implementations
- `pipeline/runner.py` - conversation generation and transcript writing
- `pipeline/tagger.py` - transcript tagging and tag validation
- `pipeline/simple_components.py` - deterministic stub victim/friend/tagger components

## Code Structure

### `pipeline/interfaces.py`

Defines the protocols for the three replaceable components:

- `VictimAgent`
- `FriendAgent`
- `TurnTagger`

If you want to plug in AI later, these are the interfaces to follow.

### `pipeline/runner.py`

Core function:

```python
run_conversation(...)
```

What it does:

- starts with the victim opening message from the role card
- alternates friend/victim turns
- stops after 3 friend turns
- writes a transcript JSON artifact

This file does not know whether the agents are heuristic or AI-backed.

### `pipeline/tagger.py`

Core function:

```python
tag_transcript_file(...)
```

What it does:

- reads one transcript file
- tags only the `friend` messages
- validates label values and text alignment
- writes one tag JSON artifact

### `pipeline/simple_components.py`

Contains the placeholder implementations:

- `SimpleVictimAgent`
- `SimpleFriendAgent`
- `HeuristicTurnTagger`

These are intentionally basic. They let you dry-run the pipeline without any AI dependency.

## How To Run It

From the repo root:

```bash
python3 dry_run_pipeline.py
```

This will create:

```text
runs/run_demo_simple/
  config/
  role-cards/
  conversations/
  tags/
```

## Example Outputs

After running the demo, inspect:

- `runs/run_demo_simple/conversations/conv_0001.json`
- `runs/run_demo_simple/tags/conv_0001.tags.json`

The transcript is the raw source artifact.

The tag file is derived from the transcript and contains per-turn friend labels.

## How To Swap In AI Later

You do not need to rewrite the runner or tagger. Replace the component methods instead.

### Replace the victim simulator

Implement a new class matching `VictimAgent`:

```python
class AIVictimAgent:
    name = "my_victim_model"
    version = "victim_v2"

    def opening_message(self, role_card):
        return role_card["conversation_seed"]["opening_message"]

    def reply(self, role_card, transcript):
        # call model here
        return "..."
```

### Replace the friend under test

Implement a new class matching `FriendAgent`:

```python
class AIFriendAgent:
    name = "my_friend_model"
    version = "friend_v2"

    def reply(self, transcript):
        # call model here
        return "..."
```

### Replace the tagger

Implement a new class matching `TurnTagger`:

```python
class AITurnTagger:
    name = "my_tagger_model"
    version = "tagger_v2"
    taxonomy_version = "taxonomy_v1"

    def tag_turn(self, transcript, friend_message, message_position_1_based):
        # call model here
        return {
            "friend_turn_index": friend_message["turn_index"],
            "message_position_1_based": message_position_1_based,
            "text": friend_message["text"],
            "structure": "hybrid",
            "primary_strategy": "reflect",
            "secondary_strategies": ["probe"],
            "notes": "...",
            "confidence": 0.9,
        }
```

Then wire those classes into `dry_run_pipeline.py` or a future batch runner.

## Role Card Schema

The current sample cards follow this shape:

```json
{
  "role_card_id": "rc_0001",
  "persona": {
    "age": 21,
    "gender": "male",
    "occupation": "college student"
  },
  "situation": {
    "current_issue": "...",
    "context": "...",
    "severity": "moderate",
    "duration": "recent_weeks"
  },
  "interaction_style": {
    "tone": "natural",
    "openness": "medium",
    "responsiveness": "medium"
  },
  "conversation_seed": {
    "opening_message": "...",
    "core_feelings": ["..."],
    "likely_themes": ["..."]
  },
  "metadata": {
    "source": "manual",
    "version": "role_card_v1"
  }
}
```

Design intent:

- role cards are the variable input
- victim behavior policy stays fixed
- friend only sees transcript history

## Transcript Format

Each generated conversation file contains:

- run metadata
- role card ID and version
- victim/friend component versions
- generation config
- stop reason
- ordered `messages`

See `foundation-spec.md` for the full schema.

## Tagging Format

Each tag file contains:

- source transcript reference and checksum
- tagger metadata
- one tag object per friend turn
- structure label
- primary strategy
- optional secondary strategies

See `tagging-output-schema.md` for the full schema.

## Current Limitations

- no batch runner yet
- no resumable manifest/state yet
- no dataset-level analysis tables yet
- current friend/victim/tagger behavior is heuristic and deterministic
- no tests yet

## Recommended Next Steps

1. Add a batch runner with resumable state.
2. Add a simple analysis script that flattens tag files into tables.
3. Swap one component at a time to AI, probably the tagger or victim first.
4. Add validation for role cards and transcript schemas.

## Related Docs

- `foundation-spec.md`
- `tagging-taxonomy.md`
- `tagging-output-schema.md`
- `run-artifact-layout.md`
- `to-do.md`

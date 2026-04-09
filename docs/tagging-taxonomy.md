# Tagging Taxonomy

This document defines how to tag `friend` turns in the conversation.

The goal is not to score quality directly. The goal is to label each friend response in a structured way so later analysis can compute diversity and distribution metrics.

## Scope

- Tag only `friend` turns.
- Tag each friend turn independently, while allowing the tagger to see the full transcript so far.
- Assign both:
  - one `structure` label
  - one `primary_strategy` label
- Optionally assign `secondary_strategies` when a turn clearly combines techniques.

## 1) Structure Labels

These labels describe the overall shape of the response.

### Allowed labels

- `question`
  - Main function is to ask for information or elaboration.
  - Usually ends with or centers on a question.
- `reflection`
  - Main function is to mirror, summarize, or validate what the victim seems to feel or mean.
- `suggestion`
  - Main function is to offer a next step, coping idea, framing, or action.
- `hybrid`
  - Two structures are both meaningfully present in the same turn, such as reflection plus question, or reflection plus suggestion.

### Structure decision rule

- Use `question` if the turn is mostly asking.
- Use `reflection` if the turn is mostly mirroring or validating and does not substantially move into advice.
- Use `suggestion` if the turn mainly proposes what to do or how to think about next steps.
- Use `hybrid` only when no single structure dominates.

## 2) Strategy Labels

These labels describe the main conversational technique used.

### Allowed primary strategies

- `probe`
  - Asks for more detail, clarification, or examples.
- `reflect`
  - Restates, mirrors, or paraphrases the victim's experience.
- `validate`
  - Normalizes or affirms the victim's feelings or reaction.
- `reframe`
  - Offers a new interpretation or perspective.
- `suggest`
  - Gives a possible next step, coping idea, or practical direction.
- `plan`
  - Breaks a problem into a specific, concrete, actionable step.
- `support`
  - Expresses care, encouragement, or companionship without much probing or advice.
- `other`
  - Use only when none of the above fit.

### Strategy boundary notes

- `reflect` vs `validate`
  - `reflect` mirrors content or emotion.
  - `validate` says the reaction makes sense or is understandable.
- `suggest` vs `plan`
  - `suggest` is broader and lighter.
  - `plan` is more concrete and action-oriented.
- `probe` can co-occur with other strategies, but only make it primary if the turn's main engine is inquiry.

## 3) Secondary Strategies

Use `secondary_strategies` only when clearly present.

Examples:
- "That sounds exhausting. What part has been hardest lately?"
  - `structure`: `hybrid`
  - `primary_strategy`: `reflect`
  - `secondary_strategies`: [`probe`]

- "It makes sense you'd feel thrown off. Maybe start with one short study block today."
  - `structure`: `hybrid`
  - `primary_strategy`: `validate`
  - `secondary_strategies`: [`suggest`]

Do not overload `secondary_strategies` just because a turn contains multiple small elements.

## 4) Hybrid Rules

Use `hybrid` only when the turn contains two meaningful parts with comparable weight.

### Use `hybrid` when

- a reflection is followed by a substantive question
- a validation is followed by a substantive suggestion
- a reflection is followed by a concrete plan and neither dominates clearly

### Do not use `hybrid` when

- the extra element is only a brief softener, such as "that sounds hard"
- the question is minimal and the rest of the turn is clearly a suggestion
- the reflection is minimal and the main function is clearly inquiry

## 5) Tagging Priority Rules

When a turn could fit multiple labels, apply these rules in order:

1. Determine `structure` from the overall shape of the turn.
2. Determine `primary_strategy` from the turn's main conversational move.
3. Add `secondary_strategies` only if another technique is clearly substantial.
4. Prefer the simplest valid annotation.

## 6) Examples

### Example A

Text:

```text
That sounds really frustrating. What part of school has felt hardest to get back into?
```

Tags:

```json
{
  "structure": "hybrid",
  "primary_strategy": "reflect",
  "secondary_strategies": ["probe"]
}
```

### Example B

Text:

```text
It makes sense that everything changing so suddenly would throw you off.
```

Tags:

```json
{
  "structure": "reflection",
  "primary_strategy": "validate",
  "secondary_strategies": []
}
```

### Example C

Text:

```text
Maybe the goal is not to force full motivation back right away, but just to make starting feel smaller.
```

Tags:

```json
{
  "structure": "suggestion",
  "primary_strategy": "reframe",
  "secondary_strategies": ["suggest"]
}
```

### Example D

Text:

```text
Would it help to pick one class and do ten minutes, just to make it feel less overwhelming?
```

Tags:

```json
{
  "structure": "suggestion",
  "primary_strategy": "plan",
  "secondary_strategies": []
}
```

### Example E

Text:

```text
I'm sorry you're carrying that mostly on your own.
```

Tags:

```json
{
  "structure": "reflection",
  "primary_strategy": "support",
  "secondary_strategies": []
}
```

### Example F

Text:

```text
When do you notice the lack of motivation most, during class time or when you try to study alone?
```

Tags:

```json
{
  "structure": "question",
  "primary_strategy": "probe",
  "secondary_strategies": []
}
```

### Example G

Text:

```text
It sounds like this is not just about school, but about feeling knocked off balance by everything changing.
```

Tags:

```json
{
  "structure": "reflection",
  "primary_strategy": "reframe",
  "secondary_strategies": ["reflect"]
}
```

### Example H

Text:

```text
That would wear a lot of people down. Have you been able to talk to anyone at school about it?
```

Tags:

```json
{
  "structure": "hybrid",
  "primary_strategy": "validate",
  "secondary_strategies": ["probe"]
}
```

### Example I

Text:

```text
Maybe do not aim for a full productive day yet. Picking one small task might be easier to restart from.
```

Tags:

```json
{
  "structure": "suggestion",
  "primary_strategy": "suggest",
  "secondary_strategies": []
}
```

### Example J

Text:

```text
So even when you sit down to work, your brain kind of shuts the whole thing down.
```

Tags:

```json
{
  "structure": "reflection",
  "primary_strategy": "reflect",
  "secondary_strategies": []
}
```

### Example K

Text:

```text
Would it help to make a list of just the assignments due this week and ignore the rest for now?
```

Tags:

```json
{
  "structure": "suggestion",
  "primary_strategy": "plan",
  "secondary_strategies": ["suggest"]
}
```

### Example L

Text:

```text
That sounds lonely, especially if everyone expects you to just adapt and keep going.
```

Tags:

```json
{
  "structure": "reflection",
  "primary_strategy": "validate",
  "secondary_strategies": ["support"]
}
```

### Example M

Text:

```text
What has changed the most since the school closure: your mood, your routine, or your sense that anything matters?
```

Tags:

```json
{
  "structure": "question",
  "primary_strategy": "probe",
  "secondary_strategies": []
}
```

### Example N

Text:

```text
It may be that motivation is not the first thing to fix here. You might need stability before motivation comes back.
```

Tags:

```json
{
  "structure": "suggestion",
  "primary_strategy": "reframe",
  "secondary_strategies": ["suggest"]
}
```

### Example O

Text:

```text
I can see why that would make it hard to care about classes right now. What has felt most pointless lately?
```

Tags:

```json
{
  "structure": "hybrid",
  "primary_strategy": "validate",
  "secondary_strategies": ["probe"]
}
```

### Example P

Text:

```text
You do not have to solve the whole semester tonight. Maybe just open one reading and stay with it for five minutes.
```

Tags:

```json
{
  "structure": "suggestion",
  "primary_strategy": "plan",
  "secondary_strategies": ["support"]
}
```

### Example Q

Text:

```text
It seems like part of you is blaming yourself for a reaction that makes sense in a disrupted situation.
```

Tags:

```json
{
  "structure": "reflection",
  "primary_strategy": "reframe",
  "secondary_strategies": ["validate"]
}
```

### Example R

Text:

```text
I'm here with you. You do not sound lazy to me; you sound overwhelmed.
```

Tags:

```json
{
  "structure": "reflection",
  "primary_strategy": "support",
  "secondary_strategies": ["validate"]
}
```

## 7) Edge Cases

- A question that also contains a tiny reflective preface such as "that sounds hard" should usually stay `question` + `probe`.
- A suggestion phrased as a question such as "Would it help to try ten minutes first?" should usually be tagged by function, not punctuation; if it is offering a concrete next step, prefer `suggestion` + `plan`.
- A validating sentence that also reframes meaningfully can take `reframe` as primary if the new interpretation is the main move.
- `support` should be primary only when the response mainly conveys care or reassurance rather than inquiry, reflection, or advice.

## 8) Metrics This Supports

This taxonomy directly supports:

- number of unique strategies used across a conversation
- percentage of turns using the same primary strategy
- distribution of `structure` by friend turn position (`turn 1`, `turn 2`, `turn 3`)
- overall share of each primary strategy across all friend turns

## 9) Recommendation

For the first version, keep one primary strategy per friend turn and allow secondary strategies sparingly.

This will keep later aggregation clean and make the dataset easier to inspect manually.

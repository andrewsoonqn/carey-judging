from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


def _pick(values: list[str], seed_text: str) -> str:
    if not values:
        return ""
    index = sum(ord(char) for char in seed_text) % len(values)
    return values[index]


def _last_message(transcript: list[dict[str, Any]], speaker: str) -> dict[str, Any]:
    for message in reversed(transcript):
        if message["speaker"] == speaker:
            return message
    raise ValueError(f"No message found for speaker={speaker}")


def _contains_question(text: str) -> bool:
    return "?" in text


def _contains_plan_language(text: str) -> bool:
    lowered = text.lower()
    plan_markers = [
        "first step",
        "pick one",
        "one small",
        "for five minutes",
        "for ten minutes",
        "this week",
        "today",
        "make a list",
        "start with",
    ]
    return any(marker in lowered for marker in plan_markers)


def _contains_suggestion_language(text: str) -> bool:
    lowered = text.lower()
    markers = [
        "maybe",
        "might help",
        "would it help",
        "could",
        "try",
        "you might",
        "it may help",
        "perhaps",
    ]
    return any(marker in lowered for marker in markers)


def _contains_validation_language(text: str) -> bool:
    lowered = text.lower()
    markers = [
        "makes sense",
        "no wonder",
        "that would wear",
        "understandable",
        "a lot of people",
        "of course",
    ]
    return any(marker in lowered for marker in markers)


def _contains_support_language(text: str) -> bool:
    lowered = text.lower()
    markers = [
        "i'm sorry",
        "i am sorry",
        "i'm here",
        "i am here",
        "you do not have to",
        "you don't have to",
        "that sounds hard",
    ]
    return any(marker in lowered for marker in markers)


def _contains_reframe_language(text: str) -> bool:
    lowered = text.lower()
    markers = [
        "not just",
        "instead of",
        "it may be that",
        "might be that",
        "part of you",
        "not the first thing to fix",
    ]
    return any(marker in lowered for marker in markers)


def _contains_reflection_language(text: str) -> bool:
    lowered = text.lower()
    starters = [
        "it sounds like",
        "that sounds",
        "so even when",
        "it seems like",
        "you feel",
        "you're feeling",
        "you are feeling",
    ]
    return any(lowered.startswith(starter) for starter in starters)


@dataclass
class SimpleVictimAgent:
    name: str = "simple_victim"
    version: str = "simple_v1"

    def opening_message(self, role_card: dict[str, Any]) -> str:
        return role_card["conversation_seed"]["opening_message"]

    def reply(self, role_card: dict[str, Any], transcript: list[dict[str, Any]]) -> str:
        friend_text = _last_message(transcript, "friend")["text"]
        issue = role_card["situation"]["current_issue"]
        context = role_card["situation"].get("context", "")
        feelings = role_card["conversation_seed"].get("core_feelings", [])
        themes = role_card["conversation_seed"].get("likely_themes", [])
        seed = f"{role_card['role_card_id']}|{len(transcript)}|{friend_text}"
        feeling = _pick(feelings or ["stuck"], seed)
        theme = _pick(themes or [issue], seed)

        if _contains_question(friend_text):
            return self._answer_question(
                friend_text, issue, context, feeling, theme, seed
            )

        if _contains_plan_language(friend_text) or _contains_suggestion_language(
            friend_text
        ):
            return self._react_to_suggestion(context, feeling, theme, seed)

        return self._elaborate(issue, context, feeling, theme, seed)

    def _answer_question(
        self,
        friend_text: str,
        issue: str,
        context: str,
        feeling: str,
        theme: str,
        seed: str,
    ) -> str:
        lowered = friend_text.lower()
        if "when" in lowered:
            options = [
                f"Usually when I sit down and try to start. That's when the {feeling} feeling hits the hardest.",
                f"Mostly at the start of the day, when I know I should be doing something and just cannot get moving.",
                f"It gets strongest when I'm alone with it and have too much time to think about the {theme} part.",
            ]
            return _pick(options, seed)

        options = [
            f"I think it's mostly the {theme} part. Since {context.lower()}, I've felt pretty {feeling}.",
            f"Honestly, {theme} has been the hardest part. I keep feeling {feeling} about it.",
            f"Probably the {theme} side of it. That's where I notice the {feeling} feeling most.",
        ]
        return _pick(options, seed)

    def _react_to_suggestion(
        self, context: str, feeling: str, theme: str, seed: str
    ) -> str:
        options = [
            f"That probably makes sense. I think small steps would feel less overwhelming right now.",
            f"I could maybe try that. I'm still feeling pretty {feeling}, but smaller sounds more doable.",
            f"Yeah, that feels more realistic than trying to fix everything at once. The {theme} part still gets to me, though.",
        ]
        return _pick(options, seed)

    def _elaborate(
        self, issue: str, context: str, feeling: str, theme: str, seed: str
    ) -> str:
        options = [
            f"Yeah, that's pretty much it. The {theme} part has been sitting with me for a while.",
            f"Exactly. It all ties back to feeling {feeling} since {context.lower()}.",
            f"That's what it feels like. I keep circling back to {theme} and not knowing how to get unstuck.",
        ]
        return _pick(options, seed)


@dataclass
class SimpleFriendAgent:
    name: str = "simple_friend"
    version: str = "simple_v1"

    def reply(self, transcript: list[dict[str, Any]]) -> str:
        latest_victim = _last_message(transcript, "victim")["text"].strip()
        friend_turn_index = (
            sum(1 for message in transcript if message["speaker"] == "friend") + 1
        )

        if friend_turn_index == 1:
            return f"That sounds really tough. What part of it has been hitting you the hardest lately?"

        if friend_turn_index == 2:
            stem = self._reflect_stem(latest_victim)
            return f"{stem} When do you notice it the most?"

        return "That makes sense. Maybe the first step is keeping the next step really small instead of trying to solve all of it at once."

    def _reflect_stem(self, victim_text: str) -> str:
        cleaned = re.sub(r"[.?!]+$", "", victim_text)
        cleaned = re.sub(
            r"^(honestly|yeah|maybe|probably|i think)\s*,?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        lowered = cleaned[:1].lower() + cleaned[1:] if cleaned else cleaned
        return f"It sounds like {lowered}."


@dataclass
class HeuristicTurnTagger:
    name: str = "heuristic_tagger"
    version: str = "tagger_v1"
    taxonomy_version: str = "taxonomy_v1"

    def tag_turn(
        self,
        transcript: list[dict[str, Any]],
        friend_message: dict[str, Any],
        message_position_1_based: int,
    ) -> dict[str, Any]:
        text = friend_message["text"]
        structure = self._structure(text)
        primary_strategy, secondary = self._strategies(text, structure)
        return {
            "friend_turn_index": friend_message["turn_index"],
            "message_position_1_based": message_position_1_based,
            "text": text,
            "structure": structure,
            "primary_strategy": primary_strategy,
            "secondary_strategies": secondary,
            "notes": self._note(structure, primary_strategy, secondary),
            "confidence": 0.7,
        }

    def _structure(self, text: str) -> str:
        has_question = _contains_question(text)
        has_suggestion = _contains_plan_language(text) or _contains_suggestion_language(
            text
        )
        has_reflection = (
            _contains_reflection_language(text)
            or _contains_validation_language(text)
            or _contains_support_language(text)
        )

        if has_question and not has_suggestion and not has_reflection:
            return "question"
        if has_suggestion and not has_question and not has_reflection:
            return "suggestion"
        if has_reflection and not has_question and not has_suggestion:
            return "reflection"
        if has_suggestion and not has_reflection and has_question:
            return "suggestion"
        if has_question and has_reflection:
            return "hybrid"
        if has_suggestion and has_reflection:
            return "hybrid"
        return "reflection"

    def _strategies(self, text: str, structure: str) -> tuple[str, list[str]]:
        candidates: list[str] = []
        if _contains_reframe_language(text):
            candidates.append("reframe")
        if _contains_plan_language(text):
            candidates.append("plan")
        if _contains_suggestion_language(text):
            candidates.append("suggest")
        if _contains_validation_language(text):
            candidates.append("validate")
        if _contains_support_language(text):
            candidates.append("support")
        if _contains_reflection_language(text):
            candidates.append("reflect")
        if _contains_question(text):
            candidates.append("probe")

        ordered = []
        for candidate in candidates:
            if candidate not in ordered:
                ordered.append(candidate)

        if not ordered:
            ordered = [self._fallback_strategy(structure)]

        primary = ordered[0]
        secondary = ordered[1:3]
        return primary, secondary

    def _fallback_strategy(self, structure: str) -> str:
        if structure == "question":
            return "probe"
        if structure == "suggestion":
            return "suggest"
        return "reflect"

    def _note(self, structure: str, primary: str, secondary: list[str]) -> str:
        if secondary:
            return f"{structure} turn with primary {primary} and secondary {', '.join(secondary)}."
        return f"{structure} turn with primary {primary}."

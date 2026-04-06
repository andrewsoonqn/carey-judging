from __future__ import annotations

from typing import Any, Protocol


RoleCard = dict[str, Any]
Message = dict[str, Any]


class VictimAgent(Protocol):
    name: str
    version: str

    def opening_message(self, role_card: RoleCard) -> str: ...

    def reply(self, role_card: RoleCard, transcript: list[Message]) -> str: ...


class FriendAgent(Protocol):
    name: str
    version: str

    def reply(self, transcript: list[Message]) -> str: ...


class TurnTagger(Protocol):
    name: str
    version: str
    taxonomy_version: str

    def tag_turn(
        self,
        transcript: list[Message],
        friend_message: Message,
        message_position_1_based: int,
    ) -> dict[str, Any]: ...

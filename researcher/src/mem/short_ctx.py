"""Lightweight session memory tuned for research agents.

The session keeps a rolling window of messages while ensuring the total
token footprint stays within the model's effective context budget. Older
messages are trimmed first, but we always preserve a small tail of the most
recent turns so the agent maintains short-term memory.
"""

from __future__ import annotations

import json
from collections import deque
from typing import Deque, List, Optional

from agents import SessionABC
from agents.items import TResponseInputItem

from src.mem.tokens import get_encoder
from src.models.model_register import LMModelSpec


def _item_to_serialisable(item: TResponseInputItem) -> str:
    """Normalise a session item to a JSON string for token counting."""

    if hasattr(item, "model_dump"):
        payload = item.model_dump(mode="json")  # type: ignore[call-arg]
    elif isinstance(item, dict):
        payload = item
    else:
        payload = str(item)

    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


class ResearchSession(SessionABC):
    """Session memory with simple token-based trimming for research runs."""

    def __init__(
        self,
        session_id: str,
        model_spec: LMModelSpec,
        *,
        max_tokens: Optional[int] = None,
        max_items: int = 64,
        tail_reserve: int = 6,
    ) -> None:
        self.session_id = session_id
        self._encoder = get_encoder(model_spec)
        self._max_tokens = max_tokens or model_spec.max_context_length or 4096
        self._max_items = max(1, max_items)
        self._tail_reserve = max(1, tail_reserve)
        self._items: Deque[TResponseInputItem] = deque()

    async def get_items(self, limit: int | None = None) -> List[TResponseInputItem]:
        if limit is None or limit >= len(self._items):
            return list(self._items)
        return list(self._items)[-limit:]

    async def add_items(self, items: List[TResponseInputItem]) -> None:
        for item in items:
            self._items.append(item)
        await self._trim()

    async def pop_item(self) -> Optional[TResponseInputItem]:
        if not self._items:
            return None
        return self._items.pop()

    async def clear_session(self) -> None:
        self._items.clear()

    async def _trim(self) -> None:
        """Trim history to respect item count and token budget constraints."""

        while len(self._items) > self._max_items:
            self._items.popleft()

        # Always keep at least tail_reserve items
        while len(self._items) > self._tail_reserve and self._token_count() > self._max_tokens:
            self._items.popleft()

    def _token_count(self) -> int:
        total = 0
        for item in self._items:
            text = _item_to_serialisable(item)
            total += len(self._encoder(text))
        return total


__all__ = ["ResearchSession"]

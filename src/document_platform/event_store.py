from __future__ import annotations

from collections import defaultdict

from .events import EventEnvelope


class InMemoryEventStore:
    def __init__(self) -> None:
        self._streams: dict[str, list[EventEnvelope]] = defaultdict(list)
        self._seen_event_ids: set[str] = set()

    def append(self, event: EventEnvelope) -> bool:
        if event.event_id in self._seen_event_ids:
            return False
        self._streams[event.document_id].append(event)
        self._seen_event_ids.add(event.event_id)
        return True

    def load_stream(self, document_id: str) -> list[EventEnvelope]:
        return list(self._streams[document_id])

    def replay(self, document_id: str) -> list[EventEnvelope]:
        return self.load_stream(document_id)

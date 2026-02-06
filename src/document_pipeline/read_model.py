from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .events import EventEnvelope


@dataclass
class DocumentState:
    document_id: str
    processed_event_ids: set[str] = field(default_factory=set)
    finalized: bool = False
    latest_stage: str | None = None
    data: dict[str, Any] = field(default_factory=dict)


def apply_event(state: DocumentState, event: EventEnvelope[Any]) -> DocumentState:
    event_id = str(event.event_id)
    if event_id in state.processed_event_ids:
        return state

    if state.finalized and event.event_type != "DocumentFinalized":
        return state

    state.processed_event_ids.add(event_id)
    state.latest_stage = event.event_type
    state.data[event.event_type] = event.payload

    if event.event_type == "DocumentFinalized":
        if state.finalized:
            return state
        state.finalized = True

    return state

"""Event handler data model -- mod event subscriptions across loaders."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EventType(Enum):
    """Common Minecraft mod events supported across all loaders."""
    PLAYER_JOIN = "player_join"
    PLAYER_LEAVE = "player_leave"
    PLAYER_RESPAWN = "player_respawn"
    PLAYER_ATTACK_ENTITY = "player_attack_entity"
    PLAYER_INTERACT_BLOCK = "player_interact_block"
    BLOCK_BREAK = "block_break"
    BLOCK_PLACE = "block_place"
    ENTITY_SPAWN = "entity_spawn"
    ENTITY_DEATH = "entity_death"
    SERVER_STARTING = "server_starting"
    SERVER_STARTED = "server_started"
    SERVER_STOPPING = "server_stopping"
    WORLD_TICK = "world_tick"
    WORLD_LOAD = "world_load"


class EventPriority(Enum):
    """Event handler priority levels."""
    HIGHEST = "highest"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    LOWEST = "lowest"


@dataclass
class EventHandler:
    """A single event handler method."""
    event_type: EventType
    handler_name: str
    priority: EventPriority = EventPriority.NORMAL
    body_lines: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type.value,
            "handler_name": self.handler_name,
            "priority": self.priority.value,
            "body_lines": self.body_lines,
        }

    @classmethod
    def from_dict(cls, data: dict) -> EventHandler:
        return cls(
            event_type=EventType(data["event_type"]),
            handler_name=data["handler_name"],
            priority=EventPriority(data.get("priority", "normal")),
            body_lines=data.get("body_lines", []),
        )

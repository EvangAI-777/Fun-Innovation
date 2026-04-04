"""Event handler Java codegen -- loader-specific event registration and handling."""

from __future__ import annotations

from mcstudio.model.event import EventType, EventHandler
from mcstudio.codegen.java import JavaWriter, to_java_string

# Fabric/Quilt: callback-based event registration
_FABRIC_EVENTS: dict[EventType, dict] = {
    EventType.PLAYER_JOIN: {
        "class": "net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents",
        "method": "JOIN",
        "params": "handler, sender, server",
    },
    EventType.PLAYER_LEAVE: {
        "class": "net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents",
        "method": "DISCONNECT",
        "params": "handler, server",
    },
    EventType.BLOCK_BREAK: {
        "class": "net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents",
        "method": "BEFORE",
        "params": "world, player, pos, state, entity",
        "returns": "true",
    },
    EventType.BLOCK_PLACE: {
        "class": "net.fabricmc.fabric.api.event.player.UseBlockCallback",
        "method": "EVENT",
        "params": "player, world, hand, hitResult",
        "returns": "net.minecraft.util.ActionResult.PASS",
    },
    EventType.PLAYER_ATTACK_ENTITY: {
        "class": "net.fabricmc.fabric.api.event.player.AttackEntityCallback",
        "method": "EVENT",
        "params": "player, world, hand, entity, hitResult",
        "returns": "net.minecraft.util.ActionResult.PASS",
    },
    EventType.SERVER_STARTING: {
        "class": "net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents",
        "method": "SERVER_STARTING",
        "params": "server",
    },
    EventType.SERVER_STARTED: {
        "class": "net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents",
        "method": "SERVER_STARTED",
        "params": "server",
    },
    EventType.SERVER_STOPPING: {
        "class": "net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents",
        "method": "SERVER_STOPPING",
        "params": "server",
    },
    EventType.WORLD_TICK: {
        "class": "net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents",
        "method": "END_WORLD_TICK",
        "params": "world",
    },
    EventType.WORLD_LOAD: {
        "class": "net.fabricmc.fabric.api.event.lifecycle.v1.ServerWorldEvents",
        "method": "LOAD",
        "params": "server, world",
    },
    EventType.ENTITY_SPAWN: {
        "class": "net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents",
        "method": "ENTITY_LOAD",
        "params": "entity, world",
    },
    EventType.ENTITY_DEATH: {
        "class": "net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents",
        "method": "AFTER_DEATH",
        "params": "entity, damageSource",
    },
    EventType.PLAYER_RESPAWN: {
        "class": "net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents",
        "method": "AFTER_RESPAWN",
        "params": "oldPlayer, newPlayer, alive",
    },
    EventType.PLAYER_INTERACT_BLOCK: {
        "class": "net.fabricmc.fabric.api.event.player.UseBlockCallback",
        "method": "EVENT",
        "params": "player, world, hand, hitResult",
        "returns": "net.minecraft.util.ActionResult.PASS",
    },
}

# Forge: @SubscribeEvent annotation on MinecraftForge.EVENT_BUS
_FORGE_EVENTS: dict[EventType, dict] = {
    EventType.PLAYER_JOIN: {"class": "net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedInEvent", "param": "event"},
    EventType.PLAYER_LEAVE: {"class": "net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent", "param": "event"},
    EventType.PLAYER_RESPAWN: {"class": "net.minecraftforge.event.entity.player.PlayerEvent.PlayerRespawnEvent", "param": "event"},
    EventType.PLAYER_ATTACK_ENTITY: {"class": "net.minecraftforge.event.entity.player.AttackEntityEvent", "param": "event"},
    EventType.PLAYER_INTERACT_BLOCK: {"class": "net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickBlock", "param": "event"},
    EventType.BLOCK_BREAK: {"class": "net.minecraftforge.event.level.BlockEvent.BreakEvent", "param": "event"},
    EventType.BLOCK_PLACE: {"class": "net.minecraftforge.event.level.BlockEvent.EntityPlaceEvent", "param": "event"},
    EventType.ENTITY_SPAWN: {"class": "net.minecraftforge.event.entity.EntityJoinLevelEvent", "param": "event"},
    EventType.ENTITY_DEATH: {"class": "net.minecraftforge.event.entity.living.LivingDeathEvent", "param": "event"},
    EventType.SERVER_STARTING: {"class": "net.minecraftforge.event.server.ServerStartingEvent", "param": "event"},
    EventType.SERVER_STARTED: {"class": "net.minecraftforge.event.server.ServerStartedEvent", "param": "event"},
    EventType.SERVER_STOPPING: {"class": "net.minecraftforge.event.server.ServerStoppingEvent", "param": "event"},
    EventType.WORLD_TICK: {"class": "net.minecraftforge.event.TickEvent.LevelTickEvent", "param": "event"},
    EventType.WORLD_LOAD: {"class": "net.minecraftforge.event.level.LevelEvent.Load", "param": "event"},
}

# NeoForge: @EventBusSubscriber with NeoForge.EVENT_BUS
_NEOFORGE_EVENTS: dict[EventType, dict] = {
    EventType.PLAYER_JOIN: {"class": "net.neoforged.neoforge.event.entity.player.PlayerEvent.PlayerLoggedInEvent", "param": "event"},
    EventType.PLAYER_LEAVE: {"class": "net.neoforged.neoforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent", "param": "event"},
    EventType.PLAYER_RESPAWN: {"class": "net.neoforged.neoforge.event.entity.player.PlayerEvent.PlayerRespawnEvent", "param": "event"},
    EventType.PLAYER_ATTACK_ENTITY: {"class": "net.neoforged.neoforge.event.entity.player.AttackEntityEvent", "param": "event"},
    EventType.PLAYER_INTERACT_BLOCK: {"class": "net.neoforged.neoforge.event.entity.player.PlayerInteractEvent.RightClickBlock", "param": "event"},
    EventType.BLOCK_BREAK: {"class": "net.neoforged.neoforge.event.level.BlockEvent.BreakEvent", "param": "event"},
    EventType.BLOCK_PLACE: {"class": "net.neoforged.neoforge.event.level.BlockEvent.EntityPlaceEvent", "param": "event"},
    EventType.ENTITY_SPAWN: {"class": "net.neoforged.neoforge.event.entity.EntityJoinLevelEvent", "param": "event"},
    EventType.ENTITY_DEATH: {"class": "net.neoforged.neoforge.event.entity.living.LivingDeathEvent", "param": "event"},
    EventType.SERVER_STARTING: {"class": "net.neoforged.neoforge.event.server.ServerStartingEvent", "param": "event"},
    EventType.SERVER_STARTED: {"class": "net.neoforged.neoforge.event.server.ServerStartedEvent", "param": "event"},
    EventType.SERVER_STOPPING: {"class": "net.neoforged.neoforge.event.server.ServerStoppingEvent", "param": "event"},
    EventType.WORLD_TICK: {"class": "net.neoforged.neoforge.event.tick.LevelTickEvent", "param": "event"},
    EventType.WORLD_LOAD: {"class": "net.neoforged.neoforge.event.level.LevelEvent.Load", "param": "event"},
}


def generate_event_handler_class(
    handlers: list[EventHandler],
    pkg: str,
    cls_name: str,
    loader: str,
) -> str:
    """Generate a Java class that handles mod events for the given loader.

    Args:
        handlers: List of event handlers to generate.
        pkg: Java package name.
        cls_name: Base mod class name (used for Events class naming).
        loader: One of "fabric", "quilt", "forge", "neoforge".

    Returns:
        Java source code string.
    """
    events_cls = f"{cls_name}Events"

    if loader in ("fabric", "quilt"):
        return _generate_fabric_events(handlers, pkg, cls_name, events_cls)
    elif loader == "forge":
        return _generate_forge_events(handlers, pkg, cls_name, events_cls)
    elif loader == "neoforge":
        return _generate_neoforge_events(handlers, pkg, cls_name, events_cls)
    else:
        raise ValueError(f"Unsupported loader for events: {loader!r}")


def _generate_fabric_events(
    handlers: list[EventHandler],
    pkg: str,
    cls_name: str,
    events_cls: str,
) -> str:
    w = JavaWriter()
    w.set_package(pkg)

    # Collect unique imports
    imports = set()
    for h in handlers:
        info = _FABRIC_EVENTS.get(h.event_type)
        if info:
            imports.add(info["class"])
    for imp in sorted(imports):
        w.add_import(imp)

    w.line()
    w.open_block(f"public class {events_cls}")

    # register() method that hooks all callbacks
    w.open_block("public static void register()")
    for h in handlers:
        info = _FABRIC_EVENTS.get(h.event_type)
        if not info:
            w.comment(f"Unsupported event: {h.event_type.value}")
            continue
        event_class = info["class"].rsplit(".", 1)[1]
        method = info["method"]
        params = info["params"]
        returns = info.get("returns")

        w.line(f"{event_class}.{method}.register(({params}) -> {{")
        for line in h.body_lines:
            w.line(f"    {line}")
        if returns:
            w.line(f"    return {returns.rsplit('.', 1)[-1]};")
        w.line("});")
    w.close_block()

    w.close_block()
    return w.build()


def _generate_forge_events(
    handlers: list[EventHandler],
    pkg: str,
    cls_name: str,
    events_cls: str,
) -> str:
    w = JavaWriter()
    w.set_package(pkg)
    w.add_import("net.minecraftforge.eventbus.api.SubscribeEvent")

    imports = set()
    for h in handlers:
        info = _FORGE_EVENTS.get(h.event_type)
        if info:
            imports.add(info["class"])
    for imp in sorted(imports):
        w.add_import(imp)

    w.line()
    w.open_block(f"public class {events_cls}")

    for h in handlers:
        info = _FORGE_EVENTS.get(h.event_type)
        if not info:
            w.comment(f"Unsupported event: {h.event_type.value}")
            continue
        event_simple = info["class"].rsplit(".", 1)[1]
        # Handle nested classes (e.g. PlayerEvent.PlayerLoggedInEvent)
        if "." in event_simple:
            event_simple = event_simple.replace(".", ".")
        w.line()
        w.annotation("SubscribeEvent")
        w.open_block(f"public static void {h.handler_name}({event_simple} {info['param']})")
        for line in h.body_lines:
            w.line(line)
        w.close_block()

    w.close_block()
    return w.build()


def _generate_neoforge_events(
    handlers: list[EventHandler],
    pkg: str,
    cls_name: str,
    events_cls: str,
) -> str:
    w = JavaWriter()
    w.set_package(pkg)
    w.add_import("net.neoforged.bus.api.SubscribeEvent")

    imports = set()
    for h in handlers:
        info = _NEOFORGE_EVENTS.get(h.event_type)
        if info:
            imports.add(info["class"])
    for imp in sorted(imports):
        w.add_import(imp)

    w.line()
    w.open_block(f"public class {events_cls}")

    for h in handlers:
        info = _NEOFORGE_EVENTS.get(h.event_type)
        if not info:
            w.comment(f"Unsupported event: {h.event_type.value}")
            continue
        event_simple = info["class"].rsplit(".", 1)[1]
        w.line()
        w.annotation("SubscribeEvent")
        w.open_block(f"public static void {h.handler_name}({event_simple} {info['param']})")
        for line in h.body_lines:
            w.line(line)
        w.close_block()

    w.close_block()
    return w.build()

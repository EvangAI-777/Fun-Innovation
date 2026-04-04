"""Entity Java class code generation."""

from __future__ import annotations

from mcstudio.model.entity import EntityType, EntityBase, AIGoalType
from mcstudio.codegen.java import JavaWriter, to_pascal_case

# Map EntityBase enum to Minecraft Java class names
_BASE_CLASS_MAP = {
    EntityBase.LIVING_ENTITY: ("LivingEntity", "net.minecraft.world.entity.LivingEntity"),
    EntityBase.MOB: ("Mob", "net.minecraft.world.entity.Mob"),
    EntityBase.PATH_FINDER_MOB: ("PathfinderMob", "net.minecraft.world.entity.PathfinderMob"),
    EntityBase.ANIMAL: ("Animal", "net.minecraft.world.entity.animal.Animal"),
    EntityBase.MONSTER: ("Monster", "net.minecraft.world.entity.monster.Monster"),
    EntityBase.WATER_ANIMAL: ("WaterAnimal", "net.minecraft.world.entity.animal.WaterAnimal"),
    EntityBase.FLYING_MOB: ("FlyingMob", "net.minecraft.world.entity.FlyingMob"),
    EntityBase.TAMABLE_ANIMAL: ("TamableAnimal", "net.minecraft.world.entity.TamableAnimal"),
}

# Map AIGoalType to Minecraft goal class names and imports
_GOAL_CLASS_MAP = {
    AIGoalType.FLOAT_SWIM: ("FloatGoal", "net.minecraft.world.entity.ai.goal.FloatGoal"),
    AIGoalType.MELEE_ATTACK: ("MeleeAttackGoal", "net.minecraft.world.entity.ai.goal.MeleeAttackGoal"),
    AIGoalType.RANGED_ATTACK: ("RangedAttackGoal", "net.minecraft.world.entity.ai.goal.RangedAttackGoal"),
    AIGoalType.WANDER_RANDOMLY: ("WaterAvoidingRandomStrollGoal", "net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal"),
    AIGoalType.LOOK_AT_PLAYER: ("LookAtPlayerGoal", "net.minecraft.world.entity.ai.goal.LookAtPlayerGoal"),
    AIGoalType.RANDOM_LOOK_AROUND: ("RandomLookAroundGoal", "net.minecraft.world.entity.ai.goal.RandomLookAroundGoal"),
    AIGoalType.FLEE_ENTITY: ("AvoidEntityGoal", "net.minecraft.world.entity.ai.goal.AvoidEntityGoal"),
    AIGoalType.PANIC: ("PanicGoal", "net.minecraft.world.entity.ai.goal.PanicGoal"),
    AIGoalType.BREED: ("BreedGoal", "net.minecraft.world.entity.ai.goal.BreedGoal"),
    AIGoalType.TEMPT: ("TemptGoal", "net.minecraft.world.entity.ai.goal.TemptGoal"),
    AIGoalType.FOLLOW_PARENT: ("FollowParentGoal", "net.minecraft.world.entity.ai.goal.FollowParentGoal"),
    AIGoalType.EAT_BLOCK: ("EatBlockGoal", "net.minecraft.world.entity.ai.goal.EatBlockGoal"),
    AIGoalType.LEAP_AT_TARGET: ("LeapAtTargetGoal", "net.minecraft.world.entity.ai.goal.LeapAtTargetGoal"),
    AIGoalType.HURT_BY_TARGET: ("HurtByTargetGoal", "net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal"),
    AIGoalType.NEAREST_ATTACKABLE_TARGET: ("NearestAttackableTargetGoal", "net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal"),
}

# Map attribute names to Minecraft Attributes constants
_ATTRIBUTE_MAP = {
    "max_health": "Attributes.MAX_HEALTH",
    "movement_speed": "Attributes.MOVEMENT_SPEED",
    "attack_damage": "Attributes.ATTACK_DAMAGE",
    "armor": "Attributes.ARMOR",
    "armor_toughness": "Attributes.ARMOR_TOUGHNESS",
    "knockback_resistance": "Attributes.KNOCKBACK_RESISTANCE",
    "follow_range": "Attributes.FOLLOW_RANGE",
    "attack_speed": "Attributes.ATTACK_SPEED",
    "attack_knockback": "Attributes.ATTACK_KNOCKBACK",
}


def generate_entity_class(entity: EntityType, package: str) -> str:
    """Generate a Java entity class extending the appropriate base class."""
    base_name, base_import = _BASE_CLASS_MAP[entity.base_class]
    cls_name = entity.java_class_name

    w = JavaWriter()
    w.set_package(package)

    # Imports
    w.add_import(base_import)
    w.add_import(
        "net.minecraft.world.entity.EntityType",
        "net.minecraft.world.level.Level",
    )

    if entity.attributes:
        w.add_import(
            "net.minecraft.world.entity.ai.attributes.AttributeSupplier",
            "net.minecraft.world.entity.ai.attributes.Attributes",
        )

    for goal in entity.goals:
        if goal.goal_type in _GOAL_CLASS_MAP:
            _, goal_import = _GOAL_CLASS_MAP[goal.goal_type]
            w.add_import(goal_import)

    if any(g.goal_type == AIGoalType.LOOK_AT_PLAYER for g in entity.goals):
        w.add_import("net.minecraft.world.entity.player.Player")

    w.line()
    w.open_block(f"public class {cls_name} extends {base_name}")

    # Constructor
    w.open_block(f"public {cls_name}(EntityType<? extends {base_name}> entityType, Level level)")
    w.line("super(entityType, level);")
    w.close_block()

    # registerGoals
    if entity.goals:
        w.line()
        w.annotation("Override")
        w.open_block("protected void registerGoals()")
        for goal in sorted(entity.goals, key=lambda g: g.priority):
            goal_expr = _goal_constructor(goal)
            w.line(f"this.goalSelector.addGoal({goal.priority}, {goal_expr});")
        w.close_block()

    # createAttributes
    if entity.attributes:
        w.line()
        w.open_block(f"public static AttributeSupplier.Builder createAttributes()")
        builder = f"{base_name}.createLivingAttributes()"
        for attr in entity.attributes:
            attr_const = _ATTRIBUTE_MAP.get(attr.attribute, f'Attributes.{attr.attribute.upper()}')
            builder += f"\n            .add({attr_const}, {attr.value})"
        w.line(f"return {builder};")
        w.close_block()

    w.close_block()
    return w.build()


def _goal_constructor(goal) -> str:
    """Generate a goal constructor expression."""
    goal_name, _ = _GOAL_CLASS_MAP.get(goal.goal_type, (goal.goal_type.value, ""))
    speed = goal.params.get("speed", 1.0)

    if goal.goal_type == AIGoalType.FLOAT_SWIM:
        return f"new {goal_name}(this)"
    if goal.goal_type == AIGoalType.MELEE_ATTACK:
        return f"new {goal_name}(this, {speed}, true)"
    if goal.goal_type == AIGoalType.WANDER_RANDOMLY:
        return f"new {goal_name}(this, {speed})"
    if goal.goal_type == AIGoalType.LOOK_AT_PLAYER:
        dist = goal.params.get("distance", 8.0)
        return f"new {goal_name}(this, Player.class, {dist}f)"
    if goal.goal_type == AIGoalType.RANDOM_LOOK_AROUND:
        return f"new {goal_name}(this)"
    if goal.goal_type == AIGoalType.PANIC:
        return f"new {goal_name}(this, {speed})"
    if goal.goal_type == AIGoalType.BREED:
        return f"new {goal_name}(this, {speed})"
    if goal.goal_type == AIGoalType.FOLLOW_PARENT:
        return f"new {goal_name}(this, {speed})"
    if goal.goal_type == AIGoalType.EAT_BLOCK:
        return f"new {goal_name}(this)"
    if goal.goal_type == AIGoalType.LEAP_AT_TARGET:
        motion = goal.params.get("motion_y", 0.4)
        return f"new {goal_name}(this, {motion}f)"
    if goal.goal_type == AIGoalType.HURT_BY_TARGET:
        return f"new {goal_name}(this)"
    if goal.goal_type == AIGoalType.NEAREST_ATTACKABLE_TARGET:
        return f"new {goal_name}(this, Player.class, true)"
    if goal.goal_type == AIGoalType.FLEE_ENTITY:
        dist = goal.params.get("distance", 6.0)
        return f"new {goal_name}(this, Player.class, {dist}f, {speed}, {speed * 1.5})"
    if goal.goal_type == AIGoalType.TEMPT:
        return f"new {goal_name}(this, {speed}, p -> false, false)"
    if goal.goal_type == AIGoalType.RANGED_ATTACK:
        interval = goal.params.get("interval", 20)
        range_val = goal.params.get("range", 15.0)
        return f"new {goal_name}(this, {speed}, {interval}, {range_val}f)"
    return f"new {goal_name}(this)"


def generate_entity_renderer(entity: EntityType, package: str, mod_class: str) -> str:
    """Generate a stub entity renderer class."""
    cls_name = entity.java_class_name
    renderer_name = f"{cls_name}Renderer"

    w = JavaWriter()
    w.set_package(package + ".client")
    w.add_import(
        "net.minecraft.client.renderer.entity.EntityRendererProvider",
        "net.minecraft.client.renderer.entity.MobRenderer",
        "net.minecraft.client.model.EntityModel",
        "net.minecraft.client.model.geom.ModelLayers",
        "net.minecraft.resources.ResourceLocation",
        f"{package}.{cls_name}",
    )
    w.line()
    w.comment(f"Stub renderer for {cls_name} -- replace model with actual implementation")
    w.open_block(f"public class {renderer_name} extends MobRenderer<{cls_name}, EntityModel<{cls_name}>>")

    w.open_block(f"public {renderer_name}(EntityRendererProvider.Context context)")
    w.line("super(context, null, 0.5f); // TODO: provide actual model")
    w.close_block()

    w.line()
    w.annotation("Override")
    w.open_block(f"public ResourceLocation getTextureLocation({cls_name} entity)")
    w.line(f'return ResourceLocation.fromNamespaceAndPath({mod_class}.MOD_ID, "textures/entity/{entity.entity_id}.png");')
    w.close_block()

    w.close_block()
    return w.build()

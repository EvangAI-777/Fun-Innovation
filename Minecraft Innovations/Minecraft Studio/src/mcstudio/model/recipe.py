"""Recipe definitions covering all vanilla recipe types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class Recipe(Protocol):
    """Protocol for all recipe types."""
    recipe_id: str
    def recipe_type(self) -> str: ...
    def to_dict(self) -> dict: ...


@dataclass
class ShapedRecipe:
    """A shaped crafting recipe (2x2 or 3x3 grid)."""
    recipe_id: str
    pattern: list[str]
    key: dict[str, str]  # symbol -> item ID
    result: str
    count: int = 1

    def __post_init__(self) -> None:
        if not (1 <= len(self.pattern) <= 3):
            raise ValueError(f"Pattern must have 1-3 rows, got {len(self.pattern)}")
        for row in self.pattern:
            if len(row) > 3:
                raise ValueError(f"Pattern row too wide: {row!r} (max 3)")

    def recipe_type(self) -> str:
        return "crafting_shaped"

    def to_dict(self) -> dict:
        return {
            "type": self.recipe_type(),
            "recipe_id": self.recipe_id,
            "pattern": self.pattern,
            "key": self.key,
            "result": self.result,
            "count": self.count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ShapedRecipe:
        return cls(
            recipe_id=data["recipe_id"],
            pattern=data["pattern"],
            key=data["key"],
            result=data["result"],
            count=data.get("count", 1),
        )


@dataclass
class ShapelessRecipe:
    """A shapeless crafting recipe."""
    recipe_id: str
    ingredients: list[str]  # list of item IDs
    result: str
    count: int = 1

    def __post_init__(self) -> None:
        if not (1 <= len(self.ingredients) <= 9):
            raise ValueError(f"Must have 1-9 ingredients, got {len(self.ingredients)}")

    def recipe_type(self) -> str:
        return "crafting_shapeless"

    def to_dict(self) -> dict:
        return {
            "type": self.recipe_type(),
            "recipe_id": self.recipe_id,
            "ingredients": self.ingredients,
            "result": self.result,
            "count": self.count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ShapelessRecipe:
        return cls(
            recipe_id=data["recipe_id"],
            ingredients=data["ingredients"],
            result=data["result"],
            count=data.get("count", 1),
        )


@dataclass
class SmeltingRecipe:
    """A furnace smelting recipe."""
    recipe_id: str
    ingredient: str
    result: str
    experience: float = 0.1
    cooking_time: int = 200

    def recipe_type(self) -> str:
        return "smelting"

    def to_dict(self) -> dict:
        return {
            "type": self.recipe_type(),
            "recipe_id": self.recipe_id,
            "ingredient": self.ingredient,
            "result": self.result,
            "experience": self.experience,
            "cooking_time": self.cooking_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SmeltingRecipe:
        return cls(
            recipe_id=data["recipe_id"],
            ingredient=data["ingredient"],
            result=data["result"],
            experience=data.get("experience", 0.1),
            cooking_time=data.get("cooking_time", 200),
        )


@dataclass
class BlastingRecipe:
    """A blast furnace recipe (half cooking time of smelting)."""
    recipe_id: str
    ingredient: str
    result: str
    experience: float = 0.1
    cooking_time: int = 100

    def recipe_type(self) -> str:
        return "blasting"

    def to_dict(self) -> dict:
        return {
            "type": self.recipe_type(),
            "recipe_id": self.recipe_id,
            "ingredient": self.ingredient,
            "result": self.result,
            "experience": self.experience,
            "cooking_time": self.cooking_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> BlastingRecipe:
        return cls(
            recipe_id=data["recipe_id"],
            ingredient=data["ingredient"],
            result=data["result"],
            experience=data.get("experience", 0.1),
            cooking_time=data.get("cooking_time", 100),
        )


@dataclass
class SmokingRecipe:
    """A smoker recipe (half cooking time of smelting)."""
    recipe_id: str
    ingredient: str
    result: str
    experience: float = 0.1
    cooking_time: int = 100

    def recipe_type(self) -> str:
        return "smoking"

    def to_dict(self) -> dict:
        return {
            "type": self.recipe_type(),
            "recipe_id": self.recipe_id,
            "ingredient": self.ingredient,
            "result": self.result,
            "experience": self.experience,
            "cooking_time": self.cooking_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SmokingRecipe:
        return cls(
            recipe_id=data["recipe_id"],
            ingredient=data["ingredient"],
            result=data["result"],
            experience=data.get("experience", 0.1),
            cooking_time=data.get("cooking_time", 100),
        )


@dataclass
class StonecuttingRecipe:
    """A stonecutter recipe."""
    recipe_id: str
    ingredient: str
    result: str
    count: int = 1

    def recipe_type(self) -> str:
        return "stonecutting"

    def to_dict(self) -> dict:
        return {
            "type": self.recipe_type(),
            "recipe_id": self.recipe_id,
            "ingredient": self.ingredient,
            "result": self.result,
            "count": self.count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> StonecuttingRecipe:
        return cls(
            recipe_id=data["recipe_id"],
            ingredient=data["ingredient"],
            result=data["result"],
            count=data.get("count", 1),
        )


@dataclass
class SmithingRecipe:
    """A smithing table recipe (base + addition -> result)."""
    recipe_id: str
    template: str
    base: str
    addition: str
    result: str

    def recipe_type(self) -> str:
        return "smithing_transform"

    def to_dict(self) -> dict:
        return {
            "type": self.recipe_type(),
            "recipe_id": self.recipe_id,
            "template": self.template,
            "base": self.base,
            "addition": self.addition,
            "result": self.result,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SmithingRecipe:
        return cls(
            recipe_id=data["recipe_id"],
            template=data["template"],
            base=data["base"],
            addition=data["addition"],
            result=data["result"],
        )


_RECIPE_TYPE_MAP = {
    "crafting_shaped": ShapedRecipe,
    "crafting_shapeless": ShapelessRecipe,
    "smelting": SmeltingRecipe,
    "blasting": BlastingRecipe,
    "smoking": SmokingRecipe,
    "stonecutting": StonecuttingRecipe,
    "smithing_transform": SmithingRecipe,
}


def recipe_from_dict(data: dict) -> Recipe:
    """Deserialize a recipe from a dict based on its 'type' field."""
    rtype = data.get("type", "")
    cls = _RECIPE_TYPE_MAP.get(rtype)
    if cls is None:
        raise ValueError(f"Unknown recipe type: {rtype!r}")
    return cls.from_dict(data)

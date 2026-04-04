"""Palette JSON validation -- check for common errors before pipeline execution."""

from __future__ import annotations

# Standard heightmap categories that a palette should cover
EXPECTED_CATEGORIES = {"bedrock", "ground_deep", "ground_shallow", "surface", "water"}


def validate_palette(data: dict) -> list[str]:
    """Validate a palette data dictionary and return a list of error/warning messages.

    Args:
        data: Parsed JSON palette data (should contain "mappings" key).

    Returns:
        List of validation messages. Empty list means valid.
    """
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["Palette must be a JSON object"]

    mappings = data.get("mappings")
    if mappings is None:
        errors.append("Missing 'mappings' key")
        return errors

    if not isinstance(mappings, dict):
        errors.append("'mappings' must be an object")
        return errors

    if not mappings:
        errors.append("'mappings' is empty")
        return errors

    # Check each mapping entry
    for category, entry in mappings.items():
        if not isinstance(entry, dict):
            errors.append(f"Category '{category}': mapping must be an object")
            continue

        has_block = "block" in entry
        has_blocks = "blocks" in entry

        if not has_block and not has_blocks:
            errors.append(f"Category '{category}': must have 'block' or 'blocks' key")
            continue

        if has_block and has_blocks:
            errors.append(f"Category '{category}': has both 'block' and 'blocks' (use one)")

        if has_block:
            block = entry["block"]
            if not isinstance(block, str):
                errors.append(f"Category '{category}': 'block' must be a string")
            elif not block.startswith("minecraft:"):
                errors.append(f"Category '{category}': block '{block}' missing 'minecraft:' prefix")

        if has_blocks:
            blocks = entry["blocks"]
            if not isinstance(blocks, list) or not blocks:
                errors.append(f"Category '{category}': 'blocks' must be a non-empty list")
            else:
                for i, b in enumerate(blocks):
                    if not isinstance(b, str):
                        errors.append(f"Category '{category}': blocks[{i}] must be a string")
                    elif not b.startswith("minecraft:"):
                        errors.append(f"Category '{category}': block '{b}' missing 'minecraft:' prefix")

                weights = entry.get("weights")
                if weights is not None:
                    if not isinstance(weights, list):
                        errors.append(f"Category '{category}': 'weights' must be a list")
                    elif len(weights) != len(blocks):
                        errors.append(
                            f"Category '{category}': weights length ({len(weights)}) "
                            f"!= blocks length ({len(blocks)})"
                        )
                    else:
                        for i, w in enumerate(weights):
                            if not isinstance(w, (int, float)) or w < 0:
                                errors.append(f"Category '{category}': weights[{i}] must be a non-negative number")

    # Check for missing standard categories
    present = set(mappings.keys())
    missing = EXPECTED_CATEGORIES - present
    if missing:
        errors.append(f"Missing standard categories: {', '.join(sorted(missing))}")

    return errors

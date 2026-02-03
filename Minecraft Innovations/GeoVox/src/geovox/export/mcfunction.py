"""Export a VoxelGrid as .mcfunction setblock commands."""

from __future__ import annotations

from pathlib import Path

from ..core.grid import VoxelGrid


def export_mcfunction(
    grid: VoxelGrid,
    output: str | Path,
    origin: tuple[int, int, int] = (0, 0, 0),
    batch_size: int = 50000,
) -> list[Path]:
    """Export a block grid as .mcfunction files with setblock commands.

    Args:
        grid: VoxelGrid with Minecraft block name strings (post-palette).
        output: Output path (extension added automatically). If the grid
            exceeds batch_size, files are numbered (output_001.mcfunction, etc.).
        origin: Minecraft world offset added to all coordinates.
        batch_size: Maximum setblock commands per file.

    Returns:
        List of written file paths.
    """
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    ox, oy, oz = origin
    commands = []
    for (x, y, z), block in grid.cells.items():
        if not isinstance(block, str):
            continue
        commands.append(f"setblock {x + ox} {y + oy} {z + oz} {block}")

    if not commands:
        return []

    # Single file if within batch size
    if len(commands) <= batch_size:
        out_path = output.with_suffix(".mcfunction")
        out_path.write_text("\n".join(commands) + "\n")
        return [out_path]

    # Split into batched files
    paths = []
    stem = output.stem
    parent = output.parent
    for i in range(0, len(commands), batch_size):
        batch = commands[i : i + batch_size]
        batch_num = (i // batch_size) + 1
        out_path = parent / f"{stem}_{batch_num:03d}.mcfunction"
        out_path.write_text("\n".join(batch) + "\n")
        paths.append(out_path)

    return paths

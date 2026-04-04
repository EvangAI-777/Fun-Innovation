"""GeoVox command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="geovox",
        description="Real-world 3D data to Minecraft world pipeline.",
    )
    parser.add_argument("--version", action="version", version=f"geovox {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    # pipeline -- the main command
    pipe = subparsers.add_parser(
        "pipeline", help="Run a full heightmap -> palette -> export pipeline"
    )
    pipe.add_argument("input", help="Path to heightmap image (PNG, TIFF)")
    pipe.add_argument("-o", "--output", required=True, help="Output path (without extension)")
    pipe.add_argument("--palette", default=None, help="Palette JSON path(s), comma-separated for composition (default: built-in vanilla-survival)")
    pipe.add_argument("--y-min", type=int, default=0, help="Minimum Y level (default: 0)")
    pipe.add_argument("--y-max", type=int, default=128, help="Maximum Y level (default: 128)")
    pipe.add_argument("--sea-level", type=int, default=None, help="Y level for water fill (default: none)")
    pipe.add_argument("--origin", default="0,0,0", help="Minecraft origin as x,y,z (default: 0,0,0)")
    pipe.add_argument("--seed", type=int, default=None, help="Random seed for palette block selection")
    pipe.add_argument("--format", choices=["mcfunction", "structure", "litematic"], default="mcfunction", help="Export format (default: mcfunction)")

    # info -- show file metadata
    info = subparsers.add_parser("info", help="Show metadata about an input file")
    info.add_argument("input", help="Path to input file")

    # preview -- ASCII terrain preview
    preview = subparsers.add_parser("preview", help="ASCII preview of a heightmap")
    preview.add_argument("input", help="Path to heightmap image")
    preview.add_argument("--width", type=int, default=80, help="Preview width in characters")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "pipeline":
        return _cmd_pipeline(args)
    elif args.command == "info":
        return _cmd_info(args)
    elif args.command == "preview":
        return _cmd_preview(args)
    return 0


def _cmd_pipeline(args: argparse.Namespace) -> int:
    from .ingest.heightmap import ingest_heightmap
    from .palette.palette import Palette, apply_palette
    from .export.mcfunction import export_mcfunction

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        origin = tuple(int(v) for v in args.origin.split(","))
        if len(origin) != 3:
            raise ValueError
    except ValueError:
        print(f"Error: invalid origin format: {args.origin} (expected x,y,z)", file=sys.stderr)
        return 1

    # Ingest
    print(f"Reading heightmap: {input_path}")
    grid = ingest_heightmap(
        input_path,
        y_scale=(args.y_min, args.y_max),
        sea_level=args.sea_level,
    )
    print(f"  {grid}")

    # Palette
    if args.palette:
        palette_paths = [Path(p.strip()) for p in args.palette.split(",")]
        for pp in palette_paths:
            if not pp.exists():
                print(f"Error: palette not found: {pp}", file=sys.stderr)
                return 1

        if len(palette_paths) == 1:
            palette = Palette.from_json(palette_paths[0], seed=args.seed)
            print(f"Applying palette: {palette.name}")
            block_grid = apply_palette(grid, palette)
        else:
            from .palette.composer import PaletteComposer, apply_composed_palette
            grid.compute_slope()
            composer = PaletteComposer()
            for pp in palette_paths:
                p = Palette.from_json(pp, seed=args.seed)
                composer.add_layer(p)
                print(f"  Layer: {p.name}")
            print("Applying composed palette")
            block_grid = apply_composed_palette(grid, composer)
    else:
        palette = _builtin_palette(args.seed)
        print(f"Applying palette: {palette.name}")
        block_grid = apply_palette(grid, palette)

    print(f"  {block_grid}")

    # Export
    if args.format == "mcfunction":
        paths = export_mcfunction(block_grid, args.output, origin=origin)
    elif args.format == "structure":
        from .export.structure import export_structure
        paths = export_structure(block_grid, args.output, origin=origin)
    elif args.format == "litematic":
        from .export.litematic import export_litematic
        paths = export_litematic(block_grid, args.output, origin=origin)
    else:
        paths = []

    print(f"Exported {len(paths)} file(s):")
    for p in paths:
        print(f"  {p}")

    return 0


def _cmd_info(args: argparse.Namespace) -> int:
    from .ingest.heightmap import _read_heightmap

    path = Path(args.input)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    data = _read_heightmap(path)
    print(f"File: {path}")
    print(f"  Shape: {data.shape[1]}x{data.shape[0]} (width x height)")
    print(f"  Value range: {data.min():.1f} - {data.max():.1f}")
    print(f"  Mean elevation: {data.mean():.1f}")
    print(f"  Columns: {data.shape[0] * data.shape[1]:,}")
    return 0


def _cmd_preview(args: argparse.Namespace) -> int:
    import numpy as np
    from .ingest.heightmap import _read_heightmap

    path = Path(args.input)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    data = _read_heightmap(path)
    rows, cols = data.shape

    # Scale to fit terminal width
    target_w = args.width
    scale = max(1, cols // target_w)
    sampled = data[::scale, ::scale]

    d_min, d_max = sampled.min(), sampled.max()
    if d_max > d_min:
        norm = (sampled - d_min) / (d_max - d_min)
    else:
        norm = np.zeros_like(sampled)

    chars = " .:-=+*#%@"
    for row in norm:
        line = "".join(chars[min(int(v * len(chars)), len(chars) - 1)] for v in row)
        print(line)

    print(f"\n{cols}x{rows} pixels, preview at 1:{scale} scale")
    return 0


def _builtin_palette(seed: int | None = None) -> Palette:
    """Return the built-in vanilla-survival palette."""
    from .palette.palette import Palette

    return Palette(
        name="vanilla-survival (built-in)",
        seed=seed,
        mappings={
            "bedrock": {"block": "minecraft:bedrock"},
            "ground_deep": {
                "blocks": ["minecraft:stone", "minecraft:andesite", "minecraft:diorite"],
                "weights": [0.7, 0.15, 0.15],
            },
            "ground_shallow": {"block": "minecraft:dirt"},
            "surface": {"block": "minecraft:grass_block"},
            "water": {"block": "minecraft:water"},
        },
    )

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
    pipe.add_argument("--format", choices=["mcfunction", "structure", "litematic", "sponge"], default="mcfunction", help="Export format (default: mcfunction)")
    pipe.add_argument("--smooth", type=int, default=None, metavar="K", help="Smooth heightmap with KxK box filter before ingest (K must be odd)")
    pipe.add_argument("--crop", default=None, metavar="X,Z,W,H", help="Crop heightmap region before ingest")
    pipe.add_argument("--resample", default=None, metavar="W,H", help="Resample heightmap to WxH before ingest")
    pipe.add_argument("--stitch", default=None, metavar="SPEC", help="Stitch multiple heightmaps: 'a.png:0,0;b.png:256,0'")

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

    # Preprocessing (applied to raw heightmap before ingest)
    from .ingest.heightmap import _read_heightmap
    from .ingest.preprocess import smooth_heightmap, crop_heightmap, resample_heightmap

    preprocessed = False

    if args.stitch:
        from .ingest.stitch import stitch_heightmaps
        tiles = []
        try:
            for part in args.stitch.split(";"):
                part = part.strip()
                if not part:
                    continue
                path_str, coords = part.rsplit(":", 1)
                col_off, row_off = (int(v) for v in coords.split(","))
                tile_path = Path(path_str.strip())
                if not tile_path.exists():
                    print(f"Error: stitch tile not found: {tile_path}", file=sys.stderr)
                    return 1
                tile_data = _read_heightmap(tile_path)
                tiles.append((tile_data, col_off, row_off))
                print(f"  Tile: {tile_path} at ({col_off},{row_off})")
        except ValueError:
            print(f"Error: invalid stitch spec: {args.stitch}", file=sys.stderr)
            print("  Expected format: 'a.png:0,0;b.png:256,0'", file=sys.stderr)
            return 1
        raw = stitch_heightmaps(tiles)
        print(f"Stitched {len(tiles)} tiles -> {raw.shape[1]}x{raw.shape[0]}")
        preprocessed = True
    else:
        raw = _read_heightmap(input_path)

    if args.crop:
        try:
            cx, cz, cw, ch = (int(v) for v in args.crop.split(","))
        except ValueError:
            print(f"Error: invalid crop format: {args.crop} (expected x,z,w,h)", file=sys.stderr)
            return 1
        raw = crop_heightmap(raw, cx, cz, cw, ch)
        print(f"Cropped to {cw}x{ch} at ({cx},{cz})")
        preprocessed = True

    if args.resample:
        try:
            rw, rh = (int(v) for v in args.resample.split(","))
        except ValueError:
            print(f"Error: invalid resample format: {args.resample} (expected w,h)", file=sys.stderr)
            return 1
        raw = resample_heightmap(raw, rw, rh)
        print(f"Resampled to {rw}x{rh}")
        preprocessed = True

    if args.smooth:
        raw = smooth_heightmap(raw, kernel_size=args.smooth)
        print(f"Smoothed with {args.smooth}x{args.smooth} kernel")
        preprocessed = True

    # Ingest
    print(f"Reading heightmap: {input_path}")
    if preprocessed:
        from .ingest.heightmap import _fill_terrain_column, BEDROCK, GROUND_DEEP, GROUND_SHALLOW, SURFACE, WATER
        from .core.grid import VoxelGrid
        import numpy as np

        grid = VoxelGrid()
        grid.metadata = {
            "source": str(input_path),
            "source_shape": raw.shape,
            "y_scale": (args.y_min, args.y_max),
            "sea_level": args.sea_level,
            "elevation": raw,
        }
        y_min, y_max = args.y_min, args.y_max
        h_min, h_max = float(raw.min()), float(raw.max())
        if h_max == h_min:
            h_max = h_min + 1
        rows, cols = raw.shape
        for z in range(rows):
            for x in range(cols):
                normalized = (float(raw[z, x]) - h_min) / (h_max - h_min)
                height = int(y_min + normalized * (y_max - y_min))
                _fill_terrain_column(grid, x, z, height, 3)
                if args.sea_level is not None and height < args.sea_level:
                    grid.fill_column(x, z, height + 1, args.sea_level, WATER)
    else:
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
    elif args.format == "sponge":
        from .export.sponge import export_sponge
        paths = export_sponge(block_grid, args.output, origin=origin)
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

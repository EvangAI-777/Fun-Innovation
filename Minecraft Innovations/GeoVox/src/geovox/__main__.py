"""Allow running geovox as a module: python -m geovox"""

from .cli import main

raise SystemExit(main())

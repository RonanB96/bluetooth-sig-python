#!/usr/bin/env python3
"""Entry point for running the Thingy:52 example as a module.

Usage:
    python -m examples.thingy52 AA:BB:CC:DD:EE:FF [options]
"""

from __future__ import annotations

import asyncio
import sys

from .thingy52_example import main

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

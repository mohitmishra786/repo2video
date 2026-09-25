"""pytest configuration for repo2video."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ManimGL parses sys.argv at import time (manimlib.config.parse_cli) and its
# argparse rejects pytest's own flags (e.g. --cov, --co), aborting collection.
# pytest has already parsed its own argv by the time conftest is imported, so
# trimming sys.argv here is safe for pytest and unblocks `manimlib` imports.
if len(sys.argv) > 1:
    sys.argv = [sys.argv[0]]

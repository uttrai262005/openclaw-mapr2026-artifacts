"""Deprecated entrypoint.

This script was renamed to `dataset_stats_check.py` for consistency in the public release.
"""

from dataset_stats_check import main


if __name__ == "__main__":
    raise SystemExit(main())

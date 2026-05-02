"""Deprecated entrypoint.

This script was renamed to `make_dataset_summary.py` for consistency in the public release.
"""

from make_dataset_summary import main


if __name__ == "__main__":
    raise SystemExit(main())

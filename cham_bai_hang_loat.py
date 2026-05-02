"""Deprecated entrypoint.

This script was renamed to `batch_grader.py` for consistency in the public release.

Usage:
  python batch_grader.py --help
"""

from batch_grader import main


if __name__ == "__main__":
    raise SystemExit(main())

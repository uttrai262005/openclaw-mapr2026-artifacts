"""chairman-agent.py

Compatibility wrapper.

Note: filename contains '-' so it can't be imported as a normal Python module.
Use `chairman_agent.py` for imports.
"""

from __future__ import annotations

from .chairman_agent import combine_results  # re-export


if __name__ == "__main__":
    raise SystemExit("Use orchestrator.py; import combine_results from chairman_agent.py")

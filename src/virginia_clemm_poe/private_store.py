# this_file: src/virginia_clemm_poe/private_store.py
"""Private atomic JSON storage for Poe HTTP exports and account cache."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def write_private_json(path: Path, data: dict[str, Any]) -> None:
    """Create mode-0600 bytes before atomically replacing the previous export."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.parent.chmod(0o700)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".poe-", suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump(data, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)

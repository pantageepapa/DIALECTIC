from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar

T = TypeVar("T")

_CACHE_PATH: Path = Path(__file__).resolve().parent.parent / ".cache"
_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


def _load_cache(cache_name: str) -> Dict[str, Any]:
    """Load the on-disk cache file (returns empty dict if missing/corrupted)."""
    if not (_CACHE_PATH / cache_name).exists():
        return {}
    try:
        with (_CACHE_PATH / cache_name).open("r", encoding="utf-8") as fp:
            return json.load(fp)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not load cache (%s). Re-creating.", exc)
        return {}


def _save_cache(cache: Dict[str, Any], cache_name: str) -> None:
    """Persist the cache dict to disk (overwrites previous file)."""
    with (_CACHE_PATH / cache_name).open("w", encoding="utf-8") as fp:
        json.dump(cache, fp, ensure_ascii=False, indent=2)


def get(key: str, cache_name: str) -> Optional[T]:
    """Return cached value for *key* if present, else None."""
    return _load_cache(cache_name).get(key)


def set(key: str, val: Any, cache_name: str) -> None:
    """Store *value* under *key* in the on-disk cache."""
    cache = _load_cache(cache_name)
    cache[key] = val
    _save_cache(cache, cache_name)


if __name__ == "__main__":
    set("test", "test", "test")
    print(get("test", "test"))

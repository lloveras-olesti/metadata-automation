"""
config_loader.py — Load and cache config.yaml for all pipeline scripts.

Usage in any script:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from config_loader import load_config

    cfg = load_config()
    client_name = cfg["client"]["name"]
"""

from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: pip install pyyaml")

_config: dict | None = None


def load_config() -> dict:
    """
    Load config.yaml from the project root (one level above scripts/).
    Caches the result after the first call — safe to call multiple times.
    Raises FileNotFoundError if config.yaml is missing.
    """
    global _config
    if _config is None:
        path = Path(__file__).parent.parent / "config.yaml"
        if not path.exists():
            raise FileNotFoundError(
                f"config.yaml not found at {path}.\n"
                "Create one by copying config.yaml.example and filling in your client values."
            )
        with open(path, encoding="utf-8") as f:
            _config = yaml.safe_load(f)
    return _config

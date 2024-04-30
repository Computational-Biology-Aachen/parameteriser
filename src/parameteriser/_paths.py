from pathlib import Path


def _default_cache_dir(path: Path | None = None) -> Path:
    path = Path.home() / ".cache" / "parameteriser" if path is None else path
    path.mkdir(exist_ok=True, parents=True)
    return path

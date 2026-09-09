import os
from pathlib import Path


def get_chromedriver_path():
    configured = os.getenv("ORANGEHRM_CHROMEDRIVER")
    if configured:
        path = Path(configured)
        if not path.is_file():
            raise FileNotFoundError(f"ChromeDriver not found: {path}")
        return str(path)

    cache_root = Path.home() / ".cache" / "selenium" / "chromedriver" / "win64"
    candidates = sorted(
        (
            version_dir / "chromedriver.exe"
            for version_dir in cache_root.iterdir()
            if version_dir.is_dir()
        ),
        key=lambda path: path.parent.name,
        reverse=True,
    ) if cache_root.is_dir() else []

    for path in candidates:
        if path.is_file():
            return str(path)

    raise FileNotFoundError(
        "No local ChromeDriver found. Set ORANGEHRM_CHROMEDRIVER or provide "
        f"a driver under {cache_root}."
    )

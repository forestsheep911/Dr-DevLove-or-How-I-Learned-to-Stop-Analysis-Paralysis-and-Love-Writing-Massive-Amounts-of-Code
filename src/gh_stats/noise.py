"""
Noise file detection for excluding non-human edits.
"""

from typing import Iterable


NOISE_FILENAMES = {
    "package-lock.json",
    "npm-shrinkwrap.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lockb",
    "composer.lock",
    "poetry.lock",
    "pipfile.lock",
    "cargo.lock",
    "gemfile.lock",
    "mix.lock",
    "pubspec.lock",
    "podfile.lock",
    "go.sum",
}

NOISE_DIR_MARKERS = (
    "node_modules/",
    "dist/",
    "build/",
    "vendor/",
    "target/",
    "coverage/",
    ".venv/",
    "venv/",
    "env/",
    ".tox/",
    ".mypy_cache/",
    ".pytest_cache/",
    "__pycache__/",
    ".gradle/",
    ".idea/",
    ".vscode/",
    "pods/",
    "deriveddata/",
)


def is_noise_path(path: str, extra_markers: Iterable[str] = ()) -> bool:
    if not path:
        return False
    normalized = path.replace("\\", "/").lower()
    filename = normalized.rsplit("/", 1)[-1]
    if filename in NOISE_FILENAMES:
        return True
    markers = list(NOISE_DIR_MARKERS) + [m.lower() for m in extra_markers]
    wrapped = f"/{normalized}"
    for marker in markers:
        marker = marker if marker.endswith("/") else f"{marker}/"
        if f"/{marker}" in wrapped:
            return True
    return False

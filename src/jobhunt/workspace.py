from __future__ import annotations

import os
import shutil
import tomllib
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

DEFAULT_HOME = "me"


class ConfigError(Exception):
    pass


def load_toml(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(f"Missing {path}. Run `jobhunt init` first.") from None
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"{path}: invalid TOML ({exc})") from None


def resolve_home(override: str | None = None) -> Path:
    raw = override or os.environ.get("JOBHUNT_HOME") or DEFAULT_HOME
    return Path(raw).expanduser().resolve()


@dataclass
class Workspace:
    root: Path
    _cache: dict = field(default_factory=dict, repr=False)

    @property
    def profile_path(self) -> Path:
        return self.root / "profile.toml"

    @property
    def cv_path(self) -> Path:
        return self.root / "cv.toml"

    @property
    def targets_dir(self) -> Path:
        return self.root / "targets"

    @property
    def cvs_dir(self) -> Path:
        return self.root / "cvs"

    @property
    def tracker_path(self) -> Path:
        return self.root / "tracker.csv"

    @property
    def status_path(self) -> Path:
        return self.root / "STATUS.md"

    @property
    def css_override(self) -> Path:
        return self.root / "cv.css"

    def exists(self) -> bool:
        return self.profile_path.exists()

    def profile(self) -> dict:
        if "profile" not in self._cache:
            data = load_toml(self.profile_path)
            validate_profile(data, self.profile_path)
            self._cache["profile"] = data
        return self._cache["profile"]

    def cv(self) -> dict:
        if "cv" not in self._cache:
            self._cache["cv"] = load_toml(self.cv_path)
        return self._cache["cv"]

    def target(self, slug: str) -> dict:
        return load_toml(self.targets_dir / f"{slug}.toml")

    def target_slugs(self) -> list[str]:
        if not self.targets_dir.exists():
            return []
        return sorted(p.stem for p in self.targets_dir.glob("*.toml"))


def validate_profile(data: dict, path: Path) -> None:
    person = data.get("person")
    if not isinstance(person, dict) or not person.get("name"):
        raise ConfigError(f"{path}: [person] needs at least `name`.")
    salary = data.get("salary", {})
    if salary and not isinstance(salary.get("targets", {}), dict):
        raise ConfigError(f"{path}: [salary].targets must be a table, e.g. {{ fullstack = 5000 }}.")


def scaffold_files() -> list[tuple[str, bytes]]:
    base = resources.files("jobhunt") / "scaffold"
    out: list[tuple[str, bytes]] = []

    def walk(node, prefix: str) -> None:
        for child in sorted(node.iterdir(), key=lambda c: c.name):
            rel = f"{prefix}{child.name}"
            if child.is_dir():
                if child.name != "__pycache__":
                    walk(child, rel + "/")
            else:
                out.append((rel, child.read_bytes()))

    walk(base, "")
    return out


def init_workspace(root: Path, force: bool = False) -> list[Path]:
    if (root / "profile.toml").exists() and not force:
        raise ConfigError(f"{root} already has a profile. Use --force to overwrite the starter files.")
    written: list[Path] = []
    for rel, payload in scaffold_files():
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(payload)
        written.append(dest)
    (root / "cvs").mkdir(exist_ok=True)
    (root / "base").mkdir(exist_ok=True)
    return written


def copy_default_css(dest: Path) -> Path:
    src = resources.files("jobhunt") / "templates" / "cv.css"
    with resources.as_file(src) as path:
        shutil.copyfile(path, dest)
    return dest

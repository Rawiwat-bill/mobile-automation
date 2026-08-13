import os
import struct
from pathlib import Path

import yaml

# default profile is a constant; the ${PROFILE} Robot var overrides at runtime.
_DEFAULT_PROFILE = "somjai"
_PROFILE_DIR = os.path.join("testdata", "onboarding")
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # libraries/ -> repo root
_MOCK_IMAGE_CANVAS = (1280, 960)  # required committed OCR mock canvas
_PROFILE_ALIASES = {"ilove": "ntb_ilove", "somjai": "ntb_somjai"}


def load_yaml(path):
    # Backward-compatible single-file loader. Flat files pass through; a top-level
    # `profiles:` block resolves `environment.active_profile` (default somjai).
    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if isinstance(data, dict) and isinstance(data.get("profiles"), dict):
        env = data.get("environment") or {}
        active = env.get("active_profile") or _DEFAULT_PROFILE
        return data["profiles"][active]
    return data


def load_profile(profile, base_dir=_PROFILE_DIR):
    # Authoritative multi-profile resolver. Precedence:
    #   explicit profile file, then legacy name alias, then matching local override.
    # Unknown profile raises before any app launch.
    profile_names = [profile]
    alias = _PROFILE_ALIASES.get(profile)
    if alias:
        profile_names.append(alias)
    committed = next(
        (os.path.join(base_dir, f"{name}.yaml") for name in profile_names if os.path.isfile(os.path.join(base_dir, f"{name}.yaml"))),
        None,
    )
    if committed is None:
        expected = ", ".join(f"{name}.yaml" for name in profile_names)
        raise ValueError(f"Unknown onboarding profile: {profile!r} (missing {expected})")
    with open(committed, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    local_names = [profile, Path(committed).stem]
    local = next((os.path.join(base_dir, f"{name}.local.yaml") for name in local_names if os.path.isfile(os.path.join(base_dir, f"{name}.local.yaml"))), None)
    if local is not None:
        with open(local, "r", encoding="utf-8") as file:
            data = _deep_merge(data, yaml.safe_load(file) or {})
    return data


def resolve_mock_card_image(rel_path):
    # Resolve a profile's ocr.mock_card_image to an absolute path (relative to project root)
    # and validate: within project root, exists, readable PNG, 1280x960 canvas.
    abs_path = rel_path if os.path.isabs(rel_path) else os.path.normpath(os.path.join(_PROJECT_ROOT, rel_path))
    abs_path = os.path.abspath(abs_path)
    if os.path.relpath(abs_path, _PROJECT_ROOT).startswith(".."):
        raise ValueError(f"Mock image outside project root: {rel_path!r}")
    if not os.path.isfile(abs_path):
        raise ValueError(f"Mock image not found: {rel_path!r}")
    with open(abs_path, "rb") as file:
        head = file.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Mock image is not a PNG: {rel_path!r}")
    width, height = struct.unpack(">II", head[16:24])  # read PNG IHDR dims via stdlib, no PIL dependency
    if (width, height) != _MOCK_IMAGE_CANVAS:
        raise ValueError(
            f"Mock image canvas {width}x{height} != required {_MOCK_IMAGE_CANVAS[0]}x{_MOCK_IMAGE_CANVAS[1]}: {rel_path!r}"
        )
    return abs_path


def resolve_profile(profile, base_dir=_PROFILE_DIR):
    # Authoritative profile + camera binding. Returns {name, data, mock_card_image(abs)}.
    # Raises on unknown profile or invalid image — before any emulator launch.
    data = load_profile(profile, base_dir)
    rel_image = (data.get("ocr") or {}).get("mock_card_image")
    if not rel_image:
        raise ValueError(f"Profile {profile!r}: missing ocr.mock_card_image")
    return {"name": profile, "data": data, "mock_card_image": resolve_mock_card_image(rel_image)}


def _deep_merge(base, override):
    out = dict(base)
    for key, val in override.items():
        out[key] = (
            _deep_merge(base[key], val)
            if isinstance(base.get(key), dict) and isinstance(val, dict)
            else val
        )
    return out


def load_onboarding_profile():
    # Robot keyword: resolves ${PROFILE} (default somjai) via load_profile.
    from robot.libraries.BuiltIn import BuiltIn  # lazy: only meaningful inside a Robot run
    profile = BuiltIn().get_variable_value("${PROFILE}") or _DEFAULT_PROFILE
    return load_profile(profile)

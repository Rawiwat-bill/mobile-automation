"""Robot listener that removes sensitive ETB values from execution artifacts.

Robot listener API v3 lets this component redact the result model before Robot
writes output.xml and log.html. Keyword names, case identifiers, statuses, and
sanitized diagnostics remain available for troubleshooting.
"""

from __future__ import annotations

from collections.abc import Iterable
import re
from typing import Any

ROBOT_LISTENER_API_VERSION = 3
_REDACTED = "[REDACTED_PROFILE_VALUE]"
_SENSITIVE_FIELDS = (
    "citizen_id",
    "mobile_number",
    "date_of_birth",
    "laser_code",
    "otp",
    "pin",
)
_QUOTED_FIELD_PATTERN = re.compile(
    r"(?P<key>[\"'](?:" + "|".join(_SENSITIVE_FIELDS) + r")[\"'])\s*[:=]\s*"
    r"(?P<quote>[\"'])(?P<value>.*?)(?P=quote)"
)
_UNQUOTED_FIELD_PATTERN = re.compile(
    r"(?P<key>\b(?:" + "|".join(_SENSITIVE_FIELDS) + r")\b)\s*[:=]\s*"
    r"(?P<value>[^,}\]\s]+)"
)
_SENSITIVE_KEYWORDS = {
    "complete etb onboarding",
    "common onboarding flow",
    "input citizen id",
    "input mobile number",
    "select date of birth",
    "input date of birth",
    "input laser code",
    "input otp",
    "set up pin",
    "enter pin using custom keypad",
    "enter confirm pin using custom keypad",
    "input text and hide keyboard",
    "input text field",
}


def _keyword_name(name: str) -> str:
    return " ".join(str(name).replace("_", " ").split()).lower()


def _as_text(value: Any) -> str:
    return value if isinstance(value, str) else str(value)


class RobotOutputSanitizer:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self) -> None:
        self._sensitive_values: set[str] = set()

    def _remember(self, values: Iterable[Any]) -> None:
        for value in values:
            text = _as_text(value)
            if text and text not in {"None", "False", "True", "${EMPTY}"}:
                self._sensitive_values.add(text)

    def _redact_text(self, text: str) -> str:
        redacted = text
        for value in sorted(self._sensitive_values, key=len, reverse=True):
            redacted = redacted.replace(value, _REDACTED)
        return redacted

    def _redact_structured_fields(self, text: str) -> str:
        def remember_quoted(match: re.Match[str]) -> str:
            self._remember([match.group("value")])
            return f"{match.group('key')}: {match.group('quote')}{_REDACTED}{match.group('quote')}"

        def remember_unquoted(match: re.Match[str]) -> str:
            self._remember([match.group("value")])
            return f"{match.group('key')}: {_REDACTED}"

        redacted = _QUOTED_FIELD_PATTERN.sub(remember_quoted, text)
        return _UNQUOTED_FIELD_PATTERN.sub(remember_unquoted, redacted)

    def _sanitize_text(self, text: str) -> str:
        return self._redact_text(self._redact_structured_fields(text))

    def _redact_args(self, name: str, args: Iterable[Any]) -> list[Any]:
        values = list(args)
        normalized = _keyword_name(name)
        if normalized in _SENSITIVE_KEYWORDS:
            if normalized == "set up pin":
                self._remember(values[:1])
                values[0:1] = [_REDACTED]
            elif normalized in {"input text field", "input text and hide keyboard"}:
                if len(values) > 1:
                    self._remember(values[1:2])
                    values[1] = _REDACTED
            else:
                self._remember(values)
                values = [_REDACTED for _ in values]
        elif normalized == "input text" and len(values) > 1:
            locator = _as_text(values[0]).lower()
            if any(token in locator for token in ("citizen", "mobile", "dob", "laser", "otp", "pin")):
                self._remember(values[1:2])
                values[1] = _REDACTED
        return [self._sanitize_text(_as_text(value)) if isinstance(value, str) else value for value in values]

    def start_keyword(self, data: Any, result: Any) -> None:
        result.args = self._redact_args(result.name, result.args)
        if isinstance(getattr(result, "doc", None), str):
            result.doc = self._sanitize_text(result.doc)

    def end_keyword(self, data: Any, result: Any) -> None:
        if isinstance(getattr(result, "message", None), str):
            result.message = self._sanitize_text(result.message)

    def log_message(self, message: Any) -> None:
        if isinstance(getattr(message, "message", None), str):
            message.message = self._sanitize_text(message.message)

    def message(self, message: Any) -> None:
        self.log_message(message)


_listener = RobotOutputSanitizer()
ROBOT_LIBRARY_LISTENER = _listener
ROBOT_LIBRARY_SCOPE = "GLOBAL"


def start_keyword(data: Any, result: Any) -> None:
    _listener.start_keyword(data, result)


def end_keyword(data: Any, result: Any) -> None:
    _listener.end_keyword(data, result)


def log_message(message: Any) -> None:
    _listener.log_message(message)


def message(message: Any) -> None:
    _listener.message(message)

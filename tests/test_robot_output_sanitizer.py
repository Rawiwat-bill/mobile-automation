from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from libraries.robot_output_sanitizer import RobotOutputSanitizer


class RobotOutputSanitizerTests(unittest.TestCase):
    def test_structured_profile_values_are_redacted_and_remembered(self) -> None:
        sanitizer = RobotOutputSanitizer()
        text = (
            "{'profile': {'citizen_id': 'SENTINEL_CITIZEN_ID', "
            "'mobile_number': 'SENTINEL_MOBILE', 'date_of_birth': 'SENTINEL_DOB', "
            "'laser_code': 'SENTINEL_LASER', 'otp': 'SENTINEL_OTP', "
            "'pin': 'SENTINEL_PIN'}}"
        )

        redacted = sanitizer._sanitize_text(text)
        follow_up = sanitizer._sanitize_text(
            "result=SENTINEL_CITIZEN_ID SENTINEL_MOBILE SENTINEL_DOB "
            "SENTINEL_LASER SENTINEL_OTP SENTINEL_PIN"
        )

        for sentinel in (
            "SENTINEL_CITIZEN_ID",
            "SENTINEL_MOBILE",
            "SENTINEL_DOB",
            "SENTINEL_LASER",
            "SENTINEL_OTP",
            "SENTINEL_PIN",
        ):
            self.assertNotIn(sentinel, redacted)
            self.assertNotIn(sentinel, follow_up)
        self.assertIn("[REDACTED_PROFILE_VALUE]", redacted)
        self.assertIn("result=[REDACTED_PROFILE_VALUE]", follow_up)

    def test_robot_output_and_log_contain_no_profile_sentinels(self) -> None:
        with tempfile.TemporaryDirectory(prefix="robot-sanitizer-") as temp:
            root = Path(temp)
            data = root / "synthetic_profile.yaml"
            data.write_text(
                "profile:\n"
                "  citizen_id: SENTINEL_CITIZEN_ID\n"
                "  mobile_number: SENTINEL_MOBILE\n"
                "  date_of_birth: SENTINEL_DOB\n"
                "  laser_code: SENTINEL_LASER\n"
                "  otp: SENTINEL_OTP\n"
                "  pin: SENTINEL_PIN\n",
                encoding="utf-8",
            )
            suite = root / "synthetic_sanitizer.robot"
            suite.write_text(
                "*** Settings ***\n"
                f"Library    {Path('libraries/config_loader.py').resolve()}\n"
                f"Library    {Path('libraries/robot_output_sanitizer.py').resolve()}\n"
                "\n"
                "*** Test Cases ***\n"
                "Sanitize Serialized Profile\n"
                f"    ${'{'}loaded{'}'}=    Load YAML    {data}\n"
                "    ${assigned}=    Set Variable    ${loaded}\n"
                "    Log    ${assigned}\n"
                "    Input Citizen ID    SENTINEL_CITIZEN_ID\n"
                "    Input OTP    SENTINEL_OTP\n"
                "    Set Up PIN    SENTINEL_PIN\n"
                "\n"
                "*** Keywords ***\n"
                "Input Citizen ID\n"
                "    [Arguments]    ${value}\n"
                "    Log    ${value}\n"
                "\n"
                "Input OTP\n"
                "    [Arguments]    ${value}\n"
                "    Log    ${value}\n"
                "\n"
                "Set Up PIN\n"
                "    [Arguments]    ${value}\n"
                "    Log    ${value}\n",
                encoding="utf-8",
            )
            output_dir = root / "output"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "robot",
                    "--outputdir",
                    str(output_dir),
                    str(suite),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            for artifact_name in ("output.xml", "log.html"):
                artifact = (output_dir / artifact_name).read_text(encoding="utf-8")
                for sentinel in (
                    "SENTINEL_CITIZEN_ID",
                    "SENTINEL_MOBILE",
                    "SENTINEL_DOB",
                    "SENTINEL_LASER",
                    "SENTINEL_OTP",
                    "SENTINEL_PIN",
                ):
                    self.assertNotIn(sentinel, artifact, artifact_name)
            output = (output_dir / "output.xml").read_text(encoding="utf-8")
            self.assertIn("[REDACTED_PROFILE_VALUE]", output)
            self.assertIn("Sanitize Serialized Profile", output)


if __name__ == "__main__":
    unittest.main()

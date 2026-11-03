import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult, get_resource_model

ROOT = Path(__file__).resolve().parents[1]
DOB = ROOT / "resources/pages/onboarding/profile_dob.resource"


def body(path: Path, name: str) -> str:
    model = get_resource_model(str(path))
    node = next(
        n for section in model.sections for n in getattr(section, "body", [])
        if n.__class__.__name__ == "Keyword" and n.name == name
    )
    return "".join(path.read_text(encoding="utf-8").splitlines(keepends=True)[node.lineno - 1 : node.end_lineno])


class EtbDobContractTests(unittest.TestCase):
    def test_wrong_month_does_not_pass_complete_dob_check(self):
        with tempfile.TemporaryDirectory(prefix="bbl-dob-contract-") as directory:
            root = Path(directory)
            (root / "dob.resource").write_text(
                "*** Settings ***\nLibrary    String\nLibrary    Collections\n\n*** Variables ***\n${PROFILE_DOB_INPUT}    dob\n&{MONTH_MAP}    11=November\n\n*** Keywords ***\n"
                + "Normalize Digits\n    [Arguments]    ${text}\n    ${normalized}=    Replace String Using Regexp    ${text}    [^0-9]    ${EMPTY}\n    RETURN    ${normalized}\n"
                + body(DOB, "Verify DOB Field Value").replace(
                    "    ${field_text}=    Get Text    ${PROFILE_DOB_INPUT}",
                    "    ${field_text}=    Evaluate    $FIELD_TEXT",
                ),
                encoding="utf-8",
            )
            suite = root / "dob.robot"
            suite.write_text(
                "*** Settings ***\nResource    dob.resource\n\n*** Test Cases ***\n"
                "Correct Month Passes\n    Set Suite Variable    ${FIELD_TEXT}    09 November 1996\n    Verify DOB Field Value    09    11    1996\n"
                "Wrong Month Fails\n    Set Suite Variable    ${FIELD_TEXT}    09 February 1996\n    Run Keyword And Expect Error    *DOB month mismatch*    Verify DOB Field Value    09    11    1996\n\n"
                "*** Keywords ***\nGet Text\n    [Arguments]    ${locator}\n    RETURN    ${FIELD_TEXT}\n",
                encoding="utf-8",
            )
            output = io.StringIO()
            code = run(str(suite), outputdir=directory, log="NONE", report="NONE", console="none", stdout=output)
            result = ExecutionResult(str(root / "output.xml"))
            self.assertEqual(code, 0, (root / "output.xml").read_text(encoding="utf-8"))
            self.assertEqual(result.suite.tests[0].status, "PASS")
            self.assertEqual(result.suite.tests[1].status, "PASS")


if __name__ == "__main__":
    unittest.main(verbosity=2)

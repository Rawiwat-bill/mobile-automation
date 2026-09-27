from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult, get_resource_model


ROOT = Path(__file__).resolve().parents[1]
RESOURCE = ROOT / "resources/pages/etb/full_screen_rgi_page.resource"


def keyword_body(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8")
    model = get_resource_model(str(path))
    node = next(
        node
        for section in model.sections
        for node in getattr(section, "body", [])
        if node.__class__.__name__ == "Keyword" and node.name == name
    )
    return "".join(text.splitlines(keepends=True)[node.lineno - 1 : node.end_lineno])


class FullScreenRGIBranchDestinationTests(unittest.TestCase):
    def test_branch_destination_accepts_proven_webview_without_requiring_package_change(self) -> None:
        destination_body = keyword_body(RESOURCE, "Full Screen RGI Branch Destination Is Open")
        close_body = keyword_body(RESOURCE, "Close Full Screen RGI Branch Destination")
        closed_body = keyword_body(RESOURCE, "Full Screen RGI In-App Branch WebView Should Be Closed")
        self.assertNotIn("FULL_SCREEN_RGI_BRANCH_DID_NOT_LEAVE_APP", destination_body)
        self.assertIn("android.webkit.WebView", destination_body)
        self.assertIn("FULL_SCREEN_RGI_BRANCH_DESTINATION_UNPROVEN", destination_body)
        self.assertIn("IN_APP_WEBVIEW", destination_body)
        self.assertIn("EXTERNAL_WEBVIEW", destination_body)
        self.assertIn("RETURN    ${destination_mode}", destination_body)
        self.assertIn("Get WebElements", close_body)
        self.assertIn("max($header_controls, key=lambda e: e.rect['x'])", close_body)
        self.assertIn("FULL_SCREEN_RGI_BRANCH_CLOSE_CONTROL_UNPROVEN", close_body)
        self.assertIn("Execute Adb Shell    input    tap", close_body)
        self.assertIn("Execute Adb Shell    input    keyevent    4", close_body)
        self.assertIn("Full Screen RGI In-App Branch WebView Should Be Closed", close_body)
        self.assertIn("FULL_SCREEN_RGI_BRANCH_DESTINATION_MODE_UNSUPPORTED", close_body)
        self.assertIn("FULL_SCREEN_RGI_BRANCH_WEBVIEW_STILL_OPEN", closed_body)
        body = destination_body + "\n" + close_body + "\n" + closed_body

        with tempfile.TemporaryDirectory(prefix="bbl-full-screen-rgi-") as directory:
            root = Path(directory)
            resource = root / "branch_destination.resource"
            resource.write_text(
                """*** Variables ***
${DEVICE_UDID}    emulator-5556
${APP_PACKAGE}    com.bangkokbank.blue.dev
${FOREGROUND}    ${EMPTY}
${SOURCE}    ${EMPTY}
${LAST_ADB}    ${EMPTY}
${RETURN_HEADER_CONTROLS}    ${True}

*** Keywords ***
"""
                + body
                + """
Get Foreground Component
    [Arguments]    ${device_udid}
    RETURN    ${FOREGROUND}

Get Source
    RETURN    ${SOURCE}

Get Window Width
    RETURN    1080

Get Window Height
    RETURN    2424

Get WebElements
    [Arguments]    ${locator}
    IF    ${RETURN_HEADER_CONTROLS}
        ${controls}=    Evaluate    [__import__('types').SimpleNamespace(rect={'x': 827, 'y': 172, 'width': 99, 'height': 99}), __import__('types').SimpleNamespace(rect={'x': 941, 'y': 172, 'width': 99, 'height': 99})]
        RETURN    ${controls}
    END
    ${controls}=    Create List
    RETURN    ${controls}

Execute Adb Shell
    [Arguments]    @{args}
    ${joined}=    Catenate    SEPARATOR=|    @{args}
    Set Test Variable    ${LAST_ADB}    ${joined}
    Set Test Variable    ${SOURCE}    <hierarchy><android.view.ViewGroup displayed="true"/></hierarchy>
""",
                encoding="utf-8",
            )
            suite = root / "branch_destination.robot"
            suite.write_text(
                """*** Settings ***
Resource    branch_destination.resource

*** Test Cases ***
In-app WebView is a proven branch destination
    Set Test Variable    ${FOREGROUND}    com.bangkokbank.blue.dev/com.bangkokbank.blue.MainActivity
    Set Test Variable    ${SOURCE}    <hierarchy><android.webkit.WebView displayed="true"/></hierarchy>
    Full Screen RGI Branch Destination Is Open

External WebView remains accepted
    Set Test Variable    ${FOREGROUND}    com.android.chrome/com.google.android.apps.chrome.Main
    Set Test Variable    ${SOURCE}    <hierarchy><android.webkit.WebView displayed="true"/></hierarchy>
    Full Screen RGI Branch Destination Is Open

In-app WebView return uses live rightmost native close control
    Set Test Variable    ${LAST_ADB}    ${EMPTY}
    Set Test Variable    ${SOURCE}    <hierarchy><android.webkit.WebView displayed="true"/></hierarchy>
    Close Full Screen RGI Branch Destination    IN_APP_WEBVIEW
    Should Be Equal As Strings    ${LAST_ADB}    input|tap|990|221
    Should Not Contain    ${SOURCE}    android.webkit.WebView

Missing in-app close control fails closed
    Set Test Variable    ${RETURN_HEADER_CONTROLS}    ${False}
    Set Test Variable    ${SOURCE}    <hierarchy><android.webkit.WebView displayed="true"/></hierarchy>
    Run Keyword And Expect Error    *FULL_SCREEN_RGI_BRANCH_CLOSE_CONTROL_UNPROVEN*    Close Full Screen RGI Branch Destination    IN_APP_WEBVIEW

External WebView return uses Android Back
    Set Test Variable    ${LAST_ADB}    ${EMPTY}
    Close Full Screen RGI Branch Destination    EXTERNAL_WEBVIEW
    Should Be Equal As Strings    ${LAST_ADB}    input|keyevent|4

Unsupported return mode fails closed
    Run Keyword And Expect Error    *FULL_SCREEN_RGI_BRANCH_DESTINATION_MODE_UNSUPPORTED*    Close Full Screen RGI Branch Destination    UNKNOWN

Same app without WebView fails closed
    Set Test Variable    ${FOREGROUND}    com.bangkokbank.blue.dev/com.bangkokbank.blue.MainActivity
    Set Test Variable    ${SOURCE}    <hierarchy><android.view.ViewGroup displayed="true"/></hierarchy>
    Run Keyword And Expect Error    *FULL_SCREEN_RGI_BRANCH_DESTINATION_UNPROVEN*    Full Screen RGI Branch Destination Is Open
""",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            stderr = io.StringIO()
            code = run(
                str(suite),
                outputdir=directory,
                log="NONE",
                report="NONE",
                console="none",
                stdout=stdout,
                stderr=stderr,
            )
            result = ExecutionResult(str(root / "output.xml"))
            self.assertEqual(
                code,
                0,
                "\n".join(test.message for test in result.suite.tests)
                + stdout.getvalue()
                + stderr.getvalue(),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

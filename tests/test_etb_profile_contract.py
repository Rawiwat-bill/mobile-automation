"""Offline F01/F02 contract checks; never run the real runner entry point.

The current run_etb function is executed in a disposable synthetic ROOT. Its
Python/Robot/CIS boundary and device preparation functions are replaced with
closed mocks. Real CIS lifecycle functions are checked separately with a fake
profile loader and mocked transport. Robot consumer checks are static, not an
Appium run or a substitute for a complete Robot suite dry-run.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, call, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# This contract runs under Python -I and never parses real YAML. Provide a
# fail-closed module boundary so importing repository code does not depend on
# globally installed PyYAML; any unexpected YAML access fails the contract.
_yaml_stub = types.ModuleType("yaml")
def _unexpected_yaml_access(*args, **kwargs):
    raise AssertionError("PROFILE_CONTRACT_UNEXPECTED_YAML_ACCESS")
_yaml_stub.safe_load = _unexpected_yaml_access
sys.modules.setdefault("yaml", _yaml_stub)

import libraries.cis_preparation as cis_preparation

RESOURCE = ROOT / "resources/keywords/etb/etb_regression_keywords.resource"

# Runs with -I -S: no site configuration, inherited Python paths, or project
# imports. Only the exact inline Python blocks of the inspected runner execute.
_BRIDGE = r'''
import json
import os
from pathlib import Path
import sys
import types
import xml.etree.ElementTree as ET

trace = Path(os.environ["CONTRACT_TRACE"])
def record(op, **data):
    with trace.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(dict(op=op, **data)) + "\n")

def forbidden(event, args):
    if event.startswith("socket.") or event in {
        "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn"
    }:
        raise RuntimeError("OFFLINE_CONTRACT_FORBIDS_LIVE_SIDE_EFFECTS")
sys.addaudithook(forbidden)

def prepare(path, key, output):
    record("prepare", path=path, key=key)
    if os.environ.get("ETB_ENVIRONMENT") == "DEV_MOCK":
        validate_mock()
        return dict(cis_clear="NOT_APPLICABLE", cis_state_ready="NOT_REQUIRED", operation_count=0)
    return dict(cis_clear="PASS", cis_clear_result="CLEARED",
                cis_state_ready="YES", operation_count=1)
def cleanup(path, key, output):
    record("cleanup", path=path, key=key)
    return dict(cis_clear="PASS", cis_state_ready="YES")
def probe():
    record("probe")
    failed = os.environ.get("CONTRACT_PROBE_FAIL") == "1"
    return dict(ready="NO" if failed else "YES",
                transport_category="TIMEOUT" if failed else "READY")
def validate_mock():
    record("mock_validation")
    if os.environ.get("CONTRACT_MOCK_FAIL") == "1":
        raise ValueError("MOCK_CIS_CONTEXT_UNAVAILABLE")
def external(path, output, selected=None):
    record("external", path=path, selected=selected)
    return dict(cis_mode="EXTERNAL_PREPARED",
                read_only_cis_verification_capability="EXTERNAL_TEAM_CONFIRMATION",
                cis_readiness_status="EXTERNALLY_CONFIRMED",
                gate_decision="EXTERNAL_TEAM_CONFIRMATION_ACCEPTED",
                selected_testcase=selected or "ALL_ETB_CASES",
                all_required_cis_ready="YES", full_runtime_gate="OPEN")
package = types.ModuleType("libraries")
package.__path__ = [str(Path(__file__).resolve().parent / "libraries")]
module = types.ModuleType("libraries.cis_preparation")
module.prepare_cis_state = prepare
module.cleanup_cis_state = cleanup
module.probe_cis_transport = probe
module.validate_mock_build_context = validate_mock
module.verify_external_cis_readiness = external
sys.modules["libraries"] = package
sys.modules["libraries.cis_preparation"] = module

# Profile-only tests isolate target/device policy at this boundary.
# The F08 suite replaces this stub with the actual guard and closed ADB mocks.
tools_package = types.ModuleType("tools")
tools_package.__path__ = []
target_guard = types.ModuleType("tools.real_device_preflight")
def validate_target_identity(serial, execution_target, environment, package, activity, competing_package, product_release="POST_MMP_1"):
    return {"target_identity": "PASS", "build_identified": True, "build_identity": "SYNTHETIC_PROFILE_CONTRACT:0", "product_release": product_release, "operation_count": 0}
target_guard.validate_target_identity = validate_target_identity
sys.modules["tools"] = tools_package
sys.modules["tools.real_device_preflight"] = target_guard

args = sys.argv[1:]
if args and args[0] == "-":
    sys.argv = args
    exec(compile(sys.stdin.read(), "<runner-inline-python>", "exec"),
         {"__name__": "__main__"})
elif args and args[0].endswith("tools/runner/etb_runtime.py"):
    script = Path(args[0])
    sys.argv = args
    exec(
        compile(script.read_text(encoding="utf-8"), str(script), "exec"),
        {"__name__": "__main__", "__file__": str(script)},
    )
elif args and args[0].endswith("tools/appium_server.py") and args[1:] in (["--ensure"], ["--reconcile"]):
    record("appium_runtime_gate")
    print("APPIUM_RUNTIME_READY=YES driver=uiautomator2 sdk=READY receipt=PASS mode=SYNTHETIC")
elif args and args[0].endswith("tools/etb_network_preflight.py"):
    record("network_runtime_gate")
    if os.environ.get("CONTRACT_NETWORK_FAIL") == "1":
        sys.exit(3)
    print("ETB_NETWORK_GATE=LOCAL_READY upstream=NOT_CHECKED service=NOT_CHECKED")
elif args[:2] == ["-m", "robot"]:
    args = args[2:]
    cases = []
    in_tests = False
    for line in Path(args[-1]).read_text(encoding="utf-8").splitlines():
        if line.strip() == "*** Test Cases ***":
            in_tests = True
        elif in_tests and line.startswith("*** "):
            break
        elif in_tests and line.strip() and not line[0].isspace():
            cases.append(dict(name=line.strip(), tags=[]))
        elif in_tests and cases and line.strip().startswith("[Tags]"):
            cases[-1]["tags"] = line.strip().split()[1:]
    if "--test" in args:
        cases = [c for c in cases if c["name"] == args[args.index("--test") + 1]]
    if "--include" in args:
        cases = [c for c in cases if args[args.index("--include") + 1] in c["tags"]]
    if not cases:
        sys.exit(252)
    variables = [args[i + 1] for i, value in enumerate(args[:-1]) if value == "--variable"]
    record("robot_dryrun" if "--dryrun" in args else "robot",
           variables=variables, names=[c["name"] for c in cases])
    output = Path(args[args.index("--outputdir") + 1])
    output.mkdir(parents=True, exist_ok=True)
    root = ET.Element("robot")
    suite = ET.SubElement(root, "suite", name="synthetic")
    for case in cases:
        test = ET.SubElement(suite, "test", name=case["name"])
        if "--dryrun" not in args:
            ET.SubElement(test, "status", status="PASS").text = ""
    ET.ElementTree(root).write(output / "output.xml")
else:
    raise RuntimeError("UNEXPECTED_PYTHON_BOUNDARY")
'''


class RunnerProfileContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="etb-profile-contract-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.trace = self.root / "trace.jsonl"
        self.suite = self.root / "suite.robot"
        self.suite.write_text(
            (ROOT / "tests/android/etb/etb_regression.robot").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        helper = self.root / "tools/runner/etb_runtime.py"
        helper.parent.mkdir(parents=True)
        helper.write_text(
            (ROOT / "tools/runner/etb_runtime.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        evidence_index = self.root / "libraries/evidence_index.py"
        evidence_index.parent.mkdir(parents=True, exist_ok=True)
        evidence_index.write_text(
            (ROOT / "libraries/evidence_index.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        case_manifest = self.root / "configs/etb_case_set.json"
        case_manifest.parent.mkdir(parents=True, exist_ok=True)
        case_manifest.write_text(
            (ROOT / "configs/etb_case_set.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        for relative in (
            "tools/runner/etb_configuration.sh",
            "tools/runner/etb_selection.sh",
            "tools/runner/etb_preflight.sh",
            "tools/runner/etb_execution.sh",
        ):
            target = self.root / relative
            target.write_text((ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8")
        self.default_profile = self.root / "testdata/onboarding/etb_cases.local.yaml"
        self.default_profile.parent.mkdir(parents=True)
        self.default_profile.write_text("cases: {}\n", encoding="utf-8")
        self.custom_profile = self.root / "synthetic profiles" / "custom cases.yaml"
        self.custom_profile.parent.mkdir()
        self.custom_profile.write_text("cases: {}\n", encoding="utf-8")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        bridge = self.root / "bridge.py"
        bridge.write_text(_BRIDGE, encoding="utf-8")
        self.python = self.bin / "fixture-python"
        self.python.write_text(
            "#!/bin/sh\nexec " + shlex.quote(sys.executable)
            + " -I -S " + shlex.quote(str(bridge)) + ' "$@"\n',
            encoding="utf-8",
        )
        self.python.chmod(0o700)
        for command in ("adb", "appium", "robot", "hermes", "curl", "wget"):
            guard = self.bin / command
            guard.write_text(
                '#!/bin/sh\nprintf \'{"op":"forbidden_command"}\\n\' >> "$CONTRACT_TRACE"\nexit 97\n',
                encoding="utf-8",
            )
            guard.chmod(0o700)
        for name in ("home", "tmp"):
            (self.root / name).mkdir()
        self.function = (ROOT / "tools/runner/etb_runner.sh").read_text(encoding="utf-8")
        self.env = {
            "PATH": str(self.bin) + ":/usr/bin:/bin",
            "HOME": str(self.root / "home"),
            "TMPDIR": str(self.root / "tmp"),
            "CONTRACT_TRACE": str(self.trace),
            "ETB_ENVIRONMENT": "DEV",
            "ANDROID_EXECUTION_TARGET": "DIAGNOSTIC_CONTROL",
            "ETB_DISK_WARN_GB": "0",
            "ETB_DISK_FAIL_GB": "0",
        }

    def run_fixture(self, args=None, env=None):
        settings = dict(self.env)
        settings.update(env or {})
        globals_ = {
            "ROOT": self.root,
            "PYTHON_BIN": self.python,
            "ETB_SUITE": self.suite,
            "ETB_OUTPUT": self.root / "reports",
            "REAL_DEVICE_PREFLIGHT": self.root / "must-not-be-called.py",
        }
        script = "set -euo pipefail\n" + "\n".join(
            name + "=" + shlex.quote(str(value)) for name, value in globals_.items()
        ) + "\n" + self.function
        for name in ("prepare_dev_environment", "prepare_sit_environment", "prepare_dev_mock_environment"):
            script += '\n' + name + '() { printf \'{"op":"device_preflight_stub"}\\n\' >> "$CONTRACT_TRACE"; }\n'
        script += '\nrun_etb "$@"\n'
        result = subprocess.run(
            ["/bin/bash", "--noprofile", "--norc", "-c", script,
             "profile-contract", "etb", *(args if args is not None else ["TC-ETB-013"])],
            cwd=self.root, env=settings, capture_output=True, text=True, timeout=20,
        )
        events = [json.loads(line) for line in self.trace.read_text(encoding="utf-8").splitlines()] if self.trace.exists() else []
        self.assertNotIn("forbidden_command", [event["op"] for event in events])
        return result, events

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_profile_forwarded(self, events, expected):
        robot_calls = [e for e in events if e["op"] in {"robot", "robot_dryrun"}]
        self.assertTrue(robot_calls)
        for event in robot_calls:
            values = [v for v in event["variables"] if v.startswith("ETB_CASE_PROFILES:")]
            self.assertEqual(values, ["ETB_CASE_PROFILES:" + str(expected)])

    def test_runner_syntax_and_executable_contract(self):
        self.assertEqual((ROOT / "run").stat().st_mode & 0o111, 0o111,
                         "run must retain its tracked executable mode")
        for script_path in (
            ROOT / "run",
            ROOT / "tools/runner/etb_runner.sh",
            ROOT / "tools/runner/etb_configuration.sh",
            ROOT / "tools/runner/etb_selection.sh",
            ROOT / "tools/runner/etb_preflight.sh",
            ROOT / "tools/runner/etb_execution.sh",
            ROOT / "tools/runner/android_environment.sh",
        ):
            result = subprocess.run(
                ["/bin/bash", "--noprofile", "--norc", "-n", str(script_path)],
                cwd=self.root, env=self.env, capture_output=True, text=True, timeout=10,
            )
            self.assert_success(result)

    def test_runner_is_orchestration_only(self):
        source = (ROOT / "tools/runner/etb_runner.sh").read_text(encoding="utf-8")
        for helper in (
            "etb_configuration.sh",
            "etb_selection.sh",
            "etb_preflight.sh",
            "etb_execution.sh",
        ):
            self.assertIn(helper, source)
        self.assertLessEqual(len(source.splitlines()), 60)
        for detail in (
            "com.bangkokbank.blue.dev",
            "com.bangkokbank.blue.sit",
            "target-guard",
            "cis-preflight",
            "sit-cis-readiness",
            "-m robot --outputdir",
        ):
            with self.subTest(detail=detail):
                self.assertNotIn(detail, source)

    def test_selected_013_does_not_prepare_unselected_001_in_runner(self):
        result, events = self.run_fixture()
        self.assert_success(result)
        self.assertEqual([e for e in events if e["op"] in {"prepare", "cleanup"}], [])
        calls = [e for e in events if e["op"] == "robot"]
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0]["names"][0].startswith("TC-ETB-013 "))
        self.assertEqual(len(calls[0]["names"]), 1)

    def test_custom_absolute_profile_reaches_every_robot_invocation(self):
        result, events = self.run_fixture(env={"ETB_CASE_PROFILES": str(self.custom_profile)})
        self.assert_success(result)
        self.assert_profile_forwarded(events, self.custom_profile)

    def test_relative_profile_with_spaces_is_resolved_once(self):
        result, events = self.run_fixture(env={"ETB_CASE_PROFILES": "synthetic profiles/custom cases.yaml"})
        self.assert_success(result)
        self.assert_profile_forwarded(events, self.custom_profile)

    def test_default_profile_is_forwarded(self):
        result, events = self.run_fixture()
        self.assert_success(result)
        self.assert_profile_forwarded(events, self.default_profile)

    def test_dry_run_needs_no_profile_contents_or_backend(self):
        self.default_profile.unlink()
        result, events = self.run_fixture(["TC-ETB-013", "--dry-run"])
        self.assert_success(result)
        self.assertTrue(events)
        self.assertTrue(all(e["op"] == "robot_dryrun" for e in events))
        self.assert_profile_forwarded(events, self.default_profile)

    def test_missing_profile_blocks_before_preparation_or_runtime(self):
        self.default_profile.unlink()
        result, events = self.run_fixture()
        self.assertEqual(result.returncode, 3)
        self.assertTrue(all(e["op"] == "robot_dryrun" for e in events))

    def test_failed_transport_probe_blocks_before_device_and_runtime(self):
        result, events = self.run_fixture(env={"CONTRACT_PROBE_FAIL": "1"})
        self.assertEqual(result.returncode, 3)
        self.assertNotIn("device_preflight_stub", [e["op"] for e in events])
        self.assertNotIn("robot", [e["op"] for e in events])
        self.assertEqual([e for e in events if e["op"] == "prepare"], [])

    def test_all_smoke_and_tag_selection_do_not_add_runner_mutations(self):
        for args in ([], ["--smoke"], ["--tag", "mule-warning"]):
            with self.subTest(args=args):
                self.trace.unlink(missing_ok=True)
                result, events = self.run_fixture(args)
                self.assert_success(result)
                self.assertEqual([e for e in events if e["op"] == "prepare"], [])
                self.assert_profile_forwarded(events, self.default_profile)

    def test_invalid_selector_stops_before_preparation(self):
        result, events = self.run_fixture(["TC-ETB-999"])
        self.assertEqual(result.returncode, 2)
        self.assertEqual(events, [])

    def test_sit_uses_same_custom_profile_for_audit_and_robot(self):
        result, events = self.run_fixture(env={
            "ETB_ENVIRONMENT": "SIT", "ETB_CASE_PROFILES": str(self.custom_profile),
        })
        self.assert_success(result)
        external = [e for e in events if e["op"] == "external"]
        self.assertEqual(external, [dict(op="external", path=str(self.custom_profile), selected="TC-ETB-013")])
        self.assert_profile_forwarded(events, self.custom_profile)
        self.assertEqual([e for e in events if e["op"] in {"prepare", "probe"}], [])

    def test_sit_smoke_and_tag_audit_exact_robot_selected_cases(self):
        scenarios = (
            (["--smoke"], ["TC-ETB-001", "TC-ETB-005"]),
            (["--tag", "mule-warning"], ["TC-ETB-013"]),
        )
        for args, expected_ids in scenarios:
            with self.subTest(args=args):
                self.trace.unlink(missing_ok=True)
                result, events = self.run_fixture(args, env={"ETB_ENVIRONMENT": "SIT"})
                self.assert_success(result)
                external_ids = [e["selected"] for e in events if e["op"] == "external"]
                self.assertEqual(external_ids, expected_ids)
                runtime = [e for e in events if e["op"] == "robot"]
                self.assertEqual(len(runtime), 1)
                runtime_ids = [name.split()[0] for name in runtime[0]["names"]]
                self.assertEqual(runtime_ids, expected_ids)

    def test_mock_build_keeps_context_validation_without_cis_preparation(self):
        result, events = self.run_fixture(env={
            "ETB_ENVIRONMENT": "DEV_MOCK", "CIS_READINESS_SOURCE": "MOCK_BUILD_NOT_REQUIRED",
        })
        self.assert_success(result)
        self.assertEqual([e["op"] for e in events].count("mock_validation"), 1)
        self.assertEqual([e for e in events if e["op"] in {"prepare", "probe"}], [])
        self.assert_profile_forwarded(events, self.default_profile)

    def test_mock_validation_failure_blocks_runtime(self):
        result, events = self.run_fixture(env={
            "ETB_ENVIRONMENT": "DEV_MOCK", "CIS_READINESS_SOURCE": "MOCK_BUILD_NOT_REQUIRED",
            "CONTRACT_MOCK_FAIL": "1",
        })
        self.assertEqual(result.returncode, 3)
        self.assertNotIn("robot", [e["op"] for e in events])
        self.assertNotIn("device_preflight_stub", [e["op"] for e in events])


class ProfileConsumerContractTests(unittest.TestCase):
    def test_robot_consumers_share_the_profile_variable(self):
        text = RESOURCE.read_text(encoding="utf-8")
        keywords = text.split("*** Keywords ***", 1)[1]
        consumers = [line for line in keywords.splitlines()
                     if re.search(r"(?:Prepare|Cleanup) CIS State\s|config_loader\.Load YAML\s", line)
                     and "${ETB_CASE_CONTRACT}" not in line]
        self.assertGreaterEqual(len(consumers), 12)
        for line in consumers:
            self.assertIn("${ETB_CASE_PROFILES}", line)
        self.assertNotIn("etb_cases.local.yaml", keywords)
        self.assertIn(
            "Run ETB Expected RGI After Laser Code    etb_tc_013",
            (ROOT / "tests/android/etb/etb_regression.robot").read_text(encoding="utf-8"),
        )

    def test_actual_cis_lifecycle_resolves_only_selected_synthetic_profile(self):
        data = {"cases": {
            "etb_tc_001": {"profile": {"citizen_id": "MASKED_SYNTHETIC_001"}},
            "etb_tc_013": {"profile": {"citizen_id": "MASKED_SYNTHETIC_013"}},
        }}
        with tempfile.TemporaryDirectory(prefix="cis-profile-contract-") as temporary:
            fixture = str(Path(temporary) / "synthetic.yaml")
            loads = []

            def load_yaml(path):
                self.assertEqual(path, fixture)
                loads.append(path)
                return copy.deepcopy(data)

            clear = Mock(return_value={"http_status": 200, "business_result_code": "Success"})
            with (
                patch.object(cis_preparation, "load_yaml", side_effect=load_yaml),
                patch.object(
                    cis_preparation,
                    "_load_profile",
                    side_effect=AssertionError("LOCAL_PROFILE_LOADING_FORBIDDEN"),
                ) as load_profile,
                patch.object(cis_preparation, "_clear_once", clear),
                patch.dict(os.environ, {"ETB_ENVIRONMENT": "DEV"}, clear=True),
            ):
                preparation = cis_preparation.prepare_cis_state(
                    fixture, "etb_tc_013", temporary
                )
                cleanup = cis_preparation.cleanup_cis_state(
                    fixture, "etb_tc_013", temporary
                )

            self.assertEqual(
                clear.call_args_list,
                [call("MASKED_SYNTHETIC_013"), call("MASKED_SYNTHETIC_013")],
            )
            self.assertEqual(loads, [fixture, fixture])
            self.assertEqual(preparation["cis_clear"], "PASS")
            self.assertEqual(cleanup["cis_clear"], "PASS")
            load_profile.assert_not_called()


if __name__ == "__main__":
    import hashlib
    for relative in (
        "run", "tools/runner/etb_runner.sh", "tools/runner/etb_configuration.sh", "tools/runner/etb_selection.sh", "tools/runner/etb_preflight.sh", "tools/runner/etb_execution.sh", "tools/runner/etb_runtime.py", "tools/runner/android_environment.sh", "libraries/cis_preparation.py",
        "resources/keywords/etb/etb_regression_keywords.resource",
        "tests/test_etb_profile_contract.py", "package.json",
    ):
        digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        print("CONTRACT_SOURCE_SHA256 " + relative + "=" + digest, flush=True)
    unittest.main(verbosity=2)

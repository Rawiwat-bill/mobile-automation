"""Offline safety regressions: real implementations, synthetic I/O only."""
from __future__ import annotations
import asyncio,importlib.util,json,tempfile,unittest,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import AsyncMock,Mock,patch
ROOT=Path(__file__).resolve().parents[1]
def load(name,rel):
    spec=importlib.util.spec_from_file_location(name,ROOT/rel)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
APP=load('offline_app','tools/appium_server.py')
PROXY=load('offline_proxy','tools/etb_proxy_server.py')
NET=load('offline_network','tools/etb_network_preflight.py')
RUNTIME=load('offline_runtime','tools/runner/etb_runtime.py')
class RuntimeResultTests(unittest.TestCase):
    def test_setup_error_code_must_not_be_business_execution(self):
        for code in ('AJI-001','RGI-107','RAI-033'):
            with self.subTest(code=code):
                t=ET.Element('test');ET.SubElement(t,'kw',name='setup',type='SETUP')
                self.assertEqual(RUNTIME._execution_status(t,'Setup failed: '+code),'SETUP_FAILED')
    def test_rai_marker_does_not_prove_environment_or_wrong_test_data(self):
        for marker in ('PROFILE_RESPONSE_UNEXPECTED_RAI_033','BLOCKED_BY_ENVIRONMENT_PROFILE_DATA_RAI_033','ETB_COMMON_ONBOARDING_DID_NOT_REACH_DOPA: RAI-033 != NEXT'):
            with self.subTest(marker=marker):
                outcome,blocker=RUNTIME._business_outcome('FAIL',marker)
                self.assertEqual(outcome,'FAIL')
                self.assertEqual(blocker,{'type':'OBSERVED_RESPONSE','code':'RAI-033'})
                self.assertEqual(RUNTIME._failure_origin(outcome,marker,marker),'UNKNOWN')
    def test_successful_teardown_nested_error_never_wins_body_failure(self):
        t=ET.Element('test');b=ET.SubElement(t,'kw',name='body')
        ET.SubElement(b,'status',status='FAIL').text='PROFILE_RESPONSE_UNEXPECTED_RAI_033'
        td=ET.SubElement(t,'kw',type='TEARDOWN');inner=ET.SubElement(td,'kw')
        ET.SubElement(inner,'status',status='FAIL').text='BLOCKED_BY_ENVIRONMENT_BACKEND_AJI_001'
        ET.SubElement(td,'status',status='PASS')
        self.assertEqual(RUNTIME._terminal_failure_text(t),'PROFILE_RESPONSE_UNEXPECTED_RAI_033')
    def test_finalize_ignores_handled_environment_error(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);root=ET.Element('robot');s=ET.SubElement(root,'suite');t=ET.SubElement(s,'test',name='TC-ETB-002 synthetic')
            handled=ET.SubElement(t,'kw',name='retry');ET.SubElement(handled,'msg').text='BLOCKED_BY_ENVIRONMENT_BACKEND_AJI_001'
            ET.SubElement(handled,'status',status='PASS')
            final=ET.SubElement(t,'kw',name='body');ET.SubElement(final,'status',status='FAIL').text='PROFILE_POPUP_CODE_UNPROVEN'
            ET.SubElement(t,'status',status='FAIL').text='PROFILE_POPUP_CODE_UNPROVEN'
            ET.ElementTree(root).write(p/'output.xml')
            RUNTIME.finalize_run_artifacts(str(p),'SYNTHETIC')
            result=json.loads((p/'run_result.json').read_text())['cases'][0]
            self.assertEqual(result['business_outcome'],'FAIL');self.assertEqual(result['failure_origin'],'UNKNOWN')
    def test_provenance_detects_content_change_with_same_head(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);p=root/'resources/keywords/common_onboarding.resource';p.parent.mkdir(parents=True);p.write_text('version one')
            with patch.object(RUNTIME,'_PROJECT_ROOT',root),patch.dict(RUNTIME.os.environ,{'ETB_DOB_STRATEGY':'STABLE_V1'},clear=True):
                before=RUNTIME._execution_binding();p.write_text('version two');after=RUNTIME._execution_binding()
            self.assertNotEqual(before['source_hashes'],after['source_hashes'])
            self.assertEqual(before['dob_strategy'],'STABLE_V1')
class AppiumOwnershipTests(unittest.TestCase):
    def test_reconcile_never_adopts_unknown_listener_or_overwrites_receipt(self):
        with patch.object(APP,'check_runtime_readiness',return_value=(False,'APPIUM_RUNTIME_RECEIPT_MISMATCH')),patch.object(APP,'_listener_pids',return_value={42}),patch.object(APP,'write_runtime_receipt') as write,patch.object(APP.subprocess,'Popen') as spawn,patch.object(APP.os,'kill') as kill:
            self.assertEqual(APP.reconcile_runtime_readiness(),(False,'APPIUM_UNMANAGED_LISTENER'))
            write.assert_not_called();spawn.assert_not_called();kill.assert_not_called()
    def test_reconcile_preserves_old_receipt_bytes_on_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'receipt.json';p.write_bytes(b'old receipt')
            with patch.object(APP,'RUNTIME_RECEIPT',p),patch.object(APP,'check_runtime_readiness',return_value=(False,'APPIUM_RUNTIME_RECEIPT_MISMATCH')),patch.object(APP,'_listener_pids',return_value={42}):
                APP.reconcile_runtime_readiness()
            self.assertEqual(p.read_bytes(),b'old receipt')
    def test_zero_listener_cannot_pass_receipt_check(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);driver=root/'node_modules/appium-uiautomator2-driver';driver.mkdir(parents=True)
            env={'APPIUM_HOME':str(root),'ANDROID_SDK_ROOT':str(root)}
            p=root/'receipt';p.write_text(json.dumps(APP.runtime_receipt_payload(env,pid=42)))
            with patch.object(APP,'build_environment',return_value=env),patch.object(APP,'_pid_alive',return_value=True),patch.object(APP,'_listener_pids',return_value=set()),patch.object(APP.urllib.request,'urlopen') as url:
                ready,category=APP.check_runtime_readiness(receipt_path=p)
            self.assertFalse(ready);self.assertEqual(category,'APPIUM_RUNTIME_LISTENER_MISSING');url.assert_not_called()
class NetworkGateTests(unittest.TestCase):
    def test_dev_diagnostic_network_guard_is_not_bound_to_one_emulator_serial(self):
        with patch.object(NET,'native_dns_readiness',return_value=(True,'READY')),patch.object(NET,'adb',return_value=Mock(returncode=0,stdout='device')),patch.object(NET,'get_proxy',return_value=NET.EXPECTED_PROXY),patch.object(NET,'charles_readiness',return_value=(True,'READY')):
            self.assertEqual(NET.enforce('emulator-5554','DEV','DIAGNOSTIC_CONTROL'),(True,'LOCAL_READY'))

    def test_managed_mode_uses_repo_proxy_without_charles(self):
        with patch.dict(NET.os.environ,{'ETB_NETWORK_PROXY_MODE':'MANAGED'}),patch.object(NET,'native_dns_readiness') as native_dns,patch.object(NET,'adb',return_value=Mock(returncode=0,stdout='device')),patch.object(NET,'get_proxy',return_value='10.0.2.2:8899'),patch.object(NET,'managed_proxy_readiness',return_value=(True,'READY')) as managed,patch.object(NET,'charles_readiness') as charles:
            self.assertEqual(NET.enforce('emulator-5556','DEV','DIAGNOSTIC_CONTROL',ensure_proxy=True),(True,'LOCAL_READY'))
        managed.assert_called_once_with(ensure=True);charles.assert_not_called();native_dns.assert_not_called()

    def test_invalid_proxy_mode_fails_closed(self):
        with patch.dict(NET.os.environ,{'ETB_NETWORK_PROXY_MODE':'INVALID'}),patch.object(NET,'adb',return_value=Mock(returncode=0,stdout='device')):
            with self.assertRaisesRegex(RuntimeError,'ETB_NETWORK_PROXY_MODE_INVALID'):
                NET.enforce('emulator-5556','DEV','DIAGNOSTIC_CONTROL')

    def test_ensure_starts_only_approved_missing_charles_once(self):
        with patch.object(NET, 'charles_readiness', side_effect=[(False, 'PROXY_LISTENER_MISSING'), (True, 'READY')]), patch.object(NET.subprocess, 'run', return_value=Mock(returncode=0)) as launch:
            self.assertEqual(NET.ensure_charles(), (True, 'READY'))
            self.assertEqual(launch.call_args.args[0], ['/usr/bin/open', '-a', '/Applications/Charles.app'])
            launch.assert_called_once()

    def test_ensure_never_replaces_unknown_proxy_listener(self):
        with patch.object(NET, 'charles_readiness', return_value=(False, 'PROXY_LISTENER_IDENTITY_MISMATCH')), patch.object(NET.subprocess, 'run') as launch:
            self.assertEqual(NET.ensure_charles(), (False, 'PROXY_LISTENER_IDENTITY_MISMATCH'))
            launch.assert_not_called()

    def test_ensure_charles_start_wait_is_bounded(self):
        with patch.object(NET, 'charles_readiness', return_value=(False, 'PROXY_LISTENER_MISSING')), patch.object(NET.subprocess, 'run', return_value=Mock(returncode=0)), patch.object(NET.time, 'monotonic', side_effect=[0, 31]), patch.object(NET.time, 'sleep') as sleep:
            self.assertEqual(NET.ensure_charles(), (False, 'CHARLES_START_TIMEOUT'))
            sleep.assert_not_called()

    def test_charles_ready_does_not_hide_failed_device_dns(self):
        with patch.object(NET, 'adb', return_value=Mock(returncode=0, stdout='device')), patch.object(NET, 'get_proxy', return_value=NET.EXPECTED_PROXY), patch.object(NET, 'charles_readiness', return_value=(True, 'READY')), patch.object(NET, 'native_dns_readiness', return_value=(False, 'DEV_BACKEND_DNS_UNAVAILABLE'), create=True):
            self.assertEqual(NET.enforce('emulator-5556', 'DEV', 'DIAGNOSTIC_CONTROL'), (False, 'DEV_BACKEND_DNS_UNAVAILABLE'))

    def test_native_dns_uses_apk_host_without_requiring_icmp_reply(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            apk = root / 'apps/android/app-dev.apk'
            apk.parent.mkdir(parents=True)
            with zipfile.ZipFile(apk, 'w') as archive:
                archive.writestr('assets/EnvironmentConfig.json', json.dumps({'API_BASE_URL': 'https://api.example.invalid'}))
            for stdout, expected in [('PING api.example.invalid (192.0.2.1) 56(84) bytes of data.', (True, 'READY')), ('', (False, 'DEV_BACKEND_DNS_UNAVAILABLE'))]:
                with self.subTest(stdout=stdout), patch.object(NET, 'ROOT', root), patch.object(NET, 'adb', return_value=Mock(returncode=1, stdout=stdout)) as adb:
                    self.assertEqual(NET.native_dns_readiness('emulator-5556'), expected)
                    self.assertIn('api.example.invalid', adb.call_args.args)
                    self.assertEqual(adb.call_args.args[0], 'emulator-5556')

    def test_native_dns_checks_startup_image_host_and_backend_host(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            apk = root / 'apps/android/app-dev.apk'
            apk.parent.mkdir(parents=True)
            with zipfile.ZipFile(apk, 'w') as archive:
                archive.writestr('assets/EnvironmentConfig.json', json.dumps({
                    'API_BASE_URL': 'https://api.example.invalid',
                    'IMAGE_BASE_URL': 'https://images.example.invalid/-/media/NCBD',
                }))
            responses = [
                Mock(returncode=0, stdout='PING api.example.invalid (192.0.2.1) 56(84) bytes of data.'),
                Mock(returncode=0, stdout='PING images.example.invalid (192.0.2.2) 56(84) bytes of data.'),
            ]
            with patch.object(NET, 'ROOT', root), patch.object(NET, 'adb', side_effect=responses) as adb:
                self.assertEqual(NET.native_dns_readiness('emulator-5556'), (True, 'READY'))
            self.assertEqual([call.args[-1] for call in adb.call_args_list], ['api.example.invalid', 'images.example.invalid'])

    def test_native_dns_rejects_invalid_apk_host_before_shell_command(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            apk = root / 'apps/android/app-dev.apk'
            apk.parent.mkdir(parents=True)
            with zipfile.ZipFile(apk, 'w') as archive:
                archive.writestr('assets/EnvironmentConfig.json', json.dumps({'API_BASE_URL': 'https://bad;command.invalid'}))
            with patch.object(NET, 'ROOT', root), patch.object(NET, 'adb') as adb:
                self.assertEqual(NET.native_dns_readiness('emulator-5556'), (False, 'DEV_BACKEND_CONFIG_INVALID'))
                adb.assert_not_called()

    def test_approved_charles_listener_and_device_proxy_are_required(self):
        with patch.object(NET,'native_dns_readiness',return_value=(True,'READY')),patch.object(NET,'adb',return_value=Mock(returncode=0,stdout='device')),patch.object(NET,'get_proxy',return_value='10.0.2.2:8888'),patch.object(NET.subprocess,'run',side_effect=[Mock(returncode=0,stdout='42\n'),Mock(returncode=0,stdout='/Applications/Charles.app/Contents/MacOS/Charles\n')]) as run,patch.object(NET.socket,'create_connection') as tcp,patch.object(NET,'set_proxy') as put:
            self.assertEqual(NET.enforce('emulator-5556','DEV','DIAGNOSTIC_CONTROL'),(True,'LOCAL_READY'))
        self.assertIn('-iTCP:8888',run.call_args_list[0].args[0])
        tcp.assert_called_once_with(('127.0.0.1',8888),timeout=2)
        put.assert_not_called()
    def test_old_proxy_port_is_rejected_before_listener_check(self):
        with patch.object(NET,'adb',return_value=Mock(returncode=0,stdout='device')),patch.object(NET,'get_proxy',return_value='10.0.2.2:8899'),patch.object(NET,'charles_readiness') as service:
            self.assertEqual(NET.enforce('emulator-5556','DEV','DIAGNOSTIC_CONTROL'),(False,'ETB_PROXY_DEVICE_CONFIG_MISMATCH'))
        service.assert_not_called()
    def test_missing_ambiguous_or_invalid_listeners_fail_closed(self):
        for stdout,code,category in [('',1,'PROXY_LISTENER_MISSING'),('42\n43\n',0,'PROXY_LISTENER_AMBIGUOUS'),('invalid',0,'PROXY_LISTENER_IDENTITY_MISMATCH'),('',2,'PROXY_LISTENER_CHECK_FAILED')]:
            with self.subTest(category=category),patch.object(NET.subprocess,'run',return_value=Mock(returncode=code,stdout=stdout)),patch.object(NET.socket,'create_connection') as tcp:
                self.assertEqual(NET.charles_readiness(),(False,category))
                tcp.assert_not_called()
    def test_another_process_on_8888_is_not_accepted_as_charles(self):
        for executable in ['/usr/bin/python3','/tmp/Charles.app/Contents/MacOS/Charles']:
            with self.subTest(executable=executable),patch.object(NET.subprocess,'run',side_effect=[Mock(returncode=0,stdout='42'),Mock(returncode=0,stdout=executable)]),patch.object(NET.socket,'create_connection') as tcp:
                self.assertEqual(NET.charles_readiness(),(False,'PROXY_LISTENER_IDENTITY_MISMATCH'))
                tcp.assert_not_called()
    def test_charles_tcp_failure_blocks_runtime(self):
        with patch.object(NET,'adb',return_value=Mock(returncode=0,stdout='device')),patch.object(NET,'get_proxy',return_value='10.0.2.2:8888'),patch.object(NET.subprocess,'run',side_effect=[Mock(returncode=0,stdout='42'),Mock(returncode=0,stdout=NET.CHARLES_EXECUTABLE)]),patch.object(NET.socket,'create_connection',side_effect=OSError('unreachable')):
            self.assertEqual(NET.enforce('emulator-5556','DEV','DIAGNOSTIC_CONTROL'),(False,'PROXY_TCP_UNAVAILABLE'))
    def test_config_mismatch_does_not_reconfigure_or_start_service(self):
        with patch.object(NET,'adb',return_value=Mock(returncode=0,stdout='device')),patch.object(NET,'get_proxy',return_value='OTHER'),patch.object(NET,'charles_readiness') as service,patch.object(NET,'set_proxy') as put:
            ready,category=NET.enforce('emulator-5556','DEV','DIAGNOSTIC_CONTROL')
        self.assertFalse(ready);self.assertEqual(category,'ETB_PROXY_DEVICE_CONFIG_MISMATCH');put.assert_not_called();service.assert_not_called()
    def test_other_targets_do_not_read_device_or_start_service(self):
        with patch.object(NET,'adb') as adb,patch.object(NET,'charles_readiness') as load:
            self.assertEqual(NET.enforce('physical-device','DEV','REAL'),(True,'NOT_APPLICABLE'))
            self.assertEqual(NET.enforce('emulator-5556','SIT','DIAGNOSTIC_CONTROL'),(True,'NOT_APPLICABLE'))
            adb.assert_not_called();load.assert_not_called()
    def test_local_readiness_does_not_claim_upstream_health(self):
        with patch.object(NET,'enforce',return_value=(True,'LOCAL_READY')),patch.object(NET.sys,'argv',['gate','--serial','emulator-5556','--environment','DEV','--execution-target','DIAGNOSTIC_CONTROL']),patch('builtins.print') as output:
            self.assertEqual(NET.main(),0)
        emitted=' '.join(str(a) for call in output.call_args_list for a in call.args)
        self.assertIn('upstream=NOT_CHECKED',emitted);self.assertIn('service=NOT_CHECKED',emitted)
class ProxyScopeTests(unittest.TestCase):
    def test_proxy_binds_loopback_not_all_interfaces(self):
        self.assertEqual(PROXY.HOST,'127.0.0.1')
    def test_unknown_listener_is_not_terminated_or_adopted(self):
        with patch.object(PROXY,'readiness',return_value=(False,'PROXY_LISTENER_UNMANAGED')),patch.object(PROXY,'listener_pids',return_value={55}),patch.object(PROXY.subprocess,'Popen') as spawn,patch.object(PROXY,'write_receipt') as write:
            self.assertEqual(PROXY.ensure(),(False,'PROXY_UNMANAGED_LISTENER'));spawn.assert_not_called();write.assert_not_called()
    def test_only_approved_dev_bootstrap_host_is_overridden(self):
        self.assertEqual(PROXY.upstream_host('www-u.bangkokbank.com'),'115.178.57.243')
        self.assertEqual(PROXY.upstream_host('WWW-U.BANGKOKBANK.COM'),'115.178.57.243')
        self.assertEqual(PROXY.upstream_host('iam-dev.tosulmara.com'),'iam-dev.tosulmara.com')
class ProxyReceiptBindingTests(unittest.TestCase):
    def test_receipt_binds_loopback_and_source(self):
        payload=PROXY.receipt_payload(42)
        self.assertEqual(payload['host'],'127.0.0.1')
        self.assertEqual(payload['port'],8899)
        self.assertEqual(len(payload['source_sha256']),64)
    def test_old_wildcard_receipt_requires_restart_not_silent_reuse(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'receipt.json';old=b'{"schema":"bbl-etb-forward-proxy/v1","pid":42,"host":"0.0.0.0","port":8899}'
            p.write_bytes(old)
            with patch.object(PROXY,'RECEIPT',p),patch.object(PROXY,'listener_pids',return_value={42}),patch.object(PROXY.socket,'create_connection') as tcp:
                self.assertEqual(PROXY.readiness(),(False,'PROXY_RUNTIME_RESTART_REQUIRED'))
            self.assertEqual(p.read_bytes(),old);tcp.assert_not_called()

class ProxyAsyncTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._tmp=tempfile.TemporaryDirectory()
        tdir=Path(self._tmp.name)
        self._p_log=patch.object(PROXY,'TELEMETRY_LOG',tdir/'tunnel_telemetry.jsonl')
        self._p_active=patch.object(PROXY,'ACTIVE_TUNNELS_FILE',tdir/'active_tunnels.json')
        self.telemetry_log=self._p_log.start()
        self.active_file=self._p_active.start()
        PROXY._ACTIVE_TUNNELS.clear()
    def tearDown(self):
        PROXY._ACTIVE_TUNNELS.clear()
        self._p_active.stop()
        self._p_log.stop()
        self._tmp.cleanup()
    def _read_records(self):
        if not self.telemetry_log.exists():
            return []
        return [json.loads(line) for line in self.telemetry_log.read_text(encoding='utf-8').splitlines() if line.strip()]
    def test_idle_timeout_remains_30_seconds_and_telemetry_path_is_private_local(self):
        self.assertEqual(PROXY.IDLE_TIMEOUT,30.0)
        self.assertEqual(
            PROXY.TELEMETRY_DIR,
            ROOT/'reports'/'investigation'/'tc004_god002_tunnel_telemetry'/'private_local',
        )
    async def test_header_timeout_closes_client_without_upstream(self):
        r=Mock();r.readuntil=AsyncMock(side_effect=asyncio.TimeoutError)
        w=Mock();w.drain=AsyncMock();w.wait_closed=AsyncMock()
        with patch.object(PROXY.asyncio,'open_connection',new_callable=AsyncMock) as connect:
            await PROXY.handle(r,w)
            connect.assert_not_called()
        w.close.assert_called()
    async def test_upstream_timeout_never_reports_tunnel_success(self):
        r=Mock();r.readuntil=AsyncMock(return_value=b'CONNECT example.invalid:443 HTTP/1.1\r\n\r\n')
        w=Mock();w.drain=AsyncMock();w.wait_closed=AsyncMock()
        with patch.object(PROXY.asyncio,'open_connection',new_callable=AsyncMock,side_effect=asyncio.TimeoutError):
            await PROXY.handle(r,w)
        payload=b''.join(call.args[0] for call in w.write.call_args_list)
        self.assertNotIn(b'200 Connection Established',payload);w.close.assert_called()
        records=self._read_records()
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]['close_reason'],'CONNECT_FAILURE')
    async def test_connect_uses_approved_host_override_without_changing_tunnel_target(self):
        r=Mock();r.readuntil=AsyncMock(return_value=b'CONNECT www-u.bangkokbank.com:443 HTTP/1.1\r\n\r\n');r.read=AsyncMock(return_value=b'')
        upstream_r=AsyncMock();upstream_r.read=AsyncMock(return_value=b'')
        upstream_w=Mock();upstream_w.drain=AsyncMock();upstream_w.close=Mock()
        w=Mock();w.drain=AsyncMock();w.close=Mock()
        with patch.object(PROXY.asyncio,'open_connection',new_callable=AsyncMock,return_value=(upstream_r,upstream_w)) as connect:
            await PROXY.handle(r,w)
        connect.assert_awaited_once_with('115.178.57.243',443)
        self.assertIn(b'200 Connection Established',b''.join(call.args[0] for call in w.write.call_args_list))
        records=self._read_records()
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]['target_host'],'www-u.bangkokbank.com')
        self.assertEqual(records[0]['target_port'],443)
        self.assertEqual(records[0]['close_reason'],'NORMAL_COMPLETION')
    async def test_monotonic_tunnel_ids_and_directional_byte_counts(self):
        for c_chunks,u_chunks in [([b'abc',b'de',b''],[b'1234567',b'']),([b'x',b''],[b'yz',b'12',b''])]:
            r=Mock();r.readuntil=AsyncMock(return_value=b'CONNECT iam-dev.tosulmara.com:443 HTTP/1.1\r\n\r\n')
            r.read=AsyncMock(side_effect=list(c_chunks))
            upstream_r=AsyncMock();upstream_r.read=AsyncMock(side_effect=list(u_chunks))
            upstream_w=Mock();upstream_w.drain=AsyncMock();upstream_w.close=Mock()
            w=Mock();w.drain=AsyncMock();w.close=Mock()
            with patch.object(PROXY.asyncio,'open_connection',new_callable=AsyncMock,return_value=(upstream_r,upstream_w)):
                await PROXY.handle(r,w)
        records=self._read_records()
        self.assertEqual(len(records),2)
        self.assertLess(records[0]['tunnel_id'],records[1]['tunnel_id'])
        self.assertEqual(records[1]['tunnel_id'],records[0]['tunnel_id']+1)
        self.assertEqual(records[0]['client_to_upstream_bytes'],5)
        self.assertEqual(records[0]['upstream_to_client_bytes'],7)
        self.assertIsNotNone(records[0]['last_client_to_upstream_at'])
        self.assertIsNotNone(records[0]['last_upstream_to_client_at'])
        self.assertEqual(records[1]['client_to_upstream_bytes'],1)
        self.assertEqual(records[1]['upstream_to_client_bytes'],4)
    async def test_directional_timeout_classification(self):
        never=asyncio.Future()
        async def wait_never(*_a):
            return await never
        r1=Mock();r1.readuntil=AsyncMock(return_value=b'CONNECT iam-dev.tosulmara.com:443 HTTP/1.1\r\n\r\n')
        r1.read=AsyncMock(side_effect=[b'req',asyncio.TimeoutError()])
        u1_r=AsyncMock();u1_r.read=AsyncMock(side_effect=wait_never)
        u1_w=Mock();u1_w.drain=AsyncMock();u1_w.close=Mock(side_effect=lambda *_a:(not never.done() and never.set_result(b'')))
        w1=Mock();w1.drain=AsyncMock();w1.close=Mock()
        with patch.object(PROXY.asyncio,'open_connection',new_callable=AsyncMock,return_value=(u1_r,u1_w)):
            await PROXY.handle(r1,w1)

        never2=asyncio.Future()
        async def wait_never2(*_a):
            return await never2
        r2=Mock();r2.readuntil=AsyncMock(return_value=b'CONNECT iam-dev.tosulmara.com:443 HTTP/1.1\r\n\r\n')
        r2.read=AsyncMock(side_effect=wait_never2)
        u2_r=AsyncMock();u2_r.read=AsyncMock(side_effect=[b'resp',asyncio.TimeoutError()])
        u2_w=Mock();u2_w.drain=AsyncMock();u2_w.close=Mock()
        w2=Mock();w2.drain=AsyncMock();w2.close=Mock(side_effect=lambda *_a:(not never2.done() and never2.set_result(b'')))
        with patch.object(PROXY.asyncio,'open_connection',new_callable=AsyncMock,return_value=(u2_r,u2_w)):
            await PROXY.handle(r2,w2)

        records=self._read_records()
        self.assertEqual(records[0]['close_reason'],'IDLE_TIMEOUT_CLIENT_TO_UPSTREAM')
        self.assertEqual(records[1]['close_reason'],'IDLE_TIMEOUT_UPSTREAM_TO_CLIENT')
    async def test_eof_and_reset_classification(self):
        # 1. CLIENT_EOF (client closes first while upstream is still open)
        u_wait=asyncio.Future()
        async def wait_u(*_a):
            return await u_wait
        r_ceof=Mock();r_ceof.readuntil=AsyncMock(return_value=b'CONNECT iam-dev.tosulmara.com:443 HTTP/1.1\r\n\r\n')
        r_ceof.read=AsyncMock(side_effect=[b'hello',b''])
        u_ceof_r=AsyncMock();u_ceof_r.read=AsyncMock(side_effect=wait_u)
        u_ceof_w=Mock();u_ceof_w.drain=AsyncMock();u_ceof_w.close=Mock(side_effect=lambda *_a:(not u_wait.done() and u_wait.set_result(b'')))
        w_ceof=Mock();w_ceof.drain=AsyncMock();w_ceof.close=Mock()
        with patch.object(PROXY.asyncio,'open_connection',new_callable=AsyncMock,return_value=(u_ceof_r,u_ceof_w)):
            await PROXY.handle(r_ceof,w_ceof)

        # 2. UPSTREAM_EOF (upstream closes first while client is still open)
        c_wait=asyncio.Future()
        async def wait_c(*_a):
            return await c_wait
        r_ueof=Mock();r_ueof.readuntil=AsyncMock(return_value=b'CONNECT iam-dev.tosulmara.com:443 HTTP/1.1\r\n\r\n')
        r_ueof.read=AsyncMock(side_effect=wait_c)
        u_ueof_r=AsyncMock();u_ueof_r.read=AsyncMock(side_effect=[b'world',b''])
        u_ueof_w=Mock();u_ueof_w.drain=AsyncMock();u_ueof_w.close=Mock()
        w_ueof=Mock();w_ueof.drain=AsyncMock();w_ueof.close=Mock(side_effect=lambda *_a:(not c_wait.done() and c_wait.set_result(b'')))
        with patch.object(PROXY.asyncio,'open_connection',new_callable=AsyncMock,return_value=(u_ueof_r,u_ueof_w)):
            await PROXY.handle(r_ueof,w_ueof)

        # 3. CONNECTION_RESET
        c_wait2=asyncio.Future()
        async def wait_c2(*_a):
            return await c_wait2
        r_rst=Mock();r_rst.readuntil=AsyncMock(return_value=b'CONNECT iam-dev.tosulmara.com:443 HTTP/1.1\r\n\r\n')
        r_rst.read=AsyncMock(side_effect=wait_c2)
        u_rst_r=AsyncMock();u_rst_r.read=AsyncMock(side_effect=ConnectionResetError('reset by peer'))
        u_rst_w=Mock();u_rst_w.drain=AsyncMock();u_rst_w.close=Mock()
        w_rst=Mock();w_rst.drain=AsyncMock();w_rst.close=Mock(side_effect=lambda *_a:(not c_wait2.done() and c_wait2.set_result(b'')))
        with patch.object(PROXY.asyncio,'open_connection',new_callable=AsyncMock,return_value=(u_rst_r,u_rst_w)):
            await PROXY.handle(r_rst,w_rst)

        records=self._read_records()
        self.assertEqual([rec['close_reason'] for rec in records],['CLIENT_EOF','UPSTREAM_EOF','CONNECTION_RESET'])
    async def test_sanitization_and_no_payload_persistence(self):
        secret_header=(
            b'POST http://iam-dev.tosulmara.com:8080/am/json/realms/alpha/authenticate?authIndexValue=SECRET_QUERY_VAL HTTP/1.1\r\n'
            b'Authorization: Bearer SECRET_BEARER_TOKEN_999\r\n'
            b'Cookie: iPlanetDirectoryPro=SECRET_COOKIE_888\r\n'
            b'X-Customer-Id: SENSITIVE_TEST_VALUE\r\n\r\n'
        )
        secret_client_payload=b'{"pin":"SENSITIVE_PIN","otp":"SENSITIVE_OTP","tokenId":"SECRET_BODY_TOKEN"}'
        secret_upstream_payload=b'HTTP/1.1 200 OK\r\n\r\n{"access_token":"SECRET_RESPONSE_TOKEN"}'
        r=Mock();r.readuntil=AsyncMock(return_value=secret_header)
        r.read=AsyncMock(side_effect=[secret_client_payload,b''])
        u_r=AsyncMock();u_r.read=AsyncMock(side_effect=[secret_upstream_payload,b''])
        u_w=Mock();u_w.drain=AsyncMock();u_w.close=Mock()
        w=Mock();w.drain=AsyncMock();w.close=Mock()
        with patch.object(PROXY.asyncio,'open_connection',new_callable=AsyncMock,return_value=(u_r,u_w)):
            await PROXY.handle(r,w)

        raw_log=self.telemetry_log.read_text(encoding='utf-8')
        for forbidden in (
            'SECRET_QUERY_VAL',
            'SECRET_BEARER_TOKEN_999',
            'SECRET_COOKIE_888',
            'SENSITIVE_TEST_VALUE',
            'SENSITIVE_PIN',
            'SENSITIVE_OTP',
            'SECRET_BODY_TOKEN',
            'SECRET_RESPONSE_TOKEN',
            '/am/json/realms/alpha/authenticate',
            'Authorization',
            'Cookie',
        ):
            self.assertNotIn(forbidden,raw_log)
        records=self._read_records()
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]['target_host'],'iam-dev.tosulmara.com')
        self.assertEqual(records[0]['target_port'],8080)
        self.assertEqual(PROXY.sanitize_target_host('https://user:pass@IAM-DEV.tosulmara.com:443/path?token=1'),'iam-dev.tosulmara.com')
        self.assertEqual(PROXY.sanitize_target_host('bad/host?token=secret'),'bad')
        self.assertEqual(PROXY.sanitize_target_host('bad;host'),'REDACTED_HOST')
    def test_confirm_pin_interval_and_terminal_request_correlation(self):
        state={
            'schema':'bbl-etb-proxy-tunnel-telemetry/v1',
            'tunnel_id':7,
            'target_host':'iam-dev.tosulmara.com',
            'target_port':443,
            'opened_at':'2026-11-02T08:52:09.500000+00:00',
            'closed_at':'2026-11-02T08:53:27.030000+00:00',
            'close_reason':'IDLE_TIMEOUT_UPSTREAM_TO_CLIENT',
            'client_to_upstream_bytes':2400,
            'upstream_to_client_bytes':1800,
            'last_client_to_upstream_at':'2026-11-02T08:52:57.030000+00:00',
            'last_upstream_to_client_at':'2026-11-02T08:52:42.715000+00:00',
            'activity':[
                {'direction':'client_to_upstream','at':'2026-11-02T08:52:41.890000+00:00','bytes':1200},
                {'direction':'upstream_to_client','at':'2026-11-02T08:52:42.715000+00:00','bytes':1800},
                {'direction':'client_to_upstream','at':'2026-11-02T08:52:57.030000+00:00','bytes':1200},
            ],
        }
        evaluated=PROXY.evaluate_tunnel_window(
            state,
            confirm_pin_start='2026-11-02T08:52:45.000000+00:00',
            confirm_pin_end='2026-11-02T08:52:57.000000+00:00',
            terminal_request_at='2026-11-02T08:52:57.030000+00:00',
        )
        self.assertTrue(evaluated['existed_across_confirm_pin_interval'])
        self.assertFalse(evaluated['upstream_bytes_increased_after_terminal_request'])
        self.assertEqual(evaluated['client_to_upstream_bytes_after_request'],1200)
        self.assertEqual(evaluated['upstream_to_client_bytes_after_request'],0)
        self.assertEqual(evaluated['tunnel_reuse'],'REUSED')
        self.assertAlmostEqual(evaluated['pre_request_idle_duration_seconds'],14.315,places=3)
if __name__=='__main__':unittest.main(verbosity=2)

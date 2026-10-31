"""RC2 cannot pass on a clean install, equal-code update or stale test evidence."""
import copy
import unittest
from scripts.prepare_rc import validate_upgrade_evidence,native_cases,check_rc1_immutable,RC1_SHA,RC1_ARTIFACT_ID,RC1_DIGEST
from scripts.test_rc_upgrade import validate_update
from scripts.rc_archive import sha256
from sedrava_version import VERSION,ANDROID_VERSION_CODE

class RC2Preparation(unittest.TestCase):
    def evidence(self):
        apk=b'unit fixture only'
        old={'application_id':'org.sedrava.app.af44c2608593529f9c803c46e60a5a99d','version_name':'0.10.0rc1','version_code':10001,'signer_certificate_sha256':'a'*64,'sha256':'b'*64}
        new={**old,'version_name':VERSION,'version_code':ANDROID_VERSION_CODE,'sha256':sha256(apk)}
        evidence={'result':'PASS','baseline_sha':RC1_SHA,'baseline_apk':old,'rc_apk':new,'install_method':'adb install -r','cold_restart_preserved':True,'preserved_tasks':{'next_id':2,'items':[{'id':1,'title':'Upgrade kept','done':False}]},'emulator':{'ro.build.version.sdk':'35','ro.kernel.qemu':'1'},'rejected_updates':[{'kind':kind,'install_method':'adb install -r','rejection_visible':True,'cold_restart_retained':True,'original_sha256':'c'*64} for kind in ('malformed','incompatible')]}
        return apk,evidence
    def test_real_update_gate_rejects_wrong_id_key_and_nonincreasing_code(self):
        _,value=self.evidence();old,new=value['baseline_apk'],value['rc_apk'];validate_update(old,new)
        for change in ({'application_id':'com.example.other'},{'signer_certificate_sha256':'d'*64},{'version_code':10001},{'version_code':1}):
            with self.subTest(change=change),self.assertRaises(ValueError):validate_update(old,{**new,**change})
    def test_collector_binds_rc1_update_to_target_bytes_restart_and_emulator(self):
        apk,value=self.evidence();validate_upgrade_evidence(value,RC1_SHA,'0.10.0rc1',10001,apk,rejected=True)
        changes=[('install_method','clean install'),('cold_restart_preserved',False),('baseline_sha','d'*40),('preserved_tasks',{}),('emulator',{'ro.build.version.sdk':'35','ro.kernel.qemu':'0'})]
        for key,bad in changes:
            with self.subTest(key=key),self.assertRaises(ValueError):validate_upgrade_evidence({**value,key:bad},RC1_SHA,'0.10.0rc1',10001,apk,rejected=True)
        with self.assertRaises(ValueError):validate_upgrade_evidence(value,RC1_SHA,'0.10.0rc1',10001,b'substituted bytes',rejected=True)
        for field,bad in [('version_code',10001),('version_name','0.10.0rc1'),('signer_certificate_sha256','d'*64),('application_id','com.example.other')]:
            changed=copy.deepcopy(value);changed['rc_apk'][field]=bad
            with self.subTest(field=field),self.assertRaises(ValueError):validate_upgrade_evidence(changed,RC1_SHA,'0.10.0rc1',10001,apk,rejected=True)
    def test_collector_requires_both_rejected_update_cases(self):
        apk,value=self.evidence()
        for bad in ([],value['rejected_updates'][:1],[value['rejected_updates'][0]]*2):
            with self.subTest(bad=bad),self.assertRaises(ValueError):validate_upgrade_evidence({**value,'rejected_updates':bad},RC1_SHA,'0.10.0rc1',10001,apk,rejected=True)
        value['rejected_updates'][0]['cold_restart_retained']=False
        with self.assertRaises(ValueError):validate_upgrade_evidence(value,RC1_SHA,'0.10.0rc1',10001,apk,rejected=True)
    def test_native_reports_count_distinct_baseline_executions_and_reject_skips(self):
        xml=b'<testsuite tests="1" failures="0" errors="0" skipped="0"><testcase classname="Seed" name="upgrade"/></testsuite>'
        files={name+'/app/build/outputs/androidTest-results/TEST.xml':xml for name in ('baseline','rc1-baseline')}
        unit,device=native_cases(files);self.assertEqual(unit,[]);self.assertEqual(len(device),2)
        for bad in (xml.replace(b'skipped="0"',b'skipped="1"'),xml.replace(b'/></testsuite>',b'><skipped/></testcase></testsuite>'),b'<!DOCTYPE x><testsuite/>'):
            with self.assertRaises(ValueError):native_cases({'app/outputs/androidTest-results/TEST.xml':bad})

    def test_original_rc1_artifact_must_still_match(self):
        metadata={'expired':False,'digest':RC1_DIGEST,'workflow_run':{'head_sha':RC1_SHA}}
        class Api:
            repo='VasiliiBabkin/sedrava'
            def get(self,path):
                self.path=path
                return metadata
        api=Api();self.assertTrue(check_rc1_immutable(api)['unchanged']);self.assertEqual(api.path,'/actions/artifacts/'+str(RC1_ARTIFACT_ID))
        for key,value in [('expired',True),('digest','sha256:'+'0'*64),('workflow_run',{'head_sha':'d'*40})]:
            old=metadata[key];metadata[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):check_rc1_immutable(api)
            metadata[key]=old

    def test_only_known_launcher_dialog_can_be_dismissed(self):
        from scripts.emulator_ui import launcher_close_point
        raw="""<hierarchy><node text="Quickstep isn't responding" package="android"/><node text="Close app" package="android" bounds="[10,20][30,60]"/></hierarchy>"""
        self.assertEqual(launcher_close_point(raw),(20,40))
        self.assertIsNone(launcher_close_point('<hierarchy><node text="restart persisted"/></hierarchy>'))
        for bad in (raw.replace('Quickstep','Sedrava Tasks'),raw.replace('package="android"','package="app"'),raw.replace('[10,20][30,60]','bad'),raw.replace('Close app','Wait')):
            with self.subTest(bad=bad),self.assertRaises(ValueError):launcher_close_point(bad)

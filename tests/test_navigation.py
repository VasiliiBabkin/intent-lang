import json
from pathlib import Path
import shutil
import subprocess
import unittest
from sedrava_core import parse, run
from sedrava_navigation import initial_session, dispatch, edit_session, select_item, restore_session, Session
from web_codegen import generate
from navigation_cases import SOURCE, steps, trace

SIMPLE='''app "Navigation"
state n = 0
action bump: n = n + 1
screen main:
    text "Home"
    button "Next" -> next_page
screen other:
    text "Other"
    button "Again" -> next_page
    button "Back" -> previous
navigation:
    initial main
    action next_page -> other using bump
    action previous -> pop
'''

class NavigationTests(unittest.TestCase):
    def test_screens_and_legacy_compatibility(self):
        p=parse(SIMPLE);self.assertEqual(p.initial_screen,'main');self.assertEqual(list(p.screens),['main','other']);self.assertTrue(p.has_navigation)
        self.assertEqual(p.screens['other'].span.line,7)
        old=parse('app "Old"\nstate main = 0\nscreen main:\n    value main\n')
        self.assertFalse(old.has_navigation);self.assertEqual(old.widgets,(('value','main'),))

    def test_shared_data_stack_bounds_and_rollback(self):
        p=parse(SIMPLE);s=initial_session(p)
        s,ok=dispatch(p,s,'$back');self.assertTrue(ok);self.assertEqual(s.stack,('main',))
        for _ in range(31): s,ok=dispatch(p,s,'next_page');self.assertTrue(ok)
        self.assertEqual(len(s.stack),32);self.assertEqual(s.state['n'],31)
        before=s;s,ok=dispatch(p,s,'next_page');self.assertFalse(ok);self.assertIs(s,before)
        for _ in range(31): s,ok=dispatch(p,s,'$back');self.assertTrue(ok)
        self.assertEqual(s.state['n'],31);self.assertEqual(s.stack,('main',))

    def test_type_target_conflict_and_reachability_diagnostics(self):
        variants=[SIMPLE.replace('initial main','initial absent'),SIMPLE.replace('-> other using','-> absent using'),SIMPLE.replace('state n = 0','state n = 0\nstate main = 0'),SIMPLE.replace('action previous -> pop','action previous -> pop using absent'),SIMPLE.replace('action previous -> pop','action bump -> pop'),SIMPLE.replace('screen other:','screen main:'),SIMPLE.replace('screen other:','screen other when n:'),SIMPLE.replace('    action previous -> pop','    action previous -> pop\n    action unused -> main'),SIMPLE.replace('    initial main','    initial main\n    initial other'),SIMPLE.replace('    action next_page -> other using bump','    action next_page -> pop'),SIMPLE.replace('navigation:\n    initial main','navigation:\n    initial main\nnavigation:\n    initial main')]
        for source in variants:
            with self.subTest(source=source),self.assertRaisesRegex(ValueError,r'Line \d+: column \d+:'):parse(source)

    def test_atomic_failed_domain_rule_does_not_navigate(self):
        p=parse(SIMPLE.replace('screen main:','rule n == 0\nscreen main:'));s=initial_session(p)
        after,ok=dispatch(p,s,'next_page');self.assertFalse(ok);self.assertIs(after,s)

    def test_selection_and_deletion_never_substitute_another_id(self):
        result=trace();self.assertFalse(result[0]['accepted']);self.assertEqual(result[5]['stack'],['main','details'])
        self.assertEqual(result[8]['state']['selected'],1);self.assertTrue(result[8]['state']['tasks']['items'][0]['done'])
        self.assertEqual(result[17]['stack'],['main']);self.assertEqual(result[17]['state']['tasks']['items'][0]['id'],2)
        self.assertFalse(result[18]['accepted']);self.assertEqual(result[20]['stack'],['main']);self.assertEqual(result[-1]['stack'],['main'])
        self.assertEqual(result[-1]['state']['tasks']['items'][0]['id'],3)

    def test_saved_navigation_validation_and_guard_normalization(self):
        p=parse(SOURCE);s=initial_session(p)
        for stack in ((),('details',),('main','missing'),('main',)*33,['main'],('main',1)):
            self.assertEqual(restore_session(p,s.state,stack).stack,('main',))
        self.assertEqual(restore_session(p,s.state,('main','details')).stack,('main',))

    def test_explicit_non_main_initial_and_embedded_navigation_test(self):
        source=SIMPLE.replace('screen main:','screen home:').replace('initial main','initial home')+'test routes: next_page, previous -> n == 1\n'
        p=parse(source);self.assertEqual(initial_session(p).stack,('home',));self.assertEqual(run(p),1)

    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_python_javascript_session_conformance(self):
        sequences=[(SOURCE,steps()),(SIMPLE,[('command','next_page')]*33+[('command','$back')]*34), (SIMPLE.replace('screen main:','rule n == 0\nscreen main:'),[('command','next_page'),('command','$back')])]
        for source,sequence in sequences:
            code=generate(source).split('<script>')[1].split('</script>')[0]
            runner=r'''const vm=require('vm');const d=JSON.parse(require('fs').readFileSync(0,'utf8'));const c=vm.createContext({document:{querySelectorAll:()=>[],getElementById:()=>null}});vm.runInContext(d.code,c);const api=vm.runInContext('({initialSession,dispatchSession,editSession,selectItem,restoreSession,restoreSnapshot,signature,persistentKeys})',c);let s=api.initialSession();const out=d.steps.map(step=>{const before=s;if(step[0]==='command')s=api.dispatchSession(s,step[1]);else if(step[0]==='input')s=api.editSession(s,step[1],step[2]);else if(step[0]==='select')s=api.selectItem(s,...step.slice(1));else if(step[0]==='recreate')s=api.restoreSession(s.state,s.stack);else {const raw=JSON.stringify({schema:1,signature:api.signature,state:Object.fromEntries(api.persistentKeys.map(k=>[k,s.state[k]]))});s=api.initialSession(api.restoreSnapshot(raw));}return {state:s.state,stack:s.stack,accepted:s!==before};});process.stdout.write(JSON.stringify(out));'''
            result=subprocess.run(['node','-e',runner],input=json.dumps({'code':code,'steps':sequence}),capture_output=True,text=True,check=True)
            self.assertEqual(json.loads(result.stdout),trace(source,sequence))

    def test_screen_binding_limits_and_identifier_boundaries(self):
        def pages(count):
            source='app "Limits"\n'
            for i in range(count):
                source+='screen page'+str(i)+':\n    text "Page"\n'
                if i+1<count: source+='    button "Next" -> go'+str(i)+'\n'
            source+='navigation:\n    initial page0\n'
            for i in range(count-1): source+='    action go'+str(i)+' -> page'+str(i+1)+'\n'
            return source
        self.assertEqual(len(parse(pages(32)).screens),32)
        with self.assertRaisesRegex(ValueError,'screen limit'):parse(pages(33))
        with self.assertRaisesRegex(ValueError,'name conflict'):parse(SIMPLE.replace('other','x'*65))
        source=SIMPLE.replace('    action previous -> pop','\n'.join('    action go'+str(i)+' -> main' for i in range(65)))
        with self.assertRaisesRegex(ValueError,'binding limit'):parse(source)

    def test_corrupt_session_edit_rejects_without_applying_data(self):
        p=parse(SIMPLE);s=Session(p.states.copy(),())
        after,ok=edit_session(p,s,'n',1);self.assertFalse(ok);self.assertIs(after,s)

    def test_cli_reports_domain_and_stack(self):
        import tempfile
        import contextlib
        import io
        from sedrava_cli import main
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'pages.sdr';path.write_text(SIMPLE,encoding='utf-8');output=io.StringIO()
            with contextlib.redirect_stdout(output): self.assertEqual(main(['run',str(path),'next_page','previous']),0)
            self.assertEqual(json.loads(output.getvalue()),{'state':{'n':1},'stack':['main']})

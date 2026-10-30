import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from sedrava_core import parse, parse_expr, evaluate
from sedrava_records import fingerprint, serialize_state, restore_snapshot
from sedrava_cli import main
from web_codegen import generate
from stability_cases import SOURCE, steps
from record_cases import trace

class StabilityAudit(unittest.TestCase):
    def test_signed_minimum_in_all_ast_positions(self):
        for expression in ('-2147483648', '0 >= -2147483648', '-2147483648 == -2147483648', '(0 == 0) and (0 > -2147483648)'):
            self.assertIn(evaluate(parse_expr(expression,{}),{}),(-2147483648,True))
        parse(SOURCE) # call argument minimum as well as RHS comparison
        for expression in ('2147483648','--2147483648','-2147483649'):
            with self.subTest(expression=expression),self.assertRaises(ValueError):evaluate(parse_expr(expression,{}),{})

    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_bounded_differential_traces(self):
        runner=r"""const vm=require('vm');const d=JSON.parse(require('fs').readFileSync(0,'utf8'));const c=vm.createContext({document:{querySelectorAll:()=>[],getElementById:()=>null}});vm.runInContext(d.code,c);let state=vm.runInContext('({...initialState})',c);const actions=vm.runInContext('actions',c), edit=vm.runInContext('editState',c);let out=[];for(const step of d.steps){let accepted=false;try{let next;if(step[0]==='input')next=edit(state,step[1],step[2]);else if(step[0]==='action')next=actions[step[1]](state);else{c.raw=JSON.stringify({schema:1,signature:vm.runInContext('signature',c),state:Object.fromEntries(vm.runInContext('persistentKeys',c).map(k=>[k,state[k]]))});next=vm.runInContext('restoreSnapshot(raw)',c);}accepted=next!==state;if(accepted)state=next;}catch(_){}out.push({state,accepted});}process.stdout.write(JSON.stringify(out));"""
        code=generate(SOURCE).split('<script>')[1].split('</script>')[0]
        for seed in range(10):
            sequence=steps(seed)
            result=subprocess.run(['node','-e',runner],input=json.dumps({'code':code,'steps':sequence}),capture_output=True,text=True,check=True,timeout=20)
            expected=[{k:v for k,v in row.items() if k!='snapshot'} for row in trace(SOURCE,sequence)]
            self.assertEqual(json.loads(result.stdout),expected,'seed '+str(seed))

    def test_schema_compatibility_is_exact_except_defaults_and_actions(self):
        p=parse(SOURCE);raw=serialize_state(p,p.states)
        for source in (SOURCE.replace('state title = ""','state title = "new default"'), SOURCE.replace('    edge = edge + 1','    edge = edge + 2')):
            self.assertEqual(fingerprint(parse(source)),fingerprint(p))
            restore_snapshot(parse(source),raw)
        for source in (SOURCE.replace('max=3','max=4'),SOURCE.replace('    score: int','    score: bool').replace('score=edge','score=false'),SOURCE.replace('persist edge\n',''),SOURCE.replace('state touched = false','state touched = 0').replace('touched = true','touched = 1')):
            with self.subTest(source=source[:60]),self.assertRaises(ValueError):restore_snapshot(parse(source),raw)

    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_rejected_storage_cannot_be_overwritten(self):
        code=generate(SOURCE).split('<script>')[1].split('</script>')[0]
        runner=r"""const vm=require('vm');const d=JSON.parse(require('fs').readFileSync(0,'utf8'));let raw=d.raw,writes=0;const c=vm.createContext({document:{querySelectorAll:()=>[],getElementById:()=>null},localStorage:{getItem:()=>raw,setItem:(_,v)=>{writes++;raw=v;}}});vm.runInContext(d.code,c);try{vm.runInContext('state=actions.minimum(state);saveSnapshot()',c);}catch(_){}process.stdout.write(JSON.stringify({raw,writes}));"""
        for raw in ('{broken',serialize_state(parse(SOURCE),parse(SOURCE).states).replace('"schema":1','"schema":2')):
            result=subprocess.run(['node','-e',runner],input=json.dumps({'code':code,'raw':raw}),capture_output=True,text=True,check=True)
            self.assertEqual(json.loads(result.stdout),{'raw':raw,'writes':0})

    def test_web_output_failure_and_source_collision_preserve_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'app.sdr';source.write_text(SOURCE);original=source.read_bytes()
            output=root/'index.html';output.write_text('existing valid output')
            with patch('os.replace',side_effect=OSError('simulated full output volume')),contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(['build','web',str(source),'--output',str(output)]),1)
            self.assertEqual(output.read_text(),'existing valid output')
            with contextlib.redirect_stderr(io.StringIO()):self.assertEqual(main(['build','web',str(source),'--output',str(source)]),1)
            self.assertEqual(source.read_bytes(),original)
            self.assertEqual(sorted(p.name for p in root.iterdir()),['app.sdr','index.html'])

    def test_cli_snapshot_replace_failure_preserves_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'a.sdr';source.write_text(SOURCE)
            saved=root/'state.json';saved.write_text(serialize_state(parse(SOURCE),parse(SOURCE).states));before=saved.read_bytes()
            with patch('os.replace',side_effect=OSError('simulated replace failure')),contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(['run',str(source),'minimum','--state-file',str(saved)]),1)
            self.assertEqual(saved.read_bytes(),before)
            self.assertEqual(sorted(p.name for p in root.iterdir()),['a.sdr','state.json'])

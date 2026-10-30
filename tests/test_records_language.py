import json
from pathlib import Path
import shutil
import subprocess
import unittest
from dataclasses import replace
from sedrava_core import parse, edit_state, transition, valid_state
from sedrava_records import ListValue, RecordValue, plain, serialize_state, restore_snapshot
from web_codegen import generate
from record_cases import SOURCE, steps, trace, invalid_snapshots, resource_source

class RecordsLanguage(unittest.TestCase):
    def test_trace_and_identity(self):
        outcomes=trace()
        self.assertFalse(outcomes[0]['accepted'])
        self.assertEqual([r['id'] for r in outcomes[-1]['state']['tasks']['items']],[2,3,4])
        self.assertEqual(outcomes[-1]['state']['tasks']['next_id'],5)
        self.assertTrue(outcomes[-1]['state']['tasks']['items'][1]['done'])

    def test_types_and_diagnostics(self):
        for expression in ('append(tasks, Task(title=1, done=false))', 'append(tasks, Task(title="x"))', 'append(tasks, Task(title="x", title="y"))', 'remove(tasks, true)', 'get(tasks, 1).missing', 'tasks == tasks', 'tasks[0]', 'append(tasks, Other(title="x"))'):
            source=SOURCE.replace('tasks = append(tasks, Task(title=title, done=false))','tasks = '+expression)
            with self.subTest(expression=expression), self.assertRaisesRegex(ValueError,r'Line \d+: column \d+:'):
                parse(source)

    def test_capacity_rules_and_atomic_failure(self):
        source=SOURCE.replace('max=100','max=1').replace('action complete:', 'rule count(tasks) <= 1\naction complete:')
        p=parse(source);s,_=edit_state(p,p.states,'title','one');s,_=transition(p,s,'add');s,_=edit_state(p,s,'title','two')
        with self.assertRaises(ValueError): transition(p,s,'add')
        self.assertEqual(s['title'],'two');self.assertEqual(s['tasks'].next_id,2)
        p=parse(SOURCE+'\nrule count(tasks) == 0\n');s,_=edit_state(p,p.states,'title','one');candidate,accepted=transition(p,s,'add');self.assertFalse(accepted);self.assertEqual(candidate,s)
        p=parse(SOURCE.replace('    tasks = remove(tasks, selected)','    title = "changed"\n    tasks = remove(tasks, selected)'));s=p.states.copy()
        with self.assertRaises(ValueError): transition(p,s,'delete')
        self.assertEqual(s,p.states)

    def test_int32_unicode_and_exhaustion(self):
        p=parse(SOURCE);s=p.states.copy()
        for title in ('😀'*1024,'é','é','  '): self.assertTrue(edit_state(p,s,'title',title)[1])
        for title in ('😀'*1025,'\ud800',1): self.assertFalse(edit_state(p,s,'title',title)[1])
        self.assertFalse(edit_state(p,s,'selected',2147483648)[1])
        s['tasks']=replace(s['tasks'],next_id=2147483647);s['title']='x'
        with self.assertRaises(ValueError): transition(p,s,'add')

    def test_strict_restore_whole_snapshot(self):
        p=parse(SOURCE);s,_=edit_state(p,p.states,'title','😀');s,_=transition(p,s,'add');raw=serialize_state(p,s)
        self.assertEqual(restore_snapshot(p,raw)['tasks'],s['tasks'])
        valid=json.loads(raw)
        cases=['{',raw+'x','['*33+'0'+']'*33,' '*200001,raw.replace('"schema":1','"schema":1,"schema":1'),raw.replace('"schema":1','"schema":1.0'),raw.replace('"id":1','"id":true'),raw.replace('"done":false','"done":1'),raw.replace('"next_id":2','"next_id":1'),raw.replace('"title":"😀"','"title":"\\ud800"'),json.dumps({**valid,'extra':1}),json.dumps({**valid,'signature':'bad'})]
        duplicate=json.loads(raw);duplicate['state']['tasks']['items']*=2;cases.append(json.dumps(duplicate))
        for bad in cases:
            with self.subTest(bad=bad[:80]),self.assertRaises(ValueError): restore_snapshot(p,bad)
        self.assertTrue(valid_state(p,s))

    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_python_web_conformance(self):
        def check(source,sequence):
            code=generate(source).split('<script>')[1].split('</script>')[0]
            runner="""const vm=require('node:vm');const data=JSON.parse(require('fs').readFileSync(0,'utf8'));const c=vm.createContext({document:{querySelectorAll:()=>[],getElementById:()=>null}});vm.runInContext(data.code,c);let current=vm.runInContext('({...initialState})',c);const actions=vm.runInContext('actions',c);const edit=vm.runInContext('editState',c);let out=[];for(const step of data.steps){let accepted=false;try{if(step[0]==='roundtrip'){c.saved=JSON.stringify({schema:1,signature:vm.runInContext('signature',c),state:Object.fromEntries(vm.runInContext('persistentKeys',c).map(k=>[k,current[k]]))});current=vm.runInContext('restoreSnapshot(saved)',c);accepted=true;}else{const next=step[0]==='input'?edit(current,step[1],step[2]):actions[step[1]](current);accepted=next!==current;current=next;}}catch(_){}out.push({state:current,accepted,snapshot:JSON.stringify({schema:1,signature:vm.runInContext('signature',c),state:Object.fromEntries(vm.runInContext('persistentKeys',c).map(k=>[k,current[k]]))})});}process.stdout.write(JSON.stringify(out));"""
            result=subprocess.run(['node','-e',runner],input=json.dumps({'code':code,'steps':sequence}),text=True,capture_output=True,check=True)
            self.assertEqual(json.loads(result.stdout),trace(source,sequence))
        check(SOURCE,steps())
        generic=(Path(__file__).parent/'fixtures/records_generic.sdr').read_text(encoding='utf-8')
        check(generic,[('action',a) for a in ('add','overflow','nested_capacity','mutate','delete','add')]+[('roundtrip',)])
        sequence=[('action','add')]*15+[('action','transient')]
        outcomes=trace(resource_source(),sequence)
        self.assertTrue(any(not row['accepted'] for row in outcomes))
        self.assertTrue(outcomes[-1]['accepted'])
        check(resource_source(),sequence)

    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_restore_rejections_match_web(self):
        p=parse(SOURCE)
        for raw in invalid_snapshots():
            with self.subTest(raw=raw[:70]), self.assertRaises(ValueError): restore_snapshot(p,raw)
        code=generate(SOURCE).split('<script>')[1].split('</script>')[0]
        runner="const vm=require('vm');const data=JSON.parse(require('fs').readFileSync(0,'utf8'));const c=vm.createContext({document:{querySelectorAll:()=>[],getElementById:()=>null}});vm.runInContext(data.code,c);const f=vm.runInContext('restoreSnapshot',c);process.stdout.write(JSON.stringify(data.cases.map(raw=>{try{f(raw);return true;}catch(_){return false;}})));"
        result=subprocess.run(['node','-e',runner],input=json.dumps({'code':code,'cases':invalid_snapshots()}),capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(result.stdout),[False]*len(invalid_snapshots()))

    def test_cli_persistence_is_transactional(self):
        import tempfile
        from sedrava_cli import main
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'state.json';source=Path(tmp)/'app.sdr';source.write_text(SOURCE,encoding='utf-8')
            self.assertEqual(main(['run',str(source),'--state-file',str(path)]),0)
            before=path.read_bytes()
            self.assertEqual(main(['run',str(source),'delete','--state-file',str(path)]),1)
            self.assertEqual(path.read_bytes(),before)
            path.write_text('{bad',encoding='utf-8')
            self.assertEqual(main(['run',str(source),'--state-file',str(path)]),1)
            self.assertEqual(path.read_text(),'{bad')

    def test_generic_records_limits_and_nested_capacity(self):
        source=(Path(__file__).parent/'fixtures/records_generic.sdr').read_text(encoding='utf-8')
        from sedrava_core import run
        p=parse(source);self.assertEqual(run(p),1)
        state,_=transition(p,p.states,'add')
        for action in ('overflow','nested_capacity'):
            with self.subTest(action=action),self.assertRaises(ValueError): transition(p,state,action)
        self.assertFalse(state['changed']);self.assertEqual(state['tags'].next_id,2)
        for capacity in ('0','101'):
            with self.assertRaises(ValueError): parse(SOURCE.replace('max=100','max='+capacity))
        for field in ('id: int','title: int','nested: Task','true: bool','class: text'):
            with self.assertRaises(ValueError): parse(SOURCE.replace('    done: bool','    done: bool\n    '+field))
        with self.assertRaises(ValueError): parse(SOURCE.replace('    done: bool','\n'.join('    field'+str(i)+': int' for i in range(17))))

    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_public_restore_adapter_never_partially_applies_collection_data(self):
        source=SOURCE.replace('persist tasks','persist tasks\npersist title')
        p=parse(source);data=json.loads(serialize_state(p,p.states));data['state']['title']='partial';data['state']['tasks']={'next_id':True,'items':[]}
        code=generate(source).split('<script>')[1].split('</script>')[0]
        runner="const vm=require('vm');const data=JSON.parse(require('fs').readFileSync(0,'utf8'));const c=vm.createContext({document:{querySelectorAll:()=>[],getElementById:()=>null}});vm.runInContext(data.code,c);c.saved=data.raw;process.stdout.write(vm.runInContext('JSON.stringify(restoreState(saved))',c));"
        result=subprocess.run(['node','-e',runner],input=json.dumps({'code':code,'raw':json.dumps(data)}),capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(result.stdout),{k:plain(v) for k,v in p.states.items()})

    def test_initial_state_resource_limit_is_checked_before_generation(self):
        source='app "Initial limit"\nrecord R:\n    x: int\n'+'\n'.join('state n'+str(i)+'=0' for i in range(6000))
        self.assertLess(len(source),100000)
        with self.assertRaisesRegex(ValueError,'Line 1: column 1: State exceeds'):
            parse(source)

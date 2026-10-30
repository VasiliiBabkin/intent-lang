"""Emit independent bounded differential corpus into generated Kotlin JVM tests."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from stability_cases import SOURCE, steps
from record_cases import trace
from android_codegen_v03 import quoted, generate
from sedrava_android_identity import project_identity,kotlin_path
from sedrava_core import parse
from sedrava_records import fingerprint
import json

def prepare(project):
    generate(SOURCE,project)
    lines=['package '+project_identity(project),'import org.junit.Test','import org.junit.Assert.*','class StabilityTest {','@Test fun independentBoundedTrace() {','var state=SedravaState()']
    for index,(step,outcome) in enumerate(zip(steps(),trace(SOURCE,steps()))):
        if step[0]=='input':
            value=quoted(step[2]) if type(step[2]) is str else str(step[2]) + ('L' if not -2147483648<=step[2]<=2147483647 else '')
            expression='editState(state,'+quoted(step[1])+','+value+')'
        elif step[0]=='action':expression='transitionState(state,'+quoted(step[1])+')'
        else:expression='restoreSnapshot(snapshotState(state))'
        lines += ['val before'+str(index)+'=state','state='+expression,
                  'assertEquals('+quoted('step '+str(index))+','+quoted(json.dumps({'schema':1,'signature':fingerprint(parse(SOURCE)),'state':outcome['state']},ensure_ascii=False,separators=(',',':')))+',snapshotState(state,true))']
        if step[0]!='roundtrip':lines.append(('assertNotSame' if outcome['accepted'] else 'assertSame')+'(before'+str(index)+',state)')
    lines += ['}','}']
    path=kotlin_path(project,'test','StabilityTest.kt');path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
if __name__=='__main__':prepare(sys.argv[1])

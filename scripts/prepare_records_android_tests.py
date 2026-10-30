"""Generate JVM assertions from the same Python traces used for Web conformance."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from android_codegen_v03 import quoted
from record_cases import SOURCE, steps, trace, invalid_snapshots
from sedrava_core import parse
from sedrava_records import fingerprint

from sedrava_android_identity import project_identity, kotlin_path


def prepare(project, source=SOURCE):
    import json
    program=parse(source)
    sequence=steps() if source == SOURCE else [('action',a) for a in ('add','overflow','nested_capacity','mutate','delete','add')]+[('roundtrip',)]
    lines=['package '+project_identity(project),'import org.junit.Test','import org.junit.Assert.*','class RecordsStateTest {','  @Test fun pythonOracle() {','    var state=SedravaState()']
    for i,(step,outcome) in enumerate(zip(sequence,trace(source,sequence))):
        lines.append('    val before_'+str(i)+'=state')
        if step[0]=='input':
            value=quoted(step[2]) if type(step[2]) is str else str(step[2])
            expression='editState(state,'+quoted(step[1])+','+value+')'
        elif step[0]=='action': expression='transitionState(state,'+quoted(step[1])+')'
        else: expression='restoreSnapshot(snapshotState(state))'
        lines.append('    state='+expression)
        raw=json.dumps({'schema':1,'signature':fingerprint(program),'state':outcome['state']},ensure_ascii=False,separators=(',',':'))
        lines.append('    assertEquals("step '+str(i)+'", restoreSnapshot('+quoted(raw)+', true), state)')
        lines.append('    assertEquals("canonical JSON '+str(i)+'", '+quoted(raw)+', snapshotState(state,true))')
        if step[0]!='roundtrip': lines.append(('    assertNotSame' if outcome['accepted'] else '    assertSame')+'(before_'+str(i)+',state)')
    if source != SOURCE:
        lines += ['  }', '}']
        path=kotlin_path(project, 'test', 'RecordsStateTest.kt')
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        print(path)
        return
    for bad in invalid_snapshots():
        if len(bad)>10000: continue  # huge constants exceed JVM class-file limits; runtime bounds checked below
        lines += ['    try { restoreSnapshot('+quoted(bad)+'); fail("Accepted invalid snapshot") } catch (_: IllegalArgumentException) {}']
    lines += ['    try { restoreSnapshot(" ".repeat(200001)); fail("Oversized JSON accepted") } catch (_: IllegalArgumentException) {}', '  }','  @Test fun strictJsonAndUnicode() {','    assertTrue(validText("😀".repeat(1024)))','    assertFalse(validText("😀".repeat(1025)))','    assertFalse(validText("\\ud800"))','    for(raw in listOf("{", "[]", "{\\\"schema\\\":1,\\\"schema\\\":1}", "0.0", "[".repeat(33)+"0"+"]".repeat(33))) {','      try { restoreSnapshot(raw); fail("Accepted corrupt JSON") } catch (_: IllegalArgumentException) {}','    }','  }','  @Test fun capacityIdentityAndRecreation() {','    var state=SedravaState()','    repeat(100) { state=transitionState(editState(state,"title","task"),"add") }','    assertEquals(101,state.sdr_tasks.next_id)','    val full=editState(state,"title","overflow")','    assertSame(full,transitionState(full,"add"))','    assertEquals(full,restoreSnapshot(snapshotState(full,true),true))','    state=transitionState(editState(state,"selected",1),"delete")','    state=transitionState(editState(state,"title","next"),"add")','    assertEquals(101,state.sdr_tasks.items.last().id)','  }','}']
    path=kotlin_path(project, 'test', 'RecordsStateTest.kt');path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(path)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('project');parser.add_argument('--source',type=Path);args=parser.parse_args();prepare(args.project,args.source.read_text(encoding='utf-8') if args.source else SOURCE)

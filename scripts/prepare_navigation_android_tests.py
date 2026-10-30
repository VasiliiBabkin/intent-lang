"""Python-oracle JVM tests beside untouched generated navigation Kotlin."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from navigation_cases import SOURCE, steps, trace
from sedrava_core import parse
from sedrava_records import fingerprint
from android_codegen_v03 import quoted as q

from sedrava_android_identity import project_identity, kotlin_path


def prepare(project, source=SOURCE):
    program=parse(source)
    sequence=steps() if source==SOURCE else [('command','next_page')]*33+[('command','$back')]*34
    lines=['package '+project_identity(project),'import org.junit.Test','import org.junit.Assert.*','class NavigationStateTest {','  @Test fun pythonOracle() {','    assertEquals(listOf("main"),restoreSessionSnapshot(emptyList(),SedravaState()).stack)', '    var session=initialSession()']
    for i,(step,outcome) in enumerate(zip(sequence,trace(source,sequence))):
        lines.append('    val before_'+str(i)+'=session')
        if step[0]=='command': expression='dispatchSession(session,'+q(step[1])+')'
        elif step[0]=='input': expression='editSession(session,'+q(step[1])+','+(q(step[2]) if type(step[2]) is str else str(step[2]))+')'
        elif step[0]=='select': expression='selectItem(session,'+q(step[1])+','+q(step[2])+','+str(step[3])+','+q(step[4])+')'
        elif step[0]=='recreate': expression='restoreSession(restoreSnapshot(snapshotState(session.state,true),true),session.stack)'
        else: expression='initialSession(restoreSnapshot(snapshotState(session.state)))'
        lines.append('    session='+expression)
        raw=json.dumps({'schema':1,'signature':fingerprint(program),'state':outcome['state']},ensure_ascii=False,separators=(',',':'))
        lines.append('    assertEquals("domain '+str(i)+'",'+q(raw)+',snapshotState(session.state,true))')
        lines.append('    assertEquals("stack '+str(i)+'",listOf('+','.join(q(k) for k in outcome['stack'])+'),session.stack)')
        lines.append(('    assertNotSame' if outcome['accepted'] else '    assertSame')+'("atomic '+str(i)+'",before_'+str(i)+',session)')
    if source!=SOURCE:
        lines += ['  }','}']
        path=kotlin_path(project, 'test', 'NavigationStateTest.kt');path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(path);return
    lines += ['  }','  @Test fun stackOverflowAndMissingRecordAreAtomic() {','    var session=initialSession()','    session=editSession(session,"new_title","one")','    session=dispatchSession(session,"add_task")','    session=selectItem(session,"tasks","selected",1,"open_details")','    repeat(30) { session=dispatchSession(session,"open_details") }','    assertEquals(32,session.stack.size)','    session=editSession(session,"title","unsaved accepted edit")','    val before=session','    assertSame(before,dispatchSession(before,"open_details"))','    assertEquals("unsaved accepted edit",before.state.sdr_title)','    assertSame(before,selectItem(before,"tasks","selected",999,"open_details"))','    assertEquals(listOf("main"),restoreSession(before.state,listOf("bad")).stack)','    session=dispatchSession(session,"delete_task")','    assertEquals(listOf("main"),session.stack)','    assertTrue(session.state.sdr_tasks.items.isEmpty())','  }','}']
    path=kotlin_path(project, 'test', 'NavigationStateTest.kt');path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(path)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('project');parser.add_argument('--source',type=Path);args=parser.parse_args()
    prepare(args.project,args.source.read_text(encoding='utf-8') if args.source else SOURCE)

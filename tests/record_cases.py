"""Shared action/input oracle for Python, emitted JS and emitted Kotlin."""
from pathlib import Path
from sedrava_core import parse, edit_state, transition
from sedrava_records import plain, serialize_state, restore_snapshot
ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'examples/task_manager.sdr').read_text(encoding='utf-8')

def steps():
    return [('action','add'),('input','title','Привет 😀'),('action','add'),('input','title','second'),('action','add'),('input','selected',1),('action','complete'),('input','title','renamed é'),('action','rename'),('action','delete'),('input','selected',1),('action','complete'),('input','title','third'),('action','add'),('input','selected',3),('action','complete'),('input','title','😀'*1025),('input','title',''),('action','rename'),('roundtrip',)]

def trace(source=SOURCE, sequence=None):
    program=parse(source);state=program.states.copy();out=[]
    for step in steps() if sequence is None else sequence:
        before=state
        try:
            if step[0]=='action': candidate, accepted=transition(program,state,step[1])
            elif step[0]=='input': candidate, accepted=edit_state(program,state,step[1],step[2])
            else: candidate=restore_snapshot(program,serialize_state(program,state));accepted=True
            if accepted: state=candidate
        except ValueError: accepted=False
        out.append({'state':{k:plain(v) for k,v in state.items()},'accepted':accepted})
        if not accepted: assert state==before
    return out


def invalid_snapshots():
    import json
    p=parse(SOURCE);s,_=edit_state(p,p.states,'title','one');s,_=transition(p,s,'add')
    raw=serialize_state(p,s)
    cases=['{','[]',' '*200001,raw+'x',raw.replace('"schema":1','"schema":1,"schema":1'),raw.replace('"schema":1','"schema":1.0'),raw.replace('"schema":1','"schema":1e0'),raw.replace('"schema":1','"schema":true'),raw.replace('"id":1','"id":true'),raw.replace('"id":1','"id":0'),raw.replace('"id":1','"id":2147483648'),raw.replace('"next_id":2','"next_id":1'),raw.replace('"done":false','"done":1'),raw.replace('"title":"one"','"title":"\\ud800"'),raw.replace('"title":"one"','"title":'+json.dumps('😀'*1025)),raw.replace('"title":"one"','"title":"one","extra":1'),raw.replace('"state":','"statex":')]
    data=json.loads(raw);data['state']['tasks']['items']*=2;cases.append(json.dumps(data))
    data=json.loads(raw);data['state']['tasks']['items']*=101;cases.append(json.dumps(data))
    data=json.loads(raw);data['signature']='old';cases.append(json.dumps(data))
    return cases

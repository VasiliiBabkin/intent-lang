"""Shared Python oracle for domain state, navigation and stable item selection."""
from pathlib import Path
from sedrava_core import parse
from sedrava_navigation import initial_session, dispatch, edit_session, select_item, restore_session
from sedrava_records import plain, serialize_state, restore_snapshot
ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'examples/task_manager_navigation.sdr').read_text(encoding='utf-8')


def steps():
    return [('command','open_details'),('input','new_title','First 😀'),('command','add_task'),('input','new_title','Second'),('command','add_task'),('select','tasks','selected',1,'open_details'),('input','title','Renamed é'),('command','rename_task'),('command','toggle_task'),('command','$back'),('command','open_details'),('recreate',),('input','title',''),('command','rename_task'),('command','back_to_tasks'),('select','tasks','selected',999,'open_details'),('select','tasks','selected',1,'open_details'),('command','delete_and_back'),('command','open_details'),('select','tasks','selected',2,'open_details'),('command','delete_task'),('command','$back'),('input','new_title','Cold launch'),('command','add_task'),('select','tasks','selected',3,'open_details'),('cold',)]


def trace(source=SOURCE, sequence=None):
    p=parse(source);current=initial_session(p);out=[]
    for step in steps() if sequence is None else sequence:
        if step[0]=='command': current,accepted=dispatch(p,current,step[1])
        elif step[0]=='input': current,accepted=edit_session(p,current,step[1],step[2])
        elif step[0]=='select': current,accepted=select_item(p,current,*step[1:])
        elif step[0]=='recreate': current=restore_session(p,current.state,current.stack);accepted=True
        else: current=initial_session(p,restore_snapshot(p,serialize_state(p,current.state)));accepted=True
        out.append({'state':{k:plain(v) for k,v in current.state.items()},'stack':list(current.stack),'accepted':accepted})
    return out

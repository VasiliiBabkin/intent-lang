"""Compare real generated JS state adapters with the Python scalar model."""
import json
import shutil
import subprocess
import unittest
from sedrava_core import parse
from web_codegen import generate
from text_cases import ROOT, operations, trace

@unittest.skipUnless(shutil.which('node'), 'Node.js required for text conformance')
class TextConformance(unittest.TestCase):
    def test_text_actions_input_and_restore_traces(self):
        sources = [(ROOT / 'examples/text_profile.sdr').read_text(encoding='utf-8'),
                   (ROOT / 'tests/fixtures/text_escaping.sdr').read_text(encoding='utf-8'),
                   'app "Empty"\nstate title = "seed"\npersist title\naction blank: title = ""\nscreen main:\n    input title\n    value title\n']
        payload, expected = [], []
        for source in sources:
            steps = operations(source)
            expected.append(trace(parse(source), steps))
            payload.append({'script': generate(source).split('<script>', 1)[1].split('</script>', 1)[0], 'steps': steps})
        runner = r'''
const vm = require('node:vm');
const data = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
const traces = data.map(({script, steps}) => {
 const context = vm.createContext({document: {querySelectorAll:()=>[], getElementById:()=>null}});
 vm.runInContext(script, context);
 const api=vm.runInContext('({actions, editState, restoreState, initialState})', context);
 let current={...api.initialState};
 return steps.map(step => {
   let accepted=null;
   if(step[0]==='restore') current=api.restoreState(step[1]);
   else {
     let next=current;
     try { next=step[0]==='action' ? api.actions[step[1]](current) : api.editState(current, step[1], step[2]); } catch (_) {}
     accepted=next!==current; current=next;
   }
   return {state: JSON.parse(JSON.stringify(current)), accepted};
 });
});
process.stdout.write(JSON.stringify(traces));
'''
        result = subprocess.run(['node', '-e', runner], input=json.dumps(payload), capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), expected)

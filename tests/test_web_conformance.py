"""Compare the Python interpreter with the generated JavaScript action functions.

Node.js is required. The generated HTML is evaluated in a sandbox with a stub DOM,
then action functions are exercised on the same sequences as the interpreter.
"""
import itertools
import json
import shutil
import subprocess
import unittest
from pathlib import Path

from sedrava_core import parse, transition
from web_codegen import generate

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "workflow.sdr"

@unittest.skipUnless(shutil.which("node"), "Node.js is required for cross-runtime conformance")
class WebConformance(unittest.TestCase):
    def test_workflow_action_sequences(self):
        source = EXAMPLE.read_text(encoding="utf-8")
        program = parse(source)
        sequences = [list(seq) for n in range(5) for seq in itertools.product(program.actions, repeat=n)]
        expected = []
        for seq in sequences:
            state = program.states.copy()
            trace = [state.copy()]
            for action in seq:
                state, _ = transition(program, state, action)
                trace.append(state.copy())
            expected.append(trace)

        html = generate(source)
        script = html.split("<script>", 1)[1].split("</script>", 1)[0]
        # Stub the DOM: only the pure generated action functions are used.
        runner = r"""
const vm = require('node:vm');
const fs = require('node:fs');
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const document = {querySelectorAll: () => []};
const context = vm.createContext({document, localStorage: {getItem: () => null, setItem: () => {}}});
vm.runInContext(payload.script, context);
const output = payload.sequences.map(seq => {
  let state = vm.runInContext('({...initialState})', context);
  const trace = [JSON.parse(JSON.stringify(state))];
  for (const action of seq) {
    state = vm.runInContext('actions', context)[action](state);
    trace.push(JSON.parse(JSON.stringify(state)));
  }
  return trace;
});
process.stdout.write(JSON.stringify(output));
"""
        result = subprocess.run(
            ["node", "-e", runner],
            input=json.dumps({"script": script, "sequences": sequences}),
            text=True, capture_output=True, timeout=30, check=True,
        )
        self.assertEqual(json.loads(result.stdout), expected)

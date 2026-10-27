"""Differential tests for rejected transitions and sequential updates."""
import json
import shutil
import subprocess
import unittest

from intent_core import parse, transition
from web_codegen import generate


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class RejectedTransitionConformance(unittest.TestCase):
    def test_invariant_rejection_and_if_else(self):
        source = """app "Guards"
state count = 0
action inc:
    count = count + 1
action dec:
    count = count - 1
action toggle:
    if count == 0:
        count = 1
    else:
        count = 0
rule count >= 0 and count <= 2
screen main:
    value count
    button "Increment" -> inc
    button "Decrement" -> dec
    button "Toggle" -> toggle
"""
        program = parse(source)
        sequence = ["dec", "inc", "inc", "inc", "toggle", "dec", "dec"]
        state = program.states.copy()
        expected = [state.copy()]
        rejected = 0
        for action in sequence:
            state, accepted = transition(program, state, action)
            rejected += not accepted
            expected.append(state.copy())
        self.assertGreaterEqual(rejected, 2)
        script = generate(source).split("<script>", 1)[1].split("</script>", 1)[0]
        runner = r"""
const vm = require('node:vm');
const fs = require('node:fs');
const data = JSON.parse(fs.readFileSync(0, 'utf8'));
const context = vm.createContext({document: {querySelectorAll: () => []}});
vm.runInContext(data.script, context);
let state = vm.runInContext('({...initialState})', context);
const actions = vm.runInContext('actions', context);
const trace = [JSON.parse(JSON.stringify(state))];
for (const name of data.sequence) {
  state = actions[name](state);
  trace.push(JSON.parse(JSON.stringify(state)));
}
process.stdout.write(JSON.stringify(trace));
"""
        result = subprocess.run(
            ["node", "-e", runner],
            input=json.dumps({"script": script, "sequence": sequence}),
            text=True, capture_output=True, check=True, timeout=30,
        )
        self.assertEqual(json.loads(result.stdout), expected)

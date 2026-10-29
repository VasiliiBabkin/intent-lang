"""Real Chromium tests. Install playwright and its Chromium before running this file."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from playwright.sync_api import sync_playwright
from web_codegen import generate


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class BrowserAlpha(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix='sedrava web ')
        handler = functools.partial(QuietHandler, directory=cls.directory.name)
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.playwright = sync_playwright().start()
        executable = os.environ.get('SEDRAVA_CHROMIUM') or shutil.which('chromium')
        cls.browser = cls.playwright.chromium.launch(executable_path=executable, args=['--no-sandbox'])
        cls.counter = 0

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.directory.cleanup()

    def setUp(self):
        self.context = self.browser.new_context()
        self.context.tracing.start(screenshots=True, snapshots=True)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))

    def tearDown(self):
        output = ROOT / 'build/browser'
        output.mkdir(parents=True, exist_ok=True)
        self.context.tracing.stop(path=str(output / (self._testMethodName + '.zip')))
        self.context.close()
        self.assertEqual(self.errors, [], 'Unhandled browser exceptions')

    def open(self, source, storage=None):
        type(self).counter += 1
        name = f'app-{self.counter}.html'
        (Path(self.directory.name) / name).write_text(generate(source), encoding='utf-8')
        if storage is not None:
            import json
            self.context.add_init_script('localStorage.setItem("sedrava:" + location.pathname + ":Sedrava 0.9 Lab", ' + json.dumps(storage) + ');')
        self.page.goto(f'http://127.0.0.1:{self.server.server_port}/{name}')

    def state(self, name):
        return self.page.locator(f'output[data-state="{name}"]').inner_text()

    def test_reference_input_constraints_and_reload(self):
        self.open((ROOT / 'examples/reference_09.sdr').read_text())
        self.assertEqual(self.state('goal'), '5')
        self.assertEqual(self.state('progress'), '0')
        field = self.page.locator('input')
        for raw in ('55', '-1', '2147483648', '1.5'):
            field.fill(raw)
            self.assertEqual(field.get_attribute('aria-invalid'), 'true')
            self.assertEqual(self.state('goal'), '5')
        field.fill('3')
        self.assertEqual(field.get_attribute('aria-invalid'), 'false')
        for _ in range(3):
            self.page.get_by_role('button', name='Add progress', exact=True).click()
        self.assertEqual(self.state('progress'), '3')
        self.assertTrue(self.page.get_by_text('Goal reached!', exact=True).is_visible())
        field.fill('2')
        self.assertEqual(self.state('goal'), '3')
        self.assertEqual(self.state('progress'), '3')
        field.fill('')
        self.page.locator('h1').first.click()
        self.assertEqual(field.input_value(), '3')
        self.page.reload()
        self.assertEqual(self.state('goal'), '3')
        self.assertEqual(self.state('progress'), '3')
        self.assertEqual(self.state('sessions'), '3')

    def test_corrupt_and_rule_invalid_storage(self):
        source = (ROOT / 'examples/reference_09.sdr').read_text()
        for saved in ('{broken', '{"goal":0,"progress":10}', '{"goal":2147483648}', 'null', '[1]', '{"goal":"oops"}'):
            self.open(source, saved)
            self.assertEqual(self.state('goal'), '5')
            self.assertEqual(self.state('progress'), '0')

    def test_overflow_action_is_atomic_and_visible(self):
        source = '''app "Overflow"
state n = 2147483647
state flag = false
action bad:
    flag = true
    n = n + 1
screen main:
    value n
    value flag
    button "Overflow" -> bad
'''
        self.open(source)
        self.page.get_by_role('button').click()
        self.assertEqual(self.state('n'), '2147483647')
        self.assertEqual(self.state('flag'), 'false')
        self.assertIn('overflow', self.page.locator('#sedrava-error').inner_text())

    def test_input_derived_overflow_is_rejected(self):
        self.open('''app "Derived input"
state n = 1
derive doubled = n * 2
screen main:
    input n
    value n
    value doubled
''')
        self.page.locator('input').fill('2147483647')
        self.assertEqual(self.state('n'), '1')
        self.assertEqual(self.page.locator('input').get_attribute('aria-invalid'), 'true')

    def test_html_script_injection_is_escaped(self):
        self.open('app "</script><script>globalThis.injected=true</script>"\nstate n = 0\nscreen main:\n    text "Safe"\n    value n\n')
        self.assertFalse(self.page.evaluate('globalThis.injected === true'))
        self.assertEqual(self.state('n'), '0')

    def test_prototype_identifier_and_signed_minimum(self):
        self.open('''app "Names"
state n = -2147483648
derive __proto__ = n + 1
screen main:
    value n
    value __proto__
''')
        self.assertEqual(self.state('n'), '-2147483648')
        self.assertEqual(self.state('__proto__'), '-2147483647')

    def test_all_ui_examples_launch_without_errors(self):
        from sedrava_core import parse
        for path in sorted((ROOT / 'examples').glob('*.sdr')):
            source = path.read_text()
            if parse(source).widgets:
                self.open(source)
                self.assertTrue(self.page.locator('body').is_visible())


if __name__ == '__main__':
    unittest.main(verbosity=2)

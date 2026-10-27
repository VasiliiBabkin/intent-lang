"""Regression tests for web output escaping."""
import unittest
from web_codegen import generate


class WebSecurityTests(unittest.TestCase):
    def test_script_end_tag_in_title_is_escaped(self):
        source = '''app "</script><script>alert(1)</script>"
state count = 0
action next: count = count + 1
screen main:
    text "Safe"
    value count
    button "Next" -> next
'''
        html = generate(source)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;/script&gt;", html)
        self.assertIn("const initialState", html)


if __name__ == "__main__":
    unittest.main()

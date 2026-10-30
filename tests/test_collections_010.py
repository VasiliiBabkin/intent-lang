import json
import unittest

from sedrava_collections import CollectionError, Task, TaskList, MAX_ITEMS


class CollectionTests(unittest.TestCase):
    def test_stable_ids_and_roundtrip(self):
        state = TaskList().add("Привет 😀").add("two")
        state = state.update(2, done=True).remove(1).add("three")
        self.assertEqual([(t.id, t.done) for t in state.items],
                         [(2, True), (3, False)])
        self.assertEqual(TaskList.restore(state.serialize()), state)

    def test_atomic_rejection(self):
        state = TaskList().add("first")
        with self.assertRaises(CollectionError):
            state.atomic(lambda s: s.add("second"),
                         lambda s: len(s.items) <= 1)
        self.assertEqual(len(state.items), 1)

    def test_capacity(self):
        state = TaskList(tuple(Task(i + 1, "x") for i in range(MAX_ITEMS)),
                         MAX_ITEMS + 1)
        with self.assertRaises(CollectionError):
            state.add("overflow")

    def test_unicode_and_invalid_titles(self):
        self.assertEqual(len(TaskList().add("😀" * 1024).items[0].title), 1024)
        for title in ("😀" * 1025, "\\ud800", "", "  "):
            with self.subTest(title=repr(title)), self.assertRaises(CollectionError):
                TaskList().add(title)

    def test_missing_identity_and_bad_types(self):
        state = TaskList().add("one")
        for action in (lambda: state.update(999, done=True),
                       lambda: state.update(1, done=1),
                       lambda: state.remove(999),
                       lambda: state.update(1, title="")):
            with self.assertRaises(CollectionError):
                action()

    def test_restore_rejects_bad_snapshots(self):
        valid = json.loads(TaskList().add("one").serialize())
        cases = ["{", "[]", json.dumps({**valid, "schema": 2}),
                 json.dumps({**valid, "next_id": True}),
                 json.dumps({**valid, "items": [valid["items"][0]] * 2}),
                 json.dumps({**valid, "items": [{"id": 1, "title": "x", "done": 1}]}),
                 json.dumps({**valid, "items": [{"id": 1, "title": "x",
                                                 "done": False, "extra": 1}]})]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(CollectionError):
                TaskList.restore(case)

    def test_id_exhaustion(self):
        with self.assertRaises(CollectionError):
            TaskList(next_id=2**31 - 1).add("x")


if __name__ == "__main__":
    unittest.main()

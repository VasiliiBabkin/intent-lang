"""Compatibility API for the original task prototype; delegates mutations to the internal language values.

New applications declare records/lists in .sdr. The schema-1 legacy codec is preserved.
"""
from dataclasses import dataclass
import json
from sedrava_records import RecordType, ListType, RecordValue, ListValue, operation

_TASK = RecordType("Task", (("title", str), ("done", bool)))
_LIST = ListType(_TASK, 100)

MAX_ITEMS = 100
MAX_TEXT = 1024
INT_MAX = 2**31 - 1


class CollectionError(ValueError):
    pass


def _integer(x):
    return type(x) is int and 0 < x <= INT_MAX


def _text(x):
    return (type(x) is str and len(x) <= MAX_TEXT
            and not any(0xD800 <= ord(c) <= 0xDFFF for c in x))


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    done: bool = False

    def __post_init__(self):
        if not _integer(self.id) or not _text(self.title) or type(self.done) is not bool:
            raise CollectionError("invalid typed task record")


@dataclass(frozen=True)
class TaskList:
    items: tuple[Task, ...] = ()
    next_id: int = 1

    def __post_init__(self):
        if (type(self.items) is not tuple or len(self.items) > MAX_ITEMS
                or not _integer(self.next_id)
                or any(type(t) is not Task for t in self.items)):
            raise CollectionError("invalid bounded collection")
        ids = [t.id for t in self.items]
        if len(ids) != len(set(ids)) or any(i >= self.next_id for i in ids):
            raise CollectionError("invalid or duplicate identity")

    def _change(self, name, *args):
        value = ListValue(_LIST, tuple((t.id, RecordValue(_TASK, (t.title, t.done))) for t in self.items), self.next_id)
        try:
            result = operation(name, [value, *args])
            return TaskList(tuple(Task(key, *record.values) for key, record in result.items), result.next_id)
        except ValueError as exc:
            raise CollectionError(str(exc)) from exc

    def add(self, title: str):
        if not _text(title) or not title.strip(): raise CollectionError("invalid title")
        return self._change('append', RecordValue(_TASK, (title, False)))

    def update(self, task_id: int, *, title=None, done=None):
        task = next((t for t in self.items if t.id == task_id), None)
        if not _integer(task_id) or task is None: raise CollectionError("missing task")
        if title is not None and (not _text(title) or not title.strip()): raise CollectionError("invalid title")
        if done is not None and type(done) is not bool: raise CollectionError("invalid boolean")
        return self._change('update', task_id, RecordValue(_TASK, (task.title if title is None else title, task.done if done is None else done)))

    def remove(self, task_id: int):
        if not _integer(task_id): raise CollectionError("missing task")
        return self._change('remove', task_id)

    def atomic(self, change, invariant=lambda state: True):
        candidate = change(self)
        if type(candidate) is not TaskList or not invariant(candidate):
            raise CollectionError("rejected candidate")
        return candidate

    def serialize(self):
        return json.dumps({"schema": 1, "next_id": self.next_id,
                           "items": [{"id": t.id, "title": t.title, "done": t.done}
                                     for t in self.items]}, ensure_ascii=True)

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not str or len(raw) > 200_000:
                raise CollectionError("invalid snapshot size")
            def no_duplicate_keys(pairs):
                result = {}
                for key, value in pairs:
                    if key in result:
                        raise CollectionError("duplicate JSON key")
                    result[key] = value
                return result
            obj = json.loads(raw, object_pairs_hook=no_duplicate_keys,
                             parse_constant=lambda value: (_ for _ in ()).throw(CollectionError("invalid JSON constant")))
            if type(obj) is not dict or set(obj) != {"schema", "next_id", "items"}:
                raise CollectionError("invalid snapshot")
            if type(obj["schema"]) is not int or obj["schema"] != 1:
                raise CollectionError("unsupported schema")
            if type(obj["items"]) is not list or len(obj["items"]) > MAX_ITEMS:
                raise CollectionError("invalid items")
            items = []
            for record in obj["items"]:
                if type(record) is not dict or set(record) != {"id", "title", "done"}:
                    raise CollectionError("invalid record")
                items.append(Task(record["id"], record["title"], record["done"]))
            return cls(tuple(items), obj["next_id"])
        except (ValueError, TypeError, KeyError, OverflowError, RecursionError) as e:
            raise CollectionError("invalid persisted collection") from e

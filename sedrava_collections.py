"""Experimental bounded task-record semantics for Sedrava 0.10.

Reference core only: not yet integrated into the .sdr parser or generators.
"""
from dataclasses import dataclass
import json

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

    def add(self, title: str):
        if not _text(title) or not title.strip() or len(self.items) >= MAX_ITEMS:
            raise CollectionError("invalid title or capacity exceeded")
        if self.next_id == INT_MAX:
            raise CollectionError("identity space exhausted")
        return TaskList(self.items + (Task(self.next_id, title),), self.next_id + 1)

    def update(self, task_id: int, *, title=None, done=None):
        if not _integer(task_id) or not any(t.id == task_id for t in self.items):
            raise CollectionError("missing task")
        if title is not None and (not _text(title) or not title.strip()):
            raise CollectionError("invalid title")
        if done is not None and type(done) is not bool:
            raise CollectionError("invalid boolean")
        return TaskList(tuple(
            Task(t.id, t.title if title is None else title,
                 t.done if done is None else done) if t.id == task_id else t
            for t in self.items), self.next_id)

    def remove(self, task_id: int):
        if not _integer(task_id) or not any(t.id == task_id for t in self.items):
            raise CollectionError("missing task")
        return TaskList(tuple(t for t in self.items if t.id != task_id), self.next_id)

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
            obj = json.loads(raw)
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

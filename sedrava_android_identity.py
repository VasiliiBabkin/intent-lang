"""Deterministic Android identity, shared by generators and verification tools."""
import hashlib
import json
import re
from pathlib import Path

# A deliberately portable lowercase subset of Java/Kotlin/Android package names.
RESERVED = frozenset('abstract as assert boolean break byte case catch char class const continue default do double else enum extends false final finally float for fun goto if implements import in instanceof int interface is long native new null object package private protected public return short static strictfp super switch synchronized this throw throws transient true try typealias typeof val var void volatile when while record sealed permits yield by constructor delegate dynamic field file get init param property receiver set setparam where actual annotation companion crossinline data expect external infix inline inner internal lateinit noinline open operator out override reified suspend tailrec vararg value _'.split())


def validate_application_id(value):
    if type(value) is not str or len(value) > 255 or not re.fullmatch(r'[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+', value) or any(part in RESERVED for part in value.split('.')):
        raise ValueError('Invalid Android application ID: use 2 or more lowercase ASCII segments, each starting with a letter; letters, digits and underscores only; no Java/Kotlin keywords; maximum 255 characters')
    return value


def application_id(name, explicit=None):
    """Exact UTF-8 title is the default identity; no paths, timestamps or random IDs."""
    return validate_application_id(explicit) if explicit is not None else 'org.sedrava.app.a' + hashlib.sha256(name.encode('utf-8')).hexdigest()[:32]


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate identity metadata key')
        result[key] = value
    return result


def project_identity(project):
    metadata = Path(project) / 'sedrava-android.json'
    try:
        if metadata.stat().st_size > 16384:
            raise ValueError('identity metadata exceeds size limit')
        data = json.loads(metadata.read_text(encoding='utf-8'), object_pairs_hook=_unique_object)
        if type(data) is not dict or set(data) != {'schema', 'application_id', 'namespace', 'title'} or type(data['schema']) is not int or data['schema'] != 1 or type(data['title']) is not str or len(data['title']) > 1024 or any(0xD800 <= ord(c) <= 0xDFFF for c in data['title']) or data['namespace'] != data['application_id']:
            raise ValueError('invalid identity metadata schema')
        return validate_application_id(data['application_id'])
    except (ValueError, OSError) as exc:
        raise ValueError(f'Invalid Android project identity at {metadata}: {exc}; regenerate in a fresh output directory') from exc


def kotlin_path(project, source_set='main', filename='MainActivity.kt'):
    return Path(project) / 'app/src' / source_set / 'java' / Path(*project_identity(project).split('.')) / filename


def prepare_identity(output, package, title):
    output = Path(output)
    metadata = output / 'sedrava-android.json'
    if metadata.exists() and project_identity(output) != package:
        raise ValueError('Android output belongs to a different application ID; choose a different --output directory')
    if not metadata.exists() and (output / 'app/src/main').exists():
        raise ValueError('Android output has no identity metadata; use a fresh --output directory for this generator')
    output.mkdir(parents=True, exist_ok=True)
    metadata.write_text(json.dumps({'schema': 1, 'application_id': package, 'namespace': package, 'title': title}, ensure_ascii=True, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def write_title(output, title):
    """Use an Android string resource so @, ?, quotes and whitespace stay data."""
    import html
    escapes = {"\\": "\\\\", '"': '\\"', "'": "\\'", "\n": "\\n", "\r": "\\r", "\t": "\\t", "@": "\\@", "?": "\\?"}
    escaped = ''.join(escapes.get(char, '\\u%04x' % ord(char) if ord(char) < 32 or ord(char) in (0xFFFE, 0xFFFF) else char) for char in title)
    target = Path(output) / 'app/src/main/res/values/strings.xml'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('<resources><string name="sedrava_app_name">"' + html.escape(escaped, quote=False) + '"</string></resources>\n', encoding='utf-8')

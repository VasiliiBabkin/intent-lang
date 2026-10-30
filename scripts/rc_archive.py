"""Bounded archive inspection for RC inputs; never execute downloaded content."""
import hashlib
import io
from pathlib import PurePosixPath
import re
import stat
import tarfile
import zipfile

MAX_BYTES = 200_000_000
MAX_FILES = 4000
PRIVATE_NAMES = {'.env', 'local.properties', 'id_rsa', 'id_ed25519', '.pypirc', '.netrc'}
PRIVATE_DIRS = {'.git', '.venv', 'venv', '__pycache__', '.gradle'}
SECRETS = [re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
           re.compile(rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
           re.compile(rb'\bgithub_pat_[A-Za-z0-9_]{30,}\b'),
           re.compile(rb'\bpypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]{20,}')]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name):
    path = PurePosixPath(name)
    if not name or '\\' in name or path.is_absolute() or '..' in path.parts or ':' in name or '\x00' in name:
        raise ValueError(f'Unsafe archive path: {name!r}')
    return path.as_posix()


def inspect_payload(name, data):
    path = PurePosixPath(safe_name(name))
    if any(part in PRIVATE_DIRS for part in path.parts) or path.name in PRIVATE_NAMES or path.suffix.lower() in {'.keystore','.jks','.p12','.pfx','.pem','.pyc','.pyo'}:
        raise ValueError(f'Private/local file in archive: {name}')
    if any(pattern.search(data) for pattern in SECRETS):
        raise ValueError(f'Potential credential/private key in archive: {name}')


def read_zip(data):
    if len(data) > MAX_BYTES:
        raise ValueError('Archive exceeds compressed size limit')
    result = {}; total = 0
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = archive.infolist()
        if len(members) > MAX_FILES:
            raise ValueError('Archive exceeds file limit')
        for member in members:
            name = safe_name(member.filename)
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode) or member.flag_bits & 1:
                raise ValueError('Symlink/encrypted archive member')
            if member.is_dir():
                continue
            total += member.file_size
            if total > MAX_BYTES or name in result:
                raise ValueError('Duplicate archive member or expanded size limit')
            payload = archive.read(member)
            inspect_payload(name, payload)
            result[name] = payload
    return result


def read_sdist(data):
    result = {}; total = 0
    if len(data) > MAX_BYTES:
        raise ValueError('Archive exceeds compressed size limit')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        for index, member in enumerate(archive):
            if index >= MAX_FILES:
                raise ValueError('Archive exceeds file limit')
            name = safe_name(member.name)
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError('Non-regular source archive member')
            total += member.size
            if total > MAX_BYTES or name in result:
                raise ValueError('Duplicate archive member or expanded size limit')
            payload = archive.extractfile(member).read()
            inspect_payload(name, payload)
            result[name] = payload
    return result


def deterministic_zip(files):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            safe_name(name)
            entry = zipfile.ZipInfo(name, date_time=(2026,1,1,0,0,0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    return output.getvalue()

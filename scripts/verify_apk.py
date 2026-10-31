"""Verify a generated APK signature and its actual merged permission surface."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import json
import hashlib


def verify(apk, sdk, expected_id=None, expected_version=None):
    tools = sdk / 'build-tools/35.0.0'
    def run(tool, *arguments):
        result = subprocess.run([str(tools / tool), *arguments, str(apk)], check=True, capture_output=True, text=True)
        return result.stdout
    signature = run('apksigner', 'verify', '--verbose', '--print-certs')
    print(signature)
    badging = run('aapt', 'dump', 'badging')
    print(badging)
    package_match = re.search(r"package: name='([^']+)'", badging)
    if not package_match:
        raise SystemExit('Missing APK application ID')
    package = package_match[1]
    version = re.search(r"versionName='([^']+)'", badging).group(1)
    code = int(re.search(r"versionCode='([0-9]+)'", badging).group(1))
    if expected_id is not None and package != expected_id:
        raise SystemExit(f'Unexpected APK ID: {package}')
    if expected_version is not None and version != expected_version:
        raise SystemExit(f'Unexpected APK version: {version}')
    # Check actual APK identity against generator output, not only AndroidX permission names.
    for parent in apk.resolve().parents:
        metadata = parent / 'sedrava-android.json'
        if metadata.is_file():
            expected = json.loads(metadata.read_text(encoding='utf-8'))['application_id']
            if package != expected:
                raise SystemExit(f'APK identity mismatch: expected {expected}, found {package}')
            break
    permissions = run('aapt', 'dump', 'permissions')
    print(permissions)
    used = set(re.findall(r"uses-permission: name='([^']+)'", permissions))
    allowed = {package + '.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION'}
    if used - allowed:
        raise SystemExit(f'Unexpected permissions: {sorted(used - allowed)}')
    if used:
        manifest = subprocess.run([str(tools / 'aapt'), 'dump', 'xmltree', str(apk), 'AndroidManifest.xml'], check=True, capture_output=True, text=True).stdout
        if not re.search(r'protectionLevel[^\n]*0x2\b', manifest):
            raise SystemExit('Internal AndroidX permission must use signature protection')
    print('PASS: APK signature and merged permission allowlist')
    certificate = re.search(r'Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]+)', signature)
    if certificate is None:
        raise SystemExit('Missing signer certificate fingerprint')
    return {'sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'application_id':package, 'version_name':version, 'version_code':code,
            'debuggable':'application-debuggable' in badging,
            'signer_certificate_sha256':certificate[1].lower(),'permissions':sorted(used)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('apk', type=Path)
    parser.add_argument('--sdk', type=Path, default=os.environ.get('ANDROID_HOME'))
    parser.add_argument('--application-id')
    parser.add_argument('--version')
    parser.add_argument('--json-output',type=Path)
    args = parser.parse_args()
    if args.sdk is None:
        parser.error('Set ANDROID_HOME or --sdk')
    result=verify(args.apk, args.sdk, args.application_id, args.version)
    if args.json_output:
        args.json_output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')

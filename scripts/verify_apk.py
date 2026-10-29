"""Verify a generated APK signature and its actual merged permission surface."""
import argparse
import os
from pathlib import Path
import re
import subprocess


def verify(apk, sdk):
    tools = sdk / 'build-tools/35.0.0'
    def run(tool, *arguments):
        result = subprocess.run([str(tools / tool), *arguments, str(apk)], check=True, capture_output=True, text=True)
        return result.stdout
    print(run('apksigner', 'verify', '--verbose'))
    print(run('aapt', 'dump', 'badging'))
    permissions = run('aapt', 'dump', 'permissions')
    print(permissions)
    used = set(re.findall(r"uses-permission: name='([^']+)'", permissions))
    allowed = {'org.sedrava.generated.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION'}
    if used - allowed:
        raise SystemExit(f'Unexpected permissions: {sorted(used - allowed)}')
    if used:
        manifest = subprocess.run([str(tools / 'aapt'), 'dump', 'xmltree', str(apk), 'AndroidManifest.xml'], check=True, capture_output=True, text=True).stdout
        if not re.search(r'protectionLevel[^\n]*0x2\b', manifest):
            raise SystemExit('Internal AndroidX permission must use signature protection')
    print('PASS: APK signature and merged permission allowlist')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('apk', type=Path)
    parser.add_argument('--sdk', type=Path, default=os.environ.get('ANDROID_HOME'))
    args = parser.parse_args()
    if args.sdk is None:
        parser.error('Set ANDROID_HOME or --sdk')
    verify(args.apk, args.sdk)

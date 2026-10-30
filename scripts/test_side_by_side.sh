#!/usr/bin/env bash
# Both untouched generators' apps have already passed their UI scenarios.
set -euo pipefail
sedrava_first=$(python -c "import json;print(json.load(open('build/navigation-android/sedrava-android.json'))['application_id'])")
sedrava_second=$(python -c "import json;print(json.load(open('build/tasks-android/sedrava-android.json'))['application_id'])")
test "$sedrava_first" != "$sedrava_second"
adb shell pm path "$sedrava_first" | tee build/side-by-side-first-package.txt
adb shell pm path "$sedrava_second" | tee build/side-by-side-second-package.txt
# Reinstall/update the first package without clearing its accepted data.
adb shell am force-stop "$sedrava_first"
adb install -r build/navigation-android/app/build/outputs/apk/debug/app-debug.apk
adb shell run-as "$sedrava_first" cat shared_prefs/sedrava_state.xml > build/side-by-side-first.xml
adb shell run-as "$sedrava_second" cat shared_prefs/sedrava_state.xml > build/side-by-side-second.xml
python - <<'PY'
import json
import xml.etree.ElementTree as E
from pathlib import Path
def tasks(path):
    r=E.parse(path).getroot()
    return json.loads(next(n.text for n in r if n.get('name')=='snapshot'))['state']['tasks']
assert tasks('build/side-by-side-first.xml')=={'next_id':3,'items':[{'id':2,'title':'Second','done':True}]}
assert tasks('build/side-by-side-second.xml')=={'next_id':3,'items':[{'id':2,'title':'restart persisted','done':False}]}
assert all('package:' in Path('build/side-by-side-'+n+'-package.txt').read_text() for n in ('first','second'))
print('PASS: two installed packages, independent persisted records, update retained data')
PY
adb shell am start -W -n "$sedrava_first"/.MainActivity
adb shell uiautomator dump /sdcard/side-by-side-ui.xml
adb shell cat /sdcard/side-by-side-ui.xml > build/side-by-side-first-ui.xml
python - <<'PY'
from pathlib import Path
s=Path('build/side-by-side-first-ui.xml').read_text()
assert 'Make room for what matters.' in s and 'One thing at a time.' not in s
PY
adb exec-out screencap -p > build/side-by-side-first.png

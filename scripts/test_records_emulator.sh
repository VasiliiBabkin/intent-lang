#!/usr/bin/env bash
# Run inside android-emulator-runner, after generating the task manager test harness.
set -euo pipefail
gradle -p build/tasks-android --no-daemon :app:connectedDebugAndroidTest
adb shell am force-stop org.sedrava.generated
adb shell run-as org.sedrava.generated cat shared_prefs/sedrava_state.xml > build/tasks-preferences.xml
python - <<'PY'
import json
import xml.etree.ElementTree as ET
root = ET.parse('build/tasks-preferences.xml').getroot()
snapshot = json.loads(next(node.text for node in root if node.attrib.get('name') == 'snapshot'))
assert snapshot['state']['tasks'] == {'next_id': 3, 'items': [{'id': 2, 'title': 'restart persisted', 'done': False}]}
PY
adb shell am start -W -n org.sedrava.generated/.MainActivity
relaunch_verified=0
for attempt in $(seq 1 10); do
  adb shell uiautomator dump /sdcard/sedrava-ui.xml
  adb shell cat /sdcard/sedrava-ui.xml > build/tasks-relaunch.xml
  if python -c "from pathlib import Path; raise SystemExit('restart persisted' not in Path('build/tasks-relaunch.xml').read_text())"; then
    relaunch_verified=1
    break
  fi
done
test "$relaunch_verified" = 1
adb exec-out screencap -p > build/tasks-relaunch.png

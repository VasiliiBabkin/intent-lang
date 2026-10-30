#!/usr/bin/env bash
set -euo pipefail
gradle -p build/navigation-android --no-daemon -Pandroid.injected.androidTest.leaveApksInstalledAfterRun=true :app:connectedDebugAndroidTest
adb shell am force-stop org.sedrava.generated
adb shell run-as org.sedrava.generated cat shared_prefs/sedrava_state.xml > build/navigation-preferences.xml
python - <<'PY'
import json
import xml.etree.ElementTree as ET
root=ET.parse('build/navigation-preferences.xml').getroot()
saved=json.loads(next(node.text for node in root if node.attrib.get('name')=='snapshot'))
assert saved['state']['tasks']=={'next_id':3,'items':[{'id':2,'title':'Second','done':True}]}, saved
PY
adb shell am start -W -n org.sedrava.generated/.MainActivity
navigation_relaunch_verified=0
for attempt in $(seq 1 10); do
  adb shell uiautomator dump /sdcard/navigation-ui.xml
  adb shell cat /sdcard/navigation-ui.xml > build/navigation-relaunch.xml
  if python -c "from pathlib import Path; t=Path('build/navigation-relaunch.xml').read_text();raise SystemExit('Make room for what matters.' not in t or 'One thing at a time.' in t)"; then
    navigation_relaunch_verified=1
    break
  fi
done
test "$navigation_relaunch_verified" = 1
adb exec-out screencap -p > build/navigation-relaunch.png

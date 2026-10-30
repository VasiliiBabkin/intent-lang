#!/usr/bin/env bash
set -euo pipefail
sedrava_package=$(python -c "import json;print(json.load(open('build/navigation-android/sedrava-android.json'))['application_id'])")
# Exercise native scalable text at 130%, including rotation/recreation and scrolling.
adb shell settings put system font_scale 1.3
cleanup_navigation_test() {
  navigation_test_status=$?
  if [ "$navigation_test_status" -ne 0 ]; then
    adb shell run-as "$sedrava_package" cat shared_prefs/sedrava_state.xml > build/navigation-failure.preferences.xml || true
    adb shell uiautomator dump /sdcard/navigation-failure.xml || true
    adb shell cat /sdcard/navigation-failure.xml > build/navigation-failure.ui.xml || true
    adb exec-out screencap -p > build/navigation-failure.png || true
    adb logcat -d -s SedravaUiFailure:V > build/navigation-failure.log || true
    python - <<'DIAGNOSTIC'
from pathlib import Path
for file in ('build/navigation-failure.preferences.xml','build/navigation-failure.log'):
    p=Path(file)
    if p.exists(): print(p.name+':\n'+p.read_text(errors='replace')[:16000])
DIAGNOSTIC
  fi
  adb shell settings put system font_scale 1.0 || true
  exit "$navigation_test_status"
}
trap cleanup_navigation_test EXIT
adb shell settings get system font_scale > build/navigation-font-scale.txt
gradle -p build/navigation-android --no-daemon -Pandroid.injected.androidTest.leaveApksInstalledAfterRun=true :app:connectedDebugAndroidTest
adb shell am force-stop "$sedrava_package"
adb shell run-as "$sedrava_package" cat shared_prefs/sedrava_state.xml > build/navigation-preferences.xml
python - <<'PY'
import json
import xml.etree.ElementTree as ET
root=ET.parse('build/navigation-preferences.xml').getroot()
saved=json.loads(next(node.text for node in root if node.attrib.get('name')=='snapshot'))
assert saved['state']['tasks']=={'next_id':3,'items':[{'id':2,'title':'Second','done':True}]}, saved
PY
adb shell am start -W -n "$sedrava_package"/.MainActivity
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
cp build/navigation-relaunch.xml build/navigation-relaunch.initial.xml
# Verify the restored task in the actual UI as well as the durable preferences.
navigation_record_verified=0
for attempt in $(seq 1 5); do
  adb shell uiautomator dump /sdcard/navigation-ui.xml
  adb shell cat /sdcard/navigation-ui.xml > build/navigation-relaunch.xml
  if python -c "import xml.etree.ElementTree as E; r=E.parse('build/navigation-relaunch.xml').getroot(); raise SystemExit(not any(n.get('text')=='Second' or n.get('content-desc')=='Open Second' for n in r.iter()))"; then
    navigation_record_verified=1
    break
  fi
  adb shell input swipe 500 750 500 250 200
done
test "$navigation_record_verified" = 1
adb exec-out screencap -p > build/navigation-relaunch.png

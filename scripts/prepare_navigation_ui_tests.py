"""Compose/device tests added beside the generated application, never into it."""
import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sedrava_android_identity import project_identity, kotlin_path

project=Path(sys.argv[1]);gradle=project/'app/build.gradle.kts'
s=re.sub(r'(versionCode = [0-9]+;)', r'testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"; \1', gradle.read_text())
s+='\ndependencies { androidTestImplementation(platform("androidx.compose:compose-bom:2024.12.01")); androidTestImplementation("androidx.compose.ui:ui-test-junit4"); androidTestImplementation("androidx.test:runner:1.6.2"); androidTestImplementation("androidx.test.ext:junit:1.2.1"); androidTestImplementation("androidx.test.uiautomator:uiautomator:2.3.0"); debugImplementation("androidx.compose.ui:ui-test-manifest") }\n';gradle.write_text(s)
p=kotlin_path(project, 'androidTest', 'NavigationUiTest.kt');p.parent.mkdir(parents=True,exist_ok=True)
p.write_text('''package org.sedrava.generated
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.UiDevice
import android.content.pm.ActivityInfo
import org.junit.Rule
import org.junit.Test
class NavigationUiTest {
  @get:Rule val ui=createAndroidComposeRule<MainActivity>()
  @Test fun sharedTasksSystemBackRotationAndDeletion() {
    ui.onNodeWithTag("screen-main").assertExists()
    ui.onNodeWithTag("input-new_title").performTextReplacement("First 😀")
    ui.onNodeWithText("Add task").performScrollTo().performClick()
    ui.onNodeWithContentDescription("Open First 😀").performScrollTo().performClick()
    ui.onNodeWithTag("screen-details").assertExists()
    ui.onNodeWithTag("input-title").performTextReplacement("Renamed")
    ui.activityRule.scenario.onActivity { it.requestedOrientation=ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE }
    ui.waitForIdle()
    ui.onNodeWithTag("screen-details").assertExists()
    ui.activityRule.scenario.recreate()
    ui.onNodeWithTag("screen-details").assertExists()
    ui.onNodeWithTag("input-title").assertTextContains("Renamed")
    ui.onNodeWithText("Save title").performScrollTo().performClick()
    ui.onNodeWithText("Toggle completion").performScrollTo().performClick()
    ui.onNodeWithText("Completed · nicely done").assertExists()
    UiDevice.getInstance(InstrumentationRegistry.getInstrumentation()).pressBack()
    ui.waitForIdle()
    ui.onNodeWithTag("screen-main").assertExists()
    ui.onNodeWithTag("input-new_title").performTextReplacement("Second")
    ui.onNodeWithText("Add task").performScrollTo().performClick()
    ui.onNodeWithContentDescription("Open Renamed").performScrollTo().performClick()
    ui.onNodeWithText("Delete task").performScrollTo().performClick()
    ui.onNodeWithTag("screen-main").assertExists()
    ui.onNodeWithTag("item-1").assertDoesNotExist()
    ui.onNodeWithTag("item-2").assertExists()
    ui.onNodeWithContentDescription("Open Second").performScrollTo().performClick()
    ui.onNodeWithTag("input-title").performTextReplacement("")
    ui.onNodeWithText("Save title").performScrollTo().performClick()
    ui.onNodeWithTag("action-error").assertExists()
    ui.onNodeWithTag("screen-details").assertExists()
    ui.onNodeWithTag("input-title").performTextReplacement("😀".repeat(1025))
    ui.onNodeWithText("Enter a valid value that satisfies the app rules.").assertExists()
    ui.onNodeWithText("Save title").assertIsNotEnabled()
    ui.onNodeWithText("Back to tasks").assertIsEnabled()
    ui.onNodeWithTag("input-title").performTextReplacement("Second")
    ui.onNodeWithText("Toggle completion").performScrollTo().performClick()
    ui.onNodeWithText("Back to tasks").performScrollTo().performClick()
    ui.onNodeWithTag("screen-main").assertExists()
    ui.onNodeWithTag("item-2").assertExists()
    ui.onNodeWithContentDescription("Open Second").performScrollTo().performClick()
    // Leave details active: a new process must still start at the declared main screen.
    ui.onNodeWithTag("screen-details").assertExists()
  }
}
'''.replace('org.sedrava.generated', project_identity(project)),encoding='utf-8');print(p)

if '--scalar' in sys.argv:
    p.write_text("""package PACKAGE
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import org.junit.Rule
import org.junit.Test
class ScalarUiTest {
  @get:Rule val ui=createAndroidComposeRule<MainActivity>()
  @Test fun repeatedEditorsDoNotEnableStaleActions() {
    ui.onNodeWithText("Count",substring=false).assertExists()
    val first=ui.onAllNodes(hasSetTextAction())[0]
    val mirror=ui.onAllNodes(hasSetTextAction())[1]
    first.performTextReplacement("12")
    ui.waitForIdle()
    mirror.assertTextContains("12")
    first.performTextReplacement("1.5")
    ui.onNodeWithText("Next").assertIsNotEnabled()
    mirror.performTextReplacement("12") // Same accepted value must not clear another editor's error.
    ui.onNodeWithText("Next").assertIsNotEnabled()
    first.performTextReplacement("12")
    ui.onNodeWithText("Next").assertIsEnabled()
    ui.onNodeWithText("Next").performScrollTo().performClick()
    ui.onNodeWithTag("screen-other").assertExists()
    ui.onNodeWithText("n: 13").assertExists()
  }
}
""".replace('PACKAGE',project_identity(project)),encoding='utf-8')

if '--seed-upgrade' in sys.argv:
    p.write_text('''package PACKAGE
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import org.junit.Rule
import org.junit.Test
class UpgradeSeedTest {
  @get:Rule val ui=createAndroidComposeRule<MainActivity>()
  @Test fun seedAcceptedDataThroughBaselineUi() {
    ui.onNodeWithTag("input-new_title").performTextReplacement("Upgrade kept")
    ui.onNodeWithText("Add task").performScrollTo().performClick()
    ui.onNodeWithContentDescription("Open Upgrade kept").assertExists()
  }
}
'''.replace('PACKAGE',project_identity(project)),encoding='utf-8')

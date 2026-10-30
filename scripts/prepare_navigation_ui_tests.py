"""Compose/device tests added beside the generated application, never into it."""
from pathlib import Path
import sys
project=Path(sys.argv[1]);gradle=project/'app/build.gradle.kts'
s=gradle.read_text().replace('versionCode = 1;','testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"; versionCode = 1;')
s+='\ndependencies { androidTestImplementation(platform("androidx.compose:compose-bom:2024.12.01")); androidTestImplementation("androidx.compose.ui:ui-test-junit4"); androidTestImplementation("androidx.test:runner:1.6.2"); androidTestImplementation("androidx.test.ext:junit:1.2.1"); androidTestImplementation("androidx.test.uiautomator:uiautomator:2.3.0"); debugImplementation("androidx.compose.ui:ui-test-manifest") }\n';gradle.write_text(s)
p=project/'app/src/androidTest/java/org/sedrava/generated/NavigationUiTest.kt';p.parent.mkdir(parents=True,exist_ok=True)
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
''',encoding='utf-8');print(p)

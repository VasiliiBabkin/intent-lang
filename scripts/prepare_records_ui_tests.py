"""Add emulator Compose interaction/rotation checks to a generated task manager."""
from pathlib import Path
import sys
project=Path(sys.argv[1])
gradle=project/'app/build.gradle.kts'
text=gradle.read_text().replace('versionCode = 1;', 'testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"; versionCode = 1;')
text+='\ndependencies { androidTestImplementation(platform("androidx.compose:compose-bom:2024.12.01")); androidTestImplementation("androidx.compose.ui:ui-test-junit4"); androidTestImplementation("androidx.test:runner:1.6.2"); androidTestImplementation("androidx.test.ext:junit:1.2.1"); debugImplementation("androidx.compose.ui:ui-test-manifest") }\n'
gradle.write_text(text)
path=project/'app/src/androidTest/java/org/sedrava/generated/RecordsUiTest.kt';path.parent.mkdir(parents=True,exist_ok=True)
path.write_text('''package org.sedrava.generated
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import org.junit.Rule
import org.junit.Test
class RecordsUiTest {
  @get:Rule val ui = createAndroidComposeRule<MainActivity>()
  @Test fun addEditCompleteRotateDeleteAndReject() {
    ui.onNodeWithText("No tasks yet / Список пуст").assertExists()
    ui.onNode(hasSetTextAction()).performTextReplacement("first 😀")
    ui.onNodeWithText("Add / Добавить").performScrollTo().performClick()
    ui.onNodeWithText("title: first 😀 · done: false").assertExists()
    ui.onNodeWithText("Select / Выбрать").performScrollTo().performClick()
    ui.onNodeWithText("Complete / Выполнено").performScrollTo().performClick()
    ui.onNodeWithText("title: first 😀 · done: true").assertExists()
    ui.onNode(hasSetTextAction()).performTextReplacement("renamed")
    ui.onNodeWithText("Rename / Переименовать").performScrollTo().performClick()
    ui.activityRule.scenario.onActivity { it.requestedOrientation = android.content.pm.ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE }
    ui.waitForIdle()
    ui.activityRule.scenario.recreate()
    ui.onNodeWithText("title: renamed · done: true").assertExists()
    ui.onNodeWithText("selected: 1").assertExists()
    ui.onNode(hasSetTextAction()).performTextReplacement("😀".repeat(1025))
    ui.onNodeWithText("Add / Добавить").performScrollTo().performClick()
    ui.onNodeWithText("title: renamed · done: true").assertExists()
    ui.onNodeWithText("Delete / Удалить").performScrollTo().performClick()
    ui.onNodeWithText("No tasks yet / Список пуст").assertExists()
    ui.activityRule.scenario.recreate()
    ui.onNodeWithText("No tasks yet / Список пуст").assertExists()
    ui.onNode(hasSetTextAction()).performTextReplacement("restart persisted")
    ui.onNodeWithText("Add / Добавить").performScrollTo().performClick()
    ui.onNodeWithText("title: restart persisted · done: false").assertExists()
  }
}
''',encoding='utf-8')
print(path)

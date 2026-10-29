"""Add JVM tests to a generated Lab project; no emulator/UI acceptance implied."""
import argparse
from pathlib import Path

TEST = '''package org.sedrava.generated
import org.junit.Assert.*
import org.junit.Test
class LabStateTest {
    @Test fun defaultsAndBoundaries() {
        assertTrue(validState(5, 0, 0))
        assertTrue(validState(1, 1, 2147483647))
        assertTrue(validState(20, 20, 1))
    }
    @Test fun rejectCorruptSnapshotsAndInput() {
        assertFalse(validState(0, 0, 0))
        assertFalse(validState(21, 0, 0))
        assertFalse(validState(3, 5, 0))
        assertFalse(validState(5, -1, 0))
        assertFalse(validState(5, 0, -1))
        assertFalse(validState(2147483647, 0, 0))
        assertFalse(validState(-2147483648, 0, 0))
    }
}
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    path = args.project / 'app/src/test/java/org/sedrava/generated/LabStateTest.kt'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEST, encoding='utf-8')
    print(path)

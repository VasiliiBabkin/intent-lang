"""Validate the built Sedrava archives before any registry upload."""
import email
import pathlib
import tarfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
EXPECTED_MODULES = {
    "sedrava.py", "sedrava_core.py", "sedrava_cli.py",
    "android_codegen.py", "android_codegen_v03.py", "web_codegen.py",
}
LICENSE_MARKER = "Apache License"
VERSION = "0.7.0a1"


def check_metadata(raw):
    metadata = email.message_from_bytes(raw)
    assert metadata.get("Name", "").lower().replace("_", "-") == "sedrava", "wrong package name"
    assert metadata.get("Version") == VERSION, "wrong package version"
    assert metadata.get("License-Expression") == "Apache-2.0", "missing SPDX license metadata"


def main():
    wheel_files = list(DIST.glob("*.whl"))
    sdist_files = list(DIST.glob("*.tar.gz"))
    assert len(wheel_files) == len(sdist_files) == 1, "expected exactly one wheel and one sdist"
    with zipfile.ZipFile(wheel_files[0]) as archive:
        names = archive.namelist()
        assert EXPECTED_MODULES.issubset(set(names)), "wheel missing Python modules"
        licenses = [name for name in names if name.endswith("/LICENSE") or "/licenses/" in name and name.endswith("LICENSE")]
        assert licenses, "wheel missing LICENSE"
        assert LICENSE_MARKER in archive.read(licenses[0]).decode(), "incorrect LICENSE"
        metadata = [name for name in names if name.endswith(".dist-info/METADATA")]
        assert len(metadata) == 1
        check_metadata(archive.read(metadata[0]))
    with tarfile.open(sdist_files[0], "r:gz") as archive:
        names = archive.getnames()
        assert all(any(name.endswith("/" + module) for name in names) for module in EXPECTED_MODULES), "sdist missing modules"
        license_files = [name for name in names if name.endswith("/LICENSE")]
        assert license_files, "sdist missing LICENSE"
        member = archive.extractfile(license_files[0])
        assert member is not None and LICENSE_MARKER in member.read().decode(), "sdist license invalid"
    print("PASS: wheel/sdist, Apache-2.0 metadata and bundled license")


if __name__ == "__main__":
    main()

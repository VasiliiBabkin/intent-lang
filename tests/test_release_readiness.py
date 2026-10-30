"""Identity, reproducible generation and installed-CLI boundary regressions."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from android_codegen_v03 import generate
from sedrava_android_identity import application_id, validate_application_id, project_identity
from sedrava_cli import main

ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'examples/task_manager_navigation.sdr').read_text(encoding='utf-8')

class ReleaseReadinessTests(unittest.TestCase):
    def test_title_identity_exact_unicode_whitespace_punctuation(self):
        titles=['Tasks','tasks',' Tasks','Tasks ','Task s','Tasks!','Задачи 😀','é','é','a'*1024]
        ids=[application_id(t) for t in titles]
        self.assertEqual(len(set(ids)),len(titles))
        for title, package in zip(titles, ids):
            self.assertEqual(package,application_id(title))
            self.assertEqual(package,'org.sedrava.app.a'+hashlib.sha256(title.encode()).hexdigest()[:32])
            self.assertEqual(package,validate_application_id(package))
        self.assertEqual(application_id('one','com.example.tasks'),application_id('two','com.example.tasks'))

    def test_strict_id_validation_and_length(self):
        for bad in ('','single','.com.a','com.a.','Com.example','com.1a','com._a','com.a-b','com.cláss','com.class','com.when','com.true','com.a\n','com.a/b','com.a"','a.'+'b'*254,None,42):
            with self.subTest(bad=bad),self.assertRaises(ValueError):validate_application_id(bad)
        self.assertEqual(len(validate_application_id('a.'+'b'*253)),255)
        self.assertEqual(validate_application_id('com.example.task_2'),'com.example.task_2')

    def test_generation_stability_namespaces_and_escaped_title(self):
        source=SOURCE.replace('Daybook · Tasks','Задачи & \\"день\\" $price')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            target=generate(source,root/'first',application_id='com.example.daybook')
            before={p.relative_to(root/'first'):p.read_bytes() for p in (root/'first').rglob('*') if p.is_file()}
            generate(source,root/'first',application_id='com.example.daybook')
            other=generate(source,root/'other',application_id='com.example.daybook')
            after={p.relative_to(root/'other'):p.read_bytes() for p in (root/'other').rglob('*') if p.is_file()}
            self.assertEqual(before,after)
            self.assertEqual(project_identity(root/'first'),'com.example.daybook')
            self.assertIn('package com.example.daybook',target.read_text())
            self.assertEqual(other.relative_to(root/'other'),Path('app/src/main/java/com/example/daybook/MainActivity.kt'))
            manifest=(root/'first/app/src/main/AndroidManifest.xml').read_text()
            import xml.etree.ElementTree as ET
            title=ET.fromstring(manifest).find('application').get('{http://schemas.android.com/apk/res/android}label')
            self.assertEqual(title,'@string/sedrava_app_name')
            resource=(root/'first/app/src/main/res/values/strings.xml').read_text()
            self.assertIn('Задачи &amp;',resource)
            self.assertIn(r'\"день\"',resource)
            self.assertNotIn('uses-permission',manifest)
            with self.assertRaisesRegex(ValueError,'different application ID'):generate(SOURCE,root/'first')
            self.assertEqual(before,{p.relative_to(root/'first'):p.read_bytes() for p in (root/'first').rglob('*') if p.is_file()})

    def test_android_title_controls_are_valid_xml_and_reproducible(self):
        import xml.etree.ElementTree as E
        from sedrava_android_identity import write_title
        title='@? " \\ '+''.join(chr(n) for n in range(32))+'\ufffe\uffff 😀'
        with tempfile.TemporaryDirectory() as tmp:
            write_title(tmp,title)
            p=Path(tmp)/'app/src/main/res/values/strings.xml';before=p.read_bytes()
            E.fromstring(before) # Raw XML-illegal Unicode scalars must be escaped for AAPT.
            self.assertIn(b'\\u0000',before);self.assertIn(b'\\ufffe',before)
            write_title(tmp,title);self.assertEqual(p.read_bytes(),before)

    def test_invalid_build_no_partial_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'bad.sdr';source.write_text('app "Bad"\nscreen main:\n    text "Bad"\n    nope\n')
            for target,out in [('web',root/'web/index.html'),('android',root/'android')]:
                err=io.StringIO()
                with contextlib.redirect_stderr(err):result=main(['build',target,str(source),'--output',str(out)])
                self.assertEqual(result,1);self.assertIn(':4:',err.getvalue());self.assertFalse(out.parent.exists() if target=='web' else out.exists())
            source.write_text(SOURCE)
            with contextlib.redirect_stderr(io.StringIO()):result=main(['build','android',str(source),'--application-id','bad-id','--output',str(root/'bad-id')])
            self.assertEqual(result,1);self.assertFalse((root/'bad-id').exists())

    def test_cli_missing_utf8_and_web_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'source.sdr'
            for data in (None,b'\xff'):
                if data is not None:path.write_bytes(data)
                with contextlib.redirect_stderr(io.StringIO()):self.assertEqual(main(['check',str(path)]),1)
            with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as exc:main(['build','web',str(path),'--application-id','com.example.app'])
            self.assertEqual(exc.exception.code,2)

    def test_corrupt_project_metadata_rejected_without_traceback_or_mutation(self):
        for raw in ('{', '{}', '[]', '{"schema":true}', '{"schema":1,"schema":1}', ' '*16385):
            with self.subTest(raw=raw[:40]),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);source=root/'app.sdr';source.write_text(SOURCE)
                output=root/'android';output.mkdir();metadata=output/'sedrava-android.json';metadata.write_text(raw)
                error=io.StringIO()
                with contextlib.redirect_stderr(error):result=main(['build','android',str(source),'--output',str(output)])
                self.assertEqual(result,1);self.assertIn('Invalid Android project identity',error.getvalue())
                self.assertEqual(metadata.read_text(),raw);self.assertFalse((output/'app').exists())

    def test_duplicate_titles_explicit_identity_and_old_package_opt_in(self):
        self.assertEqual(application_id('Duplicate'),application_id('Duplicate'))
        with tempfile.TemporaryDirectory() as tmp:
            for folder,package in [('a','com.example.one'),('b','com.example.two'),('legacy','org.sedrava.generated')]:
                code=generate(SOURCE,Path(tmp)/folder,application_id=package).read_text()
                self.assertIn('package '+package,code)
                self.assertEqual(project_identity(Path(tmp)/folder),package)

if __name__=='__main__':unittest.main()

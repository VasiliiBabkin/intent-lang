"""Build legacy app examples; static sites have a separate target and artifact."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sedrava_syntax import document_kind
from sedrava_core import parse
from web_codegen import generate

output=ROOT/'build/web';output.mkdir(parents=True,exist_ok=True)
for path in sorted((ROOT/'examples').glob('*.sdr')):
    source=path.read_text(encoding='utf-8')
    if document_kind(source)=='site':
        from sedrava_site import parse_site
        parse_site(source)
        continue
    if parse(source).widgets:(output/(path.stem+'.html')).write_text(generate(source),encoding='utf-8')

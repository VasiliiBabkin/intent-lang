"""Verify a downloaded RC directory against both inventory and recorded hashes."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.prepare_rc import verify_bundle
if __name__=='__main__':
    try:
        verify_bundle(Path(sys.argv[1]))
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('RC bundle rejected: '+str(exc),file=sys.stderr)
        raise SystemExit(1)

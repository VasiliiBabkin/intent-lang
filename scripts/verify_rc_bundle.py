"""Verify a downloaded RC directory against both inventory and recorded hashes."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.prepare_rc import verify_bundle
if __name__=='__main__':
    verify_bundle(Path(sys.argv[1]))

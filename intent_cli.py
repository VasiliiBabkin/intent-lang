"""Command line interface for the experimental Intent compiler."""
import argparse
import sys
from pathlib import Path

from intent_core import parse, run

VERSION = "0.6.0a1"

def main(argv=None):
    parser = argparse.ArgumentParser(prog="intent", description="Intent experimental compiler")
    parser.add_argument("--version", action="version", version=f"intent {VERSION}")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="Parse and type-check an Intent program")
    check.add_argument("source", type=Path)
    test = commands.add_parser("test", help="Run embedded Intent tests")
    test.add_argument("source", type=Path)
    build = commands.add_parser("build", help="Generate an application")
    build.add_argument("target", choices=("web", "android"))
    build.add_argument("source", type=Path)
    build.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        source = args.source.read_text(encoding="utf-8")
        if args.command == "check":
            parse(source)
            print(f"OK: {args.source}")
        elif args.command == "test":
            count = run(parse(source))
            print(f"PASS: {count} Intent tests")
        elif args.target == "web":
            from web_codegen import generate
            output = args.output or Path("build/web/index.html")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(generate(source), encoding="utf-8")
            print(output)
        else:
            from android_codegen_v03 import generate
            output = args.output or Path("build/generated-android")
            print(generate(source, output))
        return 0
    except (OSError, ValueError, AssertionError) as exc:
        print(f"intent: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

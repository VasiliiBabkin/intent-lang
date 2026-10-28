"""Command line interface for the experimental Sedrava compiler."""
import argparse
import re
import sys
from pathlib import Path

from sedrava_core import parse, run

VERSION = "0.7.1a1"

def main(argv=None):
    parser = argparse.ArgumentParser(prog="sedrava", description="Sedrava experimental compiler")
    parser.add_argument("--version", action="version", version=f"sedrava {VERSION}")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="Parse and type-check an Sedrava program")
    check.add_argument("source", type=Path)
    test = commands.add_parser("test", help="Run embedded Sedrava tests")
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
            print(f"PASS: {count} Sedrava tests")
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
        message = str(exc)
        match = re.match(r"Line (\d+): (?:column (\d+): )?(.*)", message)
        if match:
            print(f"{args.source}:{match.group(1)}:{match.group(2) or 1}: error: {match.group(3)}", file=sys.stderr)
        else:
            print(f"sedrava: {args.source}: {message}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

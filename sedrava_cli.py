"""Command line interface for the experimental Sedrava compiler."""
import argparse
import json
import re
import sys
from pathlib import Path

from sedrava_records import plain, serialize_state, restore_snapshot
from sedrava_core import MAX_SOURCE_CHARS, parse, run, resolve, transition

VERSION = "0.10.0.dev0"

def main(argv=None):
    parser = argparse.ArgumentParser(prog="sedrava", description="Sedrava experimental compiler")
    parser.add_argument("--version", action="version", version=f"sedrava {VERSION}")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="Parse and type-check an Sedrava program")
    check.add_argument("source", type=Path)
    execute = commands.add_parser("run", help="Print interpreter state after an optional action sequence")
    execute.add_argument("source", type=Path)
    execute.add_argument("--state-file", type=Path, help="Restore and atomically save accepted persistent state")
    execute.add_argument("actions", nargs="*", help="Actions to execute in order; no wall-clock or UI loop")
    test = commands.add_parser("test", help="Run embedded Sedrava tests")
    test.add_argument("source", type=Path)
    build = commands.add_parser("build", help="Generate an application")
    build.add_argument("target", choices=("web", "android"))
    build.add_argument("source", type=Path)
    build.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.source.stat().st_size > MAX_SOURCE_CHARS * 4:
            raise ValueError("Source exceeds size limit")
        with args.source.open(encoding="utf-8") as handle:
            source = handle.read(MAX_SOURCE_CHARS + 1)
        if args.command == "check":
            parse(source)
            print(f"OK: {args.source}")
        elif args.command == "run":
            program = parse(source)
            state = program.states.copy()
            if args.state_file and args.state_file.exists():
                if args.state_file.stat().st_size > 800000: raise ValueError('Snapshot too large')
                raw = args.state_file.read_text(encoding='utf-8')
                state = restore_snapshot(program, raw)
            for action in args.actions:
                state, accepted = transition(program, state, action)
                if not accepted:
                    raise ValueError(f"Action {action}: invariant rejected; state unchanged")
            if args.state_file:
                import os
                import tempfile
                raw = serialize_state(program, state)
                args.state_file.parent.mkdir(parents=True, exist_ok=True)
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=args.state_file.parent, delete=False) as handle:
                        temporary = handle.name
                        handle.write(raw)
                    os.replace(temporary, args.state_file)
                finally:
                    if temporary and os.path.exists(temporary): os.unlink(temporary)
            print(json.dumps({k: plain(v) for k, v in resolve(state, program.derived).items()}, ensure_ascii=False, sort_keys=True))
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
    except (OSError, ValueError, AssertionError, RecursionError) as exc:
        message = str(exc)
        match = re.match(r"Line (\d+): (?:column (\d+): )?(.*)", message)
        if match:
            print(f"{args.source}:{match.group(1)}:{match.group(2) or 1}: error: {match.group(3)}", file=sys.stderr)
        else:
            print(f"sedrava: {args.source}: {message}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

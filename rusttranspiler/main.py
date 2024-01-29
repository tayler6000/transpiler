from rusttranspiler.lex import lex
from rusttranspiler.writer import write
from os.path import exists, join
import argparse
import dis
import io
import os
import pprint
import subprocess
import sys


def tokenize(file: io.TextIOWrapper) -> dis.Bytecode:
    with file:
        data = file.read()
        tokens = dis.Bytecode(data)
    return tokens


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="RustTranspiler",
        description="Python to Rust Transpiler",
    )
    parser.add_argument("input", type=argparse.FileType("r"))
    parser.add_argument("output")
    parser.add_argument("-l", action="store_true")
    args = parser.parse_args()
    if exists(args.output) and not args.l:
        print(
            "Output directory must not already exist!\n\n"
            + f"{parser.format_help()}",
            file=sys.stderr,
        )
        return 1

    tokens = tokenize(args.input)
    lexed = lex(tokens)
    if args.l:
        pprint.pprint(lexed)
        return 0

    subprocess.run(
        [
            "cargo",
            "init",
            args.output,
            "--vcs",
            "none",
            "--quiet",
            "--offline",
        ]
    )
    write(lexed, join(args.output, "src", "main.rs"))
    cwd = os.getcwd()
    os.chdir(args.output)
    subprocess.run(["cargo-fmt"])
    os.chdir(cwd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

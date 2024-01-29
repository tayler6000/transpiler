from rusttranspiler.lex import lex, Instruction
from rusttranspiler.translate import translate
from os.path import exists, join
import argparse
import dis
import io
import os
import pprint
import subprocess
import sys


def tokenize(file: io.TextIOWrapper) -> tuple[list[str], dis.Bytecode]:
    with file:
        data = file.read()
        file.seek(0, 0)
        src = file.readlines()
        tokens = dis.Bytecode(data)
    return src, tokens


def main(input: io.TextIOWrapper) -> tuple[list[Instruction], str]:
    src, tokens = tokenize(input)
    lexed = lex(src, tokens)
    output = translate(lexed)
    return lexed, output


def cli() -> int:
    parser = argparse.ArgumentParser(
        prog="RustTranspiler",
        description="Python to Rust Transpiler",
    )
    parser.add_argument("input", type=argparse.FileType("r"))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-o", "--output", help="Output to cargo project", dest="output"
    )
    group.add_argument(
        "-l",
        "--lex",
        help="Outputs the lexed code to stdout",
        action="store_true",
        dest="lex",
    )
    group.add_argument(
        "-s",
        "--stdout",
        help="Outputs to stdout",
        action="store_true",
        dest="stdout",
    )
    group.add_argument(
        "-f",
        "--file",
        help="Outputs to a single file, not a cargo project",
        dest="file",
    )
    args = parser.parse_args()
    if args.output:
        if exists(args.output):
            print(
                "Output directory must not already exist!\n\n"
                + f"{parser.format_help()}",
                file=sys.stderr,
            )
            return 1

    if args.file:
        if exists(args.file):
            print(
                "Output file must not already exist!\n\n"
                + f"{parser.format_help()}",
                file=sys.stderr,
            )
            return 1

    lexed, output = main(args.input)

    if args.lex:
        pprint.pprint(lexed)
        return 0

    elif args.stdout:
        print(output, end="", file=sys.stdout)
        return 0

    elif args.file:
        with open(args.file, "w") as f:
            f.write(output)
        return 0

    elif args.output:
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
        with open(join(args.output, "src", "main.rs"), "w") as f:
            f.write(output)
        cwd = os.getcwd()
        os.chdir(args.output)
        subprocess.run(["cargo-fmt"])
        os.chdir(cwd)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(cli())

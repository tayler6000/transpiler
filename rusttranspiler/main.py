from rusttranspiler.tokenize import tokenize
from os.path import exists
import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="RustTranspiler",
        description="Python to Rust Transpiler",
    )
    parser.add_argument("input", type=argparse.FileType("rb"))
    parser.add_argument("output")
    args = parser.parse_args()
    if exists(args.output):
        print(
            f"Output file must not already exist!\n\n{parser.format_help()}",
            file=sys.stderr,
        )
        return 1

    print(tokenize(args.input))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

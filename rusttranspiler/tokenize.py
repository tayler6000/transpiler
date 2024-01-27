from enum import Enum
import io


class SpecialTokens(Enum):
    INDENT = "INDENT"
    UNINDENT = "UNINDENT"


def tokenize(file: io.BufferedReader) -> list[bytes | SpecialTokens]:
    tokens: list[bytes | SpecialTokens] = []
    with file:
        current_indent = 0
        breakpoint()
        for line in file:
            if line.strip() == b"":
                continue
            new_indent = current_indent
            if current_indent == 0 and line[0] == 32:
                new_indent = find_indent(line)
            elif current_indent != 0:
                if line[current_indent] == 32:
                    new_indent = find_indent(line)
                elif b" " * current_indent != line[0:current_indent]:
                    new_indent = find_indent(line)
            if current_indent > new_indent:
                tokens.append(SpecialTokens.UNINDENT)
            elif current_indent < new_indent:
                tokens.append(SpecialTokens.INDENT)
            tokens.append(line.strip())

    return tokens


def find_indent(line: bytes) -> int:
    indent = 0
    for c in line:
        if c == 32:
            indent += 1
        else:
            break
    return indent

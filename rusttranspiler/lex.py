from rusttranspiler.regex import KW_FIND
from typing import Any, NamedTuple
import dis
import pprint


class LexError(Exception):
    pass


class Instruction(NamedTuple):
    opname: str
    args: dict[str, Any]


class Kwarg(NamedTuple):
    key: str
    val: Any


END_SCOPE: None | int = None


def lex(src: list[str], t: dis.Bytecode) -> list[Instruction]:
    global END_SCOPE
    stack: list[Any] = []
    lexed: list[Instruction] = []
    tokens = list(t)
    while len(tokens) >= 1:
        x = tokens.pop(0)
        if END_SCOPE is not None:
            if END_SCOPE == x.offset:
                lexed.append(Instruction(opname="END_SCOPE", args={}))
                END_SCOPE = None
        if x.opname in ["RESUME", "PRECALL"]:
            continue  # NOOP
        elif x.opname == "KW_NAMES":
            kw_names(src, x, tokens, stack, lexed)
        elif x.opname == "LOAD_NAME":
            load_name(x, tokens, stack, lexed)
        elif x.opname == "LOAD_CONST":
            stack.append(x.argval)
        elif x.opname == "PUSH_NULL":
            stack.append(None)
        elif x.opname == "CALL":
            call(x, tokens, stack, lexed)
        elif x.opname == "RETURN_VALUE":
            if END_SCOPE is None:
                stack.pop()
                continue
            lexed.append(
                Instruction(opname="RETURN_VALUE", args={"value": stack.pop()})
            )
        else:
            raise LexError(f"Unhandled Bytecode Instruction: {x}")

    return lexed


def kw_names(
    src: list[str],
    x: dis.Instruction,
    tokens: list[dis.Instruction],
    stack: list[Any],
    lexed: list[Instruction],
) -> None:
    pos = x.positions
    if not pos:
        raise LexError("KW_NAMES Instruction did not have a position!")
    if not pos.lineno:
        raise LexError("KW_NAMES Instruction did not have a line number!")
    code = src[pos.lineno - 1][pos.col_offset : pos.end_col_offset]
    matches = KW_FIND.findall(code)
    if not matches:
        raise LexError(f"Unable to find kwargs in line of code {code=}")
    istack: list[Any] = []
    for _ in range(len(matches)):
        istack.append(stack.pop())
    for match in matches:
        arg = match[0]
        val = match[1]
        if val not in istack and val.strip() not in istack:
            raise LexError(
                f"Unable to find kwarg {arg}: {val=}\n{pprint.pformat(istack)}"
            )
        if val not in istack:
            val = val.strip()
        stack.append(Kwarg(key=arg, val=val))
        istack.pop(istack.index(val))
    assert len(istack) == 0


def load_name(
    x: dis.Instruction,
    tokens: list[dis.Instruction],
    stack: list[Any],
    lexed: list[Instruction],
) -> None:
    global END_SCOPE
    inst1 = tokens.pop(0)
    inst2 = tokens.pop(0)
    inst3 = tokens.pop(0)
    if (
        inst1.opname == "LOAD_CONST"
        and inst1.argval == "__main__"
        and inst2.opname == "COMPARE_OP"
        and inst2.argval == "=="
        and inst3.opname == "POP_JUMP_FORWARD_IF_FALSE"
    ):
        END_SCOPE = inst3.argval
        lexed.append(
            Instruction(
                opname="START_FUNCTION",
                args={"name": "main", "args": None},
            )
        )
    else:
        tokens.insert(0, inst3)
        tokens.insert(0, inst2)
        tokens.insert(0, inst1)
        stack.append(x.argval)


def call(
    x: dis.Instruction,
    tokens: list[dis.Instruction],
    stack: list[Any],
    lexed: list[Instruction],
) -> None:
    argc = x.argval
    arguments: list[Any] = []
    for _ in range(argc):
        arguments.append(stack.pop())
    arguments.reverse()
    kwargs: dict[str, Any] = {}
    to_pop: list[Kwarg] = []
    for argument in arguments:
        if type(argument) is Kwarg:
            to_pop.append(argument)
    for argument in to_pop:
        kwargs[argument.key] = argument.val
        arguments.pop(arguments.index(argument))
    stack1 = stack.pop()
    stack2 = stack.pop()
    if stack2 is None:
        func = stack1
        _self = None
    else:
        func = stack2
        _self = stack1
    inst1 = tokens.pop(0)
    if inst1.opname == "POP_TOP":
        lexed.append(
            Instruction(
                opname="CALL",
                args={
                    "context": _self,
                    "func": func,
                    "args": arguments,
                    "kwargs": kwargs,
                },
            )
        )
    elif inst1.opname == "STORE_NAME":
        lexed.append(Instruction(opname="STORE", args={"var": inst1.argval}))
        lexed.append(
            Instruction(
                opname="CALL",
                args={
                    "context": _self,
                    "func": func,
                    "args": arguments,
                },
            )
        )
    else:
        tokens.insert(0, inst1)

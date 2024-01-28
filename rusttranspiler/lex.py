from typing import Any, NamedTuple
import dis


class LexError(Exception):
    pass


class Instruction(NamedTuple):
    opname: str
    args: dict[str, Any]


def lex(t: dis.Bytecode) -> list[Instruction]:
    stack: list[Any] = []
    lexed: list[Instruction] = []
    tokens = list(t)
    end_scope: None | int = None
    while len(tokens) >= 1:
        x = tokens.pop(0)
        if end_scope is not None:
            if end_scope == x.offset:
                lexed.append(Instruction(opname="END_SCOPE", args={}))
                end_scope = None
        if x.opname in ["RESUME", "PRECALL"]:
            continue  # NOOP
        elif x.opname == "LOAD_NAME":
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
                end_scope = inst3.argval
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
        elif x.opname == "LOAD_CONST":
            stack.append(x.argval)
        elif x.opname == "PUSH_NULL":
            stack.append(None)
        elif x.opname == "CALL":
            argc = x.argval
            arguments: list[Any] = []
            for _ in range(argc):
                arguments.append(stack.pop())
            arguments.reverse()
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
                        },
                    )
                )
            elif inst1.opname == "STORE_NAME":
                lexed.append(
                    Instruction(opname="STORE", args={"var": inst1.argval})
                )
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
        elif x.opname == "RETURN_VALUE":
            if end_scope is None:
                stack.pop()
                continue
            lexed.append(
                Instruction(opname="RETURN_VALUE", args={"value": stack.pop()})
            )
        else:
            raise LexError(f"Unhandled Bytecode Instruction: {x}")

    return lexed

import shlex
from dataclasses import dataclass, field


@dataclass
class ParsedCommand:
    name: str
    args: list[str] = field(default_factory=list)
    flags: dict[str, str | bool] = field(default_factory=dict)
    pipe_grep: str | None = None


def parse_line(line: str) -> ParsedCommand | None:
    line = line.strip()
    if not line:
        return None

    pipe_grep = None
    if "|" in line:
        left, right = line.split("|", 1)
        line = left.strip()
        right = right.strip()
        if right.startswith("grep "):
            pipe_grep = right[5:].strip().strip("'\"")

    try:
        tokens = shlex.split(line)
    except ValueError:
        tokens = line.split()

    if not tokens:
        return None

    name = tokens[0].lower()
    raw = tokens[1:]

    args: list[str] = []
    flags: dict[str, str | bool] = {}

    i = 0
    while i < len(raw):
        tok = raw[i]
        if tok.startswith("--"):
            if "=" in tok:
                k, v = tok[2:].split("=", 1)
                flags[k] = v
            elif i + 1 < len(raw) and not raw[i + 1].startswith("--"):
                flags[tok[2:]] = raw[i + 1]
                i += 1
            else:
                flags[tok[2:]] = True
        else:
            args.append(tok)
        i += 1

    return ParsedCommand(name=name, args=args, flags=flags, pipe_grep=pipe_grep)

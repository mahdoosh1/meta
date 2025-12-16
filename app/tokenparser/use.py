from .parser import patternpairtype
from typing import Union

def use(patternpair: patternpairtype, text: str) -> list[tuple[str, str, str, Union[int, float], Union[int, float]]]:
    out = []
    i = 0
    line = 1
    column = 1
    n = len(text)

    while i < n:
        matched = False
        for pat, token, category, subtoken, _ in reversed(patternpair):
            m = pat.match(text, i)
            if m:
                token = (
                    (token+"["+subtoken+"]") if subtoken else token,
                    m.group(0),
                    category,
                    line,
                    column
                )
                out.append(token)
                end = min(m.end(),n)
                matched = True
                if end == n:
                    i = n
                    break
                for j in range(end-i):
                    j = text[j]
                    if j == '\n':
                        line += 1
                        column = 1
                    else:
                        column += 1
                i = end
                break
        if not matched:
            if text[i] == '\n':
                line += 1
                column = 1
            else:
                column += 1
            i += 1  # skip one char if nothing matches
    out.append(("EOF", "", "EOF", float("inf"), float("inf")))
    return out
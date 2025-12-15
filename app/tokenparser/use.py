from .parser import patternpairtype

def use(patternpair: patternpairtype, text: str) -> list[tuple[str, str, str, str]]:
    out = []
    i = 0
    n = len(text)

    while i < n:
        matched = False
        for pat, token, category, subtoken in patternpair:
            m = pat.match(text, i)
            if m:
                out.append((m.group(0), token, subtoken, category))
                i = m.end()
                matched = True
                break
        if not matched:
            i += 1  # skip one char if nothing matches
    return out
def safe_nodes(traps):
    result = []
    for n in range(1, 11):
        if n not in traps:
            result.append(n)
    return result

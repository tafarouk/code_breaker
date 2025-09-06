def clean_signal(s):
    # Keep only letters, digits, and spaces
    filtered = []
    for ch in s:
        if ch.isalnum() or ch == " ":
            filtered.append(ch)
    # Collapse multiple spaces to single using split/join
    collapsed = " ".join("".join(filtered).split())
    # Uppercase
    return collapsed.upper()

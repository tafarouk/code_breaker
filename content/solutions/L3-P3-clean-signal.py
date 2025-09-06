def clean_signal(signal):
    result = ""
    for ch in signal:
        if ch.isalpha():
            result += ch
    return result


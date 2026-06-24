# UA sorting

ALPHABET = {c: i for i, c in enumerate("абвгґдеєжзиіїйклмнопрстуфхцчшщьюя")}

def sort_ua(word):
    return [ALPHABET.get(ch.lower(), 999) for ch in word]

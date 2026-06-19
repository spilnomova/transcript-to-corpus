VESUM = set()
with open("dict/vesum.txt", "r") as f:
    for line in f.readlines():
        VESUM.add(line.strip())

FUNCTIONAL = {"PREP", "CONJ", "PRCL", "INTJ"}

def language(lemma, pos):
    # exceptions
    if lemma in {"більше", "вже", "ще"}:
        return {"ua": True, "score": 1}
    if pos in {None, "UNKN"} or lemma == "носок":
        return {"ua": False, "score": 1}
    # score
    if pos in FUNCTIONAL or lemma in {"ні", "так", "нє", "нєт", "да"}:
        score = 0.3
    else:
        score = 1
    # main logic
    if lemma in VESUM:
        return {"ua": True, "score": score}
    else:
        return {"ua": False, "score": score}

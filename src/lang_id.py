import json
import Levenshtein

FUNCTIONAL = {"PREP", "CONJ", "PRCL", "INTJ"}

CONSONANTS = set("бвгґджзйклмнпрстфхцчшщ")

VESUM = set()

with open("./data/vesum_lemmas.txt", "r") as f:
    for line in f.readlines():
        VESUM.add(line.strip())

with open('./data/wiktionary-ua2ru.json', 'r') as file:
    UA2RU = json.load(file)

with open('./data/custom-ua2ru.json', 'r') as file:
    UA2RU.update(json.load(file))

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

def similarity(string1, string2):
    string1 = "".join([char for char in string1 if char in CONSONANTS])
    string2 = "".join([char for char in string2 if char in CONSONANTS])
    return Levenshtein.ratio(string1, string2)

# similarity("кіт", "кот")

def related_to_ru(uk_word):
    # exceptions
    if uk_word in {"підлога", "хлопчик"}:
        return False
    # comparison
    try:
        ru_words = UA2RU[uk_word]
        scores = []
        for ru_word in ru_words:
            scores.append(similarity(uk_word, ru_word))
        if max(scores) > 0.6:
            return True
        else:
            return False
    except:
        if len(uk_word) > 4 and uk_word[-2:] in {"ся", "сь"}:
            return related_to_ru(uk_word[:-2])
        else:
            print("No translation found:", uk_word)
            return None

# related_to_ru("око")
# related_to_ru("побігти")

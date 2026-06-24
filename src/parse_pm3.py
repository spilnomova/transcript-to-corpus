import pymorphy3

morph = pymorphy3.MorphAnalyzer(lang="uk")

def get_morph(word):
    morphs = morph.parse(word)
    for i in range(len(morphs)):
        if morphs[i].tag.POS in {"NPRO", "PREP", "NUMR"} or \
            morphs[i].normal_form in {"бути", "хотіти", "людина"}:
            return morphs[i]
    return morphs[0]

def get_lemma(word_morph):
    fake_methods = {pymorphy3.units.by_analogy.UnknownPrefixAnalyzer,
                    pymorphy3.units.by_analogy.KnownSuffixAnalyzer.FakeDictionary}
    exceptions = {"зуби": "зуб",
                  "мишку": "мишка",
                  "червоним": "червоний"}
    if word_morph.word in {"бить", "єсть", "животіє", "мишка", "можна", "патом", "потом",
                           "носкі", "окуляри", "очки", "сходи", "хованки"}:
        return word_morph.word
    elif word_morph.word in exceptions.keys():
        return exceptions[word_morph.word]
    elif set.intersection(fake_methods,
                          set([type(i[0]) for i in word_morph.methods_stack])):
        return word_morph.word
    else:
        return word_morph.normal_form

def get_pos(word_morph):
    if word_morph.tag.POS == None:
        return "UNKN"
    elif word_morph.word == "ще":
        return "NPRO"
    else:
        return word_morph.tag.POS


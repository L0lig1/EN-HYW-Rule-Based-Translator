# Define Armenian Unicode mappings
unicode_map = {
    "a": "\u0561", "b": "\u0562", "g": "\u0563", "d": "\u0564",
    "ye": "\u0565", "z": "\u0566", "e": "\u0567", "y": "\u0568",
    "dt": "\u0569", "zh": "\u056A", "i": "\u056B", "l": "\u056C",
    "kh": "\u056D", "ts": "\u056E", "k": "\u056F", "h": "\u0570",
    "dz": "\u0571", "gh": "\u0572", "djch": "\u0573", "m": "\u0574",
    "j": "\u0575", "n": "\u0576", "sh": "\u0577", "vo": "\u0578",
    "ch": "\u0579", "p": "\u057A", "dj": "\u057B", "r": "\u057C",
    "s": "\u057D", "v": "\u057E", "t": "\u057F", "r'": "\u0580",
    "c": "\u0581", "u": "\u0582", "bp": "\u0583", "q": "\u0584",
    "ev": "\u0587", "o": "\u0585", "f": "\u0586"
}

def among(word, substrings):
    return any(substring in word for substring in substrings)

def mark_regions(word):
    vowels = ['a', 'e', 'i', 'o', 'u', 'ye', 'vo', 'y']
    pV, p2 = len(word), len(word)
    
    for i, char in enumerate(word):
        if char in vowels:
            pV = i
            break
    for i in range(pV, len(word)):
        if word[i] not in vowels:
            p2 = i
            break

    return pV, p2

def remove_adjective_suffix(word):
    adjective_suffixes = [
        "bar'", "pye's", "voren", "vovin", "aki", "lajn", 
        "r'vord", "yer'vord", "akan", "ali", "kvot", "yekyen",
        "vor'ak", "yegh", "vvoun", "yer'yen", "ar'an", "yen",
        "avyet", "gin", "iv", "at", "in"
    ]
    return word[:-len(suffix)] if among(word, adjective_suffixes) else word

def remove_verb_suffix(word):
    verb_suffixes = [
        "voum", "vvoum", "alvou", "yelvou", "vyel", "anal", 
        "yelvou'c", "alvou'c", "yal", "yyel", "alvov", "yelvov",
        "alis", "yelis", "yenal", "acnal", "yecn'yel", "cn'yel",
        "n'yel", "atyel", "votyel", "kvotyel", "tyel", "vats",
        "yecv'ye'l", "acv'ye'l", "yecir'", "acir'", "yecin'q",
        "acin'q", "vyecir'", "vyecin'q", "vyeci'q", "vyecin",
        "acr'ir'", "acr'yec", "acr'in'q", "acr'iq", "acr'in",
        "yeci'q", "aci'q", "yecin", "acin", "acar'", "acav",
        "acan'q", "acaq", "acan", "vyeci", "acr'i", "yecar'",
        "yecav", "can'q", "caq", "can", "aca", "aci", "yeca",
        "ch'ye'l", "yeci", "ar'", "av", "an'q", "aq", "an",
        "al", "yel", "yec", "ac", "vye", "a"
    ]
    return word[:-len(suffix)] if among(word, verb_suffixes) else word

def remove_noun_suffix(word):
    noun_suffixes = [
        "atsvo", "anak", "anoc", "ar'an", "ar'q", "pan", "stan", "yeghen",
        "yen'q", "ik", "ich", "iq", "mvoun'q", "jak", "jvoun", "von'q",
        "vor'd", "voc", "ch'ye'q", "vats'q", "vor'", "avvor'", "voudtjvoun",
        "vou'k", "vou'hi", "voudtj", "voudj'q", "voudjt", "voudjs",
        "voudjt", "vou's", "voi", "vouc", "voudjt'c", "cac", "vav",
        "vauc", "anv", "anq", "yanq"
    ]
    return word[:-len(suffix)] if among(word, noun_suffixes) else word

def remove_ending_suffix(word):
    ending_suffixes = [
        "nyer'y", "nyer'n", "nyer'i", "nyer'd", "yer'ic", "nyer'ic", "yer'i",
        "yer'd", "yer'n", "yer'y", "nyer'in", "voudtjann", "voudtjann'y",
        "voudtjann'd", "voudtjann", "yer'in", "in", "sa", "vodj", "ic",
        "yer'vov", "nyer'vov", "yer'voum", "nyer'voum", "voun", "voud",
        "vans", "vann'y", "vann'd", "an'y", "an'd", "van", "vodjy",
        "vodjs", "vodjd", "voc", "vouc", "voudjic", "cic", "vic", "vi",
        "vov", "a'nv", "anvou'm", "vanic", "amb", "an", "nyer'", "yer'",
        "va", "y", "n", "d", "c", "i"
    ]
    return word[:-len(suffix)] if among(word, ending_suffixes) else word

def stem(word):
    pV, p2 = mark_regions(word)
    word = remove_adjective_suffix(word)
    word = remove_verb_suffix(word)
    word = remove_noun_suffix(word)
    word = remove_ending_suffix(word)
    return word



print(stem("Խօսելով"))
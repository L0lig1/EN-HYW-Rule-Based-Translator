import re


_personalSuffix  = "եմ|ես|է|ենք|եք|են"
_npersonalSuffix = "եմ|ես|ի|ենք|եք|են"
_preteriteSuffix = "ցի|ցիր|ց|ցինք|ցիք|ցին"
_imprefectSuffix = "էի|էիր|էր|էինք|էիք|էին"
_el = "ել"
_il = "իլ"
_al = "ալ"
_um = "ում"
vowels = ["ա", "ե", "է", "ի", "օ", "ո", "ու"]
easternpatterns = {
    # Present
    "present": fr'\b\w+ում\s(?:{_personalSuffix})\b',
    # Imperfect
    "imperfect": fr'\b\w+ում\s(?:{_imprefectSuffix})\b',
    # Preterite 1 (ել)
    "preterite": fr'\b\w(ա|ե)({_preteriteSuffix})\b',
    # Present Perfect
    "presperf": fr'\b\w+ել\s(?:{_personalSuffix})\b',
    # Eastern PlusP
    "plusperf": fr'\b\w+ել\s(?:{_imprefectSuffix})\b',
    # Eastern Future
    "future": fr'\bկ\w+({_npersonalSuffix})\s\b',
    # Eastern Conditional
    "condit": fr'\bկ\w+({_imprefectSuffix})\s\b',
}

def FindEasternVerbs(eastern: str):
    eastern = eastern.lower()
    westernsentence = eastern
    for tense, pattern in easternpatterns.items():
        print(f"Pattern {tense}: {pattern}")
        foundverbs = re.findall(pattern, eastern)
        if len(foundverbs) == 0: 
            continue
        print(f"Found   {tense}: {foundverbs}")
        westernverbs = ConvertVerbsToWestern(foundverbs, tense)
        for easternverb, westernverb in zip(foundverbs, westernverbs):
            westernsentence = westernsentence.replace(easternverb, westernverb)
    return westernsentence


def ConvertVerbsToWestern(eastern_verbs: list[str], tense: str):
    western_verbs = []
    for eastern_verb in eastern_verbs:
        if tense == "present" or tense == "imperfect":
            ge = "կ'" if eastern_verb[0] in vowels else "կը "
            person = f"ու{eastern_verb.split(' ')[1]}".replace("է", "ի").replace("ե", "ի") if eastern_verb.split(' ')[0].endswith('վում') else eastern_verb.split(' ')[1]
            stem = eastern_verb.split(' ')[0].replace("վում", "") if eastern_verb.split(' ')[0].endswith('վում') else eastern_verb.split(' ')[0].replace("ում", "")
            western_verbs.append(f"{ge}{stem}{person}")
        elif tense == "future":
            eastern_verb = eastern_verb[1:]
            eastern_verb = "պիտի " + eastern_verb
            western_verbs.append(eastern_verb)
        elif tense == "presperf" or tense == "plusperf":
            western_verbs.append(eastern_verb.replace("ել ", "ած "))
    return western_verbs


print(FindEasternVerbs("""Պատասխան. մենք խստորեն դատապարտում ենք Ադրբեջանի նախագահի նկրտումները Հայաստանի տարածքային ամբողջականության դեմ և ուժի կիրառման սպառնալիքները։"""))

# a = FindEasternVerbs("""Էջմիածնի Մայր տաճար, Հայ Առաքելական եկեղեցու Էջմիածնի կաթողիկոսության գլխավոր կրոնական կառույցը: Գտնվում է Հայաստանի Հանրապետության Արմավիրի մարզի Վաղարշապատ քաղաքում։

# Կառուցվել է 301-303 թվականներին այնտեղ գոյություն ունեցող հեթանոսական տաճարի տեղում՝ խորհրդանշելով հեթանոսությունից քրիստոնեության անցումը։

# Տաճարը շրջակայքի որոշ կարևոր վաղ միջնադարյան եկեղեցիների հետ միասին 2000 թվականին ընդգրկվել են ՅՈՒՆԵՍԿՕ-ի համաշխարհային ժառանգության ցանկում: 
                     
# գերմանացի """)

# print(f"sentence with converted verbs: \n{a}")
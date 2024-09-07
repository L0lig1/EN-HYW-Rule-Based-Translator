from OrthographyConverter.ArmenianOrthographyConverter import ArmenianOrthographyConverter
from Evaluators import EvaluationMetrics
from googletrans import Translator
import time
from tqdm import tqdm
import random
from Conjugator.Conjugator import convert_eastern_conjugation
import matplotlib.pyplot as plt
import re
from Dictionary.read_dict import replace_known_words_from_dictionary
import json
import Conjugator.CustomConjugator as CustomConjugator

translator = Translator()

def count_duplicates(lst):
    """
    Counts duplicates in a list and returns a dictionary where keys are the unique elements
    and values are the counts of duplicates.
    
    Args:
    lst (list): The input list
    
    Returns:
    dict: A dictionary containing counts of duplicates
    """
    duplicate_count = {}
    for item in lst:
        if item in duplicate_count:
            duplicate_count[item] += 1
        else:
            duplicate_count[item] = 1
    # Filter out items with count less than 2 (no duplicates)
    duplicate_count = {k: v for k, v in duplicate_count.items() if v > 1}
    return duplicate_count


def shuffle_parallel_corpus(list1, list2):
    # Zip the two lists together
    zipped = list(zip(list1, list2))
    # Shuffle the zipped pairs
    random.shuffle(zipped)
    # Unzip the shuffled pairs
    shuffled_list1, shuffled_list2 = zip(*zipped)
    return shuffled_list1, shuffled_list2

def FilterInvalidCharacters(sentence):
    sentence = sentence.lower()
    pattern = r"[^ա-ֆa-z?.:0-9,՞\s']"
    cleaned_text = re.sub(pattern, "", sentence.replace('\n', ''))
    cleaned_text = re.sub(r"\s+$", "", cleaned_text)
    return cleaned_text

def ReadFile(path):
    with open(path, encoding="utf-8") as file:
        file.readline()
        return [FilterInvalidCharacters(line) for line in file.readlines()]
    
def ReadFiles(paths):
    lines = []
    for path in paths:
        lines = lines + ReadFile(path)
    return lines

def Translate(text):
    return translator.translate(text, 'hy').text

def CalculateEvals(sources, references):
    import nltk
    nltk.download('wordnet')
    bleus = []
    chrfs = []
    rouges = []
    counter = 0
    meteos = []
    english = sources
    all = []

    for source, reference in tqdm(zip(sources, references), "translating..."):
        # start = time.time()-
        en_hye_translation = Translate(source)
        conjugation_conversion_hye_to_hyw = convert_eastern_conjugation(en_hye_translation.lower())
        conjugation_conversion_hye_to_hyw = CustomConjugator.FindEasternVerbs(conjugation_conversion_hye_to_hyw)
        # if en_hye_translation != conjugation_conversion_hye_to_hyw:
        #    counter = counter + 1
        
        #     # print(f"\n{en_hye_translation}\n{conjugation_conversion_hye_to_hyw}\n")
        dict_conj_hye_to_hyw = replace_known_words_from_dictionary(conjugation_conversion_hye_to_hyw)
        hye_hyw_translation = ArmenianOrthographyConverter.SovietToMashtots(dict_conj_hye_to_hyw)
        # hye_hyw_translation = en_hye_translation
        # print(f"\nref: {reference}\nhyp: {hye_hyw_translation}\n")
        bleu = EvaluationMetrics.compute_sentence_bleu(hye_hyw_translation, reference)
        bleus.append(bleu)
        chrf = EvaluationMetrics.compute_sentence_chrf(hye_hyw_translation, reference)
        chrfs.append(chrf)
        rouge = EvaluationMetrics.compute_rouge(hye_hyw_translation, reference)[0]["rouge-l"]["f"]
        rouges.append(rouge)
        meteo = EvaluationMetrics.compute_meteor(hye_hyw_translation, reference)
        meteos.append(meteo)
        #meteo.append(EvaluationMetrics.compute_meteor(hye_hyw_translation, reference))
        all.append({
            "en": source, 
            "hye": en_hye_translation, 
            "hyw": hye_hyw_translation, 
            "ref": reference, 
            "bleu": bleu, 
            "chrf": chrf, 
            "rouge-l": rouge,
            "meteo": meteo,
        })
        if source == sources[10]:
            break

        
    # for source in zip(sources):

    with open("translations.json", 'w', encoding='utf-8') as output_file:
        json.dump(all, output_file, ensure_ascii=False, indent=4)
    
    return bleus, chrfs
    

# start = time.time()
# print(Translate("I trust it will not embarrass you; but I shall expect you to adopt this course, the only one that I can suggest to avoid complications with Messrs. Alfred Smith & Co. I am"))
# end = time.time()
# print(end - start)

dir = "./EN-HYW/EN-HYW-Rule-Based-Translator/hyw-en-parallel-corpus/"
PathListEn = [f"{dir}bible/bible.en",  f"{dir}hamazkayin/hamazkayin.en",  f"{dir}hayernaysor/hayernaysor.en",  f"{dir}aalw/aalw.en",  f"{dir}wikipedia/wikipedia.en"]
PathListHyw = [f"{dir}bible/bible.hyw", f"{dir}hamazkayin/hamazkayin.hyw", f"{dir}hayernaysor/hayernaysor.hyw", f"{dir}aalw/aalw.hyw", f"{dir}wikipedia/wikipedia.hyw"]
en = ReadFiles(PathListEn)
hyw = ReadFiles(PathListHyw)
en, hyw = shuffle_parallel_corpus(en, hyw)
#print(count_duplicates(en))

bleus, chrfs = CalculateEvals(en, hyw)
def SortRoundCountDuplicates(listOfEvals):
    listOfEvals = sorted(listOfEvals)
    listOfEvals = [round(x) for x in listOfEvals]

    listOfEvals = count_duplicates(listOfEvals)
    return listOfEvals
# bleus = SortRoundCountDuplicates(bleus)
# chrfs = SortRoundCountDuplicates(chrfs)

# plt.plot(bleus.keys(), bleus.values())
# plt.plot(chrfs.keys(), chrfs.values())
# #plt.plot([x for x in range(0, len(chrfs))], chrfs)
# plt.show()
# time.sleep(1000)
# # Make sure to close the plt object once done
# plt.close()
print(f"average bleus: {sum(bleus) / len(bleus)}\naverage chrfs: {sum(chrfs) / len(chrfs)}")
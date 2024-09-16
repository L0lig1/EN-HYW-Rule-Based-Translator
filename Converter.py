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
        conjugation_conversion_hye_to_hyw = CustomConjugator.EastToWest(conjugation_conversion_hye_to_hyw)
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
        # if any(substring in en_hye_translation for substring in [" սրա ", " սրանց ", " նրա ", " նրանց ", " նա "]):
        # if source == sources[1000]:
        #     break

        
    # for source in zip(sources):

    with open("hyrbt_translations.json", 'w', encoding='utf-8') as output_file:
        json.dump(all, output_file, ensure_ascii=False, indent=4)
    
    return bleus, chrfs, rouges, meteos
    


from gradio_client import Client
def CalculateEvalsNllb(sources, references):
    import nltk
    nltk.download('wordnet')
    bleus, chrfs, rouges, meteos, all = []
    client = Client("https://arinubar-hyw-en-demo.hf.space/--replicas/e8d1h/")
    for source, reference in tqdm(zip(sources, references), "translating..."):
        hyw_translation = client.predict(
                    "today we are going to a party and enjoy our time",	        # str  in 'Մուտքագրում | Input Text' Textbox component
                    "Անգլերէն | English",	        # Literal[Արեւմտահայերէն | Western Armenian, Անգլերէն | English]  in 'Թարգմանէ Այս Լեզուէ | Source Language' Dropdown component
                    "Արեւմտահայերէն | Western Armenian",	# Literal[Արեւմտահայերէն | Western Armenian, Անգլերէն | English]  in 'Թարգմանէ Այս Լեզուի | Target Language' Dropdown component
                    True,	            # bool  in 'Նախադասութիւններու Բաժնէ | Split into Sentences' Checkbox component
                    True,	            # bool  in 'Մշակէ | Preprocess' Checkbox component
                    1,	                # Literal[1, 2, 3, 4, 5]  in 'Որոնման Շողեր | Number of Beams' Dropdown component
                    api_name="/translate_wrapper",
                )
        bleu = EvaluationMetrics.compute_sentence_bleu(hyw_translation, reference)
        bleus.append(bleu)
        chrf = EvaluationMetrics.compute_sentence_chrf(hyw_translation, reference)
        chrfs.append(chrf)
        rouge = EvaluationMetrics.compute_rouge(hyw_translation, reference)[0]["rouge-l"]["f"]
        rouges.append(rouge)
        meteo = EvaluationMetrics.compute_meteor(hyw_translation, reference)
        meteos.append(meteo)
        all.append({
            "en": source, 
            "hyw": hyw_translation, 
            "ref": reference, 
            "bleu": bleu, 
            "chrf": chrf, 
            "rouge-l": rouge,
            "meteo": meteo,
        })
    with open("nllb_translations.json", 'w', encoding='utf-8') as output_file:
        json.dump(all, output_file, ensure_ascii=False, indent=4)
    
    return bleus, chrfs, rouges, meteos


def GetAllEvals(PathListEn, PathListHyw):
    en = ReadFiles(PathListEn)  
    hyw = ReadFiles(PathListHyw)
    en, hyw = shuffle_parallel_corpus(en, hyw)
    return CalculateEvalsNllb(en, hyw)

# start = time.time()
# print(Translate("I trust it will not embarrass you; but I shall expect you to adopt this course, the only one that I can suggest to avoid complications with Messrs. Alfred Smith & Co. I am"))
# end = time.time()
# print(end - start)
dir = "./EN-HYW/EN-HYW-Rule-Based-Translator/hyw-en-parallel-corpus/"
PathListEn = [f"{dir}american_citizen/american_citizen.en"]
PathListHyw = [f"{dir}american_citizen/american_citizen.hyw"]

bleus, chrfs, rouge, meteo = GetAllEvals(PathListEn, PathListHyw)
# print(count_duplicates(en))

def SortRoundCountDuplicates(listOfEvals):
    listOfEvals = sorted(listOfEvals)
    listOfEvals = [round(x) for x in listOfEvals]

    listOfEvals = count_duplicates(listOfEvals)
    return listOfEvals


def GetStats(file_path, key):
    with open(file_path, encoding='utf-8') as fh:
        statsfile = json.load(fh)
    deez_values = [obj[key] for obj in statsfile if key in obj]
    print("afsasf")
    return deez_values
    # for k, v in statsfile:
    #     print(k,v)

bleus = GetStats("hyrbt_uscitizen_translations.json", "meteor")

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Example list of scores ranging from 1-100
scores = bleus  # Replace this with your list of scores

# 1. Histogram
plt.figure()
# plt.hist(scores, bins=500, color='skyblue', edgecolor='black')
# plt.grid(True)
# plt.xticks(np.arange(0, 101, 10))  # X-axis ticks every 10 units
# plt.yticks(np.arange(0, plt.gca().get_ylim()[1] + 1, 10))  # Y-axis ticks every 10 units
# plt.title('Histogram')
# plt.xlabel('Scores')
# plt.ylabel('Frequency')
# plt.axvline(sum(scores) / len(scores), color='k', linestyle='dashed', linewidth=1)

# # 2. Box Plot
# plt.subplot(2, 3, 2)
# sns.boxplot(scores, color='lightgreen')
# plt.title('Box Plot')
# plt.xlabel('Scores')

# # 3. Violin Plot
plt.subplot(2, 3, 3)
sns.violinplot(scores, color='lightcoral')
plt.title('Violin Plot')
plt.xlabel('Scores')

# # 4. Heatmap (density of scores)
# plt.subplot(2, 3, 4)
# sns.histplot(scores, bins=10, kde=False, color='purple')
# plt.title('Heatmap')
# plt.xlabel('Scores')
# plt.ylabel('Density')

# # 5. Swarm Plot
# plt.subplot(2, 3, 5)
# sns.swarmplot(scores, color='blue')
# plt.title('Swarm Plot')
# plt.xlabel('Scores')

plt.tight_layout()
plt.show()
# improve conjugator

# bleus = SortRoundCountDuplicates(bleus)
# chrfs = SortRoundCountDuplicates(chrfs)

# plt.plot(bleus.keys(), bleus.values())
# plt.plot(chrfs.keys(), chrfs.values())
# #plt.plot([x for x in range(0, len(chrfs))], chrfs)
# plt.show()
# time.sleep(1000)
# # Make sure to close the plt object once done
# plt.close()
# print(f"average bleus: {sum(bleus) / len(bleus)}\naverage chrfs: {sum(chrfs) / len(chrfs)}\naverage meteo: {sum(meteo) / len(meteo)}\naverage rouge: {sum(rouge) / len(rouge)}")
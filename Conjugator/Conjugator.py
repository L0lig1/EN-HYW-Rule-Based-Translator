from playwright.sync_api import Playwright, sync_playwright, expect, Page
import json
import re
import requests
from bs4 import BeautifulSoup
import codecs
import Levenshtein
import concurrent.futures
# from ..Dictionary.read_dict import dictionary
from tqdm import tqdm
import time

_pronouns_ = {
    "0": "1s", #"1"st person "s"ingular
    "1": "2s", 
    "2": "3s", 
    "3": "1p", 
    "4": "1p", 
    "5": "1p", 
    "1s": "0",
    "2s": "1",
    "3s": "2",
    "1p": "3",
    "1p": "4",
    "1p": "5",
}


def get_table(elements, start, end, negativeprefix = ""):
    verb = {}
    for x in range(start, end):
        verbs_in_tense = {}
        tense = elements[x].inner_text().lower()
        if "imperative" in tense.lower():
            for l in [1, 3, 4]:
                # print(f"{x}: {x + (8 * (l + 1))}")
                verbs_in_tense[f"{negativeprefix}{tense}_{l}"] = elements[x + (8 * (l + 1))].inner_text().lower().replace('՜', '՛')
        else: 
            for l in range(0,6):
                verbs_in_tense[f"{negativeprefix}{tense}_{l}"] = elements[x + (8 * (l + 1))].inner_text().lower().replace('՜', '՛')
        verb[f"{negativeprefix}{tense}"] = verbs_in_tense
    return verb


def get_all_verb_conjugations(page: Page, lang: str):
    page.get_by_role("button", name=f"{lang} armenian").click(button="left")

    elements = page.query_selector_all("[id^=main-oc-]")
    # top table
    verb = {}
    for i in range(0, 12):
        verb[elements[i].inner_text().lower()] = elements[i + 12].inner_text().lower()
    # Affirmative conjugation table
    #a = get_table(elements, 25, 34)
    verb.update(get_table(elements, 25, 33))

    # Negative conjugation table
    verb.update(get_table(elements, 82, 90, "n"))
    return verb

def get_infinitive(page: Page, lang: str):
    page.get_by_role("button", name=f"{lang} armenian").click(button="left")

    infinitiveElement = page.locator("#main-oc-nomComplet").inner_html().split("<br>")[0]
    # top table
    
    # Affirmative conjugation table
    #a = get_table(elements, 25, 34)
    return infinitiveElement


def verb_eastern_and_western(page: Page, western_verb: str, inf = False):
    page.locator("#main-input-verbe").click()
    page.locator("#main-input-verbe").press("Control+a")
    page.locator("#main-input-verbe").fill(western_verb)
    page.locator("#main-input-verbe").press("Enter")
    hyw_verb = get_infinitive(page, "Western") if inf else get_all_verb_conjugations(page, "Western") 
    if "հրաժա" in western_verb:
        page.locator("#main-input-verbe").fill("հրաժարվել")
        page.locator("#main-input-verbe").press("Enter")

    hye_verb = get_infinitive(page, "Eastern") if inf else get_all_verb_conjugations(page, "Eastern")
    return {
        "hyw": hyw_verb,
        "hye": hye_verb
    }
    

def get_all_verbs(url, all_verbs_hyw_only):
    with sync_playwright() as playwright:
        # browser
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)
        all_verbs = {}
        inf = True
        for verb in all_verbs_hyw_only:
            verbinfo = verb_eastern_and_western(page, verb, inf)
            if inf:
                all_verbs[verbinfo["hye"]] = verbinfo["hyw"]
            else:
                verbname = verbinfo["hye"]["name"].split('\n')[0] if verbinfo["hye"]["name"] != "" else verbinfo["hyw"]["name"].split('\n')[0]
                all_verbs[verbname] = verbinfo
        #verbs = get_all_verbs(page, all_verbs_hyw_only)

        context.close()
        browser.close()

        return all_verbs


def read_all_hyw_verbs(path):
    # Open the JSON file for reading
    with open(path, 'r', encoding="utf-8") as file:
        # Load JSON data from the file
        data = json.load(file)

    oc_values = []

    # Iterate over each "verbe" in the JSON data
    for key, value in data.items():
        if "681" in key:
            break 
        oc_values.append(value["oc"])
    return oc_values

# all_hyw_verbs = read_all_hyw_verbs("Converter/Conjugator/Verbs/verbs.json")
# all_verb_conjugations = get_all_verbs("http://ma6.free.fr/?lang=en&hyl=oc", all_hyw_verbs)
# with open('Converter/Conjugator/Verbs/all_infinites.json', 'w', encoding="utf-8") as f:
#     json.dump(all_verb_conjugations, f, ensure_ascii=False)
# # print("a")

#def search_substring_in_dict(dictionary, eastern_word, parent_dicts = None):
    # if parent_dicts is None:
    #     parent_dicts = []

    # for key, value in dictionary.items():
    #     if isinstance(value, dict):
    #         search_substring_in_dict(value, eastern_word, parent_dicts + [{key: value}])
    #     elif isinstance(value, str) and eastern_word in value:
    #         parent_dicts.append({key: value})

    # return parent_dicts


def get_conjugations():
    with open('./EN-HYW/EN-HYW-Rule-Based-Translator/Conjugator/Verbs/_verbix_allverbs.json', 'r', encoding="utf-8") as f:
        json_data = json.load(f)
        return json_data
    
    # empty_names = []
    # for key, value in json_data.items():
    #     hye_name = value['hye']['name']
    #     if not hye_name:
    #         empty_names.append(value)

def findverbs(sentence):
    pattern = r"\b(\w*ել|\w*ալ|\w*իլ|\w*ուլ|\w*ելու|\w*ալու|\w*իլու|\w*ուլու|\w*ում\sեմ|\w*ում\sես|\w*ում\sէ|\w*ում\sենք|\w*ում\sեք|\w*ում\sեն|\w*ում\sէի|\w*ում\sէիր|\w*ում\sէր|\w*ում\sէինք|\w*ում\sէիք|\w*ում\sէին|\w*աց|\w*ել\sեմ|\w*ել\sես|\w*ել\sէ|\w*ել\sենք|\w*ել\sեք|\w*ել\sեն|\w*եմ|\w*ես|\w*է\s\w*ում|\w*ենք|\w*եք|\w*են|\w*ում)\b"
    verbs = re.findall(pattern, sentence)
    return verbs

_conjugations = get_conjugations()

# def convert_eastern_conjugation(eastern_sentence):
#     verbs = findverbs(eastern_sentence)
#     for verb in verbs:
#         if verb in _conjugations:
#             eastern_sentence = eastern_sentence.replace(verb, _conjugations[verb])
#     return eastern_sentence

def convert_eastern_conjugation(eastern_sentence):
    eastern_sentence = clean_text(eastern_sentence)
    words = eastern_sentence.split(' ')
    for i in range(len(words)):
        for j in range(i + 1, min(i + 4, len(words)) + 1):  # Consider substrings of lengths 1 to 3
            verb = ' '.join(words[i:j])  # Join words to form a phrase
            if verb in _conjugations:
                eastern_sentence = eastern_sentence.replace(verb, _conjugations[verb])
    return eastern_sentence

def only_arm_chars(word):
    word = word.lower()
    pattern = r"[^ա-ֆ']"
    cleaned_text = re.sub(pattern, "", word.replace('\n', ''))
    cleaned_text = re.sub(r"\s+$", "", cleaned_text)
    return cleaned_text
    
def clean_text(text):
    pattern = r"[^ա-ֆ0-9,՞\s']"
    cleaned_text = re.sub(pattern, "", text.replace('\n', ''))
    cleaned_text = re.sub(r"\s+$", "", cleaned_text)
    return cleaned_text

def createdict():
    dictionary = {}
    hyw_list = []
    hye_list = []
    for key, val in _conjugations.items():
        for w_key, w_value in val["hyw"].items():
            if type(w_value) == dict:
                for interkey, interval in w_value.items():
                    hyw_list.append(clean_text(interval))
            else: 
                hyw_list.append(clean_text(w_value))
        for e_key, e_value in val["hye"].items():
            if type(e_value) == dict:
                for interkey, interval in e_value.items():
                    hye_list.append(clean_text(interval))
            else: 
                hye_list.append(clean_text(e_value))

    for hye, hyw in zip(hye_list, hyw_list):
        dictionary[hye] = hyw
    with open('Converter/Conjugator/Verbs/all_verbs.json', 'w', encoding="utf-8") as f:
        json.dump(dictionary, f, ensure_ascii=False)

def process_verb_parallel(verb, lang):
    with sync_playwright() as playwright:
        # browser
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.verbix.com/")
        page.get_by_label("Consent", exact=True).click()
        verb_info = GetVerb(page, verb, lang)  # Assuming GetVerb is a function to fetch verb information from the page
        context.close()
        browser.close()
        return (verb, verb_info)

def verbix_parallel(all_verbs, lang):
    
    all_verbs_parsed = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=14) as executor:
        # Submit tasks for each verb
        futures = [executor.submit(process_verb_parallel, verb, lang) for verb in all_verbs]

        # Gather results as they complete
        for future in tqdm(concurrent.futures.as_completed(futures)):
            timestart = time.time()
            verb, verb_info = future.result()
            all_verbs_parsed[verb] = verb_info
            end = time.time()
            print(end - timestart)
    return all_verbs_parsed

def verbix_sequencial(all_verbs, lang):
    with sync_playwright() as playwright:
        # browser
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.verbix.com/")
        page.get_by_label("Consent", exact=True).click()
        all_verbs_parsed = {}
        for verb in tqdm(all_verbs):
            verb_info = GetVerb(page, verb, lang)
            all_verbs_parsed[verb] = verb_info
        context.close()
        browser.close()
        return all_verbs_parsed

def verbix_sequencial2(all_verbs, lang):
    alreadyhere = read_verbs_json("Converter/verbs.json")
    with sync_playwright() as playwright:
        # browser
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.verbix.com/")
        page.get_by_label("Consent", exact=True).click()
        all_verbs_parsed = {}
        for verb in tqdm(all_verbs):
            if verb not in alreadyhere:
                verb_info = GetVerb(page, verb, lang)
                all_verbs_parsed[verb] = verb_info
        context.close()
        browser.close()
    alreadyhere.update(all_verbs_parsed)
    with open("Converter/verbs2.json", 'w', encoding='utf-8') as output_file:
        json.dump(alreadyhere, output_file, ensure_ascii=False, indent=4)


def GetVerb(page: Page, verb: str, lang):
    lang = 135 if lang == "eastern" else 136
    page.goto(f"https://www.verbix.com/webverbix/go.php?&D1={lang}&T1={verb}")
    pronouns = page.locator('.pronoun').all()
    verbinfos = page.locator('.normal').all()
    headers = page.locator('h4').all()
    
    verb_with_info = {}
    count = 0
    tenseprefix = ""
    for i in range(0, len(pronouns)):#pronoun, verbinfo in zip(pronouns, verbinfos):
        pronoun = pronouns[i]
        if "Sg.1" in pronoun.inner_html() or ("Sg.2" in pronoun.inner_html() and "՜" in verbinfos[i].inner_html()):
            tenseprefix = headers[count].inner_html()
            count = count + 1
            if count > 8:
                tenseprefix = f"N{tenseprefix}" # Negative forms
        if "Sg" in pronoun.inner_html() or "Pl" in pronoun.inner_html():
            head = f"{tenseprefix}_{pronoun.inner_html()}"
        else:
            head = pronoun.inner_html()
        head = head.strip()
        verb_with_info[head] = verbinfos[i].inner_html()
    return verb_with_info  # Printing the dictionary with td content
     
def read_verbs(path):
    with open(path, 'r', encoding="utf-8") as file:
        verbs = file.readlines()[0]
        verbs = verbs.split(',')
        return list(set(verbs))
     
def read_verbs_json(path):
    with open(path, 'r', encoding="utf-8") as file:
        return json.load(file)



def find_most_similar_word(word, word_list):
    max_similarity = 0
    most_similar_word = None
    
    for candidate_word in word_list:
        similarity = 1 - (Levenshtein.distance(word, candidate_word) / max(len(word), len(candidate_word)))
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_word = candidate_word
    
    return most_similar_word


#_keys = ["Name","Base","Conjugation","Irregular","Root","Past Participle","Negative Participle","Negative Imperfect Participle","Subject Participle","Future Participle","Present_Sg.1","Present_Sg.2","Present_Sg.3","Present_Pl.1","Present_Pl.2","Present_Pl.3","Imperfect_Sg.1","Imperfect_Sg.2","Imperfect_Sg.3","Imperfect_Pl.1","Imperfect_Pl.2","Imperfect_Pl.3","Preterite_Sg.1","Preterite_Sg.2","Preterite_Sg.3","Preterite_Pl.1","Preterite_Pl.2","Preterite_Pl.3","Imperative_Sg.1","Imperative_Sg.2","Imperative_Sg.3","Imperative_Pl.1","Imperative_Pl.2","Imperative_Pl.3","Present Perfect_Sg.1","Present Perfect_Sg.2","Present Perfect_Sg.3","Present Perfect_Pl.1","Present Perfect_Pl.2","Present Perfect_Pl.3","Pluperfect_Sg.1","Pluperfect_Sg.2","Pluperfect_Sg.3","Pluperfect_Pl.1","Pluperfect_Pl.2","Pluperfect_Pl.3","Future_Sg.1","Future_Sg.2","Future_Sg.3","Future_Pl.1","Future_Pl.2","Future_Pl.3","Conditional_Sg.1","Conditional_Sg.2","Conditional_Sg.3","Conditional_Pl.1","Conditional_Pl.2","Conditional_Pl.3"]
def combine_json(json1, json2):
    d = dictionary()
    combined_json = {}
    for key, value in json1.items():
        if key in json2:
            combined_json[value] = json2[key]
        else:
            try:
                western = d.get_western_exact(key)
                if western in json2:
                    combined_json[value] = json2[western]
            except Exception:
                a = "a"
    return combined_json

def combine_files(file1_path, file2_path, output_path):
    d = dictionary()
    with open(file1_path, 'r', encoding='utf-8') as file1, \
         open(file2_path, 'r', encoding='utf-8') as file2:
        
        data_hye = json.load(file1)
        data_hyw = json.load(file2)
        
        combined_data = {}
        
        for k_hye, v_hye in data_hye.items():
            if k_hye in data_hyw:
                combined_data.update(combine_json(v_hye, data_hyw[k_hye]))# | combined_data
            elif k_hye == "գնալ":
                combined_data.update(combine_json(v_hye, data_hyw["երթալ"]))
            elif k_hye == "լինել":
                combined_data.update(combine_json(v_hye, data_hyw["ըլլալ"]))
            else:
                try:
                    western = d.get_western_exact(k_hye)
                    combined_data.update(combine_json(v_hye, data_hyw[western[0]]))
                except Exception:
                    a = "a"
                # most_similar_hyw_key = find_most_similar_word(k_hye, data_hyw.keys())
                # if most_similar_hyw_key:
                #     combined_data.update(combine_json(v_hye, data_hyw[most_similar_hyw_key]))
        with open(output_path, 'w', encoding='utf-8') as output_file:
            json.dump(combined_data, output_file, ensure_ascii=False, indent=4)

# Usage example
# combine_files('Converter/eastern_verbs_with_info1.json', 'Converter/western_verbs_with_info1.json', 'Converter/combined1.json')

def find_empty_dict_keys(json_data):
    empty_dict_keys = []
    for key, value in json_data.items():
        if isinstance(value, dict) and not value:
            empty_dict_keys.append(key)
    return empty_dict_keys

def retry_empties(pathread, pathwrite, lang):
    with open(pathread, 'r', encoding='utf-8') as f:
        
        data_hye = json.load(f)
        empties = find_empty_dict_keys(data_hye)
        new = verbix_sequencial(empties, lang)
        data_hye = data_hye | new
        with open(pathwrite, "w", encoding="utf-8") as file:
            json.dump(data_hye, file, ensure_ascii=False, indent=4)


def delete_empty_dict_keys(path):
    with open(path, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    keys_to_delete = [key for key, value in json_data.items() if isinstance(value, dict) and not value]
    for key in keys_to_delete:
        del json_data[key]
    with open(path, "w", encoding="utf-8") as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)


def verbix(lang: str = "eastern", seq: bool = True, dict = None):
    if seq:
        verbs_with_info = verbix_sequencial(read_verbs(f"{lang}_verbs.txt"), lang)
    else:
        verbs_with_info = verbix_parallel(read_verbs(f"{lang}_verbs.txt"), lang)
    with open(f"{lang}_verbs_with_info.json", "a", encoding="utf-8") as file:
        json.dump(verbs_with_info, file, ensure_ascii=False, indent=4)


def find_words_in_dict(input_string, word_dict):
    words = input_string.split(' ')  # Split input string into words
    found_words = []
    for i in range(len(words)):
        for j in range(i + 1, min(i + 4, len(words)) + 1):  # Consider substrings of lengths 1 to 3
            phrase = ' '.join(words[i:j])  # Join words to form a phrase
            if phrase in word_dict:
                found_words.append(phrase)
    return found_words


def ReadFile(path):
    with open(path, encoding="utf-8") as file:
        return file.readlines()
    

# def find_and_count_all():
#find_words_in_dict("Եկեղեցու անվանումը ծագում է Թադեոս և Բարդուղիմեոս հիմնադիր առաքյալների հոգևոր կոչումից", read_verbs_json("Converter/verbs.json"))


# combine_files("Converter/eastern_verbs_with_info.json", "Converter/western_verbs_with_info.json", "verbs2.json")
# verbix()
# retry_empties("Converter/western_verbs_with_info1.json", "Converter/western_verbs_with_info.json", "western")

# print("Վիքիպեդիան առցանց, բազմալեզու, խմբակային հանրագիտարանային նախագիծ է, որն արտադրում էին վիքի ձևաչափով։ ")
# print(convert_eastern_conjugation("Վիքիպեդիան առցանց, բազմալեզու, խմբակային հանրագիտարանային նախագիծ է, որն արտադրում էին վիքի ձևաչափով։ "))
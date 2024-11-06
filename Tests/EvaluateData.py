import matplotlib.pyplot as plt
import json
from collections import defaultdict
import numpy as np


def LoadJson(path):
    with open(path, 'r', encoding="utf-8") as file:#'./EN-HYW/EN-HYW-Rule-Based-Translator/Tests/hyrbt_uscitizen_translations.json', 'r', encoding="utf-8") as file:
        data = json.load(file)
    return data

# models = ["nllb", "nllb2"]#["hyrbt", "mt5-small-31", "m2m100-nr1", "m2m100-fin", "m2m100-nb3", "m2m100-2222", "nllb", "nllb2"]
datasets = ["uscitizen"]#, "test"]
datasets = ["test"]
models = ["hyrbt", "mt5-small-31", "m2m100-nr1", "m2m100-nb3", "nllb"]
modelnames = {"hyrbt": "hyrbt", "mt5-small-31": "mT5", "m2m100-nr1": "M2M-100", "m2m100-nb3": "M2M-100x", "nllb": "NLLB"}
types = ["bleu", "chrf", "rouge-l", "meteo"]
datadir = './EN-HYW/EN-HYW-Rule-Based-Translator/Tests/Data'


def sentence_is_shorter_than(sentence, this):
    return ("en" in sentence and len(sentence["en"].split(' ')) < this) or ("src" in sentence and len(sentence["src"].split(' ')) < this)

def sentence_is_longer_than(sentence, this):
    return ("en" in sentence and len(sentence["en"].split(' ')) > this) or ("src" in sentence and len(sentence["src"].split(' ')) > this)

def find_sentence(sentences, tosearch):
    for sentence in sentences:
        pref = "en" if "en" in sentence else "src"
        if sentence[pref] == tosearch:
            return sentence
    return "not found"

def RemoveSentencesShorterThan(sentences, shorterthan = 3):
    s = []
    for sentence in sentences:
        if ("en" in sentence and len(sentence["en"].split(' ')) > shorterthan) or ("src" in sentence and len(sentence["src"].split(' ')) > shorterthan):
            s.append(sentence)
    return s


def LoadAll(models, datasets, types):
    bymodel = {}
    for model in models:
        l = []
        for ds in datasets:
            if model == "nllb":
                l += LoadJson(f'{datadir}/{model}_{ds}_evals.json')[:739]
            else:
                l += LoadJson(f'{datadir}/{model}_{ds}_evals.json')
        if model in bymodel:
            bymodel[model] += l
        else:
            bymodel[model] = l
    for model in models:
        for ds in datasets:
            for t in types:
                #dicts.append(SummarizeValuesBySentenceLength(data, t))
                deez_values = [scores[t] for scores in bymodel[model]]
                average_deez = sum(deez_values) / len(deez_values)
                print(f"avg '{t[:4]}' for  model: {model[-4:]} in dataset: {ds[:4]}::: {average_deez}")
    return bymodel


def Combine(sources, refs, hyps):
    data = []
    for src, ref, hyp in zip(sources, refs, hyps):
        data.append({
            "src": src,
            "hyp": hyp,
            "ref": ref
        })
    with open(f"{datadir}/nllb2_test_evals.json", "w", encoding="utf-8") as f:
        json.dump(data, f)

def SummarizeOccurencesBySentenceLength(data):
    gb_ref_length = defaultdict(int)  # Initialize a defaultdict with int to count occurrences
    
    for obj in data:
        ref_len = len(obj['ref'].split(' '))  # Get the sentence length
        
        # Update the count of this sentence length
        gb_ref_length[ref_len] += 1  # Increment the count for this sentence length
    
    # Sorting the dictionary by sentence length
    gb_ref_length = dict(sorted(gb_ref_length.items()))
    
    return gb_ref_length


def SummarizeValuesBySentenceLength(data, score_type):
    gb_ref_length = defaultdict(list)
    for obj in data:
        ref_len = len(obj['ref'].split(' '))
        if ref_len > 100:
            continue
        # if obj[score_type] <= 1 and score_type != "bleu" and score_type != "chrf":
        #     obj[score_type] = obj[score_type] * 100
        gb_ref_length[ref_len].append(obj[score_type])
        
    average_score_by_ref_len = {
        length: sum(values) / len(values) for length, values in gb_ref_length.items()
    }
    
    average_score_by_ref_len = dict(sorted(average_score_by_ref_len.items()))
    return average_score_by_ref_len

def GetModelSummaryBySentenceLength(model_data):
    summary = {}
    for type in types:
        summary[type] = SummarizeValuesBySentenceLength(model_data, type)
    return summary

def moving_average(data, window_size=3):
    """Apply moving average smoothing."""
    return np.convolve(data, np.ones(window_size)/window_size, mode='same')

def plot_smoothed_scores(score_by_models, models, types, window_size=3):
    for score_type in types:
        fig, ax = plt.subplots(figsize=(20, 10))
        ax.set_title(f"Smoothed {score_type} Scores by Sentence Length")
        ax.set_xlabel("Sentence Length")
        ax.set_ylabel("Score")
        maxlen, maxscore = 0, 0
        for model in models:
            lengths = sorted(score_by_models[model][score_type].keys())
            scores = [score_by_models[model][score_type][length] for length in lengths]
            smoothed_scores = moving_average(scores, window_size=window_size)
            ax.plot(lengths, smoothed_scores, label=modelnames[model])
            # Apply smoothing
        
            maxlen = int(max(lengths)) if max(lengths) > maxlen else maxlen
            maxscore = int(max(scores)) if max(scores) > maxscore else maxscore

        ax.legend(title="Score Type")
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.legend()
        # Set limits for better visualization (if needed)
        plt.xlim(min(lengths), maxlen)
        if score_type == "bleu" or score_type == "chrf":
            plt.ylim(0, maxscore)
            plt.yticks([i for i in range(0, maxscore)[::2]])
        else:
            plt.ylim(0, 1)
            plt.yticks([round(i * 0.01, 1) for i in range(100)])

        plt.xticks([i for i in range(0, maxlen)][::3])
        # plt.show()
        filename = f"us_{score_type}_smoothed_scores.png"
        plt.savefig(filename)

def PlotLengthOccs(data):
    plt.figure(figsize=(20, 12))
    plt.bar(data.keys(), data.values())  # Create a bar chart
    
    plt.title(f'Number of Sentences with specified length')
    plt.xlabel('Sentence Length (Number of Words)')
    plt.ylabel('Occurence Count')
    plt.xticks([i for i in range(0, 173)][::4])  # Ensure all sentence lengths appear on x-axis
    plt.yticks([i for i in range(0, 110)][::2])  # Ensure all sentence lengths appear on x-axis
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Save the plot if needed
    plt.savefig(f'sentence_length_counts.png', dpi=300, bbox_inches='tight')

    plt.show()

def get_hyp(sentence):
    if "hyp" in sentence:
        return sentence["hyp"]
    if "hyw" in sentence:
        return sentence["hyw"]

def get_random_sentence(data_by_models):
    score_by_models = {}
    for k, v in data_by_models.items():
        for i in range(0, len(v)):
            sentence = v[i]
            if k != "hyrbt" and k == "m2m100-nr1" and sentence["bleu"] > 15 and sentence_is_shorter_than(sentence, 15) and sentence_is_longer_than(sentence, 13):
                pref = "en" if "en" in sentence else "src"
                print("-------------------------------------------------------")
                print("en:  " + sentence[pref])
                print("ref: " + sentence["ref"])
                for model in models:
                    if model == k:
                        s = sentence
                    else:
                        s = find_sentence(data_by_models[model], sentence[pref])
                    if s == "not found":
                        #print(f"NOT FOUND for model {model}")
                        continue
                    score_by_models[model] = s
                    print(model + ": " + get_hyp(s))
                    print("BLEU:    " + str(s["bleu"]))
                    print("chrF++:  " + str(s["chrf"]))
                    print("ROUGE-L: " + str(s["rouge-l"]))
                    print("METEOR:  " + str(s["meteo"]))
                print("-------------------------------------------------------")
                #return score_by_models
        if list(data_by_models.keys()).index(k) == 50:
            break

data_by_models = LoadAll(models, datasets, types)
get_random_sentence(data_by_models)

score_by_models = {}
for k, v in data_by_models.items():
    score_by_models[k] = SummarizeOccurencesBySentenceLength(v)
#PlotLengthOccs(score_by_models["hyrbt"])

for k, v in data_by_models.items():
    score_by_models[k] = GetModelSummaryBySentenceLength(v)



plot_smoothed_scores(score_by_models, models, types)
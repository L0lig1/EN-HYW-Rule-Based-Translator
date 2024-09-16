import matplotlib.pyplot as plt
import json
from collections import defaultdict
import numpy as np


def LoadJson(path):
    with open(path, 'r', encoding="utf-8") as file:#'./EN-HYW/EN-HYW-Rule-Based-Translator/Tests/hyrbt_uscitizen_translations.json', 'r', encoding="utf-8") as file:
        data = json.load(file)
    return data

models = ["nllb", "nllb2"]#["hyrbt", "mt5-small-31", "m2m100-nr1", "m2m100-fin", "m2m100-nb3", "m2m100-2222", "nllb", "nllb2"]
datasets = ["test", "uscitizen"]
models = ["nllb2"]#["hyrbt", "mt5-small-31", "m2m100-nr1", "m2m100-fin", "m2m100-nb3", "m2m100-2222", "nllb", "nllb2"]
datasets = ["test"]
types = ["bleu", "chrf", "rouge-l", "meteo"]
datadir = './EN-HYW/EN-HYW-Rule-Based-Translator/Tests/Data'

def LoadAll(models, datasets, types):
    for model in models:
        for ds in datasets:
            data = LoadJson(f'{datadir}/{model}_{ds}_ev.json')
            dicts = []
            for t in types:
                #dicts.append(SummarizeValuesBySentenceLength(data, t))
                deez_values = [obj[t] for obj in data]
                average_deez = sum(deez_values) / len(deez_values)
                print(f"avg '{t[:4]}' for {ds[:4]}: {average_deez} - model: {model}")


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

srcs, refs, hyps = [], [], []
with open(f"{datadir}/test-nllb.en", "r", encoding="utf-8") as f:
    srcs = f.readlines()
with open(f"{datadir}/test-nllb.hyw", "r", encoding="utf-8") as f:
    hyps = f.readlines()
with open(f"{datadir}/test.hyw", "r", encoding="utf-8") as f:
    refs = f.readlines()

Combine(srcs, refs, hyps)

LoadAll(models, datasets, types)
# Extract the "deez" property and calculate the average


def SummarizeValuesBySentenceLength(data, score_type):
    gb_ref_length = defaultdict(list)
    for obj in data:
        ref_len = len(obj['ref'].split(' '))
        if obj[score_type] <= 1 and score_type != "bleu" and score_type != "chrf":
            obj[score_type] = obj[score_type] * 100
        gb_ref_length[ref_len].append(obj[score_type])
        
    average_score_by_ref_len = {
        length: sum(values) / len(values)
        for length, values in gb_ref_length.items()
    }
    
    average_score_by_ref_len = dict(sorted(average_score_by_ref_len.items()))
    return average_score_by_ref_len

# dicts = [SummarizeValuesBySentenceLength("bleu"), SummarizeValuesBySentenceLength("chrf"), SummarizeValuesBySentenceLength("rouge-l"), SummarizeValuesBySentenceLength("meteo")]

plt.figure(figsize=(20, 10))
plt.title("hy_rbt scores ")
for i in range(0, len(types)): 
    curr = dicts[i]
    print(curr[2])
    def moving_average(data, window_size):
        return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

    # Apply moving average to smooth the values
    smoothed_values = moving_average(list(curr.values()), window_size=3)

    # Adjust keys to match the length of the smoothed values
    smoothed_keys = list(curr.keys())[1:-1]
    plt.plot(smoothed_keys, smoothed_values, label=types[i])
    #plt.plot(list(curr.keys()), list(curr.values()), label=types[i])
    #plt.plot(i, d, color='blue', label='Model BLEU score')

# Add labels and title
plt.xlabel('Sentence Length', fontsize=12)
plt.ylabel('Score', fontsize=12)
plt.title('Score vs Sentence Length', fontsize=14)

# Customize the grid and legend
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
print([max(length.values()) for length in dicts])
# Set limits for better visualization (if needed)
plt.xlim(0, max([max(length.keys()) for length in dicts]))
plt.ylim(0, 75)
plt.xticks([i for i in range(0, max([max(length.keys()) for length in dicts]))[::3]])
plt.yticks([i for i in range(0, 75)[::2]])


# Show the plot
plt.show()
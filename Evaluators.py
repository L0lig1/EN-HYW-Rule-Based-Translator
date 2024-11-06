from nltk.translate.bleu_score import SmoothingFunction
from sacrebleu import corpus_bleu, corpus_chrf, sentence_bleu, sentence_chrf
from transformers import M2M100Tokenizer
import evaluate
from nltk.translate.meteor_score import meteor_score
from comet import download_model, load_from_checkpoint

from rouge import Rouge 

class EvaluationMetrics:

    tok = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
    def compute_meteor(hypothesis, reference):
        if hypothesis == "" or reference == "":
            return 0
        tokref = EvaluationMetrics.tok.tokenize(reference) 
        tokhyp = EvaluationMetrics.tok.tokenize(hypothesis) 
        meteor = meteor_score([tokref], tokhyp)
        return meteor

    def compute_rouge(hypothesis, reference):
        # Compute ROUGE score
        rouge = Rouge()
        if hypothesis == "" or reference == "":
            return [{"rouge-l": {"f": 0}}]
        scores = rouge.get_scores(hypothesis, reference)
        return scores
    
    def compute_bleu(hypothesis, references):
        return corpus_bleu([hypothesis], [[references]]).score
    
    def compute_sentence_bleu(hypothesis, references):
        return sentence_bleu(hypothesis, [references]).score

    def compute_chrf(hypothesis, references):
        return corpus_chrf(hypothesis, references)
    
    def compute_sentence_chrf(hypothesis, references):
        return sentence_chrf(hypothesis, [references]).score
    
    #https://medium.com/@sthanikamsanthosh1994/understanding-bleu-and-rouge-score-for-nlp-evaluation-1ab334ecadcb
    
    def compute_xcometxxl(hypothesis, reference, source):
        comet_metric = evaluate.load("comet")
        model_output = comet_metric.compute(predictions=hypothesis, references=reference, source=source)
        # Segment-level scores
        print (model_output.scores)

        # System-level score
        print (model_output.system_score)

        # Score explanation (error spans)
        print (model_output.metadata.error_spans)
    def aaaaaaaaaa():
        model_path = download_model("comet")
        # or for example:
        # model_path = download_model("Unbabel/wmt22-comet-da")

        # Load the model checkpoint:
        model = load_from_checkpoint(model_path)

        # Data must be in the following format:
        data = [
            {
                "src": "10 到 15 分钟可以送到吗",
                "mt": "Can I receive my food in 10 to 15 minutes?",
                "ref": "Can it be delivered between 10 to 15 minutes?"
            },
            {
                "src": "Pode ser entregue dentro de 10 a 15 minutos?",
                "mt": "Can you send it for 10 to 15 minutes?",
                "ref": "Can it be delivered between 10 to 15 minutes?"
            }
        ]
        # Call predict method:
        model_output = model.predict(data, batch_size=8, gpus=1)
        print(model_output)
        print(model_output.scores) # sentence-level scores
        print(model_output.system_score) # system-level score

# Example usage:
# source = "They will continue to work in that direction in the near future."
# hypothesis = "Յառաջիկային պիտի"
# reference = "Յառաջիկային պիտի շարունակեն աշխատելու այդ ուղղութեամբ։"


# print("BLEU score: ", EvaluationMetrics.compute_sentence_bleu(hypothesis, reference))
# print("CHRF score: ", EvaluationMetrics.compute_sentence_chrf(hypothesis, reference))

# print("BLEU score:", EvaluationMetrics.se(reference,))
# print("BLEU score:            ", EvaluationMetrics.compute_bleu(hypothesis, reference))
# print("CHRF++ score:          ", EvaluationMetrics.compute_chrf(hypothesis, reference))
# print("MetricX score:", EvaluationMetrics.compute_xcometxxl(hypothesis, reference, source))

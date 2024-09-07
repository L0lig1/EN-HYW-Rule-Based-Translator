import playwright
import re
from ..Dictionary.read_dict import dictionary, char_handler
import time

eastern = """
Հայաստանը դեպի ծով ելք չունեցող պետություն է Հարավային Կովկասում։ Հյուսիսում սահմանակցում է Վրաստանին, արևելքում՝ Ադրբեջանին, հարավում՝ Իրանին, իսկ արևմուտքում՝ Թուրքիային, հարավ-արևմուտքում՝ Ադրբեջանի էքսկլավ Նախիջևանի Ինքնավար Հանրապետությանը։ Այժմյան Հայաստանը զբաղեցնում է պատմական Հայաստանի տարածքի միայն մեկ տասներորդը՝ Այրարատ, Գուգարք և Սյունիք նահանգների մի մասը[8]։

«Հայաստան» անվանումը վերաբերում է նաև ողջ Հայկական լեռնաշխարհին, որտեղ կազմավորվել և իր պատմական ուղին է անցել հայ ժողովուրդը։ Ըստ հայոց պատմահայր Մովսես Խորենացու՝ հայ ժողովրդի պատմության սկիզբն է համարվում մ.թ.ա. 2492 թվականը, երբ հայ ժողովրդի անվանադիր նախահայրը՝ Հայկ նահապետը, Հայոց ձորի ճակատամարտում հաղթել է Ասորեստանի բռնարար տիրակալ Բելին և անկախություն նվաճել[9]։ Հայալեզու ցեղերը Հայկական լեռնաշխարհի հարավարևմտյան շրջաններում ապրել են մ.թ.ա. 2-րդ հազարամյակի վերջերից։ Արամե արքայի ջանքերով մ․թ․ա․ 860 թվականին հիմնադրվել է Վանի թագավորությունը, որի գոյության ժամանակահատվածում էլ՝ մ․թ․ա․ 782 թվականին, Արգիշտի Ա թագավորը հիմնադրել է ժամանակակից մայրաքաղաք Երևանը։ Մ․թ․ա․ 1-ին դարում՝ Տիգրան Բ Մեծի կառավարման տարիներին, Մեծ Հայքի թագավորությունը հասել է իր հզորության գագաթնակետին՝ ձգվելով Կասպից ծովից մինչև Միջերկրական ծով, Կովկասյան լեռներից մինչև Միջագետքի անապատները։ 4-րդ դարում՝ 301 թվականին, Հայաստանը դարձել է առաջին պետությունն աշխարհում, որն ընդունել է քրիստոնեությունը որպես պետական կրոն։ Արշակունյաց թագավորության անկումից հետո՝ 5-րդ դարում, Հայաստանը բաժանվել է Սասանյան Պարսկաստանի և Բյուզանդիայի միջև։ 9-րդ դարում Բագրատունիները վճռական պայքար մղելով արաբ նվաճողների դեմ, վերականգնել են հայկական անկախ թագավորությունը, որը, սակայն, անկում է ապրել 1045-ին՝ Բյուզանդիայի դեմ պատերազմների և ներքին պառակտումների պատճառով։ 11-14-րդ դարերում Միջերկրական ծովի ափին գոյություն է ունեցել Կիլիկիայի հայկական իշխանությունը և ապա՝ թագավորությունը։ 
"""

vocals = {
  "ա": True,
  "ե": True,
  "է": True,
  "ի": True,
  "ո": True,
  "ու": True,
}

def check_ending(word):

    return edited_word


def replace_known_words(text):
    dic = dictionary()
    replaced_text = text.split()
    for i, word in enumerate(replaced_text):
        try:
            removespecials = char_handler.remove_special_characters(word)
            edited_word = word
            split_endings = ["ներ", "ին", "ը", "ի"]
            endingedited = False
            for ending in split_endings:
                if edited_word.endswith(ending):
                    edited_word = edited_word.split(ending)[0]
                    endingremoved = ending
                    endingedited = True
            if edited_word.endswith("ե"):
                edited_word = edited_word[:-1] + "է"
                endingedited = True
            checkending = edited_word
            #print(f"{checkending}; {checkending.endswith("ը")}")
            res = dic.get_western(checkending, True)
            if endingedited:
                res += endingremoved
            print(f"RESULT: {res} {i}")
            # if char_handler.is_special_char(checkending[-1]):
            #     res += checkending[-1]
            replaced_text[i] = res
        except ValueError:
            continue
        except Exception:
            continue
    #print(" ".join(replaced_text))
    #replaced_text = [item if isinstance(item, str) else str(item) for item in replaced_text]
    return " ".join(replaced_text)


def convert_verbs(text):
    # Define a regular expression pattern to match verbs ending with "ում են"
    pattern = r'(\w+?)ում\s(է|են)\b'

    # Define a function for replacement
    def repl(match):
        verb = match.group(1)
        if match.group(2) == 'է':
            verb = f'{verb}ի'
        elif match.group(2) == 'են':
            verb = f'{verb}են'
        if verb[0] in vocals:
            return f"կ'{verb}"
        return f'կը {verb}'

    # Perform the replacement
    result = re.sub(pattern, repl, text)
    return result


def convert_to_western(text):
    text = text.lower()
    western = convert_verbs(text)
    western = western.replace("որն", "որը")
    western = western.replace("եվ", "եւ")
    western = western.replace("յաց", "եաց")
    western = western.replace("յուն", "իւն")
    western = western.replace("ից", "էն")
    #western = re.sub(r'(\w*?)ույ(\w*)', r'\1ոյ\2', western)+
    western = re.sub(r'(\b\w)յէ(\w*\b)', r'\1ե\2', western)
    western = re.sub(r'(\w*?)և(\w*)',    r'\1եւ\2',   western)
    western = re.sub(r'(\w+)յան(\w*)',   r'\1եան\2',       western)
    western = re.sub(r'(\w+)եք(\w*)',    r'\1էք\2',       western)
    western = re.sub(r'(\w*)վի\b',       r'\1ուի',       western)
    western = re.sub(r'(\w*)ե\b',        r'\1է',       western)
    western = re.sub(r'(\w*)վել\b',      r'\1ուած',       western)
    western = re.sub(r'(\w+)ների',       r'\1ներու',     western)
    western = re.sub(r'(\w+)ված\b',      r'\1ուած',      western)
    western = re.sub(r'(\w+)վող\b',      r'\1ուող',      western)
    western = re.sub(r'(\w+)վող\b',      r'\1ուող',      western)
    western = re.sub(r'(\w*)յու(\w*)',   r'\1իւ\2',  western)
    western = re.sub(r'(\w*?)յու(\w*)',  r'\1իւ\2',  western)
    western = replace_known_words(western)
    return western



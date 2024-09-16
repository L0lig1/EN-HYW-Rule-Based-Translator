import unittest
from Conjugator.CustomConjugator import EastToWest, FindEasternVerbs

class TestStringMethods(unittest.TestCase):
    def test_find_present(self):
        eastern_sentence = "Հայերենը պատկանում է Հնդեվրոպական լեզվաընտանիքին: Այն բաժանված է երկու մասի՝ արևելահայերեն և արևմտահայերեն ստեղծել եք։ Արևելահայերենը տարածում եմ Հայաստանում, Արցախում, Իրանում և հետխորհրդային երկրներում, իսկ արևմտահայերենն օգտագործում են պատմական Արևմտյան Հայաստանում: Իրանում ես ստեղծում ես այստեղ նրանք գնում են" 
        eastern_verbs = FindEasternVerbs(eastern_sentence)
        #print(type(eastern_verbs[0]))
        print(eastern_verbs['present'])
        self.assertIn("տարածում եմ", eastern_verbs['present'])
        self.assertIn("պատկանում է", eastern_verbs['present'])
        self.assertIn("ստեղծում ես", eastern_verbs['present'])
        self.assertIn("գնում են", eastern_verbs['present'])
        self.assertNotIn("իրանում ես", eastern_verbs['present'])

        # self.assertIn("ստեղծել եք", eastern_verbs['present'])

if __name__ == '__main__':
    unittest.main()
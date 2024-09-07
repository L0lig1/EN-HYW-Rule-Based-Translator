import pandas as pd
import numpy as np
import re


class char_handler:
	def remove_special_characters(text):
		# Define a pattern to match special characters
		pattern = r'[^ա-ֆԱ-Ֆ0-9\s]'  # This pattern matches any character that is not a letter, digit, or whitespace

		# Use re.sub() to replace special characters with an empty string
		cleaned_text = re.sub(pattern, '', text)

		return cleaned_text
	
	def is_special_char(char):
		return char in "֎ 	և / § 	։ 	) 	( 	» 	« 	— 	․ 	՝ 	, 	‐ 	֊ 	… 	՜ ՛ 	՞"


class dictionary:

	filename = "./EN-HYW/EN-HYW-Rule-Based-Translator/Dictionary/ArmenianGermanDictionary.csv"

	def __init__(self):
		self.df = pd.read_csv(self.filename)
		#self.df = pd.read_excel("ArmenianGermanDictionary (3).xlsx", sheet_name=None)
	def get_western_exact(self, word):
		try:
			queryres = self.df["WESTARMENISCH"][self.df.OSTARMENISCH == char_handler.remove_special_characters(word)]
			return list(queryres.items())[0][1]
		except:
			raise ValueError("Given query not found")


	def query(self, query, columnwhere, columntoget = "", exact = False, list2str = True):

		if exact:
			res = self.df["WESTARMENISCH"][self.df.OSTARMENISCH == char_handler.remove_special_characters(query)]
			reslist = list(res.items())
			if len(reslist) == 0:
				raise Exception("No word found")
			return list(res.items())[0][1]
		else:
			res = ""
			if columntoget == "":
				res = self.df[self.df[columnwhere].str.contains(query, na=False)]
			else:
				res = self.df[self.df[columnwhere].str.contains(query, na=False)][columntoget]
			reslist_stringonly = []
			reslist = list(res.items())
			if list2str:
				for result in reslist:
					reslist_stringonly.append(f" {result[1]}")
			return reslist_stringonly
		#if len(reslist) > 1:
	# def query_like(self, query, columnwhere):
	# 	return self.df[self.df[columnwhere].str.contains(query, na=False)]
		
	def pandaquery(self, query, columnwhere):
		res = self.df.query(f"{columnwhere} == '{query}'")
		return res
		
	def column_ends_with(self, query, columnwhere):
		res = self.df[columnwhere].str.lower().str.endswith(query) == True
		return res

	def print_all(self, rows):
		print(len(rows))
		for row in rows:
			print(row)

	def get_eastern(self, word, exact = False):
		try:
			return self.query(word.lower(), "WESTARMENISCH", "OSTARMENISCH", exact)
		except Exception as e:
			raise Exception(f"{word} բառը արեւելահայերէն բառ չունի")

	def get_western(self, word, exact = False):
		try:
			return self.query(word.lower(), "OSTARMENISCH", "WESTARMENISCH", exact)
		except Exception as e:
			raise Exception(f"{word} բառը արեւմտահայերէն բառ չունի")
	def replace_in_column(self, replace_this, replace_with, column):
		self.df[column] = self.df[column].str.replace(replace_this, replace_with)

	def fill_column_with_column(self, column_to_fill, column_with_data):
		self.df[column_to_fill] = self.df[column_to_fill].fillna(self.df[column_with_data])
	
	def save(self):
		self.df.to_csv(self.filename, index=False, header=True, encoding="utf-8")

dic = dictionary()
def replace_known_words_from_dictionary(text):
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



# d = dictionary()
# # d.replace_in_column("իւն", "յուն", "OSTARMENISCH")
# # d.replace_in_column("փյունիկ", "փիւնիկ", "WESTARMENISCH")
# # #d.print_all(d.df[0:100][0:100])
# # d.replace_in_column("արդիւն", "արդյուն", "OSTARMENISCH")
# # d.fill_column_with_column("OSTARMENISCH", "WESTARMENISCH")
# # d.replace_in_column("անվանելի", "անուանելի", "WESTARMENISCH")
# # d.replace_in_column("և", "եւ", "WESTARMENISCH")
# # d.replace_in_column("լոյս", "լույս", "OSTARMENISCH")
# # d.replace_in_column("ուա", "վա", "OSTARMENISCH")
# # d.replace_in_column("լույս", "լոյս", "WESTARMENISCH")
# # # d.replace_in_column("դէպի", "դեպի", "OSTARMENISCH")
# d.df["֍գն֍"] = d.df.apply(lambda row: "֍" if row["WESTARMENISCH"].endswith("ոց") else row["֍գն֍"], axis=1)

# d.save()
# # #print(d.df.head())
# # #print(d.query("֍", "֍?֍", ["WESTARMENISCH"]))#[["WESTARMENISCH", "OSTARMENISCH", "DEUTSCH"]])
# print(d.column_ends_with("թիւն", "WESTARMENISCH")[1])#[["WESTARMENISCH", "OSTARMENISCH", "DEUTSCH"]])
# # print(d.query("լույս", "WESTARMENISCH", exact=False, list2str=False))

# # Sample data
# data = {'ColumnA': ['Value1', 'Value2', 'Value3', 'Value4'],
#         'ColumnB': ['StringA', 'StringB_suffix', 'StringC', 'StringD_suffix']}

# # Create a DataFrame
# df = pd.DataFrame(data)

# # Define the specific string you want to check for at the end of ColumnB
# specific_string = '_suffix'

# # Conditionally write to ColumnA if ColumnB ends with the specific string
# df['ColumnA'] = df.apply(lambda row: 'Something' if row['ColumnB'].endswith(specific_string) else row['ColumnA'], axis=1)

# # Display the modified DataFrame
# print(df)
# Write train, test, and validation into a file
def WriteToFile(path, data):
    with open(path, "a", encoding="utf-8") as file:
        for sentence in data:
            file.write(sentence['hyw'])

WriteToFile("/content/drive/MyDrive/Colab Notebooks/models/facebook/m2m100_418M/train.txt", raw_datasets["train"]["translation"])
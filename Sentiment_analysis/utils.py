import os
import pandas as pd
import requests
import numpy as np
import re
import tarfile
import pickle
from django.conf import settings
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer



class DatasetManager:
    """Handles the download, extraction, loading
     and shuffling of the dataset."""

    def __init__(self):
        self.dataset_file = os.path.join(settings.MEDIA_ROOT, "aclImdb.csv")
        self.dataset_folder = os.path.join(settings.MEDIA_ROOT, "aclImdb")
        self.dataset_url = "https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz"
        self.pickle_file = os.path.join(settings.MEDIA_ROOT, "movie_data.pkl")

    def get_or_download_dataset(self):

        pickle_file = self.dataset_file.replace(".csv", ".pkl")
        if os.path.exists(self.pickle_file):
            with open(self.pickle_file, "rb") as f:
                return pickle.load(f)

        if not os.path.exists(self.dataset_folder):
            self.download_and_extract_dataset()

        if os.path.exists(self.dataset_file):
            df = pd.read_csv(self.dataset_file)
        else:
            df = self._create_dataframe()

        with open(pickle_file, "wb") as f:
            pickle.dump(df, f)

        return df

    def download_and_extract_dataset(self):
        zip_path = os.path.join(settings.MEDIA_ROOT, "aclImdb_v1.tar.gz")

        if not os.path.exists(self.dataset_folder):
            print("Downloading dataset...")
            response = requests.get(self.dataset_url, stream=True)

            if response.status_code == 200:
                with open(zip_path, "wb") as f:
                    f.write(response.content)

            else:
                print("Failed to download dataset")
                return

        print("Extracting dataset...")
        with tarfile.open(zip_path, "r:gz") as tar:
            tar.extractall(path=settings.MEDIA_ROOT)
        os.remove(zip_path)

    def _create_dataframe(self):
        labels = {"pos": 1, "neg": 0}
        df = pd.DataFrame()
        for s in ("test", "train"):
            for l in ("pos", "neg"):
                path = os.path.join(self.dataset_folder, s, l)
                data_to_add = []

                for file in os.listdir(path):
                    with open(os.path.join(path, file), "r", encoding="utf-8") as infile:
                        txt = infile.read()
                        data_to_add.append([txt, labels[l]])

                df = pd.concat([df, pd.DataFrame(data_to_add, columns=["reviews", "sentiment"])], ignore_index=True)

        return self.shuffle_dataset(df)

    def shuffle_dataset(self, df):
        np.random.seed(0)
        df = df.sample(frac=1).reset_index(drop=True)
        df.to_csv(self.dataset_file, index=False)
        return df


class TextPreprocessor:
    def __init__(self):
        self.porter = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))

    def preprocessor(self, text):
        # Removes the HTML tag
        text = re.sub('<[^>]*>', '', text)

        # Extract any emoticons
        emoticons = re.findall('(?::|;|=) (?:-)?(?:\)|\(|D|P)', text.lower())

        # Removes non-word characters and convert text to lowercase
        text = re.sub('[\W]+', ' ', text.lower())

        # Reattach emotion without hyphens
        text = text + ' ' + ' '.join(emoticons).replace('-', '')

        return text

    def tokenize(self, text):
        # Separates the words for sentiment analysis
        tokens = text.split()
        return [self.porter.stem(word) for word in tokens if word.lower() not in self.stop_words]

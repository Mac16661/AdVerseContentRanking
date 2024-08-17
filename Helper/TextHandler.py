import nltk
import string
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from functools import lru_cache
from .TextToEmbeddings import TextToEmbeddings
import numpy as np

@lru_cache(maxsize=1)
class TextHandler():
    def __init__(self):
        # nltk.download('punkt') # Download the 'punkt' resource
        # nltk.download('wordnet') # Download the 'wordnet' resource
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

    def text_lowercase(self, text):
        return text.lower()

    def remove_punctuation(self, text):
        translator = str.maketrans('', '', string.punctuation)
        return text.translate(translator)

    def remove_whitespace(self, text):
        return  " ".join(text.split())


    def remove_stopwords(self, text):
        stop_words = set(stopwords.words("english"))
        word_tokens = word_tokenize(text)
        filtered_text = [word for word in word_tokens if word not in stop_words]
        return filtered_text

    def stem_words(self, text):
    #     word_tokens = word_tokenize(text)
        word_tokens = text
        stems = [self.stemmer.stem(word) for word in word_tokens]
        return stems

    def lemma_words(self, text):
    #     word_tokens = word_tokenize(text)
        word_tokens = text
        lemmas = [self.lemmatizer.lemmatize(word) for word in word_tokens]
        return lemmas

    def concat(self, lst):
        s = ""
        for i in lst:
            s = s+i+" "
        return s

    def getProcessedText(self, text):
        """
            Preprocess text data
            Args:
                text -> unprocessed texts data
            
            returns:
                pre-process text data
        """
        text = self.text_lowercase(text)
        text = self.remove_punctuation(text)
        text = self.remove_whitespace(text)
        text = self.remove_stopwords(text)
        text = self.stem_words(text)
        text = self.lemma_words(text)
        text = self.concat(text)
        return re.sub(r'[^\w\s]', '', text) # removes special char

    def sendResponse(self, args, sidReqContext, socContext, eventContext):
        """
            Process text coming from client and make it compatible to be used with next function in the chain
            
            Args: 
                args -> text data and user id
                sid -> socket id(to identify user)
                soc -> socket instance(to avoid out of context issue)
        """

        print(f"processing chunk from user -> {sidReqContext} ")

        """
            Steps->
                get text prediction 
                get text embeddings
                perform similarity search
                rank contents
                return ads as response 
        """

        if args["text"] and  args["id"]:
            processedText = self.getProcessedText(args["text"])
            embeddedText = TextToEmbeddings().textToEmbedding(processedText)
            # print(embeddedText) 
            socContext.emit("adsOut", {'message': embeddedText.shape, 'id': args["id"]}, room=sidReqContext)
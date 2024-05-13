from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from termDocFreq import TermFreq

class LemmaTokenizer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def setQuery(self, doc):
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        Q = [self.lemmatizer.lemmatize(t) for t in word_tokenize(doc) if t not in stop_words]
        self.filtered_query = ' '.join(Q)

    def getQuery(self):
        return self.filtered_query

def main():
    user_query = input("Enter your search query: ").lower()

    LemObj = LemmaTokenizer()  # Create LemmaTokenizer object
    LemObj.setQuery(user_query)  # Set the user query

    # Access the filtered query and perform further processing
    objTermFreq = TermFreq(LemObj.getQuery())  # Now, the filtered query can be accessed
    objTermFreq.term_doc_Freq()

if __name__ == "__main__":
    #start with User Query
    main()

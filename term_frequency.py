from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from db_connection import DBConnection
import numpy as np

db_connection = DBConnection()
professors = db_connection.db["professors"]
document_term_frequency = db_connection.db["document_term_frequency"]

# Lemmatizing/Stopwords
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Documents
documents = [professor.get('Research-Interest', '') + " " +
             professor.get('Education', '') + " " +
             professor.get('Contact-Info', '') for professor in professors.find()]

# Instantiate the CountVectorizer
count_vectorizer = CountVectorizer(analyzer='word', stop_words='english')

# Fit and transform
count_vectorizer.fit(documents)
count_matrix = count_vectorizer.transform(documents)
count_tokens = count_vectorizer.get_feature_names_out()

for i, professor in enumerate(professors.find()):
    doc_id = str(professor['_id'])
    for j, term in enumerate(count_tokens):
        term_frequency = int(count_matrix[i, j])
        if term_frequency != 0:
            term_doc = {
                'docId': doc_id,
                'term': term,
                'frequency': term_frequency
            }
            document_term_frequency.insert_one(term_doc)

print("Term frequencies inserted into the 'document_term_frequency' collection.")

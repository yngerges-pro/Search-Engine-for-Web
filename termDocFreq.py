from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from db_connection import DBConnection
import numpy as np

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class TermFreq:
    def __init__(self, Q):
        self.Q = Q

    def term_doc_Freq(self):
        db_connection = DBConnection()
        professors = db_connection.db["professors"]

        # Lemmatizing/Stopwords
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()

        # Documents
        documents = [professor.get('Research-Interest', '') + " " +
                    professor.get('Education', '') + " " +
                    professor.get('Contact-Info', '') for professor in professors.find()]
        # print("------------------------------------Docs---------------------------------------\n")
        # print("Docs", documents)

        countvectorizer = CountVectorizer(analyzer='word', stop_words='english')

        countvectorizer.fit(self.Q.split())
        # # Fit and transform
        # Doc_v = countvectorizer.fit_transform(documents)
        
        countvectorizer = CountVectorizer(analyzer='word', stop_words='english', vocabulary=self.Q.split())

        # Fit and transform
        Doc_v = countvectorizer.fit_transform(documents)
        
        # Transform query
        query_v = countvectorizer.fit_transform([self.Q])
        count_query = countvectorizer.get_feature_names_out()
        # Print count vectors
        print("\nCount Vectorizer Document")
        df = pd.DataFrame(data=Doc_v.toarray(), index=range(1, len(documents) + 1), columns=count_query)

        # df = df.loc[(df != 0).any(axis=1)]
        print("Document freq:\n",df)

        print("\nCount Vectorizer Query ")
        qf = pd.DataFrame(data=query_v.toarray(), index=range(1, 2), columns=count_query)
        # qf = qf.loc[(qf != 0).any(axis=1)]
        print("\nquery freq:\n",qf)

        tfidf_query = TfidfTransformer()

        tfidf_query.fit(query_v)
        tfidf_matrix = tfidf_query.fit_transform(Doc_v)

        print("\nTFIDF transformer using Count Vectorizer Query\n")
        tf_IDF = pd.DataFrame(data=tfidf_matrix.toarray(), index=range(1, len(documents) + 1), columns=count_query)
        # tf_IDF_Query = tf_IDF_Query.loc[(tf_IDF_Query != 0).any(axis=1)]
        print(tf_IDF)


        cos_sim = cosine_similarity(Doc_v, query_v)
        print(cos_sim)

        # Assuming you have computed the cosine similarity scores and stored them in the variable cos_sim
        # Also assuming you have a list of document indices doc_indices

        # Create a list of document indices
        doc_indices = list(range(1,len(documents)+1))

        # Create a list of tuples containing the document index and its cosine similarity score
        doc_similarity = [(index, score) for index, score in zip(doc_indices, cos_sim)]

        # Sort the documents based on their cosine similarity scores in descending order
        sorted_docs = sorted(doc_similarity, key=lambda x: x[1], reverse=True)

        # Retrieve the document indices in the sorted order
        sorted_indices = [doc[0] for doc in sorted_docs]

        # Now sorted_indices contains the indices of the documents ranked by their similarity to the query
        first_Five = [sorted_indices[i] for i in range(5)]
        print(first_Five)





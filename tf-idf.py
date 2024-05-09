# TfidfVectorizer
# CountVectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from pymongo import MongoClient
from db_connection import DBConnection

# Connect to MongoDB
db_connection = DBConnection()
professors_collection = db_connection.db["professors"]

# Retrieve documents from MongoDB
documents = [doc.get('Research-Interest', '') for doc in professors_collection.find({})]

# Instantiate the vectorizer object
countvectorizer = CountVectorizer(analyzer='word', stop_words='english')

# Convert the documents into a matrix
countvectorizer.fit(documents)
training_v = countvectorizer.transform(documents)

# Retrieve the terms found in the corpora
count_tokens = countvectorizer.get_feature_names_out()

# Transfer the training term matrix of CountVectorizer to TF-IDF
tfidf_training = TfidfTransformer()
tfidf_training.fit(training_v)
tfidf_training_matrix = tfidf_training.transform(training_v)

# Format TF-IDF transformed matrices
tfidf_matrices = []
for i, doc in enumerate(professors_collection.find({})):
    tfidf_matrix_dict = {}
    for j, term in enumerate(count_tokens):
        tfidf_matrix_dict[term] = tfidf_training_matrix[i, j]
    tfidf_matrices.append(tfidf_matrix_dict)

# Insert TF-IDF transformed matrices into MongoDB
for i, doc in enumerate(professors_collection.find({})):
    # Create a new field in each document to store the TF-IDF transformed matrix
    professors_collection.update_one({"_id": doc["_id"]}, {"$set": {"tfidf_matrix": tfidf_matrices[i]}})

print("TF-IDF transformed matrices inserted into MongoDB.")

from sklearn.feature_extraction.text import TfidfVectorizer
from db_connection import DBConnection
import pandas as pd

# Connect to MongoDB
db_connection = DBConnection()
professors_collection = db_connection.db["professors"]

# Retrieve documents from MongoDB and format into a list of strings
documents = []
for doc in professors_collection.find({}):
    document = ""
    for key, value in doc.items():
        if key in ["name", "title", "email", "website", "Research-Interest", "Education", "Contact-Info"]:
            document += str(value) + " "
    documents.append(document)

# Create list of terms with term frequency for each document
term_frequency_docs = []
for doc in documents:
    term_freq = {}
    for term in doc.split():
        term_freq[term] = term_freq.get(term, 0) + 1
    term_frequency_docs.append(term_freq)

# Create index mapping
index_mapping = list(range(len(documents)))

# Initialize TfIdfVectorizer
tfidf_vectorizer = TfidfVectorizer()

# Fit the vectorizer and transform the documents
tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

# Get feature names (terms)
feature_names = tfidf_vectorizer.get_feature_names_out()

# Create DataFrame for TF-IDF matrix
tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)

# Add index mapping to the DataFrame
index_mapping_df = pd.DataFrame({"Index": index_mapping})
tfidf_df = pd.concat([index_mapping_df, tfidf_df], axis=1)

# Print TF-IDF DataFrame
print("TF-IDF DataFrame:")
print(tfidf_df)

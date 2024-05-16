from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from db_connection import DBConnection
from bson import ObjectId
from tf_idf_new_terms import TermFreq

# # Define LemmaTokenizer class for lemmatization
# class LemmaTokenizer:
#     def __init__(self):
#         self.lemmatizer = WordNetLemmatizer()

#     def __call__(self, doc):
#         return [self.lemmatizer.lemmatize(t) for t in word_tokenize(doc)]


# User Query input
def UserQ():
    # Get user query
    user_query = input("Enter your search query: ").lower()

    # Remove stopwords from user query
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(user_query)
    filtered_tokens = [token for token in tokens if token not in stop_words]
    # filtered_query = ' '.join(filtered_tokens)

    Tf_idf_obj = TermFreq(filtered_tokens)
    Tf_idf_obj.term_doc_Freq()

    # lemma_token_vector = tf_idf_new_terms.vectorizer.transform([filtered_query])

    ## comparing query_v with tfidf_matrix?
    # # Cosine Similarity
    # cosine_similarities = cosine_similarity(lemma_token_vector, tf_idf_new_terms.tfidf_matrix)
    # doc_similarities = [(doc_id, sim) for doc_id, sim in zip(tf_idf_new_terms.docIDs, cosine_similarities[0])]

    # cosine_similarities = cosine_similarity(lemma_token_vector, tf_idf_new_terms.tfidf_matrix)
    # doc_similarities = [(doc_id, sim) for doc_id, sim in zip(tf_idf_new_terms.docIDs, cosine_similarities[0])]



def Ranking(doc_similarities):
    # Paginate results
    results_per_page = 5
    num_pages = (len(doc_similarities) + results_per_page - 1) // results_per_page
    current_page = 1

    while True:
        print(f"Page {current_page}:")

        start_index = (current_page - 1) * results_per_page
        end_index = min(start_index + results_per_page, len(doc_similarities))
        page_results = doc_similarities[start_index:end_index]

        db_connection = DBConnection()
        professors = db_connection.db['professors']
        
        for doc_id, similarity in sorted(page_results, key=lambda x: x[1], reverse=True):
            professor_doc = professors.find_one({"_id": ObjectId(doc_id)})
            print(professor_doc.get("website"))

        print("Next Page (N) | Previous Page (P) | Quit (Q)")
        choice = input("Enter your choice: ").strip().lower()

        if choice == 'n' and current_page < num_pages:
            current_page += 1
        elif choice == 'p' and current_page > 1:
            current_page -= 1
        elif choice == 'q':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    UserQ()


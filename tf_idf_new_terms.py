from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from db_connection import DBConnection
import pandas as pd

class TermFreq:
    def __init__(self, Q):
        self.Q = Q
        
    def term_doc_Freq(self):
        db_connection = DBConnection()
        professors = db_connection.db["professors"]

        # Documents
        documents = [professor.get('info', '') for professor in professors.find()]

        # Fit and transform CountVectorizer on documents
        countvectorizer = CountVectorizer(analyzer='word', stop_words='english')
        Doc_v = countvectorizer.fit_transform(documents)

        # Transform query
        query_v = countvectorizer.transform(self.Q)

        # Apply TF-IDF only on documents
        tfidf = TfidfTransformer()
        tfidf.fit(Doc_v)
        tfidf_matrix_Doc = tfidf.transform(Doc_v)
        tfidf_matrix_query = tfidf.transform(query_v)

        # Compute cosine similarity
        cosine_similarities = cosine_similarity(tfidf_matrix_query, tfidf_matrix_Doc)
        doc_similarities = cosine_similarities[0]

        # Get document IDs
        docIDs = [professor['_id'] for professor in professors.find({}, {"_id": 1})]

        # Combine document IDs with cosine similarities
        doc_similarities_with_ids = list(zip(docIDs, doc_similarities))

        # Sort by similarity
        doc_similarities_with_ids.sort(key=lambda x: x[1], reverse=True)

        # Paginate results
        results_per_page = 5
        num_pages = (len(doc_similarities_with_ids) + results_per_page - 1) 
        current_page = 1

        while True:
            print(f"Page {current_page}:")
            start_index = (current_page - 1) * results_per_page
            end_index = min(start_index + results_per_page, len(doc_similarities_with_ids))
            page_results = doc_similarities_with_ids[start_index:end_index]

            for doc_id, similarity in page_results:
                professor_doc = professors.find_one({"_id": doc_id})
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

from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

class LemmaTokenizer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def __call__(self, doc):
        return [self.lemmatizer.lemmatize(t) for t in word_tokenize(doc)]


user_query = input("Enter your search query: ").lower()

# Remove stopwords
stop_words = set(stopwords.words('english'))

tokens = word_tokenize(user_query)
filtered_tokens = [token for token in tokens if token not in stop_words]
filtered_query = ' '.join(filtered_tokens)

# Lemmatize
lemma_vectorizer = CountVectorizer(tokenizer=LemmaTokenizer(), token_pattern=None)
lemma_token_vector = lemma_vectorizer.fit_transform([filtered_query])

# Summarize
print("Lemma vocabulary:", lemma_vectorizer.vocabulary_)
print("Lemmatized vector shape:", lemma_token_vector.shape)
print("Lemmatized vector array:", lemma_token_vector.toarray())

# Converts lemmatized query into acceptable format for character n-grams
lemmatized_tokens = lemma_vectorizer.get_feature_names_out()

# Character n-grams
ngram_vectorizer = CountVectorizer(analyzer='char_wb', ngram_range=(5, 5))
ngram_token_vector = ngram_vectorizer.fit_transform(lemmatized_tokens)

# Placeholder for retrieving and displaying ranked documents
print("\nVocabulary (n-gram):", ngram_vectorizer.vocabulary_)
print("Encoded vector shape (n-gram):", ngram_token_vector.shape)
print("Encoded vector array (n-gram):", ngram_token_vector.toarray())

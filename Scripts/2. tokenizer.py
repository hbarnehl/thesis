"""
Tokenizer
---------
This script tokenizes the article texts and saves them as a list of lists of
lemmatized tokens. It does the following:
1. Loads the article texts from a CSV file
2. Tokenizes the texts with the Spanish language model from spaCy
3. Lemmatizes the tokens
4. Removes stopwords
5. Saves the tokens as a pickle file
6. Integrates the tokens back into the dataset
7. Creates bigrams and trigrams with Gensim
8. Saves the trigrams as a CSV file
"""

import pickle
import pandas as pd
import spacy
import gensim
import csv

# Tokenize article texts with spacy
csv_gen = (row for row in open("texts.csv"))

# Load Spanish language model
nlp = spacy.load('es_core_news_md', disable=["parser", "attribute_ruler", "ner"])

# Add stopwords
nlp.Defaults.stop_words |= {"a", "y", "o"}

# Reload language model to incorporate new stopwords
nlp = spacy.load('es_core_news_md', disable=["parser", "attribute_ruler", "ner"])

tokenlist = []

# Go through rows of article texts
for i, doc in enumerate(
    nlp.pipe(csv_gen, disable=["parser", "attribute_ruler", "ner"], n_process=4, batch_size=50)
):
    # Append lists of lemmatized tokens to tokenlist
    tokenlist.append(
        [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]
    )
    if i % 1000 == 0 and i != 0:
        print(i)

# Remove first entry, which is the column title
tokenlist = tokenlist[1:]

# Save to pickle
with open("tokens/tokens.pkl", "wb") as f:
    pickle.dump(tokenlist, f)

# Integrate tokenlist into df, useful for later structural topic model and all subsampling
# Load tokenlist
with open("tokens/tokens.pkl", "rb") as f:
    tokenlist = pickle.load(f)

# Integrate tokenlist back into dataframe
df = pd.read_csv("dataset_token_ready.csv")
df = df.assign(tokens=tokenlist)

# Save dataset as pickle (csv does not work, because it cannot save the lists of tokens as cell entries)
df.to_pickle("dataset_with_tokens.pkl")

# Create Trigrams with Gensim
# Select tokens and subsample
tokenlist = pd.read_pickle("dataset_with_tokens.pkl")[["page", "tokens"]]
tokenlist = tokenlist["tokens"].tolist()

# Make bigram and trigram models
bigram = gensim.models.Phrases(tokenlist, min_count=100, threshold=100)
trigram = gensim.models.Phrases(bigram[tokenlist], threshold=130)

trigram_mod = gensim.models.phrases.Phraser(trigram)
bigram_mod = gensim.models.phrases.Phraser(bigram)

tokenlist = [trigram_mod[bigram_mod[text]] for text in tokenlist]

tokens_trigrams = []
for doc in tokenlist:
    tokenstring = [" ".join([token for token in doc])]
    tokens_trigrams.append(tokenstring)

with open("tokens/tokens_trigrams.csv", "w") as f:
    wr = csv.writer(f)
    wr.writerows(tokens_trigrams)

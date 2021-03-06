import pickle
import pandas as pd
import spacy
import gensim
import csv

################################### Tokenize article texts with spacy

csv_gen = (row for row in open("texts.csv"))
# load spanish language model
nlp = spacy.load('es_core_news_md', disable=["parser", "attribute_ruler", "ner"])
# add stopwords
nlp.Defaults.stop_words |= {"a","y", "o"}
# reload language model to incorporate new stopwords 
nlp = spacy.load('es_core_news_md', disable=["parser", "attribute_ruler", "ner"])

tokenlist = []
# go through rows of article texts
for i, doc in enumerate(nlp.pipe(csv_gen, disable=["parser", "attribute_ruler", "ner"], n_process=4, batch_size = 50)):
    # append lists of lemmatised tokens to tokenlist
    tokenlist.append([token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha])
    if i % 1000 == 0 and i != 0: print(i)
# remove first entry, which is the column title
tokenlist = tokenlist[1:]
# save to pickle
with open(f"tokens/tokens.pkl", "wb") as f:
    pickle.dump(tokenlist, f)

# integrate tokenlist into df, useful for later structural topic model and all subsampling
# load tokenlist
with open("tokens/tokens.pkl", "rb") as f:
    tokenlist = pickle.load(f)

# integrate tokenlist back into dataframe
df = pd.read_csv("dataset_token_ready.csv")
df = df.assign(tokens=tokenlist)

# save dataset as pickle (csv does not work, because it cannot save the lists of tokens as cell entries)
df.to_pickle("dataset_with_tokens.pkl")

######################################## Create Trigrams with Gensim

# select tokens and subsample
tokenlist = pd.read_pickle("dataset_with_tokens.pkl")[["page", "tokens"]]
tokenlist = tokenlist["tokens"].tolist()

# make bigram and trigram mod
bigram = gensim.models.Phrases(tokenlist, min_count = 100, threshold = 100)
trigram = gensim.models.Phrases(bigram[tokenlist], threshold = 130)

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

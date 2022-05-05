import spacy
import pickle 
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

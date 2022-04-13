import spacy
import pickle 
csv_gen = (row for row in open("texts.csv"))
nlp = spacy.load('es_core_news_md', disable=["tok2vec", "tagger", "parser", "attribute_ruler", "ner"])
nlp.Defaults.stop_words |= {"a","y"}
nlp = spacy.load('es_core_news_md', disable=["tok2vec", "tagger", "parser", "attribute_ruler", "ner"])

tokenlist = []
for i, doc in enumerate(nlp.pipe(csv_gen, disable=["tok2vec", "tagger", "parser", "attribute_ruler", "ner"], n_process=4)):
    tokenlist.append([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])
    if i % 10000 == 0 and i != 0: print(i)
# remove first entry, which is the column title
tokenlist = tokenlist[1:]
with open(f"tokens/tokens_with_large.pkl", "wb") as f:
    pickle.dump(tokenlist, f)

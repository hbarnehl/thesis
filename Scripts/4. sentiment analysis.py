import pandas as pd
import re
import pysentimiento
import pickle

# load dataset with preprocessed text
df = pd.read_csv('/home/hennes/thesis/Data/dataset_token_ready.csv')

# define regex to search for mentions of president Ortega
regex = r'([Oo]rtega)|([Nn]uestro [Pp]residente)|[Pp]residente de [Nn]icaragua|([Cc]omandante [Dd]aniel)|[Dd]aniel y [Rr]osario'

# subset articles that contain mentions of president Ortega
df = df.loc[df['text'].str.contains(regex, na = False)].reset_index(drop = True)

# split string of texts into list of sentences
df["sentences"] = df.text.apply(lambda x: x.split("."))

# explode rows so that each row contains one sentence
df = df.explode("sentences", ignore_index = True)

# subset sentences that contain mentions of Ortega
df = df.loc[df["sentences"].str.contains(regex)].reset_index(drop = True)

# drop text column
df.drop("text", axis = 1, inplace = True)

analyzer = pysentimiento.create_analyzer(task="sentiment", lang="es")

df["sentiment"] = df["sentences"].apply(lambda x: analyzer.predict(x).output)

with open("/home/hennes/thesis/Data/dataset_sentiment.pkl", "wb") as f:
    pickle.dump(df, f)

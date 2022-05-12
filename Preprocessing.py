import glob
import pickle
import pandas as pd
import re
import dateparser

df = pd.read_csv("dataset.csv")

### Some preliminary stuff

# unify outlet names
df.loc[df["page"].str.startswith('Canal13'), "page"] = "Canal13"
df.loc[df["page"].str.startswith('100% Noticias'), "page"] = "100% Noticias"
df.loc[df["page"].str.startswith('Confidencial'), "page"] = "Confidencial"
df.loc[df["page"].str.startswith('Radio Corporacion'), "page"] = "Radio Corporacion"
df.loc[df["page"].str.startswith('Canal10'), "page"] = "Canal10"
df.loc[df["page"].str.startswith('Canal14'), "page"] = "Canal14"

# extract canal13 dates 
df.loc[df["page"] == 'Canal13', ["date"]] = df.loc[df["page"] == 'Canal13',
                                                 "url"].str.extract(r'(\d\d\d\d/\d\d/\d\d)').values
# extract canal 6 dates
df.loc[df["page"] == 'Canal6', ["date"]] = df.loc[df["page"] == 'Canal6',

                                                "url"].str.extract(r'(\d\d\d\d/\d\d/\d\d)').values
# extract radio 800 dates
df.loc[df["page"] == 'Radio 800', ["date"]] = df.loc[df["page"] == 'Radio 800',
                                                   "url"].str.extract(r'(\d\d\d\d/\d\d/\d\d)').values

# convert canal10 date to datetime
df10 = df.loc[df["page"] == "Canal10"]
df10.loc[:,'date'] = df10['date'].str.replace('de ', '', regex=True)
df10.loc[:,'date'] = df10['date'].str.replace(r'Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday', '', regex=True)
df10.loc[:,'date'] = pd.to_datetime(df10['date'])
df.loc[df["page"] == "Canal10", 'date'] = df10["date"].to_list()

# convert canal14 date to datetime
# first delete entries where only time of day was extracted
df.loc[df["page"] == "Canal14"] = df.loc[(df["page"] == "Canal14") & (df["date"].str.contains(r"\d{4}", na=False))]
# I am doing that with dateparser, because pandas cannot handle the spanish dates
df14 = df.loc[df["page"] == "Canal14"]
df14.loc[:,'date'] = df14.loc[:,'date'].apply(lambda x: dateparser.parse(x, settings={'STRICT_PARSING': True}))
df.loc[df["page"] == "Canal14", 'date'] = df14["date"].to_list()

# 100 % noticias
df100 = df.loc[df["page"] == "100% Noticias"]
# convert nan in date column to empty string so that dateparser works
df100.fillna({"date":" "}, axis=0, inplace=True)
df100.loc[:,'date'] = df100.loc[:,'date'].apply(lambda x: dateparser.parse(x, settings={'STRICT_PARSING': True}))
df.loc[df["page"] == "100% Noticias", 'date'] = df100["date"].to_list()

# canal2, canal4, confidencial, radio corporacion, radio nicaragua,
# radio primerissima are already in datetime format

# convert the rest to datetime
df.loc[:,"date"] = pd.to_datetime(df["date"])
# create year variable
df["year"] = pd.DatetimeIndex(df.date).year

df.to_csv("dataset1.csv", index = False)

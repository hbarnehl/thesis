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

# load dataset
df = pd.read_csv("dataset1.csv")

# delete duplicate articles
df.drop_duplicates(subset="url", inplace=True, ignore_index=True)

# check for articles that do not have any text in them
print("Number of articles without text per outlet")
print(df[df.text.isna()].groupby('page').size())

# there are quite some articles without text. I randomly selected some of these to verify that
# this is not a mistake in my crawler, but that they just don't have text. Indeed, they are all
# articles that only contain videos. This is reflected by the fact that the outlets in thise list
# are mostly TV and radio stations.

print("\nNumber of articles without text per year")
print(df[df.text.isna()].groupby('year').size())

# Because the models need text to work, I will discard rows without text

df = df.loc[~df.text.isna()].reset_index(drop = True)

# there is also a discrepancy in when the outlets started their work, as can be seen from the following table
print(df.groupby(['year', "page"]).agg({"text":np.size}).reset_index().pivot("page", "year", "text"))

# Because before 2015, only a single government outlet uploaded articles, I will keep only articles published
# from 2015 on

df = df.loc[df["year"]>2014]

# removing boilerplate, news agency sources, hyperlinks etc.

             # newlines, tabs etc.
repl_dict = {r"\t|\n|\r|\xa0":" ",
             # whitespace
             r"\s{2,}":" "}
df.replace({"text":repl_dict, "title":repl_dict}, regex=True, inplace = True)

            # hashtags
repl_dict = {"#": "",
             # source in some articles
            r'Fuente: El 19 Digital|Fuente: TN8':"",
             # all hyperlinks
            r"http\S+":"",
             # canal10 boilerplate
            r"Foto: Shutterstock.*": "",
            r"Foto:.*{.*": "",
            "Noticias de Nicaragua y el Mundo": "",
            r"p(\.\w+\s|\s)\{.*?\}": "",
            r"\{.*?\}": "",
            r"Normal.*X-NONE( /\* Style Definitions \*/ table\.MsoNormalTable)?": "",
             # canal4 boilerplate
            r"Canal 4 Noticias[\s\S]+Canal 4 Nicaragua. Todos los derechos reservados": "",
            r"Comparte[.\s]*?esto:[.\s]*?Tweet[.\s]*?WhatsApp[.\s]*?Telegram": "",
            "LEER TAMBIÉN": "",
            "Leer más:": "",
            "AMPLIACIÓN EN BREVE…": "",
            r"Canal 4 Noticias de Nicaragua.*": "",
             "Periodista en Multinoticias, Canal 4": "",
             # news agency
            "(EFE)":"",
             # source mentioned at end of article
            r"Con información de\:+$": "",
             # copyright stuff
            "© 100% Noticias ¡Con primicias a toda hora!":"",
            "© Getty Images":"",
            r"©\s?[Vv]iva [Nn]icaragua,? (Canal 13 )?(Previous Next)?": "",
            "© AFP":"",
            "© AP":"",
            "© creative commons": "",
            "© El 19 Digital": "",
            "© Consejo de Comunicación y Ciudadanía": "",
            "© Juventud Presidente": "",
            "© Ministerio de Gobernación": "",
             # copyrights for photographers
            r"\w+?\s+?\w+?\s+?©":"",
             # article suggestions
            "Te recomendamos:": "",
            "Quizás te interesa:":"",
            "Lee Aquí:": "",
             # twitter links
            r"pic\.twitter\.com.+?\d{4}": "",
            r"—.+?\(@.+?\).+?\d{4}":"",
             # source information
            r"Con información de:.+$": "",
            # emails
            r"\[email protected\]":""}

df.replace({"text":repl_dict, "title":repl_dict}, regex=True, inplace = True)

# the same goes for articles with very short texts.
# again, due to the focus on videos, some articles in the dataset consist only
# of a single, short sentence. Articles with less than 100-character long texts will
# therefore likewise be deleted.

df = df.loc[df["text"].apply(lambda x: len(str(x)) > 200)].reset_index(drop = True)

df.to_csv("dataset_token_ready.csv", index = False)

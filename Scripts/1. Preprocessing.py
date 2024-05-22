"""
This script preprocesses the dataset. It does the following:
1. Unifies outlet names
2. Extracts dates from URLs
3. Converts dates to datetime format
4. Deletes duplicate articles
5. Deletes articles without text
6. Deletes articles published before 2015
7. Removes boilerplate, news agency sources, hyperlinks, etc.
8. Deletes articles with less than 200 characters
9. Saves the preprocessed dataset
"""

import glob
import pickle
import pandas as pd
import re
import dateparser
import numpy as np

df = pd.read_csv("dataset.csv")

# Unify outlet names
df.loc[df["page"].str.startswith('Canal13'), "page"] = "Canal13"
df.loc[df["page"].str.startswith('100% Noticias'), "page"] = "100% Noticias"
df.loc[df["page"].str.startswith('Confidencial'), "page"] = "Confidencial"
df.loc[df["page"].str.startswith('Radio Corporacion'), "page"] = "Radio Corporacion"
df.loc[df["page"].str.startswith('Canal10'), "page"] = "Canal10"
df.loc[df["page"].str.startswith('Canal14'), "page"] = "Canal14"

# Extract dates from URLs
df.loc[df["page"] == 'Canal13', "date"] = (
    df.loc[df["page"] == 'Canal13', "url"]
    .str.extract(r'(\d\d\d\d/\d\d/\d\d)')
    .values
)
df.loc[df["page"] == 'Canal6', "date"] = (
    df.loc[df["page"] == 'Canal6', "url"]
    .str.extract(r'(\d\d\d\d/\d\d/\d\d)')
    .values
)
df.loc[df["page"] == 'Radio 800', "date"] = (
    df.loc[df["page"] == 'Radio 800', "url"]
    .str.extract(r'(\d\d\d\d/\d\d/\d\d)')
    .values
)

# Convert Canal10 date to datetime
df10 = df.loc[df["page"] == "Canal10"]
df10['date'] = df10['date'].str.replace('de ', '', regex=True)
df10['date'] = df10['date'].str.replace(
    r'Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday', 
    '', 
    regex=True
)
df10['date'] = pd.to_datetime(df10['date'])
df.loc[df["page"] == "Canal10", 'date'] = df10["date"].to_list()

# Convert Canal14 date to datetime
df = df.loc[
    (df["page"] == "Canal14") & 
    (df["date"].str.contains(r"\d{4}", na=False))
]
df14 = df.loc[df["page"] == "Canal14"]
df14['date'] = df14['date'].apply(
    lambda x: dateparser.parse(x, settings={'STRICT_PARSING': True})
)
df.loc[df["page"] == "Canal14", 'date'] = df14["date"].to_list()

# Convert 100% Noticias date to datetime
df100 = df.loc[df["page"] == "100% Noticias"]
df100.fillna({"date": " "}, axis=0, inplace=True)
df100['date'] = df100['date'].apply(
    lambda x: dateparser.parse(x, settings={'STRICT_PARSING': True})
)
df.loc[df["page"] == "100% Noticias", 'date'] = df100["date"].to_list()

# Convert the rest to datetime
df["date"] = pd.to_datetime(df["date"])
# Create year variable
df["year"] = pd.DatetimeIndex(df.date).year

df.to_csv("dataset1.csv", index=False)

# Load dataset
df = pd.read_csv("dataset1.csv")

# Delete duplicate articles
df.drop_duplicates(subset="url", inplace=True, ignore_index=True)

# Check for articles that do not have any text in them
print("Number of articles without text per outlet")
print(df[df.text.isna()].groupby('page').size())

print("\nNumber of articles without text per year")
print(df[df.text.isna()].groupby('year').size())

# Discard rows without text
df = df.loc[~df.text.isna()].reset_index(drop=True)

# Keep only articles published from 2015 on
df = df.loc[df["year"] > 2014]

# Removing boilerplate, news agency sources, hyperlinks, etc.
repl_dict = {
    r"\t|\n|\r|\xa0": " ",
    r"\s{2,}": " ",
    "#": "",
    r'Fuente: El 19 Digital|Fuente: TN8': "",
    r"http\S+": "",
    r"Foto: Shutterstock.*": "",
    r"Foto:.*{.*": "",
    "Noticias de Nicaragua y el Mundo": "",
    r"p(\.\w+\s|\s)\{.*?\}": "",
    r"\{.*?\}": "",
    r"Normal.*X-NONE( /\* Style Definitions \*/ table\.MsoNormalTable)?": "",
    r"Canal 4 Noticias[\s\S]+Canal 4 Nicaragua. Todos los derechos reservados": "",
    r"Comparte[.\s]*?esto:[.\s]*?Tweet[.\s]*?WhatsApp[.\s]*?Telegram": "",
    "LEER TAMBIÉN": "",
    "Leer más:": "",
    "AMPLIACIÓN EN BREVE…": "",
    r"Canal 4 Noticias de Nicaragua.*": "",
    "Periodista en Multinoticias, Canal 4": "",
    "(EFE)": "",
    r"Con información de\:+$": "",
    "© 100% Noticias ¡Con primicias a toda hora!": "",
    "© Getty Images": "",
    r"©\s?[Vv]iva [Nn]icaragua,? (Canal 13 )?(Previous Next)?": "",
    "© AFP": "",
    "© AP": "",
    "© creative commons": "",
    "© El 19 Digital": "",
    "© Consejo de Comunicación y Ciudadanía": "",
    "© Juventud Presidente": "",
    "© Ministerio de Gobernación": "",
    r"\w+?\s+?\w+?\s+?©": "",
    "Te recomendamos:": "",
    "Quizás te interesa:": "",
    "Lee Aquí:": "",
    r"pic\.twitter\.com.+?\d{4}": "",
    r"—.+?\(@.+?\).+?\d{4}": "",
    r"Con información de:.+$": "",
    r"\[email protected\]": ""
}

df.replace({"text": repl_dict, "title": repl_dict},
           regex=True,
           inplace=True)

# Delete articles with less than 200 characters
df = df.loc[df["text"].apply(
    lambda x: len(str(x)) > 200)].reset_index(drop=True)

df.to_csv("dataset_token_ready.csv", index=False)

# save text files separately as csv file
df["text"].to_csv("texts.csv", index = False)
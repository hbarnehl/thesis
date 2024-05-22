import pickle
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import math

# Save location of data
data_folder = "/home/hennes/thesis/Data/"
# Save location of figures
figure_loc = "/home/hennes/thesis/Figures/topics/"

# Create uniform color palette
palette = {
    "Radio Corporacion": "#dd8452",
    "Canal14": "#4c72b0",
    "Canal10": "#da8bc3",
    "regime": "#c44e52",
    "opposition": "#55a868"
}

# Set uniform figure size
sns.set(rc={'figure.figsize': (20, 10)})
# Set seaborn style
sns.set_theme(style='whitegrid', font_scale=1.8)

# ## Preparation of Data for Visualization

# Load data
df = pd.read_csv(data_folder + "topic_prevalences.csv")

# Drop Radio 800
df = df.loc[df["page"] != "Radio 800"]

# Transform date to datetime format
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Keep only data from 2017
df = df.loc[df["date"] > "2016"]

repl_dict = {
    "Canal10": "Canal10",
    'Canal4': "regime",
    'Radio la Primerisima': "regime",
    'Confidencial': "opposition",
    'Canal6': "regime",
    'Canal14': "Canal14",
    '100% Noticias': "opposition",
    'Canal13': "regime",
    'Canal2': "regime",
    'Radio Nicaragua': "regime",
    'Radio Corporacion': "Radio Corporacion"
}

# Create categories
df["position"] = df["page"].replace(repl_dict)

# Create different date periods for aggregation
df["quarter"] = df.date.dt.to_period('Q')
df['quarter'] = df['quarter'].apply(lambda x: x.strftime('%Y-%m'))

df["semiannual"] = df.date.dt.to_period('2Q')
quarts = [
    ["2022Q2", "2022Q1"],
    ["2021Q2", "2021Q1"],
    ["2021Q4", "2021Q3"],
    ["2020Q2", "2020Q1"],
    ["2020Q4", "2020Q3"],
    ["2019Q2", "2019Q1"],
    ["2019Q4", "2019Q3"],
    ["2018Q2", "2018Q1"],
    ["2018Q4", "2018Q3"],
    ["2017Q2", "2017Q1"],
    ["2017Q4", "2017Q3"],
    ["2016Q2", "2016Q1"],
    ["2016Q4", "2016Q3"]
]

for pair in quarts:
    df.loc[df["semiannual"] == pair[0], "semiannual"] = pair[1]

df['semiannual'] = df['semiannual'].apply(lambda x: x.strftime('%Y-%m'))

df["year"] = df.date.dt.to_period('Y')
df['year'] = df['year'].apply(lambda x: x.strftime('%Y'))
df['year_month'] = df['date'].apply(lambda x: x.strftime('%Y-%m'))

df['days'] = df["date"].apply(lambda x: (x.to_pydatetime() - datetime.datetime(2016, 1, 2)).days)

# These are the topics identified as being relevant to regime legitimation
relevant_cols = [
    '1 Corona Cases',
    "11 Business, Public Projects",
    '12 Legal Cases (against opposition)',
    '13 Police, Detentions, Protests',
    "16 Municipalities",
    '17 Elections, Parties',
    '19 Welfare, State-Citizen Interactions',
    '21 Press and Censorship',
    '24 Human Rights, Protests',
    '27 Conflict with OAS'
]

# ## Create Polynomial Plots for Topic Prevalences of Relevant Topics

# Set x-axis ticks
ticks = [730, 912, 1095, 1277, 1460, 1643, 1826, 2008, 2191]
dates = [df.loc[df["days"] == x, "date"].min().to_pydatetime().strftime("%Y-%m") for x in ticks]

# Find days representation for vertical lines
def find_day(date):
    return df.loc[df["date"] == date, "days"].min()

events = [
    [find_day("2018-04-18"), "beginning of\nprotests"],
    [find_day("2020-10-26"), "passing of\ncybercrime law"],
    [find_day("2021-06-20"), "series of journalist\njailings and raids\non newsrooms"],
    [find_day("2018-12-15"), "occupation of\noffices of Confidencial\nand 100% Noticias"],
    [find_day("2019-09-27"), "closure of\nnational newspaper\nEl Nuevo Diario"]
]

# Loop through these topics and create polynomial plots for them
for col in relevant_cols[1:2]:
    data = df
    figure = sns.lmplot(
        data=data, x="days", order=11, y=col, hue="position", palette=palette,
        scatter=False, height=10, aspect=2, legend=False
    )
    # Control x and y limits
    plt.ylim(0, 0.2)
    plt.xlim(700, 2220)

    # Set ticks
    for ax in figure.axes.flat:
        # Set ticks on x axis
        ax.set_xticks(ticks)
        # Label the ticks
        ax.set_xticklabels(dates)

    # Set axis names
    plt.xlabel("Time", fontsize=22)
    plt.ylabel("Topic Prevalence", fontsize=22)
    plt.legend(title="Outlet")

    # Leave some space on top of plot for title
    figure.set(xlabel="Time", ylabel=f"Topic Prevalence")
    plt.suptitle(t=f'Prevalence of {col}', ha="center", y=1.16, size="x-large")

    # Place annotated lines for regime measures
    for x in range(len(events)):
        plt.axvline(events[x][0], ymax=1, linewidth=2, color="black")
        plt.annotate(events[x][1], xy=(events[x][0], 0.205), ha='center', annotation_clip=False)

    # Save plot
    plt.savefig(figure_loc + f'{col}.png', bbox_inches="tight")

# ## Create Independence Score

# ### Create Aggregated df for Visualization

# Set seaborn style
sns.set_theme(style='whitegrid', font_scale=1.5)

# Can change level of aggregation by specifying different replacements for df.date
df = df.loc[df["date"] > "2017-12-31"]
agg_level = "semiannual"
df["date"] = df[agg_level]
df["date"] = pd.to_datetime(df["date"])

if agg_level == "quarter":
    # Uncomment this line if semiannual is chosen. First half of 2018 still not useful for topic independence
    df = df.loc[df["date"] != "2018-03"]

# Drop unneeded columns
df_agg = df.drop(columns=["docnum", "text", "tokens", "days", "quarter", "semiannual", "year", "year_month", "page"])

df_agg = (
    df_agg
    .groupby(["position", "date"])
    .agg("mean")
    .reset_index()
)

# Events to mark on plot
events = [
    [pd.to_datetime("2020-10-26"), "passing of\ncybercrime law"],
    [pd.to_datetime("2021-06-20"), "series of journalist\njailings and raids\non newsrooms"],
    [pd.to_datetime("2018-12-15"), "occupation of\noffices of Confidencial\nand 100% Noticias"],
    [pd.to_datetime("2019-09-27"), "closure of\nnational newspaper\nEl Nuevo Diario"]
]

# ### Independence Scores without Weights or NANs

#################################################
# Create df with total distance between
# regime and opposition for each date

# Create a groupby object based on date and position and calculate the difference between 'regime' and 'opposition'
df_agg_temp = df_agg[df_agg["position"].isin(["regime", "opposition"])].groupby(['date', 'position'])[relevant_cols].sum()

# Calculate the absolute difference between 'regime' and 'opposition' for each date
df_agg_temp = df_agg_temp.unstack().pipe(lambda df: abs(df.xs('regime', axis=1, level=1) - df.xs('opposition', axis=1, level=1)))

# Calculate the total distance for each date
df_distance = df_agg_temp.sum(axis=1).reset_index().rename(columns={0: 'total_distance'})

##################################################
# Choose option for independence score calculation

# "no weights", "NAN", or "weights"
option = "weights"
##################################################

# Create separate wide df for each topic
topic_dfs = {}

for x in relevant_cols:
    dfx = pd.pivot(df_agg, index="date", columns="position", values=x)

    # Merge dfx with df_distance on date
    dfx = dfx.merge(df_distance, on="date", how="left")

    # Calculate independence score for in each df
    dfx["canal10_ind"] = (((abs(dfx["Canal10"] - dfx["regime"]) - abs(dfx["Canal10"] - dfx["opposition"])) / abs(dfx["opposition"] - dfx["regime"])) + 1) / 2
    dfx["canal14_ind"] = (((abs(dfx["Canal14"] - dfx["regime"]) - abs(dfx["Canal14"] - dfx["opposition"])) / abs(dfx["opposition"] - dfx["regime"])) + 1) / 2
    dfx["Radio Corporacion_ind"] = (((abs(dfx["Radio Corporacion"] - dfx["regime"]) - abs(dfx["Radio Corporacion"] - dfx["opposition"])) / abs(dfx["opposition"] - dfx["regime"])) + 1) / 2

    if option == "no weights":
        None
    elif option == "NAN":
        # Make independence scores NA if there is no substantive difference between regime and opposition
        # The idea is that independence can only exist if topic is relevant at the time to regime legitimation
        # E.g. corona did not exist in 2018, so difference in the topic in that year should not factor into the
        # calculation of the independence of an outlet for that year
        dfx["canal10_ind"] = (dfx["canal10_ind"].where(((dfx["regime"] - dfx["opposition"]) ** 2) ** 0.5 > 0.015, np.nan))
        dfx["canal14_ind"] = (dfx["canal14_ind"].where(((dfx["regime"] - dfx["opposition"]) ** 2) ** 0.5 > 0.015, np.nan))
        dfx["Radio Corporacion_ind"] = (dfx["Radio Corporacion_ind"].where(((dfx["regime"] - dfx["opposition"]) ** 2) ** 0.5 > 0.015, np.nan))
    elif option == "weights":
        # Create weight variable, so that a topic's weight reflects its share of the total distance between regime and opposition at time t
        dfx["weight"] = abs(dfx["regime"] - dfx["opposition"]) / dfx["total_distance"]

        # Applying weights to independence scores
        dfx["canal10_ind"] = dfx["canal10_ind"] * dfx["weight"]
        dfx["canal14_ind"] = dfx["canal14_ind"] * dfx["weight"]
        dfx["Radio Corporacion_ind"] = dfx["Radio Corporacion_ind"] * dfx["weight"]

    # Save in dictionary
    topic_dfs.update({x: dfx})

# Put independence scores per topic back into one long-format df

df_ind = df_agg[df_agg["position"].isin(["Canal10", "Canal14", "Radio Corporacion"])][["position", "date"]]

for x in relevant_cols:
    df_ind[x] = pd.melt(
        topic_dfs[x].reset_index(),
        id_vars=['date'],
        value_vars=['canal10_ind', "canal14_ind", "Radio Corporacion_ind"],
        value_name="independence score"
    )["independence score"]

# Bring into long format
df_ind = pd.melt(
    df_ind,
    id_vars=["position", 'date'],
    value_vars=relevant_cols,
    value_name="independence score",
    var_name="topic"
)

# Aggregate per outlet
df_final = df_ind.drop(columns=["topic"]).groupby(["position", "date"]).agg("sum").reset_index()

# df_final.date = df_final["date"].apply(lambda x: (pd.Period.to_timestamp(x) - datetime.datetime(2017, 1, 1)).days)

sns.lineplot(data=df_final, x="date", y="independence score", hue="position", palette=palette, linewidth=3)

# Add event lines and annotations
for x in range(len(events)):
    plt.axvline(events[x][0], ymax=1, linewidth=2, color="black")
    plt.annotate(events[x][1], xy=(events[x][0], 1.03), ha='center', annotation_clip=False)

# Set plot title
plt.title("Agenda Independence Score", fontsize=25, pad=85)
# Rotate x-ticks by 315 degrees
plt.xticks(rotation=315)
# Set x axis limits
plt.xlim(pd.to_datetime("2018-07-01"), pd.to_datetime("2022-04-01"))
# Set y axis limits
plt.ylim(0, 1.01)
# Set axis names
plt.xlabel("Time", fontsize=22)
plt.ylabel("Independence Score", fontsize=22)
plt.legend(title="Outlet")
# Save figure
plt.savefig(figure_loc + f'agenda_{agg_level}.png', bbox_inches="tight")

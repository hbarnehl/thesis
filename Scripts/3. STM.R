######################## Load Libraries

library(tidyverse)
library(stm)
library(tm)
library(stmCorrViz)

######################## Load and Transform Data

# load dataframe with texts
data <- read_csv("Data/dataset_token_ready.csv")

# load tokenized texts and substitute for the text column in dataframe
tokens = read_csv("tokens/tokens_trigrams.csv", col_names = FALSE)
data$tokens <- tokens$X1

# there are some values missing for date, delete those rows
data <- data %>% 
  filter(!is.na(date))

# floor all date values to nearby day
data <- data %>% 
  transform(date = lubridate::floor_date(date, "day")) %>% 
# create days from first article variable
  transform(days = as.numeric(date-min(date))) 

# transform page column to factor
data$page <- as_factor(data$page)

# create regime, neutral, opposition factor column
data <- data %>% 
  transform(position = fct_collapse(page,
                                    regime = c("Canal2", "Canal4", "Radio la Primerisima",
                                               "Canal6", "Canal13", "Radio Nicaragua"),
                                    Radio800 = "Radio 800",
                                    Canal10 = "Canal10",
                                    Canal14 = "Canal14",
                                    RadioCorp = "Radio Corporacion",
                                    opposition = c("Confidencial", "100% Noticias")))

# remove tokens object from memory
remove(tokens)

# select relevant columns for topic model
data <- data %>% 
  select(page, text, tokens, days, date, position, title)

# save processed data
save(data, file = "Data/df_with_tokens_filtered.Rdata")

# remove all objects from memory
remove(list = ls())

######################## Preprocess Data

# load processed data
load("Data/df_with_tokens_filtered.Rdata")

# process data
data <- textProcessor(data$tokens,
                           metadata = data,
                           stem = FALSE,
                           lowercase = FALSE,
                           removenumbers = FALSE,
                           removepunctuation = FALSE,
                           language = "es",
                           removestopwords = TRUE)

# save processed data
save(data, file = "Data/stm_preprocessed_neutral_disag.Rdata")

# remove all objects from memory
remove(list = ls())

######################## Prepare Data for Model Estimation

# load processed data
load("Data/stm_preprocessed_neutral_disag.Rdata")

# prepare data for analysis
out <- prepDocuments(data$documents,
                     data$vocab,
                     data$meta,
                     lower.thresh = 288,
                     upper.thresh = floor(length(data$documents)/2))

docs <- out$documents
vocab <- out$vocab
meta <- out$meta

# save prepared data, remove everything from memory
save(docs, vocab, meta, file = "Data/stm_model_inputs_neutral_disag.Rdata")
remove(list = ls())

######################## Estimate Model

# load prepared data
load("Data/stm_model_inputs_neutral_disag.Rdata")
meta <- meta %>% 
  select(page, days, position)



# run stm
load("Data/stm_model_inputs_neutral_disag.Rdata")
i = 30
meta <- meta %>% 
  select(page, days, position)
PrevFit <- stm(documents = docs, vocab = vocab, K = i,
               prevalence =~ position*s(days),
               content =~ position,
               data = meta,
               emtol = 5e-04, max.em.its = 10)
name = str_c("Models/stm_model_content_interaction_neutral_disag",as.String(i), ".Rdata")
save(PrevFit, file = name)
rm(list = ls(all.names = TRUE))
gc()

# save stm model
save(PrevFit, file = "Models/stm_model_base.Rdata")

remove(list = ls())

######################## Investigate and Visualise Estimated Model ###########

# load prepared data
load("Models/stm_model_content_interaction_neutral_disag30.Rdata")
# load text data
load("Data/df_with_tokens_filtered.Rdata")
# load meta data
load("Data/stm_model_inputs_neutral_disag.Rdata")
remove(docs, vocab)

#################### Inspect topics


# get words associated with topics
# the frexweight needs to be set very high, otherwise the representative words
# end up being those unique to the topic
labelTopics(PrevFit, frexweight = 0.99)

# use sageLabels in case of content covariate
sageLabels(PrevFit)

# get top document associated with topics
thoughts <- findThoughts(PrevFit, texts = meta$title, n = 5, meta=meta)
plotQuote(thoughts$docs$`Topic 6`[[20]], width = 130, text.cex = 0.7, main = "Topic 6")

# give names to topics
topic_names <- c("1 Corona Cases",
                 "2 (Petrol) Prices",
                 '3 Victims (of accidents)',
                 '4 Military and Navy',
                 '5 Foreign Relations',
                 '6 Lottery, Payouts',
                 '7 Producers, Vendors, Products',
                 '8 Tourism',
                 '9 Clean Neighbourhoods, Disease Prevention',
                 '10 Weather',
                 '11 Business, Public Projects',
                 '12 Legal Cases (against opposition)',
                 '13 Police, Detentions, Protests',
                 '14 Vaccines',
                 '15 (National) Economics',
                 '16 Municipalities',
                 '17 Elections, Parties',
                 '18 Volcanos, Explosions',
                 '19 Welfare, State-Citizen Interactions',
                 '20 Hospitals',
                 '21 Press and Censorship',
                 '22 Culture, Fairs',
                 '23 Foreign Affairs',
                 '24 Human Rights, Protests',
                 '25 Traffic Accidents',
                 '26 Family',
                 '27 Conflict with OAS',
                 '28 Education, Universities',
                 '29 Church',
                 '30 Organisations, Announcements') 

# show share of documents belonging to topics with topic names
plot(PrevFit, type = "summary",
     n = 0,
     topic.names = topic_names)

# visualise topic correlation
stmCorrViz(PrevFit, "Figures/corrviz.html", documents_raw=meta$text, documents_matrix=docs,
           title="STM Model", clustering_threshold=FALSE,
           search_options = list(range_min=.05, range_max=5, step=.05),
           labels_number=7, display=TRUE, verbose=FALSE)

##################### Estimation and Visualisation of Metadata Effects

# estimate effects of metadata
prep_no_inter <- estimateEffect(1:30 ~ s(days) + position, PrevFit,
                       meta = meta, uncertainty = "Global")
save(prep_no_inter, file = "Models/estimation_30_content_no_interaction.Rdata")

summary(prep_no_inter, topics = 1)

# estimate interaction effects of position and day
prep_inter <- estimateEffect(1:30 ~ s(days)*position, PrevFit,
                       meta = meta, uncertainty = "Global")
save(prep_inter, file = "Models/estimation_30_content_interaction.Rdata")

summary(prep_inter, topics = 1)

# plot interaction of position and day
load("Models/estimation_30_content_interaction.Rdata")

for (i in seq(length(topic_names))) {
  name <- str_c("Figures/content_interaction_disag_30/positionxtime/", topic_names[[i]], ".png")
  png(file=name, width=900, height=525)
  plot(prep_inter, covariate = "days", model = PrevFit, topics = i,
       method = "continuous", moderator = "position",
       moderator.value = "opposition",
       main = str_c(topic_names[[i]], " topic prevalence over time"),
       xlab = "Time", xaxt = "n", linecol = "blue",
       printlegend = FALSE, ylim = c(0, 0.16), xlim = c(0, 2.18e+08))
  plot(prep_inter, covariate = "days", model = PrevFit, topics = i,
       method = "continuous", moderator = "position",
       moderator.value = "regime",
       xlab = "Time", xaxt = "n",linecol = "red", add = TRUE,
       printlegend = FALSE)
  plot(prep_inter, covariate = "days", model = PrevFit, topics = i,
       method = "continuous", moderator = "position",
       moderator.value = "neutral", 
       xlab = "Time", xaxt = "n",
       linecol = "green", add = TRUE,
       printlegend = FALSE)
  yearseq <- seq(from = min(meta$date),
                 to = max(meta$date),
                 by = "year")
  yearnames <- lubridate::isoyear(yearseq)
  axis(1, at = as.numeric(yearseq) - min(as.numeric(yearseq)), labels = yearnames)
  legend(1.3e+08, 0.15, c("opposition", "regime", "neutral"),
         lwd = 2, col = c("blue", "red", "green"))
  dev.off()
}

############ Show Metadata effects on topic prevalence

# show effect of position variable
for (i in seq(length(topic_names))) {
  name <- str_c("Figures/content_interaction_disag_30/position/", topic_names[[i]], ".png")
  png(file=name, width=900, height=525)
  plot(prep_no_inter, covariate = "position", topics = i, model = PrevFit,
       method = "pointestimate",
       ylim = c(0, 0.16), xlim = c(0, 2.18e+08),
       xlab = "Expected document proportion",
       main = str_c("Prevalence of ", topic_names[[i]]," by regime control"),
       labeltype = "custom",
       custom.labels = c("neutral", "regime", "opposition"))
  dev.off()
}

# show effect of time
for (i in seq(length(topic_names))) {
  name <- str_c("Figures/content_interaction_disag_30/time/", topic_names[[i]], ".png")
  png(file=name, width=900, height=525)
  plot(prep_no_inter, covariate = "days", method = "continuous",
       topics = i, model = PrevFit, printlegend = FALSE,
       ylim = c(0, 0.16), xlim = c(0, 2.18e+08),
       main = str_c("Prevalence of ",  topic_names[[i]], " over time"),
       xaxt = "n", xlab = "Time")
  yearseq <- seq(from = min(meta$date),
                 to = max(meta$date),
                 by = "year")
  yearnames <- lubridate::isoyear(yearseq)
  axis(1, at = as.numeric(yearseq) - min(as.numeric(yearseq)), labels = yearnames)
  dev.off()
}

############ Show Metadata effects on topic content

for (i in seq(length(topic_names))) {
  name <- str_c("Figures/content_interaction_disag_30/content/", topic_names[[i]], ".png")
  png(file=name, width=1200, height=1000)
  plot(PrevFit, topics = i, n = 30,
       type = "perspectives",
       covarlevels = c("regime", "opposition"),
       text.cex = 1.5,
       main = str_c("Content of ",  topic_names[[i]]))
  dev.off()
}

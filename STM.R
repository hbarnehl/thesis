######################## Load Libraries

library(tidyverse)
library(stm)
library(tm)

######################## Load and Transform Data

# load dataframe with texts
data <- read_csv("Data/dataset_token_ready.csv")

# load tokenized texts and substitute for the text column in dataframe
tokens = read_csv("Data/tokens/tokens_trigrams.csv", col_names = FALSE)
data$tokens <- tokens$X1

# there are some values missing for date, delete those rows
data <- data %>% 
  filter(!is.na(date))

# floor all date values to nearby day
data <- data %>% 
  transform(date = lubridate::floor_date(date, "day")) %>% 
# create days from first article variable
  transform(days = date-min(date))

# transform page column to factor
data$page <- as_factor(data$page)

# create regime, neutral, opposition factor column
data <- data %>% 
  transform(position = fct_collapse(page,
                                    regime = c("Canal2", "Canal4", "Radio la Primerisima",
                                               "Canal6", "Canal14", "Canal13", "Radio Nicaragua"),
                                    neutral = c("Radio 800", "Canal10"),
                                    opposition = c("Confidencial", "100% Noticias", "Radio Corporacion")))

# remove tokens object from memory
remove(tokens)

# select relevant columns for topic model
data <- data %>% 
  select(page, text, tokens, days, date, position)

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
                           removestopwords = FALSE)

# save processed data
save(data, file = "Data/stm_preprocessed.Rdata")

# remove all objects from memory
remove(list = ls())

######################## Prepare Data for Model Estimation

# load processed data
load("Data/stm_preprocessed.Rdata")

# prepare data for analysis
out <- prepDocuments(data$documents,
                     data$vocab,
                     data$meta,
                     lower.thresh = 50,
                     upper.thresh = floor(length(data$documents)/2))

docs <- out$documents
vocab <- out$vocab
meta <- out$meta

# save prepared data, remove everything from memory
save(docs, vocab, meta, file = "Data/stm_model_inputs.Rdata")
remove(list = ls())

######################## Estimate Model

# load prepared data
load("Data/stm_model_inputs.Rdata")
meta <- meta %>% 
  select(page, days, position)

# find optimal number of topics
storage <- searchK(documents = docs, vocab = vocab, K = seq.int(10, 15),
                   prevalence =~ position + s(days), data = meta)

# run stm
PrevFit <- stm(documents = docs, vocab = vocab, K = 15,
               prevalence = ~s(days) + position,
               data = meta,
               emtol = 1e-04,
               max.em.its = 30, init.type = "Spectral")

# save stm model
save(PrevFit, file = "Models/stm_model_base.Rdata")

remove(list = ls())

######################## Investigate and Visualise Estimated Model

# load prepared data
load("Models/stm_model_with_content.Rdata")
# load text data
load("Data/df_with_tokens_filtered.Rdata")
# load meta data
load("Data/stm_model_inputs.Rdata")
remove(docs, vocab)


# get words associated with topics
# the frexweight needs to be set very high, otherwise the representative words
# end up being those unique to the topic
labelTopics(PrevFit, frexweight = 0.99)

# use sageLabels in case of content covariate
sageLabels(PrevFit)

# get top document associated with topics
thoughts <- findThoughts(PrevFit, texts = meta$text, n = 1)
plotQuote(thoughts$docs[[1]], width = 100, text.cex = 0.5, main = "Topic 9")

# estimate effects of metadata
prep <- estimateEffect(1:15 ~ s(days) + position, PrevFit,
                       meta = meta, uncertainty = "Global")
summary(prep, topics = 1)

# show share of documents belonging to topics
plot(PrevFit, type = "summary")

############ Show Metadata effects on topic prevalence

# show effect of position variable
plot(prep, covariate = "position", topics = c(9), model = PrevFit,
     method = "pointestimate",
     xlab = "position",
     main = "Effect of regime control on topic")

# show effect of time
plot(prep, covariate = "days", method = "continuous", topics = 1,
     model = PrevFit, printlegend = FALSE, xaxt = "n", xlab = "Time")
yearseq <- seq(from = min(meta$date), to = max(meta$date), by "year")
yearnames <- years(yearseq)
axis(1, at = as.numeric(yearseq) - min(as.numeric(yearseq)), labels = yearseq)

############ Show Metadata effects on topic content

plot(PrevFit, topics = 9, type = "perspectives") ### why do I not need to specify the covariate?
# Because there is only one in the example from the vignette?
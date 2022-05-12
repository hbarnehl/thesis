library(tidyverse)
library(stm)
library(tm)

load("Data/stm_model_inputs.Rdata")
meta <- meta %>%
  select(page, days, position)
searchKobj <- searchK(documents = docs, vocab = vocab, K = c(20,23,25,27,29,30,32,34),
                prevalence =~ position + s(days),
                data = meta,
                emtol = 5e-04, max.em.its = 10)

save(searchKobj, file = "Models/searchK")

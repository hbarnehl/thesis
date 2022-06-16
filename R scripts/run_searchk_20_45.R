library(tidyverse)
library(stm)
library(tm)

load("Data/stm_model_inputs.Rdata")
meta <- meta %>%
  select(page, days, position)
searchKobj <- searchK(documents = docs, vocab = vocab, K = c(10, 12, 14, 16, 18, 20, 22,
                                                             24, 26, 28, 30, 32, 34, 36,
                                                             38, 40),
                prevalence =~ position + s(days),
                data = meta,
                emtol = 5e-04, max.em.its = 10)

save(searchKobj, file = "Models/searchK")

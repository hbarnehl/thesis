library(tidyverse)
library(stm)
library(tm)

for (i in seq(20, 45)) {
  load("Data/stm_model_inputs.Rdata")
  meta <- meta %>% 
    select(page, days, position)
  PrevFit <- stm(documents = docs, vocab = vocab, K = i,
                 prevalence =~ position + s(days),
                 data = meta,
                 emtol = 5e-04, max.em.its = 10)
  name = str_c("Models/stm_model_interaction_",as.String(i), ".Rdata")
  save(PrevFit, file = name)
  rm(list = ls(all.names = TRUE))
  gc()
}

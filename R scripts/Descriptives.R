library(writexl)
library(tidyverse)
library(stm)

# load prepared data
load("Models/stm_model_content_interaction_neutral_disag30.Rdata")
# load text data
load("Data/df_with_tokens_filtered.Rdata")
# load meta data
load("Data/stm_model_inputs_neutral_disag.Rdata")
remove(docs, vocab)

####################### Create top words table

# use sageLabels in case of content covariate
labels <- sageLabels(PrevFit)

score <- tibble(labels$marginal$score)
prob <- tibble(labels$marginal$prob)
frex <- tibble(labels$marginal$frex)
lift <- tibble(labels$marginal$lift)

frex <- paste(frex$`labels$marginal$frex`[,1], frex$`labels$marginal$frex`[,2],
              frex$`labels$marginal$frex`[,3], frex$`labels$marginal$frex`[,4],
              frex$`labels$marginal$frex`[,5], frex$`labels$marginal$frex`[,6],
              frex$`labels$marginal$frex`[,7], sep = ", ")

lift <- paste(lift$`labels$marginal$lift`[,1], lift$`labels$marginal$lift`[,2],
              lift$`labels$marginal$lift`[,3], lift$`labels$marginal$lift`[,4],
              lift$`labels$marginal$lift`[,5], lift$`labels$marginal$lift`[,6],
              lift$`labels$marginal$lift`[,7], sep = ", ")

prob <- paste(prob$`labels$marginal$prob`[,1], prob$`labels$marginal$prob`[,2],
              prob$`labels$marginal$prob`[,3], prob$`labels$marginal$prob`[,4],
              prob$`labels$marginal$prob`[,5], prob$`labels$marginal$prob`[,6],
              prob$`labels$marginal$prob`[,7], sep = ", ")

score <- paste(score$`labels$marginal$score`[,1], score$`labels$marginal$score`[,2],
               score$`labels$marginal$score`[,3], score$`labels$marginal$score`[,4],
               score$`labels$marginal$score`[,5], score$`labels$marginal$score`[,6],
               score$`labels$marginal$score`[,7], sep = ", ")

top_words <- tibble(prob, frex, lift, score)
write_xlsx(top_words,"top_words.xlsx")

###################### Create top documents table

top_docs <- tibble(thoughts$docs$`Topic 1`, thoughts$docs$`Topic 2`, thoughts$docs$`Topic 3`,
       thoughts$docs$`Topic 4`, thoughts$docs$`Topic 5`, thoughts$docs$`Topic 6`,
       thoughts$docs$`Topic 7`, thoughts$docs$`Topic 8`, thoughts$docs$`Topic 9`,
       thoughts$docs$`Topic 10`, thoughts$docs$`Topic 11`, thoughts$docs$`Topic 12`,
       thoughts$docs$`Topic 13`, thoughts$docs$`Topic 14`, thoughts$docs$`Topic 15`,
       thoughts$docs$`Topic 16`, thoughts$docs$`Topic 17`, thoughts$docs$`Topic 18`,
       thoughts$docs$`Topic 19`, thoughts$docs$`Topic 20`, thoughts$docs$`Topic 21`,
       thoughts$docs$`Topic 22`, thoughts$docs$`Topic 23`, thoughts$docs$`Topic 24`,
       thoughts$docs$`Topic 25`, thoughts$docs$`Topic 26`, thoughts$docs$`Topic 27`,
       thoughts$docs$`Topic 28`, thoughts$docs$`Topic 29`, thoughts$docs$`Topic 30`)

top_docs <- top_docs %>% 
  rename('1 Corona Cases' = "thoughts$docs$`Topic 1`",
         '2 Petrol Prices' = "thoughts$docs$`Topic 2`",
         '3 Victims of Accidents and Crime' = "thoughts$docs$`Topic 3`",
         '4 Military and Navy' = "thoughts$docs$`Topic 4`",
         '5 Foreign Relations' ="thoughts$docs$`Topic 5`",
         '6 Lottery, Payouts' ="thoughts$docs$`Topic 6`",
         '7 Producers, Vendors, Products' ="thoughts$docs$`Topic 7`",
         '8 Tourism' ="thoughts$docs$`Topic 8`",
         '9 Clean Neighbourhoods, Disease Prevention' ="thoughts$docs$`Topic 9`",
         '10 Weather' ="thoughts$docs$`Topic 10`",
         '11 Business, Public Projects' ="thoughts$docs$`Topic 11`",
         '12 Legal Cases (against opposition' ="thoughts$docs$`Topic 12`",
         '13 Police, Detentions, Protests' ="thoughts$docs$`Topic 13`",
         '14 Vaccines' ="thoughts$docs$`Topic 14`",
         '15 National Economics' ="thoughts$docs$`Topic 15`",
         '16 Municipalities' ="thoughts$docs$`Topic 16`",
         '17 Elections, Parties' ="thoughts$docs$`Topic 17`",
         '18 Volcanos, Explosions' ="thoughts$docs$`Topic 18`",
         '19 Welfare, State-Citizen Interactions' ="thoughts$docs$`Topic 19`",
         '20 Hospitals' ="thoughts$docs$`Topic 20`",
         '21 Press and Censorship' ="thoughts$docs$`Topic 21`",
         '22 Culture, Fairs' ="thoughts$docs$`Topic 22`",
         '23 Foreign Affairs' ="thoughts$docs$`Topic 23`",
         '24 Human Rights, Protests' ="thoughts$docs$`Topic 24`",
         '25 Traffic Accidents' ="thoughts$docs$`Topic 25`",
         '26 Family' ="thoughts$docs$`Topic 26`",
         '27 Conflict with OAS' ="thoughts$docs$`Topic 27`",
         '28 Education, Universities' ="thoughts$docs$`Topic 28`",
         '29 Church' ="thoughts$docs$`Topic 29`",
         '30 Organisations, Announcements' ="thoughts$docs$`Topic 30`")

top_docs <- top_docs %>% 
  summarise_all(funs(trimws(paste(., collapse = '; '))))

top_docs <- top_docs %>%
  pivot_longer(cols = everything(),
               names_to = "topics",
               values_to = "titles")

write_xlsx(top_docs,"top_docs.xlsx")


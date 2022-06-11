dt <- make.dt(PrevFit, meta = meta)
DT <- as.data.frame(dt)

old_names <- names(DT)[2:31]

DT <- DT %>% 
  rename_at(vars(old_names), ~ topic_names)

write.csv(DT,"topic_prevalences.csv", row.names = FALSE)

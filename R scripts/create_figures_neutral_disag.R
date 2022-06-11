# plot interaction of position and day
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
       moderator.value = "Canal10", 
       xlab = "Time", xaxt = "n",
       linecol = "green", add = TRUE,
       printlegend = FALSE)
  plot(prep_inter, covariate = "days", model = PrevFit, topics = i,
       method = "continuous", moderator = "position",
       moderator.value = "Canal14", 
       xlab = "Time", xaxt = "n",
       linecol = "orange", add = TRUE,
       printlegend = FALSE)
  plot(prep_inter, covariate = "days", model = PrevFit, topics = i,
       method = "continuous", moderator = "position",
       moderator.value = "RadioCorp", 
       xlab = "Time", xaxt = "n",
       linecol = "black", add = TRUE,
       printlegend = FALSE)
  yearseq <- seq(from = min(meta$date),
                 to = max(meta$date),
                 by = "year")
  yearnames <- lubridate::isoyear(yearseq)
  axis(1, at = as.numeric(yearseq) - min(as.numeric(yearseq)), labels = yearnames)
  legend(0, 0.15, c("opposition", "regime", "Canal10", "Canal14","Radio Corporacion"),
         lwd = 2, col = c("blue", "red", "green", "orange", "black"))
  dev.off()
}

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
       custom.labels = c("Canal10", "Canal14","Radio Corporacion", "regime", "opposition"))
  dev.off()
}


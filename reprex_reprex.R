#' ---
#' output:
#'   md_document:
#'     pandoc_args:
#'       - '--from=markdown-implicit_figures'
#'       - '--to=commonmark'
#'       - '--wrap=preserve'
#' ---



#+ reprex-setup, include = FALSE
options(tidyverse.quiet = TRUE)
knitr::opts_chunk$set(collapse = TRUE, comment = "#>", error = TRUE)
knitr::opts_knit$set(upload.fun = knitr::imgur_upload)

#+ reprex-body
library(sf)
tmp <- tempfile()
download.file("http://www.nosdonnees.fr/dataset/a8e47b0d-8d58-44c9-9ebf-400c0f2458c3/resource/b1e544a4-f065-494e-8012-843c6cc63cfc/download/quartiersmarseille.zip", tmp)
unzip(tmp)
test <- read_sf("./contours_quartiers_Marseille.shp")
test$NOM_QUA

test2 <- st_read("./contours_quartiers_Marseille.shp")
test2$NOM_QUA



test3 <- rgdal::readOGR("./contours_quartiers_Marseille.shp")
test3$NOM_QUA

test4 <- foreign::read.dbf("./contours_quartiers_Marseille.dbf")
test4$NOM_QUAR



#' <sup>Created on `r Sys.Date()` by the [reprex package](https://reprex.tidyverse.org) (v`r utils::packageVersion("reprex")`)</sup>

#' <details><summary>Session info</summary>
devtools::session_info()
#' </details>

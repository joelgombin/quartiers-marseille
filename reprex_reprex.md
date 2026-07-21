``` r
library(sf)
#> Linking to GEOS 3.7.0, GDAL 2.2.3, PROJ 5.2.0
tmp <- tempfile()
download.file("http://www.nosdonnees.fr/dataset/a8e47b0d-8d58-44c9-9ebf-400c0f2458c3/resource/b1e544a4-f065-494e-8012-843c6cc63cfc/download/quartiersmarseille.zip", tmp)
unzip(tmp)
test <- read_sf("./contours_quartiers_Marseille.shp")
test$NOM_QUA
#>   [1] "AREN"                "LES GOUDE"           "CARPIAGN"           
#>   [4] "EOURE"               "LA TREILL"           "LES CAMOIN"         
#>   [7] "LES ACCATE"          "SAINT JEAN DU DESER" "PALAM"              
#>  [10] "LES MEDECIN"         "LES MOURET"          "LES RIAU"           
#>  [13] "BELSUNC"             "CHAPITR"             "NOAILLE"            
#>  [16] "OPER"                "SAINT CHARLE"        "THIER"              
#>  [19] "GRANDS CARME"        "HOTEL DE VILL"       "LA JOLIETT"         
#>  [22] "BELLE DE MA"         "SAINT LAZAR"         "SAINT MAURO"        
#>  [25] "LA VILETT"           "LA BLANCARD"         "LES CHARTREU"       
#>  [28] "CHUTES LAVI"         "CINQ AVENUE"         "BAILL"              
#>  [31] "LE CAMA"             "LA CONCEPTIO"        "SAINT PIERR"        
#>  [34] "CASTELLAN"           "LOD"                 "NOTRE DAME DU MON"  
#>  [37] "PALAIS DE JUSTIC"    "PREFECTUR"           "VAUBA"              
#>  [40] "BOMPAR"              "ENDOUM"              "LE PHAR"            
#>  [43] "ROUCAS BLAN"         "SAINT LAMBER"        "SAINT VICTO"        
#>  [46] "BONNEVEIN"           "MONTREDO"            "PERIE"              
#>  [49] "LA PLAG"             "POINTE ROUG"         "LE ROUE"            
#>  [52] "SAINT GINIE"         "SAINTE ANN"          "VIELLE CHAPELL"     
#>  [55] "LES BAUMETTE"        "LE CABO"             "MAZARGUE"           
#>  [58] "LA PANOUS"           "LE REDO"             "SORMIO"             
#>  [61] "SAINTE MARGUERIT"    "VAUFREGE"            "LA CAPELETT"        
#>  [64] "MENPENT"             "PONT DE VIVAU"       "SAINT LOU"          
#>  [67] "SAINT TRON"          "LA TIMON"            "LA BARASS"          
#>  [70] "LA MILLIER"          "LA POMM"             "SAINT MARCE"        
#>  [73] "SAINT MENE"          "LA VALBARELL"        "LA VALENTIN"        
#>  [76] "LES CAILLOL"         "LA FOURRAGER"        "MONTOLIVE"          
#>  [79] "SAINT BARNAB"        "SAINT JULIE"         "LES TROIS LUC"      
#>  [82] "CHATEAU-GOMBER"      "LA CROIX ROUG"       "MALPASS"            
#>  [85] "LES OLIVE"           "LA ROS"              "SAINT JEROM"        
#>  [88] "SAINT JUS"           "SAINT MITR"          "LES ARNAVAU"        
#>  [91] "BON SECOUR"          "LE CANE"             "LE MERLA"           
#>  [94] "SAINT BARTHELEM"     "SAINT JOSEP"         "SAINTE MARTH"       
#>  [97] "LES AYGALADE"        "LES BOREL"           "LA CABUCELL"        
#> [100] "LA CALAD"            "LES CROTTE"          "LA DELORM"          
#> [103] "NOTRE DAME LIMIT"    "SAINT ANTOIN"        "SAINT LOUI"         
#> [106] "VERDURO"             "LA VIST"             "L'ESTAQU"           
#> [109] "SAINT ANDR"          "SAINT HENR"

test2 <- st_read("./contours_quartiers_Marseille.shp")
#> Reading layer `contours_quartiers_Marseille' from data source `/media/Data/Dropbox/quartiers marseille/contours_quartiers_Marseille.shp' using driver `ESRI Shapefile'
#> Simple feature collection with 110 features and 3 fields
#> geometry type:  POLYGON
#> dimension:      XY
#> bbox:           xmin: 884726.5 ymin: 6236283 xmax: 905584.6 ymax: 6257388
#> epsg (SRID):    NA
#> proj4string:    +proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +units=m +no_defs
test2$NOM_QUA
#>   [1] AREN                LES GOUDE           CARPIAGN           
#>   [4] EOURE               LA TREILL           LES CAMOIN         
#>   [7] LES ACCATE          SAINT JEAN DU DESER PALAM              
#>  [10] LES MEDECIN         LES MOURET          LES RIAU           
#>  [13] BELSUNC             CHAPITR             NOAILLE            
#>  [16] OPER                SAINT CHARLE        THIER              
#>  [19] GRANDS CARME        HOTEL DE VILL       LA JOLIETT         
#>  [22] BELLE DE MA         SAINT LAZAR         SAINT MAURO        
#>  [25] LA VILETT           LA BLANCARD         LES CHARTREU       
#>  [28] CHUTES LAVI         CINQ AVENUE         BAILL              
#>  [31] LE CAMA             LA CONCEPTIO        SAINT PIERR        
#>  [34] CASTELLAN           LOD                 NOTRE DAME DU MON  
#>  [37] PALAIS DE JUSTIC    PREFECTUR           VAUBA              
#>  [40] BOMPAR              ENDOUM              LE PHAR            
#>  [43] ROUCAS BLAN         SAINT LAMBER        SAINT VICTO        
#>  [46] BONNEVEIN           MONTREDO            PERIE              
#>  [49] LA PLAG             POINTE ROUG         LE ROUE            
#>  [52] SAINT GINIE         SAINTE ANN          VIELLE CHAPELL     
#>  [55] LES BAUMETTE        LE CABO             MAZARGUE           
#>  [58] LA PANOUS           LE REDO             SORMIO             
#>  [61] SAINTE MARGUERIT    VAUFREGE            LA CAPELETT        
#>  [64] MENPENT             PONT DE VIVAU       SAINT LOU          
#>  [67] SAINT TRON          LA TIMON            LA BARASS          
#>  [70] LA MILLIER          LA POMM             SAINT MARCE        
#>  [73] SAINT MENE          LA VALBARELL        LA VALENTIN        
#>  [76] LES CAILLOL         LA FOURRAGER        MONTOLIVE          
#>  [79] SAINT BARNAB        SAINT JULIE         LES TROIS LUC      
#>  [82] CHATEAU-GOMBER      LA CROIX ROUG       MALPASS            
#>  [85] LES OLIVE           LA ROS              SAINT JEROM        
#>  [88] SAINT JUS           SAINT MITR          LES ARNAVAU        
#>  [91] BON SECOUR          LE CANE             LE MERLA           
#>  [94] SAINT BARTHELEM     SAINT JOSEP         SAINTE MARTH       
#>  [97] LES AYGALADE        LES BOREL           LA CABUCELL        
#> [100] LA CALAD            LES CROTTE          LA DELORM          
#> [103] NOTRE DAME LIMIT    SAINT ANTOIN        SAINT LOUI         
#> [106] VERDURO             LA VIST             L'ESTAQU           
#> [109] SAINT ANDR          SAINT HENR         
#> 110 Levels: AREN BAILL BELLE DE MA BELSUNC BOMPAR BON SECOUR ... VIELLE CHAPELL



test3 <- rgdal::readOGR("./contours_quartiers_Marseille.shp")
#> OGR data source with driver: ESRI Shapefile 
#> Source: "/media/Data/Dropbox/quartiers marseille/contours_quartiers_Marseille.shp", layer: "contours_quartiers_Marseille"
#> with 110 features
#> It has 3 fields
test3$NOM_QUA
#>   [1] AREN                LES GOUDE           CARPIAGN           
#>   [4] EOURE               LA TREILL           LES CAMOIN         
#>   [7] LES ACCATE          SAINT JEAN DU DESER PALAM              
#>  [10] LES MEDECIN         LES MOURET          LES RIAU           
#>  [13] BELSUNC             CHAPITR             NOAILLE            
#>  [16] OPER                SAINT CHARLE        THIER              
#>  [19] GRANDS CARME        HOTEL DE VILL       LA JOLIETT         
#>  [22] BELLE DE MA         SAINT LAZAR         SAINT MAURO        
#>  [25] LA VILETT           LA BLANCARD         LES CHARTREU       
#>  [28] CHUTES LAVI         CINQ AVENUE         BAILL              
#>  [31] LE CAMA             LA CONCEPTIO        SAINT PIERR        
#>  [34] CASTELLAN           LOD                 NOTRE DAME DU MON  
#>  [37] PALAIS DE JUSTIC    PREFECTUR           VAUBA              
#>  [40] BOMPAR              ENDOUM              LE PHAR            
#>  [43] ROUCAS BLAN         SAINT LAMBER        SAINT VICTO        
#>  [46] BONNEVEIN           MONTREDO            PERIE              
#>  [49] LA PLAG             POINTE ROUG         LE ROUE            
#>  [52] SAINT GINIE         SAINTE ANN          VIELLE CHAPELL     
#>  [55] LES BAUMETTE        LE CABO             MAZARGUE           
#>  [58] LA PANOUS           LE REDO             SORMIO             
#>  [61] SAINTE MARGUERIT    VAUFREGE            LA CAPELETT        
#>  [64] MENPENT             PONT DE VIVAU       SAINT LOU          
#>  [67] SAINT TRON          LA TIMON            LA BARASS          
#>  [70] LA MILLIER          LA POMM             SAINT MARCE        
#>  [73] SAINT MENE          LA VALBARELL        LA VALENTIN        
#>  [76] LES CAILLOL         LA FOURRAGER        MONTOLIVE          
#>  [79] SAINT BARNAB        SAINT JULIE         LES TROIS LUC      
#>  [82] CHATEAU-GOMBER      LA CROIX ROUG       MALPASS            
#>  [85] LES OLIVE           LA ROS              SAINT JEROM        
#>  [88] SAINT JUS           SAINT MITR          LES ARNAVAU        
#>  [91] BON SECOUR          LE CANE             LE MERLA           
#>  [94] SAINT BARTHELEM     SAINT JOSEP         SAINTE MARTH       
#>  [97] LES AYGALADE        LES BOREL           LA CABUCELL        
#> [100] LA CALAD            LES CROTTE          LA DELORM          
#> [103] NOTRE DAME LIMIT    SAINT ANTOIN        SAINT LOUI         
#> [106] VERDURO             LA VIST             L'ESTAQU           
#> [109] SAINT ANDR          SAINT HENR         
#> 110 Levels: AREN BAILL BELLE DE MA BELSUNC BOMPAR BON SECOUR ... VIELLE CHAPELL

test4 <- foreign::read.dbf("./contours_quartiers_Marseille.dbf")
test4$NOM_QUAR
#>   [1] ARENC                LES GOUDES           CARPIAGNE           
#>   [4] EOURES               LA TREILLE           LES CAMOINS         
#>   [7] LES ACCATES          SAINT JEAN DU DESERT PALAMA              
#>  [10] LES MEDECINS         LES MOURETS          LES RIAUX           
#>  [13] BELSUNCE             CHAPITRE             NOAILLES            
#>  [16] OPERA                SAINT CHARLES        THIERS              
#>  [19] GRANDS CARMES        HOTEL DE VILLE       LA JOLIETTE         
#>  [22] BELLE DE MAI         SAINT LAZARE         SAINT MAURON        
#>  [25] LA VILETTE           LA BLANCARDE         LES CHARTREUX       
#>  [28] CHUTES LAVIE         CINQ AVENUES         BAILLE              
#>  [31] LE CAMAS             LA CONCEPTION        SAINT PIERRE        
#>  [34] CASTELLANE           LODI                 NOTRE DAME DU MONT  
#>  [37] PALAIS DE JUSTICE    PREFECTURE           VAUBAN              
#>  [40] BOMPARD              ENDOUME              LE PHARO            
#>  [43] ROUCAS BLANC         SAINT LAMBERT        SAINT VICTOR        
#>  [46] BONNEVEINE           MONTREDON            PERIER              
#>  [49] LA PLAGE             POINTE ROUGE         LE ROUET            
#>  [52] SAINT GINIEZ         SAINTE ANNE          VIELLE CHAPELLE     
#>  [55] LES BAUMETTES        LE CABOT             MAZARGUES           
#>  [58] LA PANOUSE           LE REDON             SORMIOU             
#>  [61] SAINTE MARGUERITE    VAUFREGES            LA CAPELETTE        
#>  [64] MENPENTI             PONT DE VIVAUX       SAINT LOUP          
#>  [67] SAINT TRONC          LA TIMONE            LA BARASSE          
#>  [70] LA MILLIERE          LA POMME             SAINT MARCEL        
#>  [73] SAINT MENET          LA VALBARELLE        LA VALENTINE        
#>  [76] LES CAILLOLS         LA FOURRAGERE        MONTOLIVET          
#>  [79] SAINT BARNABE        SAINT JULIEN         LES TROIS LUCS      
#>  [82] CHATEAU-GOMBERT      LA CROIX ROUGE       MALPASSE            
#>  [85] LES OLIVES           LA ROSE              SAINT JEROME        
#>  [88] SAINT JUST           SAINT MITRE          LES ARNAVAUX        
#>  [91] BON SECOURS          LE CANET             LE MERLAN           
#>  [94] SAINT BARTHELEMY     SAINT JOSEPH         SAINTE MARTHE       
#>  [97] LES AYGALADES        LES BORELS           LA CABUCELLE        
#> [100] LA CALADE            LES CROTTES          LA DELORME          
#> [103] NOTRE DAME LIMITE    SAINT ANTOINE        SAINT LOUIS         
#> [106] VERDURON             LA VISTE             L'ESTAQUE           
#> [109] SAINT ANDRE          SAINT HENRI         
#> 110 Levels: ARENC BAILLE BELLE DE MAI BELSUNCE BOMPARD ... VIELLE CHAPELLE
```

<sup>Created on 2019-11-22 by the [reprex package](https://reprex.tidyverse.org) (v0.3.0)</sup>

<details>

<summary>Session info</summary>

``` r
devtools::session_info()
#> ─ Session info ──────────────────────────────────────────────────────────
#>  setting  value                       
#>  version  R version 3.6.1 (2019-07-05)
#>  os       Ubuntu 18.04.3 LTS          
#>  system   x86_64, linux-gnu           
#>  ui       X11                         
#>  language (EN)                        
#>  collate  fr_FR.UTF-8                 
#>  ctype    fr_FR.UTF-8                 
#>  tz       Europe/Paris                
#>  date     2019-11-22                  
#> 
#> ─ Packages ──────────────────────────────────────────────────────────────
#>  package     * version    date       lib source                         
#>  assertthat    0.2.1      2019-03-21 [3] CRAN (R 3.5.3)                 
#>  backports     1.1.5      2019-10-02 [3] CRAN (R 3.6.1)                 
#>  callr         3.3.2      2019-09-22 [3] CRAN (R 3.6.1)                 
#>  class         7.3-15     2019-01-01 [4] CRAN (R 3.5.2)                 
#>  classInt      0.4-1      2019-08-06 [1] CRAN (R 3.6.1)                 
#>  cli           1.1.0      2019-03-19 [3] CRAN (R 3.5.3)                 
#>  crayon        1.3.4      2017-09-16 [3] CRAN (R 3.5.0)                 
#>  DBI           1.0.0      2018-05-02 [1] CRAN (R 3.6.0)                 
#>  desc          1.2.0      2018-05-01 [3] CRAN (R 3.5.0)                 
#>  devtools      2.2.1      2019-09-24 [3] CRAN (R 3.6.1)                 
#>  digest        0.6.22     2019-10-21 [1] CRAN (R 3.6.1)                 
#>  e1071         1.7-2      2019-06-05 [1] CRAN (R 3.6.0)                 
#>  ellipsis      0.3.0      2019-09-20 [1] CRAN (R 3.6.1)                 
#>  evaluate      0.14       2019-05-28 [3] CRAN (R 3.6.0)                 
#>  foreign       0.8-72     2019-08-02 [4] CRAN (R 3.6.1)                 
#>  fs            1.3.1      2019-05-06 [3] CRAN (R 3.6.0)                 
#>  glue          1.3.1.9000 2019-11-14 [1] Github (tidyverse/glue@f8dc26f)
#>  highr         0.8        2019-03-20 [3] CRAN (R 3.5.3)                 
#>  htmltools     0.4.0      2019-10-04 [3] CRAN (R 3.6.1)                 
#>  KernSmooth    2.23-16    2019-10-15 [4] CRAN (R 3.6.1)                 
#>  knitr         1.25       2019-09-18 [3] CRAN (R 3.6.1)                 
#>  lattice       0.20-38    2018-11-04 [4] CRAN (R 3.5.1)                 
#>  magrittr      1.5        2014-11-22 [3] CRAN (R 3.5.0)                 
#>  memoise       1.1.0      2017-04-21 [1] CRAN (R 3.6.0)                 
#>  pillar        1.4.2      2019-06-29 [1] CRAN (R 3.6.0)                 
#>  pkgbuild      1.0.6      2019-10-09 [3] CRAN (R 3.6.1)                 
#>  pkgconfig     2.0.3      2019-09-22 [3] CRAN (R 3.6.1)                 
#>  pkgload       1.0.2      2018-10-29 [3] CRAN (R 3.5.1)                 
#>  prettyunits   1.0.2      2015-07-13 [3] CRAN (R 3.5.0)                 
#>  processx      3.4.1      2019-07-18 [3] CRAN (R 3.6.1)                 
#>  ps            1.3.0      2018-12-21 [3] CRAN (R 3.5.2)                 
#>  R6            2.4.1      2019-11-12 [1] CRAN (R 3.6.1)                 
#>  Rcpp          1.0.2      2019-07-25 [1] CRAN (R 3.6.0)                 
#>  remotes       2.1.0      2019-06-24 [3] CRAN (R 3.6.0)                 
#>  rgdal         1.4-7      2019-10-28 [1] CRAN (R 3.6.1)                 
#>  rlang         0.4.1      2019-10-24 [1] CRAN (R 3.6.1)                 
#>  rmarkdown     1.16       2019-10-01 [1] CRAN (R 3.6.1)                 
#>  rprojroot     1.2        2017-01-16 [3] CRAN (R 3.5.0)                 
#>  sessioninfo   1.1.1      2018-11-05 [3] CRAN (R 3.5.1)                 
#>  sf          * 0.8-0      2019-09-17 [1] CRAN (R 3.6.1)                 
#>  sp            1.3-1      2018-06-05 [1] CRAN (R 3.6.0)                 
#>  stringi       1.4.3      2019-03-12 [3] CRAN (R 3.5.3)                 
#>  stringr       1.4.0      2019-02-10 [3] CRAN (R 3.5.2)                 
#>  testthat      2.2.1      2019-07-25 [1] CRAN (R 3.6.1)                 
#>  tibble        2.1.3      2019-06-06 [1] CRAN (R 3.6.0)                 
#>  units         0.6-5      2019-10-08 [1] CRAN (R 3.6.1)                 
#>  usethis       1.5.1      2019-07-04 [3] CRAN (R 3.6.1)                 
#>  withr         2.1.2      2018-03-15 [3] CRAN (R 3.5.0)                 
#>  xfun          0.10       2019-10-01 [1] CRAN (R 3.6.1)                 
#>  yaml          2.2.0      2018-07-25 [3] CRAN (R 3.5.1)                 
#> 
#> [1] /home/joel/R/x86_64-pc-linux-gnu-library/3.6
#> [2] /usr/local/lib/R/site-library
#> [3] /usr/lib/R/site-library
#> [4] /usr/lib/R/library
```

</details>

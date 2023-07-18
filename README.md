# StreetMapDatabase

This repository contains an accessible and readily analyzable street names database for the US and a large part of Europe, as described in the paper [*Tabulating and Visualizing Street Name Data in the U.S. and Europe*](https://osf.io/4v2bx/) (Carmona-Derqui, D., Gutiérrez-Mora, D. & Oto-Peralías, D.). It also contains the processed files used as the basis for the search apps on the [StNamesLab website](https://en.stnameslab.com/) and the Python code used to process them. The files have been separated into directories according to the search app to which they belong. For more information, see [Carmona-Derqui et al. (2023)](https://osf.io/4v2bx/).

## General info

CRS `EPSG:4326` is used for the geometries of all processed files. `utf-8` encoding is used for all street names processed files, except for the Spain's 2001-2022 street names files which use `latin1` encoding. 

Special characters are handled in a particular way to minimize the loss of information. Most of them are *normalized* to its basic form (i.e. `á` to `a`). When the characters were too important for a language, they were replaced by their [html entity](https://oinam.github.io/entities/) to keep the character and avoid errors. Please, keep this in mind when executing queries to search for street names in certain languages. 

Street names tables are provided in csv files, using `$` as delimiter. For more information, see [Carmona-Derqui et al. (2023)](https://osf.io/4v2bx/) or the Python code provided. The requirements and data sources needed to obtain these tables are shown below.

## Europe

Street names data files from [OpenStreetMap](https://www.openstreetmap.org) are used to get the processed files. The raw data files for each country were downloaded in autum 2022. They can be downloaded from [Geofabrik.de](https://download.geofabrik.de/europe.html). Also, [GISCO's last available comunnes layer](https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/communes#communes16) is needed to assign each street to the comunne where it is localted. All other required files are provided in the repository.
| Source                       | Type        | Link |
|------------------------------|-------------|------|
| OpenStreetMap                | street data | [link](https://download.geofabrik.de/europe.html) |
| European Commission (GISCO)  | comunne data| [link](https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/communes#communes16) |

## North America

The United States is the only North American country currently available in the repository, but other countries will be included soon. Street names data files from [OpenStreetMap](https://www.openstreetmap.org) are used to get the processed files. The raw data files for each state were downloaded in autum 2022. They can be downloaded from [Geofabrik.de](https://download.geofabrik.de/north-america/us.html). Also, the United States Census Bureau [TIGER/Line Shapefiles layer](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2022.html#list-tab-BTALRXTZNDNCPWZV4F) is needed to assign each street to the county where it is localted. All other required files are provided in the repository.
| Source                        | Type        | Link |
|-------------------------------|-------------|------|
| OpenStreetMap                 | street data | [link](https://download.geofabrik.de/north-america/us.html) |
| United States Census Bureau   | county data| [link](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2022.html#list-tab-BTALRXTZNDNCPWZV4F) |  

## Spain

Street names data files from [Instituto Nacional de Estadística](https://www.ine.es/ss/Satellite?L=es_ES&c=Page&cid=1259952026632&p=1259952026632&pagename=ProductosYServicios%2FPYSLayout) are used to get the processed files. The files contain data from 2001 to 2022. Street names data from this source is provided in regional (aka * *provincial* * ) format or in national format. We use regional or national data depending on the availability of the data at the time we processed it. Have a look at the Python code to see which format was used for each year. If you want to replicate the process to get the files, be sure to use the same format for each year or do the corresponding modifications to the code. For years 2001 to 2003, data referred to July 1st, while for the rest to January 1st.
| Source | Type | Link |
|-----------------------------------|-------------|------|
| Instituto Nacional de Estadística | street data | [link](https://www.ine.es/ss/Satellite?L=es_ES&c=Page&cid=1259952026632&p=1259952026632&pagename=ProductosYServicios%2FPYSLayout) |

## How to open the files

The data files containing the streets have been compressed using [Winrar](https://www.win-rar.com) (v. 6.02). To open the files you can use any compatible program. Some files have been uploaded in parts, but can be easily opened using Winrar in the same way as single files: [https://www.win-rar.com/open-rar-file.html?&L=0](https://www.win-rar.com/open-rar-file.html?&L=0).

## Citation
If you use the data provided in this repository or obtanied throught the web search apps on STNAMES LAB, please cite:
Carmona-Derqui, D., Gutiérrez Mora, D., & Oto-Peralías, D. (2023). "Tabulating and Visualizing Street Name Data in the U.S. and Europe". Environment and Planning B: Urban Analytics and City Science, forthcoming.

## Contributing to the StreetNamesDatabase
Researchers and other users interested in expanding the geographic coverage of the StreetNamesDatabase and the associated search apps are encouraged to contact the authors (dotoper@upo.es or memerto@gmail.com) to provide assitance regarding i) the country's language and its special characters, ii) a geographic layer containing the boundaries of towns or other local administrative units, and iii) testing the search app.

We also welcome suggestions by researchers and other users for improving the Database and web search app to expand their capabilities and usefulness for the analysis of street names.

## Acknowledgements
We thank Oliver Wach, Ph.D. Candidate / Research Fellow from School of Business and Economics (Freie Universitaet Berlin), for his help to include Poland in the dataset.

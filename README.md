# StreetMapDatabase

This repository contains an accessible and readily analyzable street names database for North America and a large part of Europe, as described in the paper [*Tabulating and Visualizing Street Name Data in the U.S. and Europe*](https://journals.sagepub.com/doi/abs/10.1177/23998083231190711). It also contains the processed files used as the basis for the search apps on the [StNamesLab website](https://en.stnameslab.com/) and the Python code used to process them. The files have been separated into directories according to the search app to which they belong. For more information, see [Carmona-Derqui et al. (2023)](https://journals.sagepub.com/doi/abs/10.1177/23998083231190711) (open-access version [here](https://osf.io/4v2bx/)).

## General info

CRS `EPSG:4326` is used for the geometries of all processed files. `utf-8` encoding is used for all street names processed files, except for the Spain's 2001-2022 street names files which use `latin1` encoding.

Special characters are handled in a particular way to minimize the loss of information. Most of them are *normalized* to its basic form (i.e. `á` to `a`). When the characters were too important for a language, they were replaced by their [html entity](https://oinam.github.io/entities/) to keep the character and avoid errors. Please, keep this in mind when executing queries to search for street names in certain languages.

Street names tables are provided in csv files, using `$` as delimiter. For more information, see [Carmona-Derqui et al. (2023)](https://osf.io/4v2bx/) or the Python code provided. The requirements and data sources needed to obtain these tables are shown below.

## Europe

Street names data files from [OpenStreetMap](https://www.openstreetmap.org) are used to get the processed files. The raw data files for each country were downloaded in autum 2022 from [Geofabrik.de](https://download.geofabrik.de/europe.html). Also, [GISCO's last available comunnes layer](https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/communes#communes16) is needed to assign each street to the commune where it is localted. All other required files are provided in the repository.
| Source | Type | Link |
|------------------------------|-------------|------|
| OpenStreetMap | street data | [link](https://download.geofabrik.de/europe.html) |
| European Commission (GISCO) | comunne data| [link](https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/communes#communes16) |

## North America

Street names data files from [OpenStreetMap](https://www.openstreetmap.org) are used to get the processed files. The raw data files for the US were downloaded in autum 2022, while for Canada and Mexico in autum 2023, from [Geofabrik.de](https://download.geofabrik.de/north-america/us.html). The table below shows the layers used in each country to assign streets to the administrative territorial division where they are located. All other required files are provided in the repository.

| Country | Source | Type | Link |
| --- | --- | --- | --- |
| Canada | Census Subdivision Boundary File | census division<sup>1</sup> | [link](https://www150.statcan.gc.ca/n1/en/catalogue/92-162-X) |
| Mexico | Marco Geoestadístico, División política municipal | municipality | [link](http://www.conabio.gob.mx/informacion/gis/?vns=gis_root/dipol/mupal/mun22gw) |
| US  | United States Census Bureau | county data<sup>1</sup> | [link](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2022.html#list-tab-BTALRXTZNDNCPWZV4F) |

<sup>1</sup> For Canada and the US we also assign streets to the census subdivision/municipality and to census designated place (if any) where they are located, respectively.

## Spain

Street names data files from [Instituto Nacional de Estadística](https://www.ine.es/ss/Satellite?L=es_ES&c=Page&cid=1259952026632&p=1259952026632&pagename=ProductosYServicios%2FPYSLayout) are used to get the processed files. The files contain data from 2001 to 2022. Street names data from this source is provided in regional (aka * *provincial* * ) format or in national format. We use regional or national data depending on the availability of the data at the time we processed it. Have a look at the Python code to see which format was used for each year. If you want to replicate the process to get the files, be sure to use the same format for each year or do the corresponding modifications to the code. For years 2001 to 2003, data referred to July 1st, while for the rest to January 1st.
| Source | Type | Link |
|-----------------------------------|-------------|------|
| Instituto Nacional de Estadística | street data | [link](https://www.ine.es/ss/Satellite?L=es_ES&c=Page&cid=1259952026632&p=1259952026632&pagename=ProductosYServicios%2FPYSLayout) |

## How to open the files

The data files containing the streets have been compressed using [Winrar](https://www.win-rar.com) (v. 6.02). To open the files you can use any compatible program. Some files have been uploaded in parts, but can be easily opened using Winrar in the same way as single files: [https://www.win-rar.com/open-rar-file.html?&L=0](https://www.win-rar.com/open-rar-file.html?&L=0).

## Citation

If you use the data provided in this repository or obtanied throught the web search apps on STNAMES LAB, please cite:  
Carmona-Derqui, D., Gutiérrez-Mora, D., & Oto-Peralías, D. (2023). Tabulating and visualizing street-name data in the US and Europe. Environment and Planning B: Urban Analytics and City Science, 50(7), 1981-1987. https://doi.org/10.1177/23998083231190711

An open-access version is available at https://osf.io/4v2bx/

## Contributing to the StreetNamesDatabase

Researchers and other users interested in expanding the geographic coverage of the StreetNamesDatabase and the associated search apps are encouraged to contact the authors (dotoper@upo.es or memerto@gmail.com) to provide assitance regarding i) the country's language and its special characters, ii) a geographic layer containing the boundaries of towns or other local administrative units, and iii) testing the search app.

We also welcome suggestions by researchers and other users for improving the Database and web search app to expand their capabilities and usefulness for the analysis of street names.

## Acknowledgements

We thank Oliver Wach, Ph.D. Candidate / Research Fellow from School of Business and Economics (Freie Universitaet Berlin), for his help to include Poland in the dataset.

# StreetMapDatabase

This repository contains the processed files used as the basis for the search apps on the [StNamesLab website](https://en.stnameslab.com/) and the Python code used to process them. The files have been separated into directories according to the search app to which they belong. For more information, see [this publication](https://osf.io/4v2bx/).

## General info

CRS `EPSG:4326` is used for the geometries of all processed files. Encoding `utf-8` is used for all street names, but special characters are handled in a particular way to minimize the loss of information. Most of them are * *normalize* * to its basic form (i.e. `á` to `a`). When the characters were too important for a language, they were replaced by their [html entity](https://oinam.github.io/entities/) to preserve the character and avoid errors. Please, keep this in mind when executing queries to search for street names in certain languages. For more information, see [this publication](https://osf.io/4v2bx/) or the Python code in each case.

The requirements and the source of the data needed to obtain the files for each search app are shown below.

## Spain

Street names data files from [Instituto Nacional de Estadística](https://www.ine.es/ss/Satellite?L=es_ES&c=Page&cid=1259952026632&p=1259952026632&pagename=ProductosYServicios%2FPYSLayout) are used to get the processed files. The files contain data from 2001 to 2022, except for the years 2002 and 2003. Street names data from this source is provided in regional (aka * *provincial* * ) format or in national format. We use regional or national data depending on the availability of the data at the time we processed it. Have a look at the Python code to see which format was used for each year. If you want to replicate the process to get the files, be sure to use the same format for each year or do the corresponding modifications to the code.

| Source                            | Type        | Link |
|-----------------------------------|-------------|------|
| Instituto Nacional de Estadística | street data | [link](https://www.ine.es/ss/Satellite?L=es_ES&c=Page&cid=1259952026632&p=1259952026632&pagename=ProductosYServicios%2FPYSLayout) |


## Europe

Street names data files from [OpenStreetMap](https://www.openstreetmap.org) are used to get the processed files. The raw data files for each country were downloaded in autum 2022. They can be downloaded from [Geofabrik.de](https://download.geofabrik.de/europe.html). Also, [GISCO's last available comunnes layer](https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/communes#communes16) is needed to assign the comunne to each street and remove duplicates. All other required files are provided in the repository.

| Source                       | Type        | Link |
|------------------------------|-------------|------|
| OpenStreetMap                | street data | [link](https://download.geofabrik.de/europe.html) |
| European Commission (GISCO)  | comunne data| [link](https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/communes#communes16) |

## North America

Currently only the United States files are available in the repository, but other countries will be included near in the future. Street names data files from [OpenStreetMap](https://www.openstreetmap.org) are used to get the processed files. The raw data files for each state were downloaded in autum 2022. They can be downloaded from [Geofabrik.de](https://download.geofabrik.de/north-america/us.html). Also, the United States Census Bureau [TIGER/Line Shapefiles layer](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2022.html#list-tab-BTALRXTZNDNCPWZV4F) is needed to assign the county to each street and remove duplicates. All other required files are provided in the repository.

| Source                        | Type        | Link |
|-------------------------------|-------------|------|
| OpenStreetMap                 | street data | [link](https://download.geofabrik.de/north-america/us.html) |
| United States Census Bureau   | county data| [link](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2022.html#list-tab-BTALRXTZNDNCPWZV4F) |

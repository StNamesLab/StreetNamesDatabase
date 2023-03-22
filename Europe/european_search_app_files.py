# -*- coding: unicode -*-
"""
INFO about output files:

    CRS =  EPSG:4326
    Encoding = utf-8
    
"""
# IMPORTS
import os
import re
import geopy # version 2.2.0
import string
import warnings
import pandas as pd # version 1.5.1
import numpy as np # version 1.23.4
import geopandas as gpd #version 0.12.1
from shapely.geometry import Polygon # version 1.8.5.post1
from stopwords import stopwords as sw_lists # requires the stopwords.py file

### SECTION: CONFIG
# folders must exist before running the code
wd = '' # working directory
log = True # if True, all functions will print valuable information to the console

comunnes_filepath = '' # GISCO comunnes file relative path, from working directory
comunnes_vars = ['COMM_ID', 'COMM_NAME', 'geometry', 'CNTR_CODE']

boundaries_filepath = r'europe_limits.geojson' # custom countries boundaries file relative path, from working directory
countries_boundaries_vars = ['geometry', 'CNTR_CODE']

base_crs = 'EPSG:4326' # used for input and output GeoDataframes
aux_crs = 'EPSG:25830' # used to perform some operations that require a projected CRS

rawfiles_root = r'' # path to OSM files folder, from working directory
output_path = r'' # path to write output files, , from working directory
filename = 'gis_osm_roads_free_1.shp' # name of the file containing the streets, from rawfiles_root directories

"""
This character is used as sep to save the processed street names file to csv format
and is also removed from the OSM original street names and comunnes names.
The characters "," and ";" can be used since pandas handles them when saving string 
variables, but other characters are recommended to completely avoid that kind of errors.
"""
output_csv_sep = '$'

### SECTION: INPUTS
# COUNTRIES
countries_to_keep = [
    'ES', # Spain
    'UK', # UK
    'FR', # France
    'PT', # Portugal
    'DE', # Germany
    'IT', # Italy
    'BE', # Belgium
    'AT', # Austria
    'IE', # Ireland
    'CH', # Switzerland
    'NO', # Norway
    'DK', # Denmark
    'SE', # Sweden
    'NL', # Netherlands
    'FI', # Finland
    'PL' # Poland
]

codes_to_names = {
    'ES': "Spain",
    'UK': "UK",
    'FR': "France",
    'PT': "Portugal",
    'DE': "Germany",
    'IT': "Italy",
    'BE': "Belgium",
    'AT': "Austria",
    'IE': "Ireland",
    'CH': "Switzerland",
    'NO': "Norway",
    'DK': "Denmark",
    'SE': "Sweden",
    'NL': "Netherlands",
    'FI': "Finland",
    'PL': "Poland"
}

codes_to_filenames = {
    'ES': "spain",
    'UK': "great-britain",
    'FR': "france",
    'PT': "portugal",
    'DE': "germany",
    'IT': "italy",
    'BE': "belgium",
    'AT': "austria",
    'IE': "ireland-and-northern-ireland",
    'CH': "switzerland",
    'NO': "norway",
    'DK': "denmark",
    'SE': "sweden",
    'NL': "netherlands",
    'FI': "finland",
    'PL': "poland"
}

# SPECIAL CHARACTERS
reverse_char_conversion = {
    'a': ['ª','?','À','Á','Â','Ã','Ä','Å','à','á','â','ã','ä','å','a','a','?','?','a','?'],
    'ae': ['Æ', 'æ'],
    'b': ['?','?'],
    'e': ['?','È','É','Ê','Ë','è','é','ê','ë','E','e','e','e','?','?'],
    # ROMAN NUMERAL ONE, UTF-16 0x2160, MAY INTRODUCE ERRORS WHEN USING CERTAIN ENCODINGS
    'i': ['Í','Î','Ï','ì','í','î','ï','i','i','?','?','?','?'],
    'o': ['º','?','Ò','Ó','Ô','Ö','Ø','ò','ó','ô','õ','ö','ø','o','o','?','?'],
    'oe': ['O','o'],
    'u': ['Ù','Ú','Û','Ü','ù','ú','û','ü','u','u','u','u','u'],
    'c': ['C','c','C','c','?','?'],
    'm':['?', '?',],
    'r': ['R','r','?'],
    's': ['S','s','S','s','S','s','?','?'],
    't': ['t','t','?','?'],
    'w': ['w'],
    'y': ['ý','ÿ','y','?','?','?'],
    'z': ['z','Z','z','Z','z','?','Z'],
    'd': ['d','d'],
    'l': ['l','L','l'],
    'n': ['n','n','?','N'],
    'k': ['?','?','?'],
    'h': ['?','?'],
    'p': ['?','?'],
    'x': ['?', '?'],
    'no': ['?'],
    'ii': ['?'], # ROMAN NUMERAL TWO, UTF-16 0x2161, MAY INTRODUCE ERRORS WHEN USING CERTAIN ENCODINGS
    'iii': ['?'], # ROMAN NUMERAL THREE, UTF-16 0x2162, MAY INTRODUCE ERRORS WHEN USING CERTAIN ENCODINGS
    'iv': ['?'], # ROMAN NUMERAL FOUR, UTF-16 0x2173, MAY INTRODUCE ERRORS WHEN USING CERTAIN ENCODINGS
    'v': ['?'], # ROMAN NUMERAL FIVE, UTF-16 0x2164, MAY INTRODUCE ERRORS WHEN USING CERTAIN ENCODINGS
    ' ': ['\u2009','\u200b', '-','-','?','-','-','"','.','.','\u202f','*', '.', ',', ';', ':', '-', '_', '!', '¡', '¿', '?', '+', "'", '"']
}


reverse_keep_chars = {
    # relevant special characters
    '&ccedil;': ['Ç','ç'],
    '&ntilde;': ['Ñ','ñ'],
    'ss': ['ß','?', '?']
}


country_to_stopwords = {
    # stopwords lists to be used for each country
    'ES': ['spanish', 'catalan', 'galician', 'basque'],
    'UK': ['english'],
    'FR': ['french'],
    'PT': ['portuguese'],
    'DE': ['german'],
    'IT': ['italian'],
    'BE': ['german', 'french', 'dutch'],
    'AT': ['german'],
    'IE': ['english', 'irish'],
    'CH': ['german', 'french', 'italian'],
    'NO': ['norwegian'],
    'DK': ['danish'],
    'SE': ['swedish'],
    'NL': ['dutch'],
    'FI': ['finnish'],
    'PL': ['polish']
}

# REVERSED DICTIONARIES
# DO NOT MODIFY
filenames_to_codes = {v: k for k, v in codes_to_filenames.items()}
char_conversion = {char:k for k, v in reverse_char_conversion.items() for char in v}
keep_chars = {char:k for k, v in reverse_keep_chars.items() for char in v}

# FUNCTIONS
def load_country_osm_layer(code, log=False):
    """
    Loads previously downloaded data from Open Street Map. 
    
    OSM doesn't provide unified layers for all countries, so users have to download
    regional data and concat the layers to get many country layers. This function 
    use the rawfiles_root constant that was defined in the first lines of the code.
    
    This function works with the following folder/subfolder structure:
        
        rawfiles_root\CN-latest-free.shp\
        
    with WD being the working directory, rawfiles_root the constant path defined in 
    the config section and CN being the country name linked to the country code.
    If the function finds the constant filename (by default, "gis_osm_roads_free_1.shp")
    among the content of the folder, it loads the shp file and go on. If the 
    filename is not among the content, the function identify the contents as
    subfolders that contain regional layers and try to read them all to concat
    them to a single layer. In this case, the following structure is used:
        
        rawfiles_root\CN-latest-free.shp\subfolder
        
    for each region to find its filename ("gis_osm_roads_free_1.shp") file.
        
    INPUTS:
        code - String with two chars that must match any of the country codes defined 
            in the INPUTs section of the code.
        log - Boolean. If True, the function prints useful information about the 
            loading process.
    
    RETURN: GeoDataframe with all the data for the specified country code.
    """
    folder = f'{rawfiles_root}\\{codes_to_filenames[code]}-latest-free.shp'
    content = os.listdir(folder)
    
    if log:
        print(f'Country: {codes_to_filenames[code]}')
    
    if filename in content:
    
        if log:
            print(f'Loading {folder}\\{filename} ...', end=' ')
            
        joint_df = gpd.read_file(f'{folder}\\{filename}')
        
        if log:
            print('DONE.')
            
        joint_df = joint_df.loc[~joint_df['name'].isna(), ['name', 'geometry']].copy()
       
    else:
        joint_df = gpd.GeoDataFrame(columns=['name', 'geometry'], geometry='geometry')
        joint_df = joint_df.set_crs(base_crs, allow_override=True)
        
        for subfolder in content:

            if log:
                print(f'Loading {folder}\\{subfolder}\\{filename} ...', end=' ')
                
            tmp_df = gpd.read_file(f'{folder}\\{subfolder}\\{filename}')
            
            if log:
                print(f'DONE.')
                
            tmp_df = tmp_df.loc[~tmp_df['name'].isna(), ['name', 'geometry']]
            tmp_df = tmp_df.set_crs(tmp_df.crs.srs, allow_override=True)
            joint_df = gpd.GeoDataFrame(pd.concat([joint_df, tmp_df], ignore_index=True), crs=tmp_df.crs.srs)
            
    return joint_df
        

def clean_eur_words(word, char_conversion, keep_chars, stopwords):
    """
    Performs the following operations to get a "clean" street name:
        
        1.- Remove parenthesis using regex.
        2.- Turn all characters to lowercase.
        3.- Remove all stopwords.
        4.- "Normalize" special characters.
        5.- Remove any character that's not inside the allowed_chars constant.
        6.- Replace relevant special characters by their html entity.
        7.- Replace all types of empty spaces by a single space.
        
    INPUTS:
        word - String with the name of the street to be cleaned.
        char_conversion - Dict with the special characters to be "normalized".
        keep_chars - Dict with the special characters to be replaced by their html entity.
        stopwords - List of the stopwords to be removed.
    
    RETURN: String, with a clean street name.
    """
    # allowed_chars defines what characters are allowed to be in the word at the end of the function
    allowed_chars = string.ascii_letters + string.digits + string.whitespace + 'çÇñÑß??'
    
    # remove parenthesis
    word = re.sub(r'\([^)]*\)', '', word)
    
    # turn all characters to lowercase
    word = word.lower()
    
    # look for stopwords three times to ensure empty spaces don't "hide" any stopword
    for _ in range(3):
        word = re.sub('|'.join(stopwords), ' ', word)
    
    # normalize special characters
    word = ''.join([char_conversion[c] if c in char_conversion.keys() else c for c in word])
    
    # only allowed chars in the final word
    word = ''.join([c for c in word if c in allowed_chars])
    
    # relevant allowed special characters are replaced by their html entity
    word = ''.join([keep_chars[c] if c in keep_chars.keys() else c for c in word])
    
    # all types of empty spaces are replaced by a single empty space
    word = re.sub(r'\s\s+', ' ', word).strip()
    
    # empty spaces at the end and at the beginning are used to make it easier to identify single words in street names
    return f' {word} '

def remove_duplicates_eur(df, log=False):
    """
    Performs dissolve and explode operations to remove the most part of
    the duplicated streets. The function uses a buffer of 100 meters and the
    street name to identify the duplicates. This function also uses the aux_crs
    and base_crs constants that were defined in the CONFIG section.
    
    INPUTS:
        df - GeoDataframe with the streets.
        log - Boolean. If true, the function prints useful information to the
            console.
            
    RETURN: GeoDataframe after the dissolve and explode operations.
    """
    pre_df = df.copy()    
    
    if log:
        print(f'** REMOVE DUPLICATES **')
        print(f'N?of streets before: {pre_df.shape[0]}')
    
    # Apply buffer
    pre_df = pre_df.to_crs(aux_crs)
    pre_df = gpd.GeoDataFrame(pre_df, geometry=pre_df.buffer(100), crs=pre_df.crs)
    pre_df = pre_df.to_crs(base_crs)
    
    # Apply dissolve
    pre_df = pre_df.dissolve(by='name')
    pre_df['name'] = pre_df.index
    if log:
        print(f'N?of streets after dissolve: {pre_df.shape[0]}')
    
    # Apply explode
    pre_df = pre_df.explode(index_parts=False)
    if log:
        print(f'N?of streets after explode: {pre_df.shape[0]}')
        
    pre_df.reset_index(drop=True, inplace=True)
    
    return pre_df

def get_repr_point_boundary(df, boundaries_df, log=False):
    """
    Gets the representative point of each geometry and removes
    the points that fall outside the country boundary defined by
    boundaries_df GeoDataFrame layer. This function also uses the 
    aux_crs and base_crs constants that were defined in the CONFIG 
    section.
    
    INPUTS:
        df - GeoDataframe containing the streets geometries.
        boundaries_df - GeoDataframe layer containing boundaries for
            all the countries.
        log - Boolean. If True, the function prints useful information
            to the console.
            
    RETURN: GeoDataframe layer containing the representative points
        instead of the previous geometry.
    """
    pre_df = df.copy()
    
    prev_streets_n = pre_df.shape[0]
    
    pre_df = pre_df.to_crs(aux_crs)
    pre_df['geometry'] = pre_df.geometry.representative_point()
    pre_df = pre_df.to_crs(base_crs)
    
    # remove points that fall outside the boundaries of the european countries
    pre_df = gpd.overlay(pre_df, boundaries_df, how='intersection')
    
    if log:
        print(f'** GET REPRESENTATIVE POINT **')
        print(f'{prev_streets_n - pre_df.shape[0]} streets were remove: outside of the boundary.')
        
    missings = sum(pre_df["name"].isna())
    if missings:
        warnings.warn(f'Missing values in street names after overlay with boundaries: {missings}')
    
    return pre_df

def remove_empty_only_digits_names(df, log=False):
    """
    Removes street names that match any of these:
        
        - The name contains only numbers.
        - The name is empty.
        
    INPUTS:
        df - The GeoDataframe with all the street names in a column
                called "name".
                
    RETURN: GeoDataframe without those street names.
    """
    pre_df = df.copy()
        
    only_has_digits = pre_df['name'].apply(lambda x: x.strip().replace(' ', '').isdigit())
    empty_names = pre_df['name'].apply(lambda x: x.strip() == '')
    to_remove = (only_has_digits | empty_names)
    pre_df = pre_df.loc[~to_remove].copy()
    
    return pre_df

def apply_overlay_nearest(df, country_comunnes, log=False):
    """ 
    GISCO comunnes layers has limited accuracy. Since they don't match
    exactly the comunnes boundaries, some streets fall outside those layers
    and a simple overlay seems to be insufficient to assign each street to
    its corresponding comunne. This function performs the following operations
    to fix this issue and checks the results to discard inconsistencies:
        
        1.- Overlay the comunne layer to the representative point of
            each street to assign them a comunne using the intersection
            mode.
        2.- Overlay the comunne layer to the representative point of 
            each street to get all streets that fall outside this layer
            using the difference mode.
        3.- Apply sjoin_nearest to assign a comunne to all the streets
            that doesn't have one.
    
    INPUTS:
        predf - GeoDataframe with all the streets and their representative
            point.
        country_comunnes - GeoDataframe layer with all the comunnes for the
            the country.
        log - Boolean. If True, prints valuable information about the procress
            to the console.
    
    RETURN: GeoDataframe.
        
    """
    pre_df = df.copy()
    
    if log:
        print(f'** APPLY OVERLAY **')
        print(f'Unique names before overlay: {len(pre_df["name"].unique())}')
    
    full_df = gpd.overlay(pre_df, country_comunnes, how='intersection')
    
    # we apply overlay to check if there are streets that don't match any comunne
    # and link them to the nearest comunne with the sjoin_nearest method
    difference = gpd.overlay(pre_df, country_comunnes, how='difference')
    
    # uid is used to identify duplicates created by sjoin_nearest when a point is
    # equidistant to multiple comunnes
    difference['uid'] = difference.index
    
    nearest_n = gpd.sjoin_nearest(difference.to_crs(aux_crs), country_comunnes.to_crs(aux_crs), how='left')
    nearest_n = nearest_n.to_crs(base_crs)
    
    # we keep the first duplicate. We don't know what's the correct one since they are
    # equidistant to the comunnes.
    nearest_n.drop_duplicates(subset='uid', inplace=True)
    
    if sum(nearest_n["COMM_ID"].isna()) > 0:
        warnings.warn('WARNING! One or more streets are not linked to a comunne after sjoin_nearest.')
        
    full_df = gpd.GeoDataFrame(pd.concat([full_df, nearest_n], ignore_index=True), crs=full_df.crs.srs)
        
    # Check if everything went well with overlay and sjoin_nearest
    diff = pre_df.shape[0] - full_df.shape[0]
    if diff:
        warnings.warn(f'WARNING! - The are differences after applying overlay: {diff} streets ({round(diff / pre_df.shape[0], 4) * 100} %).')
    
    if log:
        print(f'N?of streets after overlay: {full_df.shape[0]}')
        
    return full_df

def remove_csv_sep(df, sep, cols_to_check, log=False):
    """
    Replaces sep from every value of the columns cols_to_check
    in the DataFrame df.
    
    INPUTS:
        df - GeoDataFrame containing the columns cols_to_check.
        sep - String with the character to be replaced.
        cols_to_check - String series of the df that needs to
            have sep removed from their values.
            
    RETURN: GeoDataFrame
    """
    pre_df = df.copy()
    
    def remove_sep(word):
        return word.replace(sep, ' ')
    
    if log:
        print('** REMOVE SEPARATOR FROM COLUMNS **')
    
    for col in cols_to_check:
        matches = sum(pre_df[col].apply(lambda x: sep in x))
        if matches:
            if log:
                print(f'Found {matches} names with {sep} in column {col}.')
            pre_df[col] = pre_df[col].apply(remove_sep)

    return pre_df

def transform_coords(df):
    """
    Transforms the column geometry, that contains POINT objects with
    coordinates x and y, to lon (longitude) and lat (latitude) columns.
    
    INPUTS:
        df - GeoDataframe.
        
    RETURN: GeoDataframe.
    """
    pre_df = df.copy()
    
    coords = [[point.x, point.y] for point in pre_df['geometry']]
    pre_df['lon'] = [x[0] for x in coords]
    pre_df['lat'] = [x[1] for x in coords]
    
    return pre_df
    
os.chdir(wd)

## COMUNNES FILES
# comunnes layer to assign a comunne to each street
shp_file = gpd.read_file(f'{os.getcwd()}\\{comunnes_filepath}')
comunnes = shp_file.loc[shp_file['CNTR_CODE'].isin(countries_to_keep), comunnes_vars]

# countries boundaries to remove the streets that fall outside of them
cntr_file = gpd.read_file(f'{os.getcwd()}\\{boundaries_filepath}')
cntr_file = cntr_file.to_crs(base_crs)
countries_boundaries_df = cntr_file.loc[cntr_file['CNTR_CODE'].isin(countries_to_keep), countries_boundaries_vars]

"""
The following code uses the previous functions and inputs to process 
the street names data files from OSM in this order for each country:

    1.- Load the layer cointaining all the streets for the country and
        filter the comunnes layer to get only those associated to it.
    2.- Remove duplicated streets.
    3.- Process the street names.
    4.- Remove street names that are empty or contain only digits.
    5.- Get the representative point for each street.
    6.- Apply overlay and sjoin_nearest to fix some inconsistencies.
    7.- Transform the geometry of each representative point to separate
        values in the columns lon and lat, that stand for longitude
        and latitude.
    
The details for every step can be found at the comments or documentation
of the corresponding function. OSM original street names are included in
the output files among the comunne names, the comunne codes, the geometries
and the processed street names, but the constant output_csv_sep is removed
from comunne names and original OSM street names to avoid errors when saving
the file.
"""
for code in countries_to_keep:
            
    # 1.- Setup and file loading
    country_comunnes = comunnes[comunnes['CNTR_CODE'] == code]
    
    """
    Northern Ireland's streets are included in the Ireland files, but
    we need to process them alongside the streets of the UK, so we filter
    the comunnes to get all the comunnes in both cases and remove the
    streets that don't match the country later in the code.
    """
    if code == 'UK':
        country_muns = gpd.GeoDataFrame(
            pd.concat(
                [
                    country_comunnes, 
                    comunnes[comunnes['CNTR_CODE'] == 'IE'].copy()
                ], 
                ignore_index=True
            ), 
            crs=comunnes.crs.srs
        )
    elif code == 'IE':
        country_muns = gpd.GeoDataFrame(
            pd.concat(
                [
                    country_comunnes, 
                    comunnes[comunnes['CNTR_CODE'] == 'UK'].copy()
                ], 
                ignore_index=True
            ), 
            crs=comunnes.crs.srs
        )
    
    country_comunnes.drop(columns=['CNTR_CODE'], inplace=True)
    
    boundaries_df = countries_boundaries_df[countries_boundaries_df['CNTR_CODE'] == code]
    
    df = load_country_osm_layer(code, log)
    
    ## PROCESSING SECTION
    # 2.- Removing duplicates
    df = remove_duplicates_eur(df, log)
    
    # 3.- Processing the street names
    country_sw = [word for sw_list in country_to_stopwords[code] for word in sw_lists[sw_list]]
    df['osm_name'] = df['name']
    df['name'] = df['name'].apply(lambda x: clean_eur_words(x, char_conversion, keep_chars, country_sw))
    
    # 4.- Removing thoes streets with empty names or "only-digits" names
    df = remove_empty_only_digits_names(df, log)
    
    # 5.- Getting the representative point for each street
    df = get_repr_point_boundary(df[['geometry', 'name', 'osm_name']], boundaries_df, log)
    
    # 6.- Performing overlay and sjoin_nearest
    df = apply_overlay_nearest(df, country_comunnes, log)  
    
    df.rename(columns={'COMM_ID': 'mun_code', 'name': 'st_name', 'COMM_NAME': 'mun_name', 'CNTR_CODE': 'country_code'}, inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # keep only the streets for UK or IE to process Northern Ireland's streets properly
    if code == 'UK':
        df = df[df['country_code'] == 'UK'].copy()
    elif code =='IE':
        df = df[df['country_code'] == 'IE'].copy()
           
    cols_to_remove_sep = ['osm_name', 'mun_name']
    df = remove_csv_sep(df, output_csv_sep, cols_to_remove_sep, log)
    
    # 7.- Transform geometry into latitude and longitude colums (lat, lon)
    df = transform_coords(df)
    
    ## OUTPUT
    df[['osm_name', 'st_name', 'mun_code', 'mun_name', 'lon', 'lat']].to_csv(
        f'{output_path}/stn_{code}.csv', 
        sep=output_csv_sep, encoding="utf-8", 
        index=False
    )
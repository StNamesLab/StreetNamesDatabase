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

counties_filepath = '' # US Census Bureau Tiger/Line counties file, relative path from working directory
counties_vars = ['GEOID', 'NAME', 'geometry']
counties_to_states_filepath = '.\counties_to_states.csv' # merge with this file to get state names, relative path from working directory
output_path = '' # relative path to write output files, from working directory

base_crs = 'EPSG:4326' # used for input and output GeoDataframes
aux_crs = 'EPSG:25830' # used to perform some operations that require a projected CRS

rawfiles_root = '' # absolute path to OSM folder containing the files with the streets
filename = 'gis_osm_roads_free_1.shp' # name of the file containing the streets

"""
This character is used as sep to save the processed street names file to csv format
and is also removed from the OSM original street names, county and state names.
The characters "," and ";" can be used since pandas handles them when saving string 
variables, but other characters are recommended to completely avoid that kind of errors.
"""
output_csv_sep = '$'

### SECTION: INPUTS
# SPECIAL CHARACTERS
reverse_char_conversion = {
    'a': ['ª','ᵃ','À','Á','Â','Ã','Ä','Å','à','á','â','ã','ä','å','ā','ą','ȃ','а','ă','А'],
    'ae': ['Æ', 'æ'],
    'b': ['В','в'],
    'e': ['ᵉ','È','É','Ê','Ë','è','é','ê','ë','Ė','ė','ę','ě','е','ё'],
    # ROMAN NUMERAL ONE, UTF-16 0x2160, MAY INTRODUCE ERRORS WHEN USING CERTAIN ENCODINGS
    'i': ['Í','Î','Ï','ì','í','î','ï','ĩ','ī','Ⅰ','І','і','ї'],
    'o': ['º','ᵒ','Ò','Ó','Ô','Ö','Ø','ò','ó','ô','õ','ö','ø','ō','ő','о','О'],
    'oe': ['Œ','œ'],
    'u': ['Ù','Ú','Û','Ü','ù','ú','û','ü','ŭ','ů','ű','ǜ','ų'],
    'c': ['Ć','ć','Č','č','С','с'],
    'm':['М', 'м',],
    'r': ['Ř','ř','ȓ'],
    's': ['Ś','ś','Ş','ş','Š','š','ș','ṣ'],
    't': ['ť','ŧ','Т','т'],
    'w': ['ŵ'],
    'y': ['ý','ÿ','ŷ','У','у','ў'],
    'z': ['ź','Ż','ż','Ž','ž','ẑ','Ź'],
    'd': ['ď','đ'],
    'l': ['ľ','Ł','ł'],
    'n': ['ń','ň','ŋ','Ń'],
    'k': ['Ḱ','К','к'],
    'h': ['Н','н'],
    'p': ['Р','р'],
    'x': ['Х', 'х'],
    'no': ['№'],
    'ii': ['Ⅱ'], # ROMAN NUMERAL TWO, UTF-16 0x2161, MAY INTRODUCE ERRORS WHEN USING CERTAIN ENCODINGS
    'iii': ['Ⅲ'], # ROMAN NUMERAL THREE, UTF-16 0x2162, MAY INTRODUCE ERRORS WHEN USING CERTAIN ENCODINGS
    'iv': ['Ⅳ'], # ROMAN NUMERAL FOUR, UTF-16 0x2173, MAY INTRODUCE ERRORS WHEN USING CERTAIN ENCODINGS
    'v': ['Ⅴ'], # ROMAN NUMERAL FIVE, UTF-16 0x2164, MAY INTRODUCE ERRORS WHEN USING CERTAIN ENCODINGS
    ' ': ['\u2009','\u200b', '‐','‑','‒','–','—','„','•','…','\u202f','*', '.', ',', ';', ':', '-', '_', '!', '¡', '¿', '?', '+', "'", '"']
}


reverse_keep_chars = {
    # relevant special characters
    '&ccedil;': ['Ç','ç'],
    '&ntilde;': ['Ñ','ñ'],
    'ss': ['ß','ẞ', 'ẞ']
}

states_codes_to_names = {
    # state_code : state_name
    '01':'Alabama',
    '02':'Alaska',
    '04':'Arizona',
    '05':'Arkansas',
    '06':'California',
    '08':'Colorado',
    '09':'Connecticut',
    '10':'Delaware',
    '11':'District of Columbia',
    '12':'Florida',
    '13':'Georgia',
    '15':'Hawaii',
    '16':'Idaho',
    '17':'Illinois',
    '18':'Indiana',
    '19':'Iowa',
    '20':'Kansas',
    '21':'Kentucky',
    '22':'Louisiana',
    '23':'Maine',
    '24':'Maryland',
    '25':'Massachusetts',
    '26':'Michigan',
    '27':'Minnesota',
    '28':'Mississippi',
    '29':'Missouri',
    '30':'Montana',
    '31':'Nebraska',
    '32':'Nevada',
    '33':'New Hampshire',
    '34':'New Jersey',
    '35':'New Mexico',
    '36':'New York',
    '37':'North Carolina',
    '38':'North Dakota',
    '39':'Ohio',
    '40':'Oklahoma',
    '41':'Oregon',
    '42':'Pennsylvania',
    '44':'Rhode Island',
    '45':'South Carolina',
    '46':'South Dakota',
    '47':'Tennessee',
    '48':'Texas',
    '49':'Utah',
    '50':'Vermont',
    '51':'Virginia',
    '53':'Washington',
    '54':'West Virginia',
    '55':'Wisconsin',
    '56':'Wyoming',
    '72':'Puerto Rico',
    '78':'Virgin Islands'
}

us_stopwords = sw_lists['english']

# REVERSED DICTIONARIES
# DO NOT MODIFY
char_conversion = {char:k for k, v in reverse_char_conversion.items() for char in v}
keep_chars = {char:k for k, v in reverse_keep_chars.items() for char in v}

# FUNCTIONS
def clean_us_words(word, char_conversion, keep_chars, stopwords):
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
    allowed_chars = string.ascii_letters + string.digits + string.whitespace + 'çÇñÑßẞẞ'
    
    # remove parenthesis
    word = re.sub(r'\([^)]*\)', '', word)
    
    # a special character used for beta is replaced by the standard one
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

def remove_duplicates_us(df, log=False):
    """
    Performs dissolve and explode operations to remove the most part of
    the duplicated streets. The function uses a buffer of 500 meters and the
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
        print(f'Nº of streets before: {pre_df.shape[0]}')
    
    # Apply buffer
    pre_df = pre_df.to_crs(aux_crs)
    pre_df = gpd.GeoDataFrame(pre_df, geometry=pre_df.buffer(500), crs=pre_df.crs)
    pre_df = pre_df.to_crs(base_crs)
    
    # Apply dissolve
    pre_df = pre_df.dissolve(by='name')
    pre_df['name'] = pre_df.index
    if log:
        print(f'Nº of streets after dissolve: {pre_df.shape[0]}')
    
    # Apply explode
    pre_df = pre_df.explode(index_parts=False)
    if log:
        print(f'Nº of streets after explode: {pre_df.shape[0]}')
        
    pre_df.reset_index(drop=True, inplace=True)
    
    return pre_df

def get_repr_point(df):
    """Gets the representative point of each geometry and removes
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
    
    if log:
        print("** REMOVE EMPTY AND 'ONLY-NUMBERS' STREET NAMES **")
        previous_n = pre_df.shape[0]
        
    only_has_digits = pre_df['name'].apply(lambda x: x.strip().replace(' ', '').isdigit())
    empty_names = pre_df['name'].apply(lambda x: x.strip() == '')
    to_remove = (only_has_digits | empty_names)
    pre_df = pre_df.loc[~to_remove].copy()
    
    if log:
        print(f"{previous_n - pre_df.shape[0]} streets were removed: empty or only-digits name.")
    
    return pre_df

def apply_overlay_nearest(df, counties_layer, log=False):
    """ 
    Assigns the corresponding county to each street.
        
        1.- Overlay the counties layer to the representative point of
            each street to assign them a county using the intersection
            mode.
        2.- Overlay the counties layer to the representative point of 
            each street to get all streets that fall outside this layer
            using the difference mode.
        3.- Apply sjoin_nearest to assign a county to all the streets
            that doesn't have one.
    
    INPUTS:
        predf - GeoDataframe with all the streets and their representative
            point.
        counties_layer - GeoDataframe layer with all the counties.
        log - Boolean. If True, prints valuable information about the procress
            to the console.
    
    RETURN: GeoDataframe.
        
    """
    pre_df = df.copy()
    
    if log:
        print(f'** APPLY OVERLAY **')
        print(f'Unique names before overlay: {len(pre_df["name"].unique())}')
    
    full_df = gpd.overlay(pre_df, counties_layer, how='intersection')
    
    # we apply overlay to check if there are streets that don't match any county
    # and link them to the nearest county with the sjoin_nearest method
    difference = gpd.overlay(pre_df, counties_layer, how='difference')
    
    # uid is used to identify duplicates created by sjoin_nearest when a point is
    # equidistant to multiple county
    difference['uid'] = difference.index
    
    nearest_n = gpd.sjoin_nearest(difference.to_crs(aux_crs), counties_layer.to_crs(aux_crs), how='left')
    nearest_n = nearest_n.to_crs(base_crs)
    
    # we keep the first duplicate. We don't know what's the correct one since they are
    # equidistant to the counties.
    nearest_n.drop_duplicates(subset='uid', inplace=True)
    
    if sum(nearest_n["GEOID"].isna()) > 0:
        warnings.warn('¡WARNING! One or more streets are not linked to a county after sjoin_nearest.')
        
    full_df = gpd.GeoDataFrame(pd.concat([full_df, nearest_n], ignore_index=True), crs=full_df.crs.srs)
        
    # Check if everything went well with overlay and sjoin_nearest
    diff = pre_df.shape[0] - full_df.shape[0]
    if diff:
        warnings.warn(f'¡WARNING! - The are differences after applying overlay: {diff} streets ({round(diff / pre_df.shape[0], 4) * 100} %).')
    
    if log:
        print(f'Nº of streets after overlay: {full_df.shape[0]}')
        
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
        log - Boolean. If True, shows how many street names
            containing the sep character were found in cols_to_check.
            
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

def assign_state(df):
    """
    Assigns state code and name to each street based on county_code and
    the states_codes_to_names dict.
    
    INPUTS:
        df - GeoDataframe containing the street data.

    RETURN: GeoDataframe.
    """
    pre_df = df.copy()
    
    pre_df['state_code'] = pre_df['county_code'].apply(lambda x: x[:2])
    pre_df['state_name'] = pre_df['state_code'].apply(lambda x: states_codes_to_names[x])
    
    missings = sum(pre_df['state_name'].isna()) + sum(pre_df['state_code'].isna())
    if missings:
        warnings.warn(f'{missings} missing values have been introduced while running the assign_state function.')
        
    return pre_df
    
os.chdir(wd)

## Counties files
### counties layer to assign a county to each street
shp_file = gpd.read_file(f'.\\{counties_filepath}')
counties = shp_file.loc[:, counties_vars]
counties = counties.to_crs(base_crs)

states_folder = f'{rawfiles_root}\\united-states-latest-free.shp'

states_content = [fold for fold in os.listdir(states_folder)]

all_df = pd.DataFrame(
    columns=[
        'osm_name', 
        'st_name', 
        'county_code', 
        'county_name', 
        'state_code', 
        'state_name', 
        'lon',
        'lat'
    ])

"""
The following code uses the previous functions and inputs to process 
the street names data files from OSM in this order for each country:

    1.- Load the layer cointaining all the streets for the state.
    2.- Remove duplicated streets.
    3.- Process the street names.
    4.- Remove street names that are empty or contain only digits.
    5.- Get the representative point for each street.
    6.- Apply overlay and sjoin_nearest.
    7.- Merge with the counties-to-states dataframe.
    8.- Transform the geometry of each representative point to separate
        values in the columns lon and lat, that stand for longitude
        and latitude.
    
The details for every step can be found at the comments or documentation
of the corresponding function. OSM original street names are included in
the output files among the county names, the county codes, the state names
, the state codes, the geometries and the processed street names, but the 
constant output_csv_sep is removed from county ,state and original 
OSM street names to avoid errors when saving and loading the file.
"""
for state in states_content:
    
    # 1.- SETUP AND FILE LOADING
    state_filepath = f'{states_folder}\\{state}\\{filename}'
    print(f'Loading {state_filepath} ...', end=' ')
    df = gpd.read_file(f'{state_filepath}')
    print('DONE.')

    # PROCESSING SECTION
    # 2.- Removing duplicates
    df = remove_duplicates_us(df, log)
    
    # 3.- Processing the street names
    df['osm_name'] = df['name']
    df['name'] = df['name'].apply(lambda x: clean_us_words(x, char_conversion, keep_chars, us_stopwords))
    
    # 4.- Removing the streets with empty names or "only-digits" names
    df = remove_empty_only_digits_names(df, log)
    
    # 5.- Getting the representative point for each street
    df = get_repr_point(df[['geometry', 'name', 'osm_name']])
    
    # 6.- Performing overlay and sjoin_nearest
    df = apply_overlay_nearest(df, counties, log)  
    
    df.rename(columns={'GEOID': 'county_code', 'name': 'st_name', 'NAME': 'county_name'}, inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    #7.- Get state_code and state_name columns
    df = assign_state(df)
            
    cols_to_remove_sep = ['osm_name', 'county_name', 'state_name']
    df = remove_csv_sep(df, output_csv_sep, cols_to_remove_sep, log)
    
    # 8.- Transform geometry into latitude and longitude colums (lat, lon) 
    df = transform_coords(df)
    
    cols_to_drop = ['geometry', 'uid', 'index_right']
    df.drop(columns=cols_to_drop, inplace=True)

    all_df = pd.concat([all_df, df], ignore_index=True)
    
all_df.to_csv(f'{output_path}/stn_US.csv', sep=output_csv_sep, encoding="utf-8", index=False)

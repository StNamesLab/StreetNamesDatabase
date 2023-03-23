"""
RAW INPUT FILES AND FOLDERS SETUP

This code is intended to work with the following folder/files setup:

    root
        files
            clean_data
            2001
            2004
            2005
            2006
            2007
            2008
            2009
            2010
            2011-2022
            
The folder root contains this code and the files folder.
The folder "files" contains the folders clean_data, 2001, 2004, etc.
The folder clean_data is used to store the output files.
All the other folders inside the "files" folder store streets raw data
for the corresponding year from INE:

https://www.ine.es/ss/Satellite?L=es_ES&c=Page&cid=1259952026632&p=1259952026632&pagename=ProductosYServicios%2FPYSLayout 

All these folders must be created and all the raw data files must be placed
into their corresponding folder before running the code.

INE doesn't follow a common convention for the names of the streets 
raw data files, so the process to load all the data may be complex. If the
import_data function is used, then data for years 2004 to 2010 (including both)
is intended to be in regional (provincial) files (one file per region/province,
per year). Data for the years 2001 and 2011 to 2022 is intended to be in national
files (one single file per year). The names of the data files for years 2011 
to 2022 must match the following pattern:

    VIAS-NAL.F{XX}
    
with {XX} being the last two digits of the year (for example, VIAS-NAL.F22 
if the file contains data of 2022). To simplify the loading process, it is
highly recommended to modify the name of those files to match sush pattern
before running the code.

At the end of the code the dictionary "years_to_attrs" is defined. This
dictionary contains the type of file (prov_nat), preffix (pref) and suffix
(suf) for each year. The information contained in this dictionary must match
the names of the streets raw data files. If prov_nat=="prov", then pref and
suf are used by the import_data function to get the name of the file. But if
prov_nat=="nat", then only the year is used to get the name with the pattern
described above (VIAS-NAL.F{XX}).

"""
# Import libraries
import os
import re
import pandas as pd

# some pandas methods are deprecated so this code throw some warnings
# the following two lines could be used to avoid those warnings, but
# they will also hide all warnings from other packages
#import warnings
#warnings.filterwarnings("ignore")

# THIS SCRIPT CREATES NATIONAL-LEVEL RAW-DATA FILES FOR THE YEARS 2004-2010
root_files = '' # SET ROOT_FILES BEFORE RUNNING THE CODE
output_path = 'clean_data'
csv_separator = '$'

# DEFINITION OF FUNCTIONS TO IMPORT AND CLEAN THE DATASET OF SPANISH STREET NAMES
def import_data(prov_nat,year,pref,suf):
    """
    This function imports the raw data and, when the data are provided in province files, it merges the province files.
    'prov_nat' takes the string values 'prov' and 'nat'.
    'year' has to be some of the following strings:'04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22'.
    'pre' and 'suf' are the (string) characters before and after the province number in the provincial files.
        When using national data, pref and suf are not used and can be filled with any value.
    """
    assert (prov_nat=='prov' or prov_nat=='nat'), 'prov_yes can only take the string values prov and nat'
    if prov_nat=='prov':
        for p in range(1,53):
            p2=str(p)
            if p<10:
                vias=root_files+'/20'+year+'/'+pref+'0'+p2+suf
            else:
                vias=root_files+'/20'+year+'/'+pref+p2+suf
            streets = pd.read_table(vias, encoding='latin_1', header=None )
            if p==1:
                all_streets=streets.copy(deep=True)
            else:
                all_streets=all_streets.append(streets, ignore_index=True)
    else:
        if year=='01':
            vias=root_files+'/2001/VIASG010831'
        else:
            vias=root_files+'/2011-2022/VIAS-NAL.F'+year
        all_streets = pd.read_table(vias, encoding='latin_1', header=None )
    print(year+'-total # streets (raw data):', all_streets.count())
    return all_streets
    

def create_structure(all_streets):
    """
    This function divides the characters into columns (ie., variables),
    add variable names and create and mun_code indicator
    """
    #CREATING VARIABLES/COLUMNS:
    #Extracting substring by position
    CPRO =all_streets[0].str[0:2]
    CMUM =all_streets[0].str[2:5]
    CVIA =all_streets[0].str[5:10]
    TIPOINF =all_streets[0].str[10:11]
    CDEV =all_streets[0].str[11:13]
    FVAR =all_streets[0].str[13:21]
    CVAR =all_streets[0].str[21:22]
    CVIA_var =all_streets[0].str[22:27]
    TVIA =all_streets[0].str[27:32]
    POS =all_streets[0].str[32:33]
    NVIAL =all_streets[0].str[33:83]
    NVIAC =all_streets[0].str[83:108]
    #DATASET CREATED
    dataset=pd.concat([CPRO,CMUM,CVIA,TIPOINF,CDEV,FVAR,CVAR,CVIA_var,TVIA,POS,NVIAL,NVIAC], axis=1)
    dataset.columns=['CPRO','CMUM','CVIA','TIPOINF','CDEV','FVAR','CVAR','CVIA_var','TVIA','POS','NVIAL','NVIAC']
    #CREATING A MUN_CODE VARIABLE:
    dataset['mun_code']=dataset['CPRO']+dataset['CMUM']
    #Output of the fuction
    return dataset
    
def remove_empty_only_digits_names(df):
    """
    Removes street names that match any of these:
        
        - The name contains only numbers.
        - The name is empty.

    """
    pre_df = df.copy()
        
    only_has_digits = pre_df['stname'].apply(lambda x: x.strip().replace(' ', '').isdigit())
    empty_names = pre_df['stname'].apply(lambda x: x.strip() == '')
    to_remove = (only_has_digits | empty_names)
    pre_df = pre_df.loc[~to_remove].copy()
    
    return pre_df

def data_cleaning(final):
    '''
    This function cleans the data:
     1. Preparing variable for text analysis
     2. Removing very short street names (length<=2)
     3. Removing repeated names in the same municipality
     4. Removing columns that I do not need
     *For more details and comments on this, see earlier files in which I import and clean the data.
    '''
    # Remove black spaces before and after the string (this is particularly important here in Python)
    final['NVIAL']=final['NVIAL'].str.strip()
    final['NVIAC']=final['NVIAC'].str.strip()
    # I first create variables measuring the length of the variables NVIAL and NVIAC
    final['len_nvial']=final['NVIAL'].str.len()
    final['len_nviac']=final['NVIAC'].str.len()
    # Conversion into lowercase:
    final['stname']=final['NVIAL'].str.lower()
    #Replacing accent marks
    final['stname'] = final['stname'].str.replace('á','a')
    final['stname'] = final['stname'].str.replace('é', 'e')
    final['stname'] = final['stname'].str.replace('í', 'i')
    final['stname'] = final['stname'].str.replace('ó', 'o')
    final['stname'] = final['stname'].str.replace('ú', 'u')
    final['stname'] = final['stname'].str.replace('à', 'a')
    final['stname'] = final['stname'].str.replace('è', 'e')
    final['stname'] = final['stname'].str.replace('ì', 'i')
    final['stname'] = final['stname'].str.replace('ò', 'o')
    final['stname'] = final['stname'].str.replace('ù', 'u')
    final['stname'] = final['stname'].str.replace('ü', 'u')
    #Remove text between parenthesis
    final['stname']=final['stname'].apply(lambda x: re.sub(r"\(.*\)", "", x))
    #Replacing some characters: (,),-,",
    characters_list=('(',')','/','-','"',',','.',"'",':')
    for c in characters_list:
        final['stname'] = final['stname'].str.replace(c, ' ')
    #Adding blank spaces before and after
    final['stname'] = ' '+final['stname']+' '
    #Replace common stopwords in street names:
    for stopW in [' a ',' al ',' en ',' el ',' la ',' los ',' las ',' de ',' del ',' y ',' desde ',' l ',' els ',' ls ',' les ',' n ',' des ',' ao ',' o ',' do ',' os ',' as ',' e ',' eta ',' d ',' dende ']:
        final['stname'] = final['stname'].str.replace(stopW, ' ')
    #I replace those instances of two or more spaces together
    for spaces in ['      ','     ','    ','   ','  ']:
        final['stname'] = final['stname'].str.replace(spaces, ' ')
    # Removing street names too short (lenght 0, 1 or 2)
    final['stname_len']=final['stname'].str.len()-2 # because of the two spaces added
    # Here I finally remove rows with too short street names (<=2 letters)
    final=final[final['stname_len']>2]
    # REMOVE Duplicates
    # I think that what matters is the combination "tipo de via"-"nombre de via", consequently:
    final.drop_duplicates(subset=['mun_code','TVIA','stname'],inplace=True )
    # DROP COLUMNS that I am not going to use
    final.drop(['CPRO','CMUM','TIPOINF','CDEV','FVAR','CVAR','CVIA_var','POS','NVIAC'], axis=1, inplace=True)
    #Create a variable with the combination mun_code & CVIA
    final['code_munvia']=final['mun_code']+'_'+final['CVIA']
    final.drop_duplicates(subset=['code_munvia'], inplace=True) # I remove duplicates in the unlikely event there are some
    # Remove empty or only-digits street names
    final = remove_empty_only_digits_names(final)
    # This counts the total number of rows (i.e., observations)
    print('total # streets (cleaned data):', len(final.index)) 
    #Return
    return final      


# Very initial settings
os.chdir(root_files)

# INPUTS
years_to_attrs = {
    '01': {'prov_nat': 'nat'},
    '04': {'prov_nat': 'prov', 'pref': 'VIASP'},
    '05': {'prov_nat': 'prov', 'pref': 'VIASP', 'suf': 'G050315'},
    '06': {'prov_nat': 'prov', 'pref': 'viasP', 'suf': 'G060315'},
    '07': {'prov_nat': 'prov', 'pref': 'P', 'suf': '.G070314V'},
    '08': {'prov_nat': 'prov', 'pref': 'VIASP'},
    '09': {'prov_nat': 'prov', 'pref': 'VIAS_P', 'suf': '_G090312'},
    '10': {'prov_nat': 'prov', 'pref': 'P', 'suf': 'VIAS.F091231'},
    '11': {'prov_nat': 'nat'},
    '12': {'prov_nat': 'nat'},
    '13': {'prov_nat': 'nat'},
    '14': {'prov_nat': 'nat'},
    '15': {'prov_nat': 'nat'},
    '16': {'prov_nat': 'nat'},
    '17': {'prov_nat': 'nat'},
    '18': {'prov_nat': 'nat'},
    '19': {'prov_nat': 'nat'},
    '20': {'prov_nat': 'nat'},
    '21': {'prov_nat': 'nat'},
    '22': {'prov_nat': 'nat'}
}

for year, attrs in years_to_attrs.items():
        
    for attr in ['prov_nat', 'pref', 'suf']:
        if attr not in attrs:
            attrs[attr] = ''
            
    prov_nat = attrs['prov_nat']
    pref = attrs['pref']
    suf = attrs['suf']
    all_streets = import_data(prov_nat,year,pref,suf)
    final = create_structure(all_streets)
    final = data_cleaning(final)   
    final.to_csv(root_files + '/' + output_path + '/CALLEJERO' + year+ '.csv', encoding='latin_1', sep=csv_separator, index=False)  

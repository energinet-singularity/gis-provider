from json import dumps
import pandas as pd
import numpy as np
import logging
import os
import re

# Initialize log
log = logging.getLogger(__name__)
# Constants / filepaths
# GIS_FILEPATH = os.path.dirname(__file__) + '/../tests/valid-testdata/GIS_data.xlsx'
GIS_FILEPATH = os.path.dirname(__file__) + '/../real-data/GIS_Driftstr_luftledning_koordinater_decimalgrader_05042022.xls'
MRID_FILEPATH = os.path.dirname(__file__) + '/../real-data/seg_line_mrid_PREPROD.csv'
MRID_EXPECTED_HEADER_NAMES = ['ACLINESEGMENT_MRID', 'LINE_EMSNAME', 'DLR_ENABLED']

def convert_voltage_level_to_letter(voltage_level: int) -> str:
    """Converts voltage level to voltage letter representation.

    Parameters
    ----------
    voltage_level : int
        Voltage level in kV.

    Returns
    -------
    str
        Voltage letter.

    Example
    -------
        convert_voltage_level_to_letter(400)
        C
    """
    if voltage_level >= 420:
        voltage_letter = 'B'
    elif 380 <= voltage_level < 420:
        voltage_letter = 'C'
    elif 220 <= voltage_level < 380:
        voltage_letter = 'D'
    elif 110 <= voltage_level < 220:
        voltage_letter = 'E'
    elif 60 <= voltage_level < 110:
        voltage_letter = 'F'
    elif 45 <= voltage_level < 60:
        voltage_letter = 'G'
    elif 30 <= voltage_level < 45:
        voltage_letter = 'H'
    elif 20 <= voltage_level < 30:
        voltage_letter = 'J'
    elif 10 <= voltage_level < 20:
        voltage_letter = 'K'
    elif 6 <= voltage_level < 10:
        voltage_letter = 'L'
    elif 1 <= voltage_level < 6:
        voltage_letter = 'M'
    elif voltage_level < 1:
        voltage_letter = 'N'

    return voltage_letter


def parse_csv_file_to_dataframe(file_path: str, header_index: int = 0) -> pd.DataFrame:
    '''
    Read CSV file and parse it to pandas dataframe.
    Parameters
    ----------
    file_path: str
        Full path of the excel file.
    header_index: int
        Index number for row to be used as header (Default = 0)
    Returns
    -------
        pd.DataFrame
            A dataframe containing the data from csv file.
    '''
    # Trying to read data from CSV file and convert it to a dataframe.
    try:
        dataframe = pd.read_csv(file_path, delimiter=',', on_bad_lines='skip',
                                header=header_index)
        dataframe.drop(dataframe.head(1).index, inplace=True)
        log.info(f'CSV data in "{file_path}" was parsed to dataframe.')
    except Exception as e:
        log.exception(f'Parsing data from: "{file_path}" failed with message: {e}.')
        raise

    return dataframe


def parse_dataframe_columns_to_dictionary(dataframe: pd.DataFrame, dict_key: str, dict_value: str) -> dict:
    '''
    Read two dataframe columns and parse them to a dictonary.
    Parameters
    ----------
    dataframe: pd.DataFrame
        Dataframe to convert.
    dict_key: str
        Column name to be used as key for the dictonary
    dict_value: str
        Column name to be used as value for the dictonary
    Returns
    -------
        dict
            A dictionary with the key/value specified by the user.
    '''

    # Checking the dictonary key and value to ensure that the user input is found in the dataframe.
    if dict_key not in dataframe:
        raise ValueError(f'The column "{dict_key}" does not exist in the dataframe.')

    if dict_value not in dataframe:
        raise ValueError(f'The column "{dict_value}" does not exist in the dataframe.')

    # Converting dataframe into a dictonary using user input to set key and value of the dictonary.
    try:
        dict_set = dataframe.set_index(dict_key).to_dict()[dict_value]
        log.info(f'Dataframe was parsed to a dictonary with key: "{dict_key}" and value: "{dict_value}".')
        log.debug(dumps(dict_set, indent=4, ensure_ascii=False))

    except Exception as e:
        log.exception(f'Creating dictonary from dataframe columns "{dict_key}" and "{dict_value}" failed with message: {e}')
        raise

    return dict_set


def convert_gis_name_to_ets_name(file_path: str) -> list:
    GIS_COLUMN_NAME = 'Name'
    translated_gis_name_list = []
    list_of_names_falling_outside_regex = []

    # Import of GIS data and create a list from the Name column
    gis_name_list = pd.read_excel(io=file_path)[GIS_COLUMN_NAME].tolist()

    # Find unique names from the GIS column 'Name'
    gis_name_list_unique = np.unique(gis_name_list)

    for line in gis_name_list_unique:
        # Regex expression to restructur the gis name from GIS name to ETS name.
        # (?P<STN1>\w{3,4}?) makes a group 'STN1' and input a word between 3-4 chars
        # (?P<volt>\d{3}) makes a group 'volt' and expects a 3 long digit
        # (?P<STN2>\w{3,4}?) makes a group 'STN2' and input should be a word between 3-4 chars
        # (?P<id>\d)? makes a group 'id' and if there is a digit it the end of the name it stores it
        match = re.match('^(?P<STN1>\w{3,4}?)_?(?P<volt>\d{3})_(?P<STN2>\w{3,4}?)(?P<id>\d)?$', line)
        if match:
            # Converting the extracted voltage letter to a number from the function convert_voltage_level_to_letter
            volt = convert_voltage_level_to_letter(int(match.group('volt')))
            # The restructed name matching the syntax of SCADA EMS names
            ets_name = f"{volt}_{match.group('STN1')}-{match.group('STN2')}"
            if match.group('id') is not None:
                ets_name += f'-{match.group("id")}'
            translated_gis_name_list.append(ets_name)
        else:
            list_of_names_falling_outside_regex.append(line)
    log.info('Regex expression have been run on GIS names')
    
    # Sort the list of names
    translated_gis_name_list.sort()
    log.debug(translated_gis_name_list)

    return translated_gis_name_list


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(name)s - %(message)s')
    log.setLevel(logging.INFO)

    # Variable input (consider moving this)
    MRID_KEY_NAME = 'LINE_EMSNAME'
    MRID_VALUE_NAME = 'ACLINESEGMENT_MRID'

    # Parsing data from MRID csv file
    mrid_dataframe = parse_csv_file_to_dataframe(MRID_FILEPATH)

    # Converting MRID dataframe to a dictonary
    mrid_dictonary = parse_dataframe_columns_to_dictionary(mrid_dataframe, MRID_KEY_NAME, MRID_VALUE_NAME)

    gis_to_ets_name = convert_gis_name_to_ets_name(GIS_FILEPATH)

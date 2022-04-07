# Module import
from singupy import conversion
from singupy import api as singuapi
from os import path, environ, stat
from time import sleep, time
from json import dumps
import pandas as pd
import logging
import re

# Initialize log
log = logging.getLogger(__name__)
if environ.get('DEBUG', 'FALSE').upper() == 'FALSE':
    # __main__ will output INFO-level, everything else stays at WARNING
    logging.basicConfig(format="%(levelname)s:%(asctime)s:%(name)s - %(message)s")
    logging.getLogger(__name__).setLevel(logging.INFO)
elif environ['DEBUG'].upper() == 'TRUE':
    # Set EVERYTHING to DEBUG level
    logging.basicConfig(format="%(levelname)s:%(asctime)s:%(name)s - %(message)s", level=logging.DEBUG)
    log.debug('Setting all logs to debug-level')
else:
    raise ValueError(f"'DEBUG' env. variable is '{environ['DEBUG']}', but must be either 'TRUE', 'FALSE' or unset.")

# Input from user
# API variables
API_DB_NAME = environ.get('API_DB_NAME', 'GIS_DATA')
API_PORT = environ.get('API_PORT', '5000')
MOCK_DATA = environ.get('MOCK_DATA', 'False')
# Variables for the data that should be enriched.
GIS_FILENAME = environ.get('GIS_FILENAME', 'GIS_Driftstr_luftledning_koordinater_decimalgrader_05042022.xls')
GIS_SHEET = environ.get('GIS_SHEET', 'GIS_Driftstr_luftledning_koordi')
GIS_COLUMN_NAME = environ.get('GIS_COLUMN_NAME', 'Name')
LINE_NAME_REGEX = environ.get('LINE_NAME_REGEX', r'^(?P<STN1>\w{3,4}?)_?(?P<volt>\d{3})_(?P<STN2>\w{3,4}?)(?P<id>\d)?$')
# ETS mapping environment variables.
ETS_COLUMN_DLR_ENABLED = environ.get('ETS_DLR_ENABLED_COLUMN', 'DLR_ENABLED')
ETS_COLUMN_MRID = environ.get('ETS_MRID_COLUMN', 'ACLINESEGMENT_MRID')
ETS_FILENAME = environ.get('ETS_FILENAME', 'seg_line_mrid_PROD.csv')
ETS_COLUMN_NAME = environ.get('ETS_NAME_COLUMN', 'LINE_EMSNAME')
# Mapping variables to enforce a specific translation.
MAP_COLUMN_GIS_NAME = environ.get('MAP_COLUMN_GIS_NAME', 'GIS Name')
MAP_COLUMN_ETS_NAME = environ.get('MAP_COLUMN_ETS_NAME', 'ETS Name')
MAP_FILENAME = environ.get('MAP_FILENAME', 'Gis_map.xlsx')
MAP_SHEET = environ.get('MAP_SHEET', 'GisMapping')


# Docker folder (all new data is by configuration getting sent to the '/data/' folder)
docker_folder = '/data/'

# Checking to see if the user want to use mock data within the code.
if MOCK_DATA.upper() == 'TRUE':
    docker_folder = '/testdata/'
    log.warning(f'Env. variable "MOCK_DATA" = {MOCK_DATA}. Using test-data for input.')
elif not MOCK_DATA.upper() == 'FALSE':
    raise ValueError(f'"MOCK_DATA" env. variable is set to: "{MOCK_DATA}" but must be either: "True", "False" or unset.')

# Chosen filepaths
MRID_FILEPATH = docker_folder + ETS_FILENAME
GIS_FILEPATH = docker_folder + GIS_FILENAME
MAP_FILEPATH = docker_folder + MAP_FILENAME


def load_mrid_csv_file(file_path: str) -> pd.DataFrame:
    '''
    Read CSV file and parse it to pandas dataframe.

    Parameters
    ----------
    file_path: str
        Full path of the csv file.
    header_index: int
        Index number for row to be used as header (Default = 0)

    Returns
    -------
    pd.DataFrame
        A DataFrames containing the data from csv file.
    '''
    # Read data from CSV to dataframe and drop row with index 0 as it contains only hyphens
    try:
        dataframe = pd.read_csv(file_path, delimiter=',', on_bad_lines='skip', encoding='cp1252')
        dataframe.drop(0, inplace=True)
        log.info(f'CSV data in "{file_path}" was parsed to DataFrame.')
    except Exception as e:
        log.exception(f'Parsing data from: "{file_path}" failed with message: {e}.')
        raise e

    return dataframe


def parse_excel_sheets_to_dataframe(file_path: str, sheets: list, header_index: int = 0) -> dict[str, pd.DataFrame]:
    """Read sheets from excel file and parse them to a dictionary of pandas DataFrames.

    Parameters
    ----------
    file_path : str
        Full path of the excel file.
    sheets : str
        List with names of sheets in excel.
    header_index : int
        Index number for row to be used as header on sheets (Default = 0)

    Returns
    -------
    dict[str, pd.DataFrame]
        A dictionary of DataFrames containing the data from excel sheet.
        The dictionary key will be name of sheet.
    """
    # Try to read data from excel file to dictionary of DataFrames.
    try:
        df_dictionary = pd.read_excel(file_path, sheet_name=sheets, header=header_index)
        log.info(f"Excel data from sheet(s): '{sheets}' in: '{file_path}' was parsed to dataframe dictionary.")
    except Exception as e:
        log.exception(f"Parsing data from sheet(s): '{sheets}' in excel file: '{file_path}' failed with message: '{e}'.")
        raise e

    return df_dictionary


def parse_dataframe_columns_to_dictionary(dataframe: pd.DataFrame, dict_key: str, dict_value: str
                                          ) -> dict[str, tuple[str, int]]:
    '''
    Read two dataframe columns and parse them to a dictionary.

    Parameters
    ----------
    dataframe: pd.DataFrame
        Dataframe to convert.
    dict_key: str
        Column name to be used as key for the dictionary
    dict_value: str
        Column name to be used as value for the dictionary

    Returns
    -------
    dict[str, union(str, int)]
        Extract key-value pair (based on user-input) into a dictionary
    '''

    # Checking the dictionary key and value to ensure that the user input is found in the dataframe.
    for col_name in [dict_key, dict_value]:
        if col_name not in dataframe:
            raise ValueError(f'The column "{col_name}" does not exist in the dataframe.')

    # Extract two columns from the dataframe and create a dictionary from them.
    try:
        dict_set = dataframe.set_index(dict_key)[dict_value].to_dict()
        log.info(f'Dataframe was parsed to a dictionary with key: "{dict_key}" and value: "{dict_value}".')
        log.debug(dumps(dict_set, indent=4, ensure_ascii=False))

    except Exception as e:
        log.exception(f'Creating dictionary from dataframe columns "{dict_key}" and "{dict_value}" failed with message: {e}')
        raise e

    return dict_set


def map_gis_to_ets_line_name(gis_dataframe: pd.DataFrame, gis_column: str, regex: str) -> tuple[dict[str, str], list[str]]:
    '''
    Maps gis line name to expected ETS line name and returns as a dictionary including a list of line
    names that could not be mapped.

    Parameters
    ----------
    gis_dataframe: pd.DataFrame
        Dataframe containing the gis line names.
    column_name: str
        Name of the column containing the gis line names.
    regex: str
        User specified regex expression.

    Returns
    -------
    dict[str, str]
        A dictionary mapping gis line name to expected ETS line name.
    list[str]
        A list of gis line names that could not be mapped with the regex.
    '''

    gis_line_name_to_ets_line_name = {}
    non_translatable = []

    # Checking column constant from the user input to ensure that column is found in the dataframe.
    if gis_column not in gis_dataframe:
        raise ValueError(f'The column "{gis_column}" does not exist in the specified dataframe.')

    # Removing spaces from the names in the gis_names
    gis_dataframe[gis_column] = gis_dataframe[gis_column].str.replace(" ", "")

    # Getting the list of unique names from GIS column
    gis_names = list(gis_dataframe[gis_column].unique())

    for name in gis_names:
        match = re.match(regex, name)
        if match:
            # Converting the extracted voltage number to a letter with the function 'kv_to_letter'
            volt = conversion.kv_to_letter(int(match.group('volt')))
            # Constructing "ets_name" from domain known pattern
            ets_name = f"{volt}_{match.group('STN1')}-{match.group('STN2')}"
            if match.group('id') is not None:
                ets_name += f'_{match.group("id")}'
            gis_line_name_to_ets_line_name[name] = ets_name
        else:
            non_translatable.append(name)
    log.info(f'The specified regex: "{regex}" expression have been run on the input list.')

    # Review the non_translatable and informing the user if there is any names not translated
    if non_translatable:
        log.warning(f'List of names not translated by the function:{non_translatable}')
    else:
        log.info('All names from the GIS dataframe have been translated.')

    return gis_line_name_to_ets_line_name, non_translatable


def enrich_gis_dataframe(gis_dataframe: pd.DataFrame, mrid_dataframe: pd.DataFrame,
                         gis_line_name_to_ets_line_name: dict[str, str], ets_name_to_mrid: dict[str, str],
                         bad_line_names: list[str], gis_column_name: str, new_column_name: str,
                         ets_column_name: str, ets_dlr_enabled_column: str) -> pd.DataFrame:
    '''
    Enriches the gis dataframe with the ETS MRIDs and remove untranslated lines.

    Parameters
    ----------
    gis_dataframe: pd.DataFrame
        Dataframe containing GIS data - the dataframe to enrich.
    mrid_dataframe: pd.DataFrame
        Dataframe containing ETS data
    gis_line_name_to_ets_line_name: dict[str, str]
        Mapping between gis line name and ets line name
    ets_name_to_mrid: dict[str, str]
        Mapping between ets line name and mrid
    bad_line_names: list[str]
        List of gis line names that should be removed from the dataset
        (i.e. lines that could not be translated into ETS line names).
    gis_column_name: str
        Name of the column in gis_dataframe which contains the gis line names.
    new_column_name: str
        Name of the (new) column that should store the ets line names
    ets_name_column: str
        Name of the column in mrid_dataframe that contains the ets names.
    ets_dlr_enabled_column: str
        Name of the column in mrid_dataframe which contains enabled state

    Returns
    -------
    pd.DataFrame
        Clone of gis_dataframe enriched with MRID data, minus non-translated rows.
    '''
    # Checking to see if there are lines in the MRID list with enabled DLR that can not be found in GIS data
    lines_with_dlr_enabled = mrid_dataframe[mrid_dataframe[ets_dlr_enabled_column].str.upper() == "YES"][ets_column_name]
    missing_gis_data = list(set(lines_with_dlr_enabled) - set(gis_line_name_to_ets_line_name.values()))

    if missing_gis_data:
        log.error(f'Some lines set up for DLR have no GIS data available, they are:{missing_gis_data}')
    else:
        log.info('Gis data is found for all lines in the MRID file with DLR enabled.')

    # Generate a dictionary map used to enrich the gis_dataframe with MRID
    gis_name_to_mrid = {k: ets_name_to_mrid.get(v, v) for k, v in gis_line_name_to_ets_line_name.items()}
    gis_dataframe[new_column_name] = gis_dataframe[gis_column_name].map(gis_name_to_mrid)

    # Removing any names that could not be translated to represent a clean dataframe that only contains
    # information that can be looked up with MRID.
    gis_dataframe = gis_dataframe[~gis_dataframe[gis_column_name].isin(bad_line_names)]

    return gis_dataframe


def verify_translated_names_against_ets(translate_gis_name_to_ets: dict[str, str], mrid_dataframe: pd.DataFrame,
                                        ets_column_name: str):
    '''
    The function checks if there are lines in the ETS dataset which is not represented in the GIS dataset.
    This is for logging and to be able to see when introducing a new dataset wether the quality stays the same.

    Parameters
    ----------
    gis_line_name_to_ets_line_name: dict[str, str]
        The dict containing the translated names from GIS.
    mrid_dataframe: pd.DataFrame
        Dataframe with all ETS information in.
    ETS_COLUMN_NAME: str
        The specific column in the MRID dataframe that contains the names of lines.

    Returns
    -------
    None
    '''
    REGEX = r'^[CDE]_'

    # Comparing the converted names from GIS to the list of names in ETS.
    lines_not_in_gis = list(set(mrid_dataframe[ets_column_name]).difference(list(translate_gis_name_to_ets.values())))
    # The result is filtered with a regex expression to omit low voltage levels from ETS.
    missing_lines_in_gis = list(line for line in lines_not_in_gis if re.match(REGEX, line))

    missing_lines_in_gis.sort()
    log.info(f'List of not found lines in GIS data set: {missing_lines_in_gis}')


if __name__ == '__main__':
    # Initialize of variables and API
    gis_time_init = mrid_time_init = 0

    gis_data_api = singuapi.DataFrameAPI(dbname=API_DB_NAME, port=API_PORT)
    log.info(f'Started API on port {gis_data_api.web.port}')

    while True:
        start_time = time()
        if path.isfile(GIS_FILEPATH) and path.isfile(MRID_FILEPATH):
            if stat(GIS_FILEPATH).st_mtime > gis_time_init or stat(MRID_FILEPATH).st_mtime > mrid_time_init:
                if stat(GIS_FILEPATH).st_mtime > gis_time_init:
                    gis_time_init = stat(GIS_FILEPATH).st_mtime

                    # Parsing data from GIS excel file
                    log.info('New GIS file, importing new file.')
                    gis_dataframe = parse_excel_sheets_to_dataframe(GIS_FILEPATH, [GIS_SHEET])[GIS_SHEET]
                    translate_gis_name_to_ets, non_translatable =\
                        map_gis_to_ets_line_name(gis_dataframe, GIS_COLUMN_NAME, LINE_NAME_REGEX)

                if stat(MRID_FILEPATH).st_mtime > mrid_time_init:
                    mrid_time_init = stat(MRID_FILEPATH).st_mtime

                    # Parsing data from MRID csv file
                    log.info('New MRID file, importing new file.')
                    mrid_dataframe = load_mrid_csv_file(MRID_FILEPATH)

                    # Converting MRID dataframe to a dictionary
                    ets_name_to_mrid = parse_dataframe_columns_to_dictionary(mrid_dataframe, ETS_COLUMN_NAME, ETS_COLUMN_MRID)

                try:
                    # Creating mapping between GIS and ETS if the names are not in agreement.
                    map_gis_ets_dataframe = parse_excel_sheets_to_dataframe(MAP_FILEPATH, [MAP_SHEET])[MAP_SHEET]

                    # Creating a dict from the mapping dataframe
                    map_gis_to_ets_name = parse_dataframe_columns_to_dictionary(map_gis_ets_dataframe,
                                                                                MAP_COLUMN_GIS_NAME, MAP_COLUMN_ETS_NAME)

                    # Replacing the names in the original 'translate_gis_name_to_ets' with the mapping dict
                    translate_gis_name_to_ets = {k: map_gis_to_ets_name.get(v, v) for k, v in
                                                 translate_gis_name_to_ets.items()}
                except Exception as e:
                    log.warning(f'Creating dataframe from "{MAP_FILEPATH}" failed with message: {e}. ' +
                                'Ensure that there is no need for forcing specific mapping names.')

                # Logging difference between GIS and ETS names.
                verify_translated_names_against_ets(translate_gis_name_to_ets, mrid_dataframe, ETS_COLUMN_NAME)

                # Creating the new GIS dataframe with the ACLINESEGMENT_MRID column
                enriched_gis_dataframe = enrich_gis_dataframe(gis_dataframe, mrid_dataframe, translate_gis_name_to_ets,
                                                              ets_name_to_mrid, non_translatable, GIS_COLUMN_NAME,
                                                              ETS_COLUMN_MRID, ETS_COLUMN_NAME, ETS_COLUMN_DLR_ENABLED)

                log.info('Data collection is done.')
                log.debug(f'Dataframe is: {enriched_gis_dataframe}')

                # Passing the new dataframe to the API
                gis_data_api[API_DB_NAME] = enriched_gis_dataframe

            else:
                log.info(f'Files at: "{GIS_FILEPATH}" and "{MRID_FILEPATH}" have not changed.')

        else:
            log.error(f'Files not found at: "{GIS_FILEPATH}" and "{MRID_FILEPATH}"')

        log.info(f'Data collection took: {time() - start_time} seconds')
        sleep(60)

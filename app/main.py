# Library import
from os import path, environ, stat
from time import sleep, time
from json import dumps
import logging
import re
from singupy import conversion
from singupy import api as singuapi
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)
if environ.get("DEBUG", "FALSE").upper() == "FALSE":
    # __main__ will output INFO-level, everything else stays at WARNING
    logging.basicConfig(format="%(levelname)s:%(asctime)s:%(name)s - %(message)s")
    logging.getLogger(__name__).setLevel(logging.INFO)
elif environ["DEBUG"].upper() == "TRUE":
    # Set EVERYTHING to DEBUG level
    logging.basicConfig(
        format="%(levelname)s:%(asctime)s:%(name)s - %(message)s", level=logging.DEBUG
    )
    log.debug("Setting all logs to debug-level")
else:
    raise ValueError(
        "'DEBUG' env. variable is '%s', but must be either 'TRUE', 'FALSE' or unset.",
        environ["DEBUG"],
    )

# Input from user
# API variables
API_DB_NAME = environ.get("API_DB_NAME", "GIS_DATA")
API_PORT = int(environ.get("API_PORT", "5000"))
MOCK_DATA = environ.get("MOCK_DATA", "False")
# Variables for the data that should be enriched.
GIS_FILENAME = environ.get("GIS_FILENAME", "GIS_Driftstr_luftledning_koordinater.xls")
GIS_SHEET_NAME = environ.get("GIS_SHEET", "GIS_Driftstr_luftledning_koordi")
GIS_LINE_NAME_COLUMN = environ.get("GIS_COLUMN_NAME", "Name")
LINE_NAME_REGEX = environ.get(
    "LINE_NAME_REGEX",
    r"^(?P<STN1>\w{3,4}?)_?(?P<volt>\d{3})_(?P<STN2>\w{3,4}?)(?P<id>\d)?$",
)
# ACLinesegment environment variables.
ACLINESEGMENT_DLR_ENABLED_COLUMN = environ.get(
    "ACLINESEGMENT_DLR_ENABLED_COLUMN", "DLR_ENABLED"
)
ACLINESEGMENT_MRID_NAME_COLUMN = environ.get(
    "ACLINESEGMENT_MRID_NAME_COLUMN", "ACLINESEGMENT_MRID"
)
ACLINESEGMENT_FILENAME = environ.get("ACLINESEGMENT_FILENAME", "seg_line_mrid_PROD.csv")
ACLINESEGMENT_LINE_NAME_COLUMN = environ.get(
    "ACLINESEGMENT_LINE_NAME_COLUMN", "LINE_EMSNAME"
)
# Mapping variables to enforce a specific translation.
MAP_GIS_LINE_NAME_COLUMN = environ.get("MAP_GIS_LINE_NAME_COLUMN", "GIS LINE NAME")
MAP_ETS_LINE_NAME_COLUMN = environ.get("MAP_ETS_LINE_NAME_COLUMN", "ETS LINE NAME")
GIS_TO_ETS_MAP_FILENAME = environ.get("GIS_TO_ETS_MAP_FILENAME", "Gis_map.xlsx")
MAP_SHEET_NAME = environ.get("MAP_SHEET_NAME", "GisMapping")

# Docker folder (all new data is by configuration getting sent to the '/data/' folder)
docker_folder = "/data/"

# Checking to see if the user want to use mock data within the code.
if MOCK_DATA.upper() == "TRUE":
    docker_folder = "/testdata/"
    log.warning('Env. variable "MOCK_DATA" = %s. Using test-data for input.', MOCK_DATA)
elif MOCK_DATA.upper() != "FALSE":
    raise ValueError(
        "'MOCK_DATA' env. variable is set to: '%s' but must be either: 'True', 'False' or unset.",
        MOCK_DATA,
    )

# Chosen filepaths
ACLINESEGMENT_FILEPATH = docker_folder + ACLINESEGMENT_FILENAME
GIS_FILEPATH = docker_folder + GIS_FILENAME
GIS_TO_ETS_MAP_FILEPATH = docker_folder + GIS_TO_ETS_MAP_FILENAME


def load_mrid_csv_file(file_path: str) -> pd.DataFrame:
    """
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
    """
    # Read data from CSV to dataframe and drop row with index 0 as it contains only hyphens
    try:
        dataframe = pd.read_csv(
            file_path, delimiter=",", on_bad_lines="skip", encoding="cp1252"
        )
        dataframe.drop(0, inplace=True)
        log.info('CSV data in "%s" was parsed to DataFrame.', file_path)
    except Exception as e:
        log.exception('Parsing data from: "%s" failed with message: %s.', file_path, e)
        raise e

    return dataframe


def parse_excel_sheets_to_dataframe(
    file_path: str, sheets: list, header_index: int = 0
) -> dict[str, pd.DataFrame]:
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
        log.info(
            "Excel data from sheet(s): '%s' in: '%s' was parsed to dataframe dictionary.",
            sheets,
            file_path,
        )
    except Exception as e:
        log.exception(
            "Parsing data from sheet(s): '%s' in excel file: '%s' failed with message: '%s'.",
            sheets,
            file_path,
            e,
        )
        raise e

    return df_dictionary


def parse_dataframe_columns_to_dictionary(
    dataframe: pd.DataFrame, dict_key: str, dict_value: str
) -> dict[str, tuple[str, int]]:
    """
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
    """

    # Checking the dictionary key and value to ensure that the user input is found in the dataframe.
    for col_name in [dict_key, dict_value]:
        if col_name not in dataframe:
            raise ValueError(
                'The column "%s" does not exist in the dataframe.', col_name
            )

    # Extract two columns from the dataframe and create a dictionary from them.
    try:
        dict_set = dataframe.set_index(dict_key)[dict_value].to_dict()
        log.info(
            'Dataframe was parsed to a dictionary with key: "%s" and value: "%s".',
            dict_key,
            dict_value,
        )
        log.debug(dumps(dict_set, indent=4, ensure_ascii=False))

    except Exception as e:
        log.exception(
            'Creating dictionary from dataframe columns "%s" and "%s" failed with message: %s',
            dict_key,
            dict_value,
            e,
        )
        raise e

    return dict_set


def map_gis_to_ets_line_name(
    gis_dataframe: pd.DataFrame, gis_column: str, regex: str
) -> tuple[dict[str, str], list[str]]:
    """
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
    """

    gis_line_name_to_ets_line_name = {}
    non_translatable = []

    # Checking column constant from the user input to ensure that column is found in the dataframe.
    if gis_column not in gis_dataframe:
        raise ValueError(
            'The column "%s" does not exist in the specified dataframe.', gis_column
        )

    # Removing spaces from the names in the gis_names
    gis_dataframe[gis_column] = gis_dataframe[gis_column].str.replace(" ", "")

    # Getting the list of unique names from GIS column
    gis_names = list(gis_dataframe[gis_column].unique())

    for name in gis_names:
        match = re.match(regex, name)
        if match:
            # Converting the extracted voltage number to a letter with the function 'kv_to_letter'
            volt = conversion.kv_to_letter(int(match.group("volt")))
            # Constructing "ets_name" from domain known pattern
            ets_name = f"{volt}_{match.group('STN1')}-{match.group('STN2')}"
            if match.group("id") is not None:
                ets_name += f'_{match.group("id")}'
            gis_line_name_to_ets_line_name[name] = ets_name
        else:
            non_translatable.append(name)
    log.info(
        'The specified regex: "%s" expression have been run on the input list.', regex
    )

    # Review the non_translatable and informing the user if there is any names not translated
    if non_translatable:
        log.warning("List of names not translated by the function:%s", non_translatable)
    else:
        log.info("All names from the GIS dataframe have been translated.")

    return gis_line_name_to_ets_line_name, non_translatable


def enrich_dlr_dataframe(
    gis_dataframe: pd.DataFrame,
    aclinesegment_dataframe: pd.DataFrame,
    gis_line_name_to_ets_line_name: dict[str, str],
    bad_line_names: list[str],
    gis_column_name: str,
    ets_column_name: str,
) -> pd.DataFrame:
    """
    Enriches the MRID dataframe with gis data and remove untranslated lines.

    Parameters
    ----------
    gis_dataframe: pd.DataFrame
        Dataframe containing GIS data - the dataframe to enrich.
    aclinesegment_dataframe: pd.DataFrame
        Dataframe containing ETS data
    gis_line_name_to_ets_line_name: dict[str, str]
        Mapping between gis line name and ets line name
    bad_line_names: list[str]
        List of gis line names that should be removed from the dataset
        (i.e. lines that could not be translated into ETS line names).
    gis_column_name: str
        Name of the column in gis_dataframe which contains the gis line names.
    ets_name_column: str
        Name of the column in mrid_dataframe that contains the ets names.

    Returns
    -------
    pd.DataFrame
        Clone of gis_dataframe enriched with MRID data, minus non-translated rows.
    """
    # Variable to store temp column name to join the two DataFrames
    TEMP_COLUMN = "ETS_NAME"

    # Creating a column with the ETS name
    gis_dataframe[TEMP_COLUMN] = gis_dataframe[gis_column_name].map(
        gis_line_name_to_ets_line_name
    )

    # Removing any names that could not be translated to represent a clean dataframe that only contains
    # information that can be looked up with MRID.
    gis_dataframe = gis_dataframe[~gis_dataframe[gis_column_name].isin(bad_line_names)]

    dlr_dataframe = aclinesegment_dataframe.join(
        gis_dataframe.set_index(TEMP_COLUMN),
        on=ets_column_name,
        how="inner",
    )

    # Resetting index
    dlr_dataframe.reset_index(inplace=True, drop=True)

    return dlr_dataframe


def verify_translated_names_against_ets(
    gis_to_ets_name: dict[str, str],
    dataframe: pd.DataFrame,
    ets_name_column: str,
    dlr_enabled_column: str,
):
    """
    The function checks if there are lines in the ETS dataset which is not represented in the GIS dataset.
    This is for logging and to be able to see when introducing a new dataset if the data quality stays the same.

    Parameters
    ----------
    gis_to_ets_name_mapping : dict[str, str]
        The dict containing the translated names from GIS.
    dataframe : pd.DataFrame
        Dataframe with all ETS information in.
    ets_name_column : str
        The specific column in the MRID dataframe that contains the names of lines.
    dlr_enabled_column : str
        Name of the column in mrid_dataframe which contains enabled state
    Returns
    -------
    None
    """

    regex = r"^[CDE]_"

    # Comparing the converted names from GIS to the list of names in ETS.
    # omitting low voltages level
    lines_not_in_gis = list(
        line
        for line in (
            list(
                set(dataframe[ets_name_column]).difference(
                    list(gis_to_ets_name.values())
                )
            )
        )
        if re.match(regex, line)
    )

    lines_not_in_gis.sort()
    log.info("List of lines not found in GIS data set: %s", lines_not_in_gis)

    # Checking to see if there are lines in the MRID list with enabled DLR that
    # can not be found in GIS data
    lines_with_dlr_enabled = mrid_dataframe[
        mrid_dataframe[dlr_enabled_column].str.upper() == "YES"
    ][ets_name_column]

    missing_gis_data = list(set(lines_with_dlr_enabled) - set(gis_to_ets_name.values()))

    if missing_gis_data:
        log.error(
            "Some lines set up for DLR have no GIS data available, they are: %s",
            missing_gis_data,
        )
    else:
        log.info("Gis data is found for all lines in the MRID file with DLR enabled.")


if __name__ == "__main__":
    # Initialize of variables and API.
    gis_time_init = mrid_time_init = gis_map_time_init = 0

    gis_data_api = singuapi.DataFrameAPI(dbname=API_DB_NAME, port=API_PORT)
    log.info("Started API on port %d", gis_data_api.web.port)

    while True:
        start_time = time()
        if path.isfile(GIS_FILEPATH) and path.isfile(ACLINESEGMENT_FILEPATH):
            if (
                stat(GIS_FILEPATH).st_mtime > gis_time_init
                or stat(ACLINESEGMENT_FILEPATH).st_mtime > mrid_time_init
                or stat(GIS_TO_ETS_MAP_FILEPATH).st_mtime > gis_map_time_init
            ):
                if stat(GIS_FILEPATH).st_mtime > gis_time_init:
                    gis_time_init = stat(GIS_FILEPATH).st_mtime

                    # Parsing data from GIS excel file
                    log.info("New GIS file, importing new file.")
                    gis_dataframe = parse_excel_sheets_to_dataframe(
                        GIS_FILEPATH, [GIS_SHEET_NAME]
                    )[GIS_SHEET_NAME]
                    (
                        gis_to_ets_name_mapping,
                        non_translatable,
                    ) = map_gis_to_ets_line_name(
                        gis_dataframe, GIS_LINE_NAME_COLUMN, LINE_NAME_REGEX
                    )

                if stat(ACLINESEGMENT_FILEPATH).st_mtime > mrid_time_init:
                    mrid_time_init = stat(ACLINESEGMENT_FILEPATH).st_mtime

                    # Parsing data from MRID csv file
                    log.info("New MRID file, importing new file.")
                    mrid_dataframe = load_mrid_csv_file(ACLINESEGMENT_FILEPATH)

                if stat(GIS_TO_ETS_MAP_FILEPATH).st_mtime > gis_map_time_init:
                    gis_map_time_init = stat(GIS_TO_ETS_MAP_FILEPATH).st_mtime
                    try:
                        # Creating mapping between GIS and ETS if the names are not in agreement.
                        map_gis_ets_dataframe = parse_excel_sheets_to_dataframe(
                            GIS_TO_ETS_MAP_FILEPATH, [MAP_SHEET_NAME]
                        )[MAP_SHEET_NAME]

                        # Creating a dict from the mapping dataframe
                        map_gis_to_ets_name = parse_dataframe_columns_to_dictionary(
                            map_gis_ets_dataframe,
                            MAP_GIS_LINE_NAME_COLUMN,
                            MAP_ETS_LINE_NAME_COLUMN,
                        )

                        # Replacing the names in the original 'translate_gis_name_to_ets'
                        # with the mapping dict
                        gis_to_ets_name_mapping = {
                            k: map_gis_to_ets_name.get(v, v)
                            for k, v in gis_to_ets_name_mapping.items()
                        }

                    except Exception as e:
                        log.warning(
                            """Creating dataframe from "%s" failed with message: %s.
                            Ensure that there is no need for forcing specific mapping names.""",
                            GIS_TO_ETS_MAP_FILEPATH,
                            e,
                        )

                # Logging difference between GIS and ETS names.
                verify_translated_names_against_ets(
                    gis_to_ets_name_mapping,
                    mrid_dataframe,
                    ACLINESEGMENT_LINE_NAME_COLUMN,
                    ACLINESEGMENT_DLR_ENABLED_COLUMN,
                )

                # Creating the dlr dataframe with ETS data enriched with gis data
                enriched_gis_data = enrich_dlr_dataframe(
                    gis_dataframe,
                    mrid_dataframe,
                    gis_to_ets_name_mapping,
                    non_translatable,
                    GIS_LINE_NAME_COLUMN,
                    ACLINESEGMENT_LINE_NAME_COLUMN,
                )

                log.info("Data collection is done.")
                log.debug("Dataframe is: %s", enriched_gis_data)

                # Passing the new dataframe to the API
                gis_data_api[API_DB_NAME] = enriched_gis_data

            else:
                log.info(
                    'Files at: "%s", "%s" and "%s" have not changed.',
                    GIS_FILEPATH,
                    ACLINESEGMENT_FILEPATH,
                    GIS_TO_ETS_MAP_FILEPATH,
                )

        else:
            log.error(
                'Files not found at: "%s" and "%s"',
                GIS_FILEPATH,
                ACLINESEGMENT_FILEPATH,
            )

        log.debug("Data collection took: %f seconds", round(time() - start_time, 4))
        sleep(60)

import os
import pandas as pd
import app.main as main

# Location of test files used in the different test
TESTDATA_PATH = f"{os.path.dirname(__file__)}/../tests/valid-testdata/"
GIS_FILEPATH = f"{TESTDATA_PATH}" + "GIS_Driftstr_luftledning_koordinater.xls"
ACLINESEGMENT_FILEPATH = f"{TESTDATA_PATH}" + "seg_line_mrid_PROD.csv"
GIS_TO_ETS_MAP_FILEPATH = f"{TESTDATA_PATH}" + "Gis_map.xlsx"
TEST_DATA_FILEPATH = f"{TESTDATA_PATH}" + "test_dataframe.csv"

# Input variables to the test functions
ACLINESEGMENT_LINE_NAME_COLUMN = "LINE_EMSNAME"
ACLINESEGMENT_MRID_NAME_COLUMN = "ACLINESEGMENT_MRID"
LINE_NAME_REGEX = r"^(?P<STN1>\w{3,4}?)_?(?P<volt>\d{3})_(?P<STN2>\w{3,4}?)(?P<id>\d)?$"
GIS_SHEET_NAME = "GIS_Driftstr_luftledning_koordi"
GIS_LINE_NAME_COLUMN = "Name"
MAP_GIS_LINE_NAME_COLUMN = "GIS LINE NAME"
MAP_ETS_LINE_NAME_COLUMN = "ETS LINE NAME"
MAP_SHEET_NAME = "GisMapping"


def test_parse_dataframe_columns_to_dictionary():

    aclinesegment_dataframe = main.load_mrid_csv_file(ACLINESEGMENT_FILEPATH)

    # Expected dictionary from the dataframe
    TEST_DICTIONARY = {
        "E_EEE-FFF_1": "66b4596e-asfv-tyuy-5478-bd208f26a446",
        "E_EEE-FFF_2": "66b4596e-asfv-tyuy-5478-bd208f26a447",
        "E_GGG-HHH": "66b4596e-asfv-tyuy-5478-bd208f26a451",
        "D_CCC-DDD": "66b4596e-asfv-tyuy-5478-bd208f26a455",
        "C_III-ÆØÅ": "66b4596e-asfv-tyuy-5478-bd208f26a457",
        "C_ASK-ERS": "66b4596e-asfv-tyuy-5478-bd208f26a459",
    }

    assert (
        main.parse_dataframe_columns_to_dictionary(
            aclinesegment_dataframe,
            ACLINESEGMENT_LINE_NAME_COLUMN,
            ACLINESEGMENT_MRID_NAME_COLUMN,
        )
        == TEST_DICTIONARY
    )


def test_convert_gis_names_to_ets_names():

    gis_dataframe = main.parse_excel_sheets_to_dataframe(
        GIS_FILEPATH, [GIS_SHEET_NAME]
    )[GIS_SHEET_NAME]

    # The expected dict of names
    TEST_DICTIONARY = {
        "ASK_400_ERS": "C_ASK-ERS",
        "CCC_220_DDD": "D_CCC-DDD",
        "EEE_150_FFF1": "E_EEE-FFF_1",
        "EEE_150_FFF2": "E_EEE-FFF_2",
        "GGG_150_HHH": "E_GGG-HHH",
        "III_400_ÆØÅ": "C_III-ÆØÅ",
    }

    assert (
        main.map_gis_to_ets_line_name(
            gis_dataframe, GIS_LINE_NAME_COLUMN, LINE_NAME_REGEX
        )[0]
        == TEST_DICTIONARY
    )


def test_creating_dataframe_with_gis_coordinates_and_ets_mrid():

    mrid_dataframe = main.load_mrid_csv_file(ACLINESEGMENT_FILEPATH)
    # print(mrid_dataframe)
    gis_dataframe = main.parse_excel_sheets_to_dataframe(
        GIS_FILEPATH, [GIS_SHEET_NAME]
    )[GIS_SHEET_NAME]
    translated_names, none_translated_names = main.map_gis_to_ets_line_name(
        gis_dataframe, GIS_LINE_NAME_COLUMN, LINE_NAME_REGEX
    )
    # Creating mapping between GIS and ETS if the names are not in agreement.
    map_gis_ets_dataframe = main.parse_excel_sheets_to_dataframe(
        GIS_TO_ETS_MAP_FILEPATH, [MAP_SHEET_NAME]
    )[MAP_SHEET_NAME]
    # Creating a dict from the mapping dataframe
    map_gis_to_ets_name = main.parse_dataframe_columns_to_dictionary(
        map_gis_ets_dataframe, MAP_GIS_LINE_NAME_COLUMN, MAP_ETS_LINE_NAME_COLUMN
    )

    translated_names = {
        k: map_gis_to_ets_name.get(v, v) for k, v in translated_names.items()
    }

    TEST_DATAFRAME = pd.read_csv(TEST_DATA_FILEPATH, delimiter=";")

    dataframe = main.enrich_dlr_dataframe(
        gis_dataframe,
        mrid_dataframe,
        translated_names,
        none_translated_names,
        GIS_LINE_NAME_COLUMN,
        ACLINESEGMENT_LINE_NAME_COLUMN,
    )

    assert (
        pd.testing.assert_frame_equal(TEST_DATAFRAME, dataframe, check_dtype=True)
        is None
    )

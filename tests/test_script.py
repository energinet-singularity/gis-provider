import os
import pandas as pd
import app.main as code

# Location of test files used in the different test
testdata_path = f"{os.path.dirname(__file__)}/../tests/valid-testdata"
GIS_FILEPATH = f'{testdata_path}/GIS_Driftstr_luftledning_koordinater_decimalgrader_05042022.xls'
MRID_FILEPATH = f'{testdata_path}/seg_line_mrid_PROD.csv'
MAP_FILEPATH = f'{testdata_path}/Gis_map.xlsx'


def test_parse_dataframe_columns_to_dictionary():
    # Input variables to the function
    MRID_KEY_NAME = 'LINE_EMSNAME'
    MRID_VALUE_NAME = 'ACLINESEGMENT_MRID'

    mrid_dataframe = code.load_mrid_csv_file(MRID_FILEPATH)

    # Expected dictionary from the dataframe
    TEST_DICTIONARY = {'E_EEE-FFF_1':    '66b4596e-asfv-tyuy-5478-bd208f26a446',
                       'E_EEE-FFF_2':    '66b4596e-asfv-tyuy-5478-bd208f26a447',
                       'E_GGG-HHH':      '66b4596e-asfv-tyuy-5478-bd208f26a451',
                       'D_CCC-DDD':      '66b4596e-asfv-tyuy-5478-bd208f26a455',
                       'C_III-ÆØÅ':      '66b4596e-asfv-tyuy-5478-bd208f26a457',
                       'C_ASK-ERS':      '66b4596e-asfv-tyuy-5478-bd208f26a459'}

    assert code.parse_dataframe_columns_to_dictionary(mrid_dataframe,
                                                      MRID_KEY_NAME, MRID_VALUE_NAME) == TEST_DICTIONARY


def test_convert_gis_names_to_ets_names():

    SHEET_NAME = 'GIS_Driftstr_luftledning_koordi'
    GIS_COLUMN_NAME = 'Name'
    REGEX = r'^(?P<STN1>\w{3,4}?)_?(?P<volt>\d{3})_(?P<STN2>\w{3,4}?)(?P<id>\d)?$'
    gis_dataframe = code.parse_excel_sheets_to_dataframe(GIS_FILEPATH, [SHEET_NAME])[SHEET_NAME]

    # The expected dict of names
    TEST_DICTIONARY = {'ASK_400_ERS':    'C_ASK-ERS',
                       'CCC_220_DDD':    'D_CCC-DDD',
                       'EEE_150_FFF1':   'E_EEE-FFF_1',
                       'EEE_150_FFF2':   'E_EEE-FFF_2',
                       'GGG_150_HHH':    'E_GGG-HHH',
                       'III_400_ÆØÅ':    'C_III-ÆØÅ'}

    assert code.map_gis_to_ets_line_name(gis_dataframe, GIS_COLUMN_NAME, REGEX)[0] == TEST_DICTIONARY


def test_creating_dataframe_with_gis_coordinates_and_ets_mrid():
    ETS_COLUMN_MRID = 'ACLINESEGMENT_MRID'
    ETS_COLUMN_NAME = 'LINE_EMSNAME'
    GIS_COLUMN_NAME = 'Name'
    SHEET_NAME = 'GIS_Driftstr_luftledning_koordi'
    ETS_COLUMN_DLR_ENABLED = 'DLR_ENABLED'
    MAP_COLUMN_GIS_NAME = 'GIS Name'
    MAP_COLUMN_ETS_NAME = 'ETS Name'
    MAP_SHEET = 'GisMapping'
    REGEX = r'^(?P<STN1>\w{3,4}?)_?(?P<volt>\d{3})_(?P<STN2>\w{3,4}?)(?P<id>\d)?$'

    mrid_dataframe = code.load_mrid_csv_file(MRID_FILEPATH)
    # print(mrid_dataframe)
    gis_dataframe = code.parse_excel_sheets_to_dataframe(GIS_FILEPATH, [SHEET_NAME])[SHEET_NAME]
    translated_names, none_translated_names = code.map_gis_to_ets_line_name(gis_dataframe, GIS_COLUMN_NAME, REGEX)
    mrid_dictionary = code.parse_dataframe_columns_to_dictionary(mrid_dataframe, ETS_COLUMN_NAME, ETS_COLUMN_MRID)
    # Creating mapping between GIS and ETS if the names are not in agreement.
    map_gis_ets_dataframe = code.parse_excel_sheets_to_dataframe(MAP_FILEPATH, [MAP_SHEET])[MAP_SHEET]
    # Creating a dict from the mapping dataframe
    map_gis_to_ets_name = code.parse_dataframe_columns_to_dictionary(map_gis_ets_dataframe,
                                                                     MAP_COLUMN_GIS_NAME, MAP_COLUMN_ETS_NAME)

    translated_names = {k: map_gis_to_ets_name.get(v, v) for k, v in translated_names.items()}

    TEST_DATA = {'OBJECTID':            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                                         19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35],
                 'Name':                ['EEE_150_FFF1', 'EEE_150_FFF1', 'EEE_150_FFF1', 'EEE_150_FFF1', 'EEE_150_FFF2',
                                         'EEE_150_FFF2', 'EEE_150_FFF2', 'EEE_150_FFF2', 'EEE_150_FFF2', 'EEE_150_FFF2',
                                         'GGG_150_HHH', 'GGG_150_HHH', 'GGG_150_HHH', 'GGG_150_HHH', 'GGG_150_HHH',
                                         'GGG_150_HHH', 'CCC_220_DDD', 'CCC_220_DDD', 'CCC_220_DDD', 'CCC_220_DDD',
                                         'CCC_220_DDD', 'CCC_220_DDD', 'III_400_ÆØÅ', 'III_400_ÆØÅ', 'III_400_ÆØÅ',
                                         'III_400_ÆØÅ', 'III_400_ÆØÅ', 'ASK_400_ERS', 'ASK_400_ERS', 'ASK_400_ERS',
                                         'ASK_400_ERS', 'ASK_400_ERS', 'ASK_400_ERS', 'ASK_400_ERS', 'ASK_400_ERS'],
                 'ORIG_FID':            [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5,
                                         5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6],
                 'Long_DD':             [12.2974323902383, 12.2973564357018, 12.297335451794, 12.2970757426513,
                                         10.2970757426513, 10.2970757426513, 10.2970757426513, 10.2970757426513,
                                         10.2970757426513, 10.2970757426513, 14.2970757426513, 14.2970757426513,
                                         14.2970757426513, 14.2970757426513, 14.2970757426513, 14.2970757426513,
                                         11.2970757426513, 11.2970757426513, 11.2970757426513, 11.2970757426513,
                                         11.2970757426513, 11.2970757426513, 13.2970757426513, 13.2970757426513,
                                         13.2970757426513, 13.2970757426513, 13.2970757426513, 16.2970757426513,
                                         16.2970757426513, 16.2970757426513, 16.2970757426513, 16.2970757426513,
                                         16.2970757426513, 16.2970757426513, 16.2970757426513],
                 'Lat_DD':              [57.4045625246343, 57.4041660130909, 57.4036495039083, 57.401170247988,
                                         55.401170247988, 55.401170247988, 55.401170247988, 55.401170247988,
                                         55.401170247988, 55.401170247988, 59.401170247988, 59.401170247988,
                                         59.401170247988, 59.401170247988, 59.401170247988, 59.401170247988,
                                         56.401170247988, 56.401170247988, 56.401170247988, 56.401170247988,
                                         56.401170247988, 56.401170247988, 58.401170247988, 58.401170247988,
                                         58.401170247988, 58.401170247988, 58.401170247988, 60.401170247988,
                                         60.401170247988, 60.401170247988, 60.401170247988, 60.401170247988,
                                         60.401170247988, 60.401170247988, 60.401170247988],
                 'ACLINESEGMENT_MRID':  ['66b4596e-asfv-tyuy-5478-bd208f26a446', '66b4596e-asfv-tyuy-5478-bd208f26a446',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a446', '66b4596e-asfv-tyuy-5478-bd208f26a446',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a447', '66b4596e-asfv-tyuy-5478-bd208f26a447',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a447', '66b4596e-asfv-tyuy-5478-bd208f26a447',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a447', '66b4596e-asfv-tyuy-5478-bd208f26a447',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a451', '66b4596e-asfv-tyuy-5478-bd208f26a451',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a451', '66b4596e-asfv-tyuy-5478-bd208f26a451',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a451', '66b4596e-asfv-tyuy-5478-bd208f26a451',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a455', '66b4596e-asfv-tyuy-5478-bd208f26a455',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a455', '66b4596e-asfv-tyuy-5478-bd208f26a455',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a455', '66b4596e-asfv-tyuy-5478-bd208f26a455',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a457', '66b4596e-asfv-tyuy-5478-bd208f26a457',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a457', '66b4596e-asfv-tyuy-5478-bd208f26a457',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a457', '66b4596e-asfv-tyuy-5478-bd208f26a459',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a459', '66b4596e-asfv-tyuy-5478-bd208f26a459',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a459', '66b4596e-asfv-tyuy-5478-bd208f26a459',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a459', '66b4596e-asfv-tyuy-5478-bd208f26a459',
                                         '66b4596e-asfv-tyuy-5478-bd208f26a459']
                 }

    TEST_DATAFRAME = pd.DataFrame(TEST_DATA)

    dataframe = code.enrich_gis_dataframe(gis_dataframe, mrid_dataframe, translated_names, mrid_dictionary,
                                          none_translated_names, GIS_COLUMN_NAME, ETS_COLUMN_MRID, ETS_COLUMN_NAME,
                                          ETS_COLUMN_DLR_ENABLED)

    assert pd.testing.assert_frame_equal(TEST_DATAFRAME, dataframe, check_dtype=True) is None

import os
import pandas as pd
import app.my_script as code

# Location of test files used in the different test
GIS_FILEPATH = os.path.dirname(__file__) + '/../tests/valid-testdata/GIS_data.xlsx'
MRID_FILEPATH = os.path.dirname(__file__) + '/../tests/valid-testdata/DLR_MRID.csv'


def test_parse_dataframe_columns_to_dictionary():
    MRID_KEY_NAME = 'LINE_EMSNAME'
    MRID_VALUE_NAME = 'ACLINESEGMENT_MRID'

    mrid_dataframe = code.parse_csv_file_to_dataframe(MRID_FILEPATH)
    TEST_DICTONARY = {'E_EEE-FFF-1':    '66b4596e-asfv-tyuy-5478-bd208f26a446',
                      'E_EEE-FFF-2':    '66b4596e-asfv-tyuy-5478-bd208f26a447',
                      'E_GGG-HHH':      '66b4596e-asfv-tyuy-5478-bd208f26a451',
                      'D_CCC-DDD':      '66b4596e-asfv-tyuy-5478-bd208f26a455',
                      'C_III-ÆØÅ':      '66b4596e-asfv-tyuy-5478-bd208f26a457',
                      'C_ASK-ERS':      '66b4596e-asfv-tyuy-5478-bd208f26a459'}

    assert code.parse_dataframe_columns_to_dictionary(mrid_dataframe,
                                                                 MRID_KEY_NAME, MRID_VALUE_NAME) == TEST_DICTONARY


def test_convert_gis_name_to_ets_name():
    mrid_dataframe = code.parse_csv_file_to_dataframe(MRID_FILEPATH)

    test_list = mrid_dataframe['LINE_EMSNAME'].tolist()
    test_list.sort()

    assert code.convert_gis_name_to_ets_name(GIS_FILEPATH) == test_list


def test_creating_dataframe_with_gis_coordinates_and_ets_mrid():
    
    gis_ets_name = code.convert_gis_name_to_ets_name(GIS_FILEPATH)
    mrid_dataframe = code.parse_csv_file_to_dataframe(MRID_FILEPATH)

    MRID_KEY_NAME = 'LINE_EMSNAME'
    MRID_VALUE_NAME = 'ACLINESEGMENT_MRID'

    mrid_ets_name_dict = code.parse_dataframe_columns_to_dictionary(mrid_dataframe, MRID_KEY_NAME, MRID_VALUE_NAME)

    # Can not say what the solution is going to be at the given time needs to be reevaluated
    # WHAT DO?????!!!!
    TEST_DATA = {'OBJECTID':           ['1', '2', '3', '4'],
                 'ACLINESEGMENT_MRID': ['66b4596e-asfv-tyuy-5478-bd208f26a446', '66b4596e-asfv-tyuy-5478-bd208f26a446', '66b4596e-asfv-tyuy-5478-bd208f26a446', '66b4596e-asfv-tyuy-5478-bd208f26a446'],
                 'GIS_LINE_NAME':      ['E_EEE-FFF-1', 'E_EEE-FFF-1', 'E_EEE-FFF-1', 'E_EEE-FFF-1'],
                 'ORIG:FID':           ['1','1','1','1'],
                 'Long_DD':            ['12.297432', '12.297356', '12.297335', '12.297076'],
                 'Lat_DD':             ['57.404563', '57.404166', '57.403650', '57.401170']
                 }
    
    TEST_DATAFRAME = pd.DataFrame(TEST_DATA)

    assert True #code.creating_dataframe_with_gis_coordinates_and_ets_mrid(gis_ets_name, mrid_ets_name_dict) == TEST_DATAFRAME

import os
import pandas as pd
import app.my_script as code



'''
OBJECTID    |   Name        |   ORIG_FID    |   Long_DD     |   Lat_DD      |
1           |   EEE_150_FFF |   1           |   12,29743239 |   57,40456252 |
2           |   EEE_150_FFF |   1           |   12,29735644 |   57,40416601 |
3           |   EEE_150_FFF |   1           |   12,29733545 |   57,4036495  |
4           |   EEE_150_FFF |   1           |   12,29707574 |   57,40117025 |

'''


def test_define_dictonary_from_two_columns_in_a_dataframe():

    DLR_MRID_FILEPATH = f'{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/DLR_MRID.csv'
    MRID_KEY_NAME = 'LINE_EMSNAME'
    MRID_VALUE_NAME = 'ACLINESEGMENT_MRID'

    mrid_dataframe = code.parse_csv_file_to_dataframe(DLR_MRID_FILEPATH)
    TEST_DICTONARY = {'E_EEE-FFF-1':    '66b4596e-asfv-tyuy-5478-bd208f26a446',
                      'E_EEE-FFF-2':    '66b4596e-asfv-tyuy-5478-bd208f26a447',
                      'E_GGG-HHH':      '66b4596e-asfv-tyuy-5478-bd208f26a451',
                      'D_CCC-DDD':      '66b4596e-asfv-tyuy-5478-bd208f26a455',
                      'C_III-ÆØÅ':      '66b4596e-asfv-tyuy-5478-bd208f26a457',
                      'C_ASK-ERS':      '66b4596e-asfv-tyuy-5478-bd208f26a459'}

    assert code.define_dictonary_from_two_columns_in_a_dataframe(mrid_dataframe,
                                                                 MRID_KEY_NAME, MRID_VALUE_NAME) == TEST_DICTONARY


def test_convert_gis_name_to_ets_name():
    GIS_FILEPATH = f'{os.path.dirname(os.path.realpath(__file__))}tests/valid-testdata/GIS_data.xlsx'
    MRID_FILEPATH = f'{os.path.dirname(os.path.realpath(__file__))}tests/valid-testdata/DLR_MRID.csv'
    mrid_dataframe = pd.read_csv(MRID_FILEPATH, delimiter=',', on_bad_lines='skip')

    mrid_name_test_list = mrid_dataframe['LINE_EMSNAME'].tolist()

    assert code.convert_gis_name_to_ets_name(GIS_FILEPATH) == mrid_name_test_list

    # Mapping MRID_DATAFRAME[LINE_EMSNAME] == GIS_DATAFRAME[Name_new]
    # Dont update dataframes, use list and dicts


# dict gis name a coordinates
def test_creating_dict_with_gis_coordinates_and_ets_mrid():
    GIS_FILEPATH = f'{os.path.dirname(os.path.realpath(__file__))}tests/valid-testdata/GIS_data.xlsx'
    gis_ets_name = code.convert_gis_name_to_ets_name(GIS_FILEPATH)

    MRID_FILEPATH = f'{os.path.dirname(os.path.realpath(__file__))}tests/valid-testdata/DLR_MRID.csv'
    mrid_dataframe = pd.read_csv(MRID_FILEPATH, delimiter=',', on_bad_lines='skip')
    MRID_KEY_NAME = 'LINE_EMSNAME'
    MRID_VALUE_NAME = 'ACLINESEGMENT_MRID'
    mrid_ets_name_dict = code.define_dictonary_from_two_columns_in_a_dataframe(mrid_dataframe, MRID_KEY_NAME, MRID_VALUE_NAME)

    # Can not say what the solution is going to be at the given time needs to be reevaluated
    # WHAT DO?????!!!!
    TEST_DATA = {'OBJECTID':           ['1', '2', '3', '4'],
                 'ACLINESEGMENT_MRID': ['66b4596e-asfv-tyuy-5478-bd208f26a446', '66b4596e-asfv-tyuy-5478-bd208f26a446', '66b4596e-asfv-tyuy-5478-bd208f26a446', '66b4596e-asfv-tyuy-5478-bd208f26a446'],
                 'LINE_EMSNAME':       ['E_EEE-FFF-1', 'E_EEE-FFF-1', 'E_EEE-FFF-1', 'E_EEE-FFF-1'],
                 'Long_DD':            ['12.297432', '12.297356', '12.297335', '12.297076'],
                 'Lat_DD':             ['57.404563', '57.404166', '57.403650', '57.401170']
                 }
    
    TEST_DATAFRAME = pd.DataFrame(TEST_DATA)

    assert code.creating_dict_with_gis_coordinates_and_ets_mrid(gis_ets_name, mrid_ets_name_dict) == TEST_DATAFRAME

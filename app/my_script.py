import pandas as pd
import numpy as np
import logging
import os
import re

# Initialize log
log = logging.getLogger(__name__)


# Constants / filepaths
# GIS_FILEPATH2 = os.path.dirname(__file__) + '/../tests/valid-testdata/GIS_data.xlsx'
GIS_FILEPATH = os.path.dirname(__file__) + '/../real-data/GIS_Driftstr_luftledning_koordinater_decimalgrader_05042022.xls'
MRID_FILEPATH = os.path.dirname(__file__) + '/../tests/valid-testdata/DLR_MRID.csv'
MRID_KEY_NAME = 'LINE_EMSNAME'
MRID_VALUE_NAME = 'ACLINESEGMENT_MRID'
MRID_EXPECTED_HEADER_NAMES = ['ACLINESEGMENT_MRID', 'LINE_EMSNAME', 'DLR_ENABLED']

def convert_gis_name_to_ets_name(file_path: str):
    GIS_COLUMN_NAME = 'Name'
    gis_dataframe = pd.read_excel(io=file_path)

    # Make list of names from GIS data
    Name_list = gis_dataframe[GIS_COLUMN_NAME].tolist()
    # Find unique names
    Name_list_unique = np.unique(Name_list)

    # Splitting list (consider reqular expression!!)
    # test_list = [re.findall("_",Name_list_unique) for s in Name_list_unique]
    new_list_1 = [i.split('_') for i in Name_list_unique]
    new_list_2 = []
    new_list_3 = []
    new_list_4 = []
    new_list_5 = []

    for i in new_list_1:
        if len(i) == 3:
            new_list_2.append(i)
        elif len(i) != 3:
            new_list_3.append(i)
        else:
            print(f'Unexpected line seqment name in the column "{GIS_COLUMN_NAME}"')

    # print(new_list_3)

    for k in new_list_2:
        for i in k:
            if len(i) > 6:
                new_list_4.append(k)

    print(new_list_4)

    new_list_5 = new_list_2
    for i in new_list_4:
        if i in new_list_2:
            new_list_5.remove(i)

    print(new_list_5)

    translated_gis_name_list = ''
    return translated_gis_name_list

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(name)s - %(message)s')
    log.setLevel(logging.INFO)

    convert_gis_name_to_ets_name(GIS_FILEPATH)

from tokenize import Name
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


def convert_gis_name_to_ets_name(file_path: str):
    GIS_COLUMN_NAME = 'Name'
    gis_name_list = pd.read_excel(io=file_path)[GIS_COLUMN_NAME].tolist()

    # Find unique names
    Name_list_unique = np.unique(gis_name_list)
    print(Name_list_unique)
    good_list = []
    bad_list = []

    for ln in Name_list_unique:
        match = re.match('^(?P<STN1>\w{3,4}?)_?(?P<volt>\d{3})_(?P<STN2>\w{3,4}?)(?P<id>\d)?$', ln)
        if match:
            volt = convert_voltage_level_to_letter(int(match.group('volt')))
            ets_name = f"{volt}_{match.group('STN1')}-{match.group('STN2')}"
            if match.group('id') is not None:
                ets_name += f'-{match.group("id")}'
            good_list.append(ets_name)
        else:
            bad_list.append(ln)

    print(f'First list {good_list}\n')
    print(f'Second list {bad_list}\n')



    translated_gis_name_list = ''
    return translated_gis_name_list

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(name)s - %(message)s')
    log.setLevel(logging.INFO)

    convert_gis_name_to_ets_name(GIS_FILEPATH)

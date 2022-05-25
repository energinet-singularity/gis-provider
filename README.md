# GIS-provider
This container parses a file containing GIS data into a pandas dataframe, enrich it with meta data and provides access to it through an API.

## Description
This repository contains a python-script that will read a proprietary GIS dataset from a given file, convert it to a pandas dataframe and then prepare it for access through an API. The line-names from the GIS file are translated via a regex (regular expression) and a mapping file into an "ETS" name, while a third file can be used to enforce a fixed translation of GIS to ETS line name.\
The script is intended to be run within a kubernetes setup, so a Dockerfile is provided as well, as is a set of helm charts.

### Exposed environment variables
| Name | Description | Default |
|--|--|--|
|API_DB_NAME|Name of the dataframe/table in the API|GIS_DATA|
|API_PORT|The port that the API is exposed to|5000|
|MOCK_DATA|Set to 'TRUE' to use included test-data for mocking|FALSE|
|DEBUG|Set to 'TRUE' to enable debug logging|FALSE|
<br/>

#### Variables for the data that should be enriched
| Name | Description | Default |
|--|--|--|
|GIS_FILENAME|Name of the file containing GIS data|GIS_Driftstr_luftledning_koordinater_decimalgrader_05042022.xls|
|GIS_SHEET|Name of the sheet containing GIS data|GIS_Driftstr_luftledning_koordi|
|GIS_COLUMN_NAME|The column name to identify which column is going to be translated|Name|
<br/>

#### ETS mapping environment variables 
| Name | Description | Default |
|--|--|--|
|ETS_FILENAME|Filename of the csv file|seg_line_mrid_PROD.csv|
|ETS_COLUMN_DLR_ENABLED|Name of column indicating if DLR should be enabled or not|DLR_ENABLED|
|ETS_COLUMN_MRID|Name of the column containing the unique identifier|ACLINESEGMENT_MRID|
|ETS_COLUMN_NAME|The column name that is going to link the two files together|LINE_EMSNAME|
<br/>

#### Mapping variables to enforce a specific translation
| Name | Description | Default |
|--|--|--|
|MAP_FILENAME|Name of the mapping file|Gis_map.xlsx|
|MAP_COLUMN_GIS_NAME|Name of the column with existing translated name in the GIS dataframe|GIS Name|
|MAP_COLUMN_ETS_NAME|Name of the column that state the new translated name|ETS Name|
|MAP_SHEET|Specific sheet to use in the excel file|GisMapping|

### Input
The script takes three files as input:
- The GIS excel file
- The ETS csv file containing ETS name, MRID and enabled (Yes/No) state for each line
- A mapping/translation file to forced translation of specific names (this file is optional)

For more information on how the files are structured please look into the tests/valid-testdata folder that is supplied in the repository.

### Output
The output will be an API that can be queried with SQL to get information from the enriched GIS dataframe.

## Getting Started
The quickest way to have something running is through docker (see the section [Running container](#running-container)).

Feel free to either import the python-file as a lib or run it directly - or use HELM to spin it up as a pod in kubernetes. These methods are not documented and you will need the know-how yourself.

### Dependencies
* Custom 'singupy' python module, available here: https://github.com/energinet-singularity/singupy
* The files mentioned under [Input](#input). It is possible to mock a set of input files with the MOCK_DATA environment variable.

#### Python (if not run as part of the container)
The python script can probably run on any python 3.9+ version, but your best option will be to check the Dockerfile and use the same version as the container. Further requirements (python packages) can be found in the app/requirements.txt file.

#### Docker
Built and tested on version 20.10.7.

#### HELM (only relevant if using HELM for deployment)
Built and tested on version 3.7.0.

### Running container
Below you will see two options to spin up the container locally, one with using your own data and one with using built in mock data.

#### Using own data source
1. Clone the repository to a suitable place
````bash
git clone https://github.com/energinet-singularity/gis-provider.git
````

2. Build the container and create a volume
````bash
docker build gis-provider/ -t gis-provider
docker volume create gis-provider-pvc
````

3. Start the container in docker (change the environment variables to fit your setup, see section [Exposed environment variables](#exposed-environment-variables))
````bash
docker run -v gis-provider-pvc:/data/ -it --rm gis-provider:latest
````
The container will now be running interactively and you will be able to see the log output. To start sending files through, you will have to supply files to the created volume. This can be done with 'cp' if you have sudo rights to the system you are spinning up the container.

#### Using mock data
1. Clone the repository to a suitable place
````bash
git clone https://github.com/energinet-singularity/gis-provider.git
````

2. Build the container
````bash
docker build gis-provider/ -t gis-provider
````

3. Start the container in docker
````bash
docker run -e MOCK_DATA=True -it --rm gis-provider:latest
````
The container will now be running interactively and you will be able to see the log output while the container runs.

#### SQL commands
When the container is running in your local environment you can use the following bash command to query data from it. The example below assumes you are using Mock data with default settings, please change "localhost" with the IP that your API is running on.

````bash
 curl -d '{"sql-query": "SELECT * FROM GIS_DATA;"}' -H 'Content-Type: application/json' -X POST http://localhost:5000/
````
For more information regarding the API setup and structure, refer to the custom module at https://github.com/energinet-singularity/singupy

## Help
See the open issues for a full list of proposed features (and known issues). 
If you are facing unidentified issues with the application, please submit an issue or ask the authors.

## Version History
* 1.0.0:
    * First production-ready version

## License
This project is licensed under the Apache-2.0 License - see the LICENSE.md file for details.

# Templated repo <!-- Change to repo name! -->

<!-- Insert a very short description of what the script/repo is for -->

<!-- TABLE OF CONTENTS -->
<!--
If VERY heavy readme, update and use this TOC
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>
-->

## Description

<!--
-- Insert a more detailed description here, and use the below headers where relevant --

### Exposed environment variables

|Name|Default|Description|
|--|--|--|

### Input

### Output

-->

<!-- GETTING STARTED -->
## Getting Started

The quickest way to have something running is through docker (see the section [Running container](#running-container)).

Feel free to either import the python-file as a lib or run it directly - or use HELM to spin it up as a pod in kubernetes. These methods are not documented and you will need the know-how yourself (the files have been prep'ed to our best ability though).

### Dependencies

<!-- Describe general dependencies here - what is neeeded to run the script/container/helm? -->
  
#### Python (if not run as part of the container)

The python script can probably run on any python 3.9+ version, but your best option will be to check the Dockerfile and use the same version as the container. Further requirements (python packages) can be found in the app/requirements.txt file.

#### Docker

<!--
Describe here what is needed before it can be run in docker - environment variables, volumes etc.

Give an example if relevant:

Example:
```sh
docker run my_script -v someVolume:/data -e MYVAR=smith"
```
 -->

#### HELM (only relevant if using HELM for deployment)

<!--
Describe here what is needed before it can be run in docker - environment variables, volumes etc.

You could use this:
The default helm values/properties are set in a way that allows the helm chart to be installed and run without crashes, but it will not be useful. To spin up the environment with helm, make sure to set (or overwrite) values to something meaningful.
-->


### Running container

<!-- PLEASE REMEMBER TO UPDATE THIS GUIDE!!! -->

1. Clone the repo to a suitable place
````bash
git clone http://myrepo.git
````

2. Build the container
````bash
docker build my_script -t my_script:latest
````

3. Start the container in docker (change variables to fit your environment)
````bash
docker run -e MYVAR=foo -it --rm my_script:latest
````

## Help
<!-- replace 'open issues' below with link like this: [open issues](https://github.com/energinet-singularity/<repo-name>/issues) -->
See the open issues for a full list of proposed features (and known issues).
If you are facing unidentified issues with the application, please submit an issue or ask the authors.

## Version History

* 0.0.1:
    * First ever version - nice!

## License

This project is licensed under the Apache-2.0 License - see the LICENSE and NOTICE file for further details.

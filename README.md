# Docker container for the RISICO model

This repo contains a Docker container that allow to run the RISICO model using WRF output.

## Content of the repo

* src: source directory for the containers
  * RISICO2015: RISICO binary
  * adapter: input and ouput python adapters for RISICO
  * risico: static data and configuration for the RISICO model
* build.sh: build script for the container
* run.sh: run script for the RISICO model inside the container

## Build

To build the image, after you clone the repo locally, run the ```build.sh``` shell script

## Run RISICO

* Create a ```data``` folder in the host machine
* Copy the WRF output to the ```data/wrf``` directory
* ```data/wrf``` directory should contain a folder for each worf model run used, e.g. 20200615, 20200616, 20200617 etc
* Copy the observations netcdf to the ```data/observations``` directory
* Run the model in your host, replacing ```/path/to/data/```with the absolute path of the data directory and 
```RUNDATE``` in YYYYMMDDHHMM format (HH and MM should be 0000).
```bash
  docker run  -it \
    -v /path/to/data/:/home/risico/data \
    risico \
    $RUNDATE
```
* the output of the RISICO model will be placed in the data/output directory

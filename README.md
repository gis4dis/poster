# Poster

Application for geo-spatial data collection and processing. 

## requirements

Python 3.2+ due to folder creation.

## How to run local dev environment (docker-compose).
3 basic docker(-compose) commands that are needed for developing

### 1) `docker-compose -f stack.yml up`
Run whole cluster { Django + Celery + Redis + Postgis + (Mongo) } 
If it runs the first time, it will also build "web" docker container.


### 2) `docker-compose -f stack.yml build`
Rebuilds "web" docker container.
 
Rebuilding of the container is needed when changing "requirements.txt".
(See Dockerfile)

### 3) `docker-compose -f stack.yml rm -v`
This command removes created temporary volumes. 
Sometimes is needed after new builds.



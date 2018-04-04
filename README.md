# Poster

Application for geo-spatial data collection and processing. 

## Requirements for production

* Python 3.2+

## Requirements for local development
* docker (https://www.docker.com/community-edition#/download)
  * Linux post-install: [enable Docker for non-root user](https://docs.docker.com/install/linux/linux-postinstall/)
* docker-compose (https://docs.docker.com/compose/install/)

both installed on localhost.

## How to run local dev environment

- run
```bash
git clone git@github.com:gis4dis/poster.git
cd poster

# copy exapmle.env as .env - it should have reasonable defaults.
cp example.env .env
```

- If you have PostgreSQL (or something else) running at local port 5432, stop it.

- run
```bash 
# Run the whole cluster on localhost { Django + Celery + Redis + Postgis + (Mongo) }.
# The first run will also runs `docker-compose build` automatically, which builds the "web" docker container and downloads other containers.
docker-compose up

# Make django migrations (creates DB structures).
./dcmanage.sh migrate

# Create Django superuser
./dcmanage.sh createsuperuser
```
- Login with superuser at http://localhost:8000/admin

- You can also import some data with `./dcmanage.sh ala_import` and check it at http://localhost:8000/admin/ala/observation/.


### Other basic commands

#### `docker-compose build`
(Re)builds the "web" docker container.

This will (re)build the web docker image with new 
 *requirement.txt* file

For more information see *Dockerfile*.

#### `docker-compose rm -v`
This command removes created temporary volumes that were
 attached to docker containers.
 
When the docker containers are not properly shut, 
 the attached volume(s) can in some cases stay
 detached but created and running `docker-compose up` will
 end with error, complaining about "same volume names".

### Advanced commands

#### `docker-compose up | tee docker.log`

Taken from `man tee` page:

|*tee - read from standard input and write to standard output and files*

This command will send output (logs) of all docker containers to:
* terminal
* file `docker.log`

You can use this log file to further examine and filter logs with your
 favorite tool. (grep, less, ...)
 The logfile will get erased on every new run (feature).
 
#### `less -R docker.log` + `&search-term⏎`

This will open *docker.log* file in less (-R flag preserves 
 the terminal colors). Then you can you in-build filter function
 to obtain only the logs you are interested in.

#### `sudo docker-compose logs --tail 20 poster_celery_worker`
This will display last 20 log messages from `poster_celery_worker` service.
 You can find the service names in *docker-compose.yml* file as well as in
 the log prepended on each line. 
 
If you omit the `--tail #` flag it will display **all logs** 
 from **all previous runs**. Use it with caution.

#### Import DB dump
```
psql postgres://postgres:postgres@localhost:5432/postgres < /path/to/dump
```

## Top level files

### *.buildpacks*
Buildpacks are used when building slug for deployment. Below are some examples.

```
https://github.com/heroku/heroku-buildpack-apt
https://github.com/mojodna/heroku-buildpack-gdal.git
https://github.com/heroku/heroku-buildpack-python.git#009d0ddb
https://github.com/heroku/heroku-buildpack-python.git
https://github.com/weibeld/heroku-buildpack-run.git
```

### *Aptfile*
 * used by *https://github.com/heroku/heroku-buildpack-apt*

Contains list of "to-be-installed" apt packages for the build.

### *buildpack-run.sh*
 * used by *https://github.com/weibeld/heroku-buildpack-run.git*

Contains shell script that will be run on build.

### *dcmanage.sh*
Shell wrapper for docker-compose commands that shoud be used to run "manage.py" commands
but on development docker environment

### *docker-compose.yml*
Basic docker-compose file used to spin up development environment.

### *example.env*
Example environment variable settings for the application.

### *manage.py*
Standard Django manage.py script
 * used by *https://github.com/heroku/heroku-buildpack-python.git*

### *Procfile*
Processes defined to be run on container deployment to server

### *requirements.txt*
Python dependencies file.
 * used by *https://github.com/heroku/heroku-buildpack-python.git*

### *runtime.txt*
Python runtime version dependency.
 * used by *https://github.com/heroku/heroku-buildpack-python.git*

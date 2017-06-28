# Poster
Application that accepts POST requests for data collection.

## requirements

Python 3.2+ due to folder creation.

See https://docs.python.org/3/library/os.html#os.makedirs

# Installation
Clone the repository

## git clone
```
git clone https://github.com/gis4dis/poster poster
cd poster
```

## Running application on localhost

This is standard Django application. So ideally we need to install Python 3 virtualenv first

### Virtualenv
Python 3.3+ has module `venv` included for this purpose. On older Pythons consult internet how to create virtualenv.
```
python3 -m venv /path/to/env/poster
source /path/to/env/poster/bin/activate
```

### Requirements.txt
After activation of virtualenv we can install all python requirements from file.
But first update pip, since older versions have some bugs.
```
pip install --upgrade pip
pip install -r requirements.txt
```

### configure local_settings.py
Django needs local_settings.py for custom properties that are specific only for this environment.
Sensible details can be found in local_settings_example.py so copy it to local_settings.py in the same folder.

```
cp src/poster/local_settings{_example,}.py
```
and set `DEBUG = True` and `SECRET_KEY` to some random unpredictable string.
See more at: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key

### running dev server
Then you can run local development server:
```
cd src
python ./manage.py runserver
```

## Running application on server (prepared by kickup)

The virtual environment is already prepared for this app in the folder 
`/opt/poster-app/viertualenv`, so we don't need to install this by ourselves.

Ideally clone the application into `/opt/poster-app/poster` directory so you can use 
included deployment script (`scripts/deploy.sh`). Otherwise you need to update the scripts with proper PATHS.

### deploy
You don't want to use git as primary source for your deployment. Generally it is not a good practise 
to expose your .git folder (although the git is publicly available). So the deployment script has 3 basic functions.

* `./deploy web`
  * This will pull the master branch and run dry rsync, which lists all the changes that will be done.
* `./deploy web go`
  * This will run rsync and override/delete all the files listed previously
* `./deploy web manage`
  * This command runs Django's collect static and migrate commands (interactively)
  
### configure local_settings.py
Setup needed local_settings.py for custom properties on the server.
Copy local_settings_example.py and update the values to fit the needs.

```
cp /opt/poster-app/src/poster/local_settings{_example,}.py
vim /opt/poster-app/src/poster/local_settings.py
```

### create symlink
As a "I know what I am doing" safety, you need to point to correct wsgi.py entrypoint.
The server (uwsgi) expects the main application entrypoint at /opt/poster-app/src/wsgi.py
The Django application has its own wsgi.py located at /opt/poster-app/src/poster/wsgi.py
so we make a symlink to required path
```
rm /opt/poster-app/src/wsgi.py
ln -s /opt/poster-app/src/poster/wsgi.py /opt/poster-app/src/wsgi.py
```


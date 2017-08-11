# Poster
Application that accepts POST requests for data collection.

## requirements

Python 3.2+ due to folder creation.

See https://docs.python.org/3/library/os.html#os.makedirs

# Installation
Installation differs in some parts if you want to run this on localhost or prod server.
But it is standard Django application. So the steps are:

1) Clone repository
2) create and install Python 3 virtualenv
3) configure `local_settings.py`
4) run application


## Running application on localhost

### 1) Clone repository
```
git clone https://github.com/gis4dis/poster poster
```

### 2) create and install Python 3 virtualenv

Python 3.3+ has module `venv` included for this purpose. (For older Python versions
consult the internet on how to create virtualenv.)

```
python3 -m venv /path/to/env/poster
source /path/to/env/poster/bin/activate
```

After activation of virtualenv we can install all python requirements from file.
But first update pip, since older versions have some bugs.
```
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required Python packages for the application.

### 3) configure `local_settings.py`
Django has its basic configuration in file called `settings.py`. There is all the
configuration for application. Most of the parts of the configuration can be used
on all environments (local development, testing, production ...) But some parts
are specific only for some environments (Logging, paths, etc.). Because of this
there is second file you need to create called `local_settings.py`.

There is a template `local_settings_example.py` which you can copy and use as
starting point. Actually for local development you can just copy the file and
make just minor changes.

```
cp src/poster/local_settings{_example,}.py
```

and set `DEBUG = True` and `SECRET_KEY` to some random unpredictable string.
See more at: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key

The nice and simple *python code* `SECRET_KEY` generator can be found on:
http://techblog.leosoto.com/django-secretkey-generation/

Here it is:
```
python -c 'import random; import string; print "".join([random.SystemRandom().choice(string.digits + string.letters + string.punctuation) for i in range(100)])'
```

### 4) running local dev server
Django has local development server included so you can just run:
```
cd src
python ./manage.py runserver
```

## Running the application on server (prepared by kickup)

Here is one more step which includes deploying the source code from cloned git repo.
You don't want to use git as primary source for your deployment. Generally it is not
a good practise to expose your .git folder (although the git is publicly available).
**2.5) deploy**

```
sudo su poster-app
```

### 1) Clone repository
Ideally clone the application into `/opt/poster-app/poster` directory so you can use
included deployment script (`scripts/deploy.sh`).
Otherwise you need to update this scripts with proper PATHS.

```
git clone https://github.com/gis4dis/poster /opt/poster-app/poster
```

### 2) create and install Python 3 virtualenv

The virtual environment is already prepared for this app in the folder
`/opt/poster-app/virtualenv`, so we don't need to install this by ourselves.


### 2.5) deploy
Deployment script has 3 basic functions.

* `./deploy web`
  * This will pull the master branch and run dry rsync, which lists all the changes that will be done.
* `./deploy web go`
  * This will run rsync and override/delete all the files listed previously
* `./deploy web manage`
  * This command runs Django's collect static and migrate commands (interactively)

Now we need to run only first two, so run:
```
./deploy web
./deploy web go
```
don't run `./deploy web manage` yet, since you need to configure the `local_settings.py` in next step

### 3) configure local_settings.py
Setup needed local_settings.py for custom properties on the server.
Copy local_settings_example.py and update the values to fit the needs.

```
cp /opt/poster-app/src/poster/local_settings{_example,}.py
vim /opt/poster-app/src/poster/local_settings.py
```

### 3.5) deploy run manage
Now you can run manage script:
```
./deploy web manage
```

This will copy staticfiles to correct directory and prepare database.

If you are using sqlite, check the database file has correct owner:
```
chown poster-app:poster-app /opt/poster-app/db.sqlite3
```

### 4) Final touches

Create import folder by default in /opt/poster-app/import and set proper chown.
(this should match the path you've set in `local_setting.py`)
This folder will be used for imported data, so it also needs proper write access

```
mkdir /opt/poster-app/import
chown poster-app:poster-app /opt/poster-app/import
chmod 0770 /opt/poster-app/import
```

As a "I know what I am doing" safety, you need to point to correct wsgi.py entrypoint.
The server (uwsgi) expects the main application entrypoint at /opt/poster-app/src/wsgi.py
The Django application has its own wsgi.py located at /opt/poster-app/src/poster/wsgi.py
so we make a symlink to required path

```
rm /opt/poster-app/src/wsgi.py
ln -s /opt/poster-app/src/poster/wsgi.py /opt/poster-app/src/wsgi.py
chown poster-app:poster-app /opt/poster-app/src/wsgi.py -h
```

And as last thing we create touch-to-update file, which when touched will reload
the uwsgi with the new content.
```
touch /opt/poster-app/version.py
```

# Summary
```
sudo su poster-app
source /opt/poster-app/virtualenv/bin/activate

git clone https://github.com/gis4dis/poster /opt/poster-app/poster
cd /opt/poster-app/poster/scripts/

pip install -r /opt/poster-app/src/requirements.txt

./deploy.sh web
./deploy.sh web go

cp /opt/poster-app/src/poster/local_settings{_example,}.py
vim /opt/poster-app/src/poster/local_settings.py


./deploy.sh web manage

mkdir /opt/poster-app/import
chown poster-app:poster-app /opt/poster-app/import
chmod 0770 /opt/poster-app/import

rm /opt/poster-app/src/wsgi.py
ln -s /opt/poster-app/src/poster/wsgi.py /opt/poster-app/src/wsgi.py
chown poster-app:poster-app /opt/poster-app/src/wsgi.py -h

touch /opt/poster-app/version.py

```

# Summary v2

```
vagrant up
vagrant reload
vagrant ssh

sudo su poster-app
pip install -r /opt/poster-app/src/requirements.txt

cp /opt/poster-app/src/poster/local_settings{_example,}.py
vim /opt/poster-app/src/poster/local_settings.py

mkdir /opt/poster-app/import
chown poster-app:poster-app /opt/poster-app/import
chmod 0770 /opt/poster-app/import

rm /opt/poster-app/src/wsgi.py
ln -s /opt/poster-app/src/poster/wsgi.py /opt/poster-app/src/wsgi.py
chown poster-app:poster-app /opt/poster-app/src/wsgi.py -h

cd /opt/poster-app/src/

python manage.py migrate
python manage.py collectstatic
touch /opt/poster-app/version.py

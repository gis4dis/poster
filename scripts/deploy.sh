ERRORSTRING="Usage: ./deploy web [go|manage|django]"

if [ $# -eq 0 ]
    then
        echo $ERRORSTRING;
elif [ $1 == "web" ]
    then
        if [[ -z $2 ]]
            then
                git pull
                echo "Running dry-run"
                rsync --dry-run -az --force --delete --progress --exclude-from=deploy_exclude.txt ../src/ /opt/poster-app/src
        elif [ $2 == "go" ]
            then
                echo "Running actual deploy"
                rsync -az --force --delete --progress --exclude-from=deploy_exclude.txt ../src/ /opt/poster-app/src
        elif [ $2 == "manage" ]
            then
                echo "Running manage scripts"
                source /opt/poster-app/virtualenv/bin/activate
                cd /opt/poster-app/src; python manage.py collectstatic -c; python manage.py migrate --noinput
                chown poster-app:poster-app /opt/poster-app/src -R
                touch /opt/poster-app/version.py
        elif [ $2 == "django" ]
            then
                echo "Running django command"
                source /opt/poster-app/virtualenv/bin/activate
                cd /opt/poster-app/src
                python manage.py $3

        else
            echo $ERRORSTRING;
        fi
fi

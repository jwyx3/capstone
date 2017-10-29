# package
* apt-get install python3-dev libmysqlclient-dev

# setup
* start celery worker: `celery -A backend worker -l info`
* start celery beat: `$ celery -A backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`
* `python manage.py createsuperuser`

# setup mysql
* run: `docker exec -i mysql mysql --password=passw0rd < ./setup.sql`

# some issues:
* ValueError: The database backend does not accept 0 as a value for AutoField.
  * Edit the migration file and remove the argument default=0 in AddField operations.
* django.db.utils.OperationalError: (1050, "Table 'api_ad' already exists")
  * `python manage.py migrate --fake-initial` 
* ImportError: cannot import name '__check_build'
  * install scipy [link](https://stackoverflow.com/questions/15274696/importerror-in-importing-from-sklearn-cannot-import-name-check-build)
* find which column has NaN
  * `pd.isnull(df).sum() > 0`
  
# deployment
* [checklist](https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/)
  
# TODO
* error logging
* performance - more cache
* monitoring
* test casehttp://www.tocker.ca/2014/03/10/configuring-mysql-to-use-minimal-memory.html

# TODO: feature
* alert
* training dashboard

# mysql min
* [min.cnf in mysqld](http://www.tocker.ca/2014/03/10/configuring-mysql-to-use-minimal-memory.html)

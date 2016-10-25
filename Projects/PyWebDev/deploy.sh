# FILE: deploy.sh

# SERVER SPECIFIC VARIABLES
SERVER=localhost 						# TODO set your server here!
PORT1=3000 												# TODO set your ports here!

# GROUP VARIABLES
GROUP=root											# TODO set you group number
SECRET=root 										# TODO set your secret

# STATIC RESOURCE paths									# TODO make sure you have a backup folder
IMAGES=static/images									# and that the paths are correct
IMAGES_BACKUP=static/images_backup

# SQL SCRIPT PATH										# TODO make sure paths are correct
SQL_CREATE=sql/tbl_create.sql
SQL_LOAD=sql/load_data.sql

# ASSIGNMENT VARIABLES
PROJECT=p3												# TODO project number here (for sql)


echo "Resetting static resources from backup..."
rm $IMAGES/*
cp $IMAGES_BACKUP/* $IMAGES/
echo "Done."


echo "Resetting SQL database..."
SQL_QUERY="drop database $GROUP$PROJECT; create database $GROUP$PROJECT; use $GROUP$PROJECT; source $SQL_CREATE; source $SQL_LOAD;"
mysql -u $GROUP -p"$SECRET" -e "$SQL_QUERY"
echo "Done."

echo "Starting server on $SERVER"
python app.py
echo "Done."

import MySQLdb
import MySQLdb.cursors
import config
import os
import hashlib
import uuid
from werkzeug.utils import secure_filename
from flask import url_for

def connect_to_database():
    options = {
        'host': config.env['host'],
        'user': config.env['user'],
        'passwd': config.env['password'],
        'db': config.env['db'],
        'cursorclass' : MySQLdb.cursors.DictCursor
    }
    db = MySQLdb.connect(**options)
    db.autocommit(True)
    return db
db = connect_to_database();


# this method should return a list of all users from database
def get_users_list():
    c = db.cursor();
    c.execute("SELECT username FROM User;");
    results = c.fetchall();
    users = [];
    for row in results:
        users.append(row['username']);
    return users;


def does_user_exist(username):
    c = db.cursor();
    c.execute("SELECT username FROM User WHERE username = '{}';".format(username));
    result = c.fetchone();
    if result is None:
        return False
    else:
        return True

# given a username, this method should return a list of albums that belong to this user, 
# include title and albumid and access
def get_albums_list(username):
    c = db.cursor();
    c.execute("SELECT title, albumid, access, lastupdated FROM Album WHERE username = '{}';".format(username));
    results = c.fetchall();
    return results;


# this method should delete the album with given albumid from the database, albumid is a string
def delete_album(albumid):
    c = db.cursor();
    c.execute("SELECT p.picid, p.format FROM Photo p LEFT JOIN Contain c ON c.picid = p.picid WHERE c.albumid = {};".format(albumid));
    results = c.fetchall();
    for f in results:
        filename = f['picid'] + '.' + f['format'];
        os.remove(os.path.join(config.env['IMAGE_FOLDER'], filename));

    c.execute("DELETE c.*, p.* FROM Contain c LEFT JOIN Photo p ON p.picid = c.picid WHERE c.albumid = {};".format(albumid));
    c.execute("DELETE FROM AlbumAccess where albumid = {};".format(albumid));
    c.execute("DELETE FROM Album where albumid = {};".format(albumid));
    print(albumid)
    pass


# this method should add a new album to the database, given username and title
def add_album(username, title):
    c = db.cursor();
    c.execute("INSERT INTO Album (title, username) VALUES('{}', '{}');".format(title, username));
    print(username)
    print(title)


def does_album_exist(albumid):
    c = db.cursor();
    c.execute("SELECT albumid FROM Album WHERE albumid = {};".format(albumid));
    result = c.fetchone();
    if result is None:
        return False;
    return True;


def does_pic_exist(picid):
    c = db.cursor();
    c.execute("SELECT picid FROM Photo WHERE picid = '{}';".format(picid));
    result = c.fetchone();
    if result is None:
        return False;
    return True;


# this method should return a list of photos given an albumid, the photo should include picid and format, date and caption
def get_photos_list(albumid):
    c = db.cursor();
    c.execute("SELECT Contain.albumid, Contain.caption, Photo.date, Photo.format, Photo.picid, Contain.sequencenum FROM Photo JOIN Contain ON Photo.picid = Contain.picid WHERE Contain.albumid = {};".format(albumid));
    results = c.fetchall();
    return results;


# this method should return the album id that a picture belongs to (given the picid)
def get_album_id(picid):
    c = db.cursor();
    c.execute("SELECT albumid FROM Contain WHERE picid = '{}';".format(picid));
    result = c.fetchone();
    return result['albumid'];


# this method should delete the photo from database and the static/images/ folder
# albumid and picid are given
def delete_photo(albumid, picid):
    c = db.cursor();
    c.execute("SELECT format FROM Photo WHERE picid = '{}';".format(picid));
    result = c.fetchone();
    fmt = result['format'];
    os.remove(os.path.join(config.env['IMAGE_FOLDER'], picid + '.' + fmt));
    
    c.execute("DELETE FROM Contain WHERE albumid = {} AND picid = '{}';".format(albumid, picid));
    c.execute("DELETE FROM Photo WHERE picid = '{}';".format(picid));


# this method should save the image to both the database and the static/images folder, remember renaming the image as hash.format
def save_photo(upload_file, albumid):
    c = db.cursor();
    filename = secure_filename(upload_file.filename)
    m = hashlib.md5(str(albumid) + filename)
    c.execute("SELECT * FROM Photo WHERE picid = '{}';".format(m.hexdigest()));
    results = c.fetchall();
    if len(results) > 0:
        return;
    fmt = (filename.split('.'))[1];
    upload_file.save(os.path.join(config.env['IMAGE_FOLDER'], m.hexdigest() + '.' + fmt))
    
    c.execute("INSERT INTO Photo (picid, format) VALUES ('{}', '{}');".format(m.hexdigest(), fmt));
    c.execute("INSERT INTO Contain (albumid, picid) VALUES ({}, '{}');".format(albumid, m.hexdigest()));


# this method should get public albums id in database
def get_all_public_albums():
    c = db.cursor();
    c.execute("SELECT albumid, title FROM Album WHERE access = 'public';");
    results = c.fetchall();
    return results;


# return all the private albums id for this user
def get_private_albums(username):
    c = db.cursor();
    c.execute("SELECT albumid, title FROM Album WHERE username = '{}' AND access = 'private';".format(username));
    results = c.fetchall(); 
    return results;


# return all the shared private albums' id for this user
def get_shared_private_albums(username):
    c = db.cursor();
    c.execute("SELECT a.albumid, a.title FROM Album a LEFT JOIN AlbumAccess c ON a.albumid = c.albumid WHERE c.username = '{}';".format(username));
    results = c.fetchall();
    return results;


# return all the information about this user, { "first name", firstname; "last name", lastname}
def get_user_info(username):
   c = db.cursor();
   c.execute("SELECT firstname, lastname, email FROM User WHERE username = '{}';".format(username));
   result = c.fetchone();
   return result;


# if this username exists, return True; Otherwise, False
def does_username_exist(username):
    c = db.cursor();
    c.execute("SELECT username FROM User WHERE username = '{}';".format(username));
    result = c.fetchone();
    if result is None:
        return False
    else:
        return True


# check if the username and password is correct
def check_login(username, password):
    c = db.cursor();
    if does_username_exist(username) == False:
        return False;
    c.execute("SELECT password FROM User WHERE username = '{}';".format(username));
    result = c.fetchone();
    algorithm, salt, md5 = result['password'].split('$');
    
    m = hashlib.new(algorithm);
    m.update(salt + password);
    password_hash = m.hexdigest();
    
    if password_hash == md5: 
        return True
    else:
        return False
    
# create a new user, user_info is a dict
# the user_info contains username, first name, last name, password1, password2, email
# all the checks have been completed: password1 equals to password2
def create_user(user_info):
    c = db.cursor();
    algorithm = 'sha512';
    salt = uuid.uuid4().hex;
    
    m = hashlib.new(algorithm);
    m.update(salt + user_info['password1'])
    password_hash = m.hexdigest();

    password_database = algorithm + '$' + salt + '$' + password_hash;
    
    c.execute("INSERT INTO User (username, firstname, lastname, password, email) VALUES ('{}', '{}', '{}', '{}', '{}');".format(user_info['username'], user_info['firstname'], user_info['lastname'], password_database, user_info['email']));
    

# update a user
# the user_info must have username, it may contain firstname/lastname/password1/password2/email
# all the checks have been completed: password1 equals to password2
def update_user(user_info):
    c = db.cursor();
    # if update password, need to generate new md5
    if ('password1' in user_info and user_info['password1'] != ""):
        algorithm = 'sha512';
        salt = uuid.uuid4().hex;
        m = hashlib.new(algorithm);
        m.update(salt + user_info['password1']);
        password_hash = m.hexdigest();
        password_database = algorithm + '$' + salt + '$' + password_hash;
        c.execute("UPDATE User SET password = '{}' WHERE username = '{}';".format(password_database, user_info['username']));
    if ('firstname' in user_info):
        c.execute("UPDATE User SET firstname = '{}' WHERE username = '{}';".format(user_info['firstname'], user_info['username']));
    if ('lastname' in user_info):
        c.execute("UPDATE User SET lastname = '{}' WHERE username = '{}';".format(user_info['lastname'], user_info['username']));
    if ('email' in user_info):
        c.execute("UPDATE User SET email = '{}' WHERE username = '{}';".format(user_info['email'], user_info['username']));
    

# given a username, this method should return a list of public albums that belong to this user, 
# include title and albumid
def get_public_albums_list(username):
    c = db.cursor();
    c.execute("SELECT albumid, title FROM Album WHERE access = 'public' AND username = '{}'".format(username));
    return c.fetchall();


# set an album to be public, delete all the perimissions given to users(from albumAccess)
def set_album_public(albumid):
    c = db.cursor();
    c.execute("DELETE FROM AlbumAccess WHERE albumid = {}".format(albumid));
    c.execute("UPDATE Album SET access = 'public' WHERE albumid = {}".format(albumid));


# set an album to be private
def set_album_private(albumid):
    c = db.cursor();
    c.execute("UPDATE Album SET access = 'private' WHERE albumid = {}".format(albumid));


# return if this album belongs to the user
def check_album_belong(username, albumid):
    c = db.cursor();
    c.execute("SELECT username FROM Album WHERE albumid = {}".format(albumid));
    result = c.fetchone();
    return username == result['username'];


# return a dictionary with all the album's informations in it
# {"title", "created", "lastupdated", "access"}
# get_album_title can be deleted if this function is done
def get_album_info(albumid):
    c = db.cursor();
    c.execute("SELECT username, title, created, lastupdated, access FROM Album WHERE albumid = {}".format(albumid));
    return c.fetchone();


# return a list of users that are granted to visit the private album
# this album is guaranteed to be private
def get_grant_users_list(albumid):
    c = db.cursor();
    c.execute("SELECT username FROM AlbumAccess WHERE albumid = {}".format(albumid));
    result = c.fetchall();
    users = [];
    for u in result:
        users.append(u['username']);
    return users;


# allow a user to visit this private album
def grant_user_album(username, albumid):
    c = db.cursor();
    c.execute("SELECT albumid FROM Album WHERE username = '{}' AND albumid = '{}';".format(username, albumid));
    # if this album belongs to the user
    result = c.fetchone();
    if result is not None:
        return;

    c.execute("SELECT username FROM AlbumAccess WHERE albumid = {} AND username = '{}';".format(albumid, username));
    result = c.fetchone();
    if result is None:
        c.execute("INSERT INTO AlbumAccess (username, albumid) VALUES ('{}', {});".format(username, albumid));
    else:
        return;


# revoke a user from visiting this private album
def revoke_user_album(username, albumid):
    c = db.cursor();
    c.execute("DELETE FROM AlbumAccess WHERE username = '{}' AND albumid = {};".format(username, albumid));

# update the caption for a picture
def update_pic_caption(picid, caption):
    c = db.cursor();
    c.execute("SELECT albumid FROM Contain WHERE picid = '{}';".format(picid));
    result = c.fetchone();
    albumid = result['albumid'];
    c.execute("UPDATE Album SET lastupdated = CURRENT_TIMESTAMP WHERE albumid = {};".format(albumid));
    c.execute("UPDATE Contain SET caption = '{}' WHERE picid = '{}';".format(caption, picid));

# get photo information from picid
# picid is guaranteed to be existed
def get_photo_info(picid):
    c = db.cursor();
    c.execute("SELECT format FROM Photo WHERE picid = '{}';".format(picid));
    result = c.fetchone();
    fmt = result['format'];
    c.execute("SELECT albumid, caption FROM Contain WHERE picid = '{}';".format(picid));
    result = c.fetchone();
    aid = result['albumid'];
    cpt = result['caption'];
    return {"albumid": aid, "format": fmt, "caption": cpt};


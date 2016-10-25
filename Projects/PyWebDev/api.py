from flask import *
from flask import json
import extensions
import validation

api = Blueprint('api', __name__, template_folder='templates')

error_messages = {'1': 'This username is taken', '2': 'Usernames must be at least 3 characters long', '3': 'Usernames may only contain letters, digits, and underscores', '4': 'Passwords must be at least 8 characters long', '5': 'Passwords must contain at least one letter and one number', '6': 'Passwords may only contain letters, digits, and underscores', '7': 'Passwords do not match', '8': 'Email address must be valid', '9': 'Username must be no longer than 20 characters', '10': 'Firstname must be no longer than 20 characters', '11': 'Lastname must be no longer than 20 characters', '12': 'Email must be no longer than 40 characters'};

@api.route('/api/v1/user', methods = ['GET', 'POST', 'PUT'])
def user_api():
    errors = [];
    if request.method == 'GET':
        if 'username' in session:
        # there is a valid session
            user_info = extensions.get_user_info(session['username']);
            return json.jsonify(username=session['username'],
                                firstname=user_info['firstname'],
                                lastname=user_info['lastname'],
                                email=user_info['email']);
        # if not valid 
        else:
            errors.append({"message": "You do not have the necessary credentials for the resource"});
            return json.jsonify(errors=errors), 401;

    elif request.method == 'POST':
        data = request.json;
        if ('username' not in data or 'password1' not in data or 'password2' not in data or 'firstname' not in data or 'lastname' not in data or 'email' not in data):
            errors.append({"message": "You did not provide the necessary fields"});
            return json.jsonify(errors=errors), 422;
        
        # All fields are existed
        error_dict = validation.check_errors('user', data);
        if len(error_dict) == 0:
            # valid create new user
            extensions.create_user(data);
            return json.jsonify(username=data['username'],
                                firstname=data['firstname'],
                                lastname=data['lastname'],
                                email=data['email']), 201;
        else:
            for i in range(0, 13):
                code = str(i);
                if code in error_dict:
                    errors.append({"message": error_messages[code]});
            return json.jsonify(errors=errors), 422
    elif request.method == 'PUT':
    # update user info
        if 'username' not in session:
            errors.append({"message": "You do not have the necessary credentials for the resource"});
            return json.jsonify(errors=errors), 401;

        data = request.json;
        if session['username'] != data['username']:
            errors.append({"message": "You do not have the necessary permissions for the resource"});
            return json.jsonify(errors=errors), 403;

        if ('username' not in data or 'password1' not in data or 'password2' not in data or 'firstname' not in data or 'lastname' not in data or 'email' not in data):
            errors.append({"message": "You did not provide the necessary fields"});
            return json.jsonify(errors=errors), 422;

        error_dict = validation.check_errors('user_edit', data);
        if len(error_dict) == 0:
        # valid update user
            extensions.update_user(data);
            return json.jsonify();
        else:
            for i in range(0, 13):
                code = str(i);
                if code in error_dict:
                    errors.append({"message": error_messages[code]});
            return json.jsonify(errors=errors), 422

@api.route('/api/v1/login', methods=['POST'])
def login_api():
    errors = [];
    data = request.json;
    if 'username' not in data or 'password' not in data:
        errors.append({"message": "You did not provide the necessary fields"}); 
        return json.jsonify(errors=errors), 422;
    
    # come here with all necessary fields
    error_dict = validation.check_errors(route="login", user_info=data)

    if (len(error_dict) == 0):
    # sucessfully login
        session['username'] = data['username']
        return json.jsonify(username=data['username']);

    # login fails!
    elif '13' in error_dict:
        errors.append({"message": "Username does not exist"});
        return json.jsonify(errors=errors), 404;
    else:
        errors.append({"message": "Password is incorrect for the specified username"});
        return json.jsonify(errors=errors), 422;

@api.route('/api/v1/logout', methods = ['POST'])
def logout_api():
    if 'username' in session:
    # successfully logout
        session.pop('username', None);
        return jsonify(), 204;

    else:
    # failed
        errors = [{"message": "You do not have the necessary credentials for the resource"}];
        return json.jsonify(errors=errors), 401;

@api.route('/api/v1/album/<albumid>', methods = ['GET'])
def album_route(albumid):
    if request.method == 'GET':
        errors = []

        if not extensions.does_album_exist(albumid=albumid):
            # albumid not exist
            errors.append({"message" : "The requested resource could not be found"})
            return jsonify(errors=errors), 404

        album_info = extensions.get_album_info(albumid=albumid)
        # albumid existed
        if 'username' in session:
            username = session["username"]

            if (album_info['access'] == "private"):
                if extensions.check_album_belong(username=username, albumid=albumid):
                    pass
                elif username in extensions.get_grant_users_list(albumid=albumid):
                    pass
                # not have access
                else:
                    errors.append({"message" : "You do not have the necessary permissions for the resource"})
                    return jsonify(errors=errors), 403

        # public should not fail
        elif (album_info['access'] == "private"):
                errors.append({"message" : "You do not have the necessary credentials for the resource"}) 
                return jsonify(errors=errors), 401
        
        # all check finished to reach here
        photos_list = extensions.get_photos_list(albumid)

        options = {
            "access": album_info['access'],
            "albumid": int(albumid),
            "created": album_info['created'],
            "lastupdated": album_info['lastupdated'],
            "pics": photos_list,
            "title": album_info['title'],
            "username": album_info['username'],
        }

        return jsonify(options)

@api.route('/api/v1/pic/<picid>', methods = ['GET', 'PUT'])
def pic_api(picid):
    errors = [];

    if request.method == 'GET':
        if not extensions.does_pic_exist(picid):
        # picid not exist
            errors.append({"message": "The requested resource could not be found"});
            return json.jsonify(errors=errors), 404;

        pic_info = extensions.get_photo_info(picid);
        album_info = extensions.get_album_info(pic_info['albumid']);
      
        # if public, GET should not fail
        if album_info['access'] == 'private':
            # no session
            if 'username' not in session:
                errors.append({"message": "You do not have the necessary credentials for the resource"});
                return json.jsonify(errors=errors), 401;

            elif not extensions.check_album_belong(session['username'], pic_info['albumid']) and not session['username'] in extensions.get_grant_users_list(pic_info['albumid']):
                # do not have access
                errors.append({"message": "You do not have the necessary permissions for the resource"});
                return json.jsonify(errors=errors), 403;

        # valid here
        photo_list = extensions.get_photos_list(pic_info['albumid']);
        prev = "";
        nxt = "";
        for i in range(0, len(photo_list)):
            if (photo_list[i])['picid'] == picid:
                if i > 0:
                    prev = photo_list[i-1]['picid'];
                if i < len(photo_list) - 1:
                    nxt = photo_list[i+1]['picid'];
                break;

        return json.jsonify(albumid=pic_info['albumid'],
                            caption=pic_info['caption'],
                            format=pic_info['format'],
                            next=nxt,
                            picid=picid,
                            prev=prev);

    if request.method == 'PUT':
        data = request.json;

        if 'albumid' not in data or 'caption' not in data or 'format' not in data or 'next' not in data or 'picid' not in data or 'prev' not in data:
            # miss field
            errors.append({"message": "You did not provide the necessary fields"});
            return json.jsonify(errors=errors), 422;

        if not extensions.does_pic_exist(picid):
        # picid not exist
            errors.append({"message": "The requested resource could not be found"});
            return json.jsonify(errors=errors), 404;

        # no session
        if 'username' not in session:
            errors.append({"message": "You do not have the necessary credentials for the resource"});
            return json.jsonify(errors=errors), 401;

        pic_info = extensions.get_photo_info(picid);
        album_info = extensions.get_album_info(pic_info['albumid']);
      
        if not extensions.check_album_belong(session['username'], pic_info['albumid']):
            # do not have access
            errors.append({"message": "You do not have the necessary permissions for the resource"});
            return json.jsonify(errors=errors), 403;

        # validation finished, check if only caption is modified
        photo_list = extensions.get_photos_list(pic_info['albumid']);
        prev = "";
        nxt = "";
        for i in range(0, len(photo_list)):
            if (photo_list[i])['picid'] == picid:
                if i > 0:
                    prev = photo_list[i-1]['picid'];
                if i < len(photo_list) - 1:
                    nxt = photo_list[i+1]['picid'];
                break;

        if data['albumid'] != pic_info['albumid'] or pic_info['format'] != data['format'] or data['next'] != nxt or data['prev'] != prev or picid != data['picid']:
            # other field changed
            errors.append({"message": "You can only update caption"});
            return json.jsonify(errors=errors), 403

        # check finished
        extensions.update_pic_caption(picid, data['caption']);
        return json.jsonify(data), 200


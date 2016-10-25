from flask import *
import extensions

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp', 'gif'])

album = Blueprint('album', __name__, template_folder='templates')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@album.route('/album/edit', methods=['POST', 'GET'])
def album_edit_route():
    if 'username' not in session:
        return redirect(url_for('login.login_route'))

    else:
        if request.method == 'POST':

            op = request.form.get('op')

            # five kinds of post requests
            # delete: delete a image
            # add: add a image
            # access: change the album to public or private
            # grant: grant a user to access a private album
            # revoke: revoke a user from accessing an album

            if op == "delete":
                albumid = request.form.get('albumid')
                picid = request.form.get('picid')
                extensions.delete_photo(albumid=albumid, picid=picid)
                
            elif op == "add":
                albumid = request.form.get('albumid')
                upload_file = request.files['file']

                if upload_file.filename == '':
                    pass
                else:
                    if upload_file and allowed_file(upload_file.filename):
                        extensions.save_photo(upload_file=upload_file, albumid=albumid)

            elif op == "access":
                albumid = request.form['albumid']
                access = request.form['access']
                if access == "public":
                    extensions.set_album_public(albumid=albumid)
                else:
                    extensions.set_album_private(albumid=albumid)

            elif op == "grant":
                albumid = request.form['albumid']
                username = request.form['username']
                if not extensions.does_user_exist(username=username):
                    abort(404)
                extensions.grant_user_album(username=username, albumid=albumid)

            elif op == "revoke":
                albumid = request.form['albumid']
                username = request.form['username']
                extensions.revoke_user_album(username=username, albumid=albumid)
                
            else:
                print("Error")

        if "albumid" not in request.args:
            abort(404)

        albumid = request.args.get("albumid")
        username = session["username"]

        if not extensions.does_album_exist(albumid=albumid):
            abort(404)

        if not extensions.check_album_belong(username=username, albumid=albumid):
            abort(403)

        album_info = extensions.get_album_info(albumid=albumid)
        user_info = extensions.get_user_info(username=username)
        photos_list = extensions.get_photos_list(albumid=albumid)

        options = {
            "edit": True,
            "logged_in": True,
            "albumid": albumid,
            "album_info": album_info,
            "user_info": user_info,
            "photos_list": photos_list
        }

        if album_info['access'] == "private":
            grant_users_list = extensions.get_grant_users_list(albumid=albumid)
            options["grant_users_list"] = grant_users_list

        return render_template("album_edit.html", **options)

@album.route('/album')
def album_route():
    if "albumid" not in request.args:
        abort(404)

    albumid = request.args.get("albumid")

    options = {
        "albumid": albumid
    }

    return render_template("album.html", **options)

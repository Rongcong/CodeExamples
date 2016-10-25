from flask import *
import extensions

albums = Blueprint('albums', __name__, template_folder='templates')

@albums.route('/albums/edit', methods=['POST', 'GET'])
def albums_edit_route():
    if "username" not in session:
        return redirect(url_for('login.login_route'))
    else:
        if request.method == 'POST':
            op = request.form.get('op')

            if op == "delete":
                albumid = request.form.get('albumid')
                extensions.delete_album(albumid=albumid)

            elif op == "add":
                username = request.form.get('username')
                title = request.form.get('title')
                extensions.add_album(username=username, title=title)

            else:
                print("Error")

        # no problem if username comes from session
        username = session['username']
        user_info = extensions.get_user_info(username=username)
        albums_list = extensions.get_albums_list(username=username)

        options = {
            "edit": True,
            "logged_in": True,
            "username": username,
            "user_info": user_info,
            "albums_list": albums_list
        }
        
        return render_template("albums.html", **options)


@albums.route('/albums')
def albums_route():
    # visit the public page
    if "username" in request.args:
        username = request.args.get("username")
        if not extensions.does_user_exist(username=username):
            abort(404)

        albums_list = extensions.get_public_albums_list(username=username)

        options = {
            "edit": False,
            "logged_in": False,
            "username": username,
            "albums_list": albums_list
        }

        return render_template("albums.html", **options)

    else:
        if 'username' not in session:
            return redirect(url_for('login.login_route'))
        else:
            username = session["username"]
            user_info = extensions.get_user_info(username=username)
            albums_list = extensions.get_albums_list(username=username)

            options = {
                "edit": False,
                "logged_in": True,
                "username": username,
                "user_info": user_info,
                "albums_list": albums_list
            }

            return render_template("albums.html", **options)

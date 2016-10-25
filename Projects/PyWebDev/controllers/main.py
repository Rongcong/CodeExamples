from flask import *
import extensions

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def main_route():
    if 'username' in session:
        username = escape(session['username'])
        user_info = extensions.get_user_info(username=username)
        public_albums = extensions.get_all_public_albums()
        private_albums = extensions.get_private_albums(username=username)
        shared_albums = extensions.get_shared_private_albums(username=username)

        options = {
                   'username': username,
                   'user_info': user_info,
                   'albums_list': (public_albums + private_albums + shared_albums),
                   'logged_in': True
                  }
        
        return render_template("index_private.html", **options)

    else:
        public_albums_list = extensions.get_all_public_albums()
        users_list = extensions.get_users_list()
        options = {
                   'users_list': users_list,
                   'public_albums_list': public_albums_list,
                   'logged_in': False
                  }

        return render_template("index_public.html", **options)
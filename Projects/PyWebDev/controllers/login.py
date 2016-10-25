from flask import *
import extensions
import validation

login = Blueprint('login', __name__, template_folder='templates')

@login.route('/login')
def login_route():
    if 'username' in session:
        return redirect(url_for('user.user_edit_route'))
    else:
        return render_template("login.html")



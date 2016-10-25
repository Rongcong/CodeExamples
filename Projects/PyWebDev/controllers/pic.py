from flask import *
import extensions

pic = Blueprint('pic', __name__, template_folder='templates')

@pic.route('/pic')
def pic_route():
    if "picid" not in request.args:
        abort(404)

    picid = request.args.get("picid")


    options = {"picid": picid}

    return render_template("pic.html", **options)
from flask import Flask, render_template, abort
from api import *
import extensions
import controllers
import config
import os

# Initialize Flask app with the template folder address
app = Flask(__name__, template_folder='templates')

# Register the controllers
app.register_blueprint(controllers.album, url_prefix=config.env['url_prefix'])
app.register_blueprint(controllers.albums, url_prefix=config.env['url_prefix'])
app.register_blueprint(controllers.pic, url_prefix=config.env['url_prefix'])
app.register_blueprint(controllers.main, url_prefix=config.env['url_prefix'])
app.register_blueprint(controllers.user, url_prefix=config.env['url_prefix'])
app.register_blueprint(controllers.login, url_prefix=config.env['url_prefix'])
app.register_blueprint(api, url_prefix=config.env['url_prefix'])


app.secret_key = '\xf6\xdb[\xf2&\x82^u\x9c\xa2\xd8\x84\x03\x15\xef\xa2\xa0w\xe1+\xb4\xb6\x14c'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(APP_ROOT, 'static/images')
config.env['IMAGE_FOLDER'] = IMAGE_FOLDER

# Listen on external IPs
# For us, listen to port 3000 so you can just run 'python app.py' to start the server
if __name__ == '__main__':
    # listen on external IPs
    app.run(host=config.env['host'], port=config.env['port'], debug=True)

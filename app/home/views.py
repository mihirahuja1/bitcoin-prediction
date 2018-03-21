from flask import render_template, Blueprint

home_mod = Blueprint('home', __name__, template_folder='templates', static_folder='static')


@home_mod.route('/')
def home():
    return render_template('home/index.html')

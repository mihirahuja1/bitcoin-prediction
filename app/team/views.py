from flask import render_template, Blueprint

team_mod = Blueprint('team', __name__, template_folder='templates', static_folder='static')


@team_mod.route('/team')
def team():
    return render_template('ViewTeam.html')

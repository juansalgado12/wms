from flask import Blueprint, render_template

bp = Blueprint('home', __name__)

@bp.route('/')
def welcome():
    return render_template('welcome.html')
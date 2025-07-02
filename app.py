from flask import Flask, render_template, redirect, url_for
from laser.views import laser_bp
from turntable.views import turntable_bp
from analyse.views import analyse_bp

app = Flask(__name__)
app.register_blueprint(laser_bp)
app.register_blueprint(turntable_bp)
app.register_blueprint(analyse_bp, url_prefix='/analyse')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyse')
def analyse_redirect():
    return redirect(url_for('analyse.index'))

if __name__ == '__main__':
    app.run(debug=True)

from app import app
from flask import render_template

# This is for rendering the home page
@app.route('/') #ask why this isnt working
def index():
    return render_template('index.html')

@app.route('/aboutme')
def aboutme():
    return render_template('aboutme.html')


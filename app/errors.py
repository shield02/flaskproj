#!/usr/bin/env python
from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_fond_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internl_error(error):
    db.session.rolback()
    return render_template('500.html'), 500

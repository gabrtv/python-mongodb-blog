#!/usr/bin/env python
from flask import Flask, redirect
from flask.globals import request
from flask.templating import render_template
import datetime
import os
import pymongo
import time
from pymongo.errors import AutoReconnect

app = Flask(__name__)

@app.route("/")
def index():
    db = connect_db()
    posts = db.posts.find().sort('date', pymongo.DESCENDING)
    return render_template('index.html', posts=posts)

@app.route("/post/new", methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        title = request.form.get('post[title]', None)
        body = request.form.get('post[body]', None)
        if not title or not body:
            return render_template('post.html', error='Must provide title and body')
        # create a post in mongodb
        db = connect_db()
        post = {'title': title, 'body': body, 'date': datetime.datetime.now()}
        success, attempts = False, 1
        while success is False and attempts < 10:
            try:
                db.posts.insert(post)
                success = True
            except AutoReconnect:
                attempts += 1
                time.sleep(3)
        return redirect('/')
    else:
        return render_template('post.html')

def connect_db():
    db_host = os.environ.get('MONGODB_HOST', 'localhost')
    db_port = os.environ.get('MONGODB_PORT', 27017)
    replicaset = os.environ.get('MONGODB_REPLSET', None)
    if replicaset:
        host_port = "%(db_host)s:%(db_port)s" % locals()
        conn = pymongo.MongoReplicaSetClient(host_port, replicaSet=replicaset, 
                    read_preference=pymongo.ReadPreference.PRIMARY_PREFERRED)
    else:
        conn = pymongo.MongoClient(db_host)
    return conn['blog']

if __name__ == "__main__":
    # NOTE: debug True breaks PyDev debugger
    app.debug = os.environ.get('DEBUG', True)
    host = os.environ.get('BIND', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port)

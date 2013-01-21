#!/usr/bin/env python
from flask import Flask, redirect
from flask.globals import request
from flask.templating import render_template
from pymongo.errors import AutoReconnect
import datetime
import json
import os
import pymongo
import time

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
    hosts = json.loads(os.environ.get('MONGODB_HOSTS', '["localhost"]'))
    db_port = json.loads(os.environ.get('MONGODB_PORT', 27017))
    replicaset = json.loads(os.environ.get('MONGODB_REPLSET', None))
    if replicaset:
        conn_str = ",".join([ h+':'+str(db_port) for h in hosts])
        conn = pymongo.MongoReplicaSetClient(conn_str, replicaSet=replicaset, 
                    read_preference=pymongo.ReadPreference.PRIMARY_PREFERRED)
    else:
        conn = pymongo.MongoClient("hosts[0]:"+str(db_port))
    return conn['blog']

if __name__ == "__main__":
    # NOTE: debug True breaks PyDev debugger
    app.debug = os.environ.get('DEBUG', True)
    host = os.environ.get('BIND', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port)

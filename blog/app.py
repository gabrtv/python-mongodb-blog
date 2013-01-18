from flask import Flask, redirect
from flask.globals import request
from flask.templating import render_template
import datetime
import os
import pymongo

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
        db.posts.insert(post)
        return redirect('/')
    else:
        return render_template('post.html')

def connect_db():
    db_host = os.environ.get('MONGODB_HOST', 'localhost')
    replicaset = os.environ.get('MONGODB_REPLSET', None)
    conn = pymongo.MongoClient(db_host, replicaset=replicaset)
    return conn['blog']

if __name__ == "__main__":
    # NOTE: debug True breaks PyDev debugger
    app.debug = os.environ.get('DEBUG', True)
    app.run(host="0.0.0.0")

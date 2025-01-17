import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys

stdout_fileno = sys.stdout
stderr_fileno = sys.stderr

# Total amount of connections to the database
connectionCount = 0


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global connectionCount
    connectionCount += 1
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    article = connection.execute('SELECT * FROM posts WHERE id = ?',
                                 (post_id,)).fetchone()

    connection.close()
    return article


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application
@app.route('/')
def index():
    posts = getPosts()
    return render_template('index.html', posts=posts)


def getPosts():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return posts


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.debug('A non-existing article is accessed and a 404 page is returned')
        stderr_fileno.write('A non-existing article is accessed and a 404 page is returned\n')
        return render_template('404.html'), 404
    else:
        app.logger.info('Article %s retrieved!', post_id)
        stdout_fileno.write('Article ' + str(post_id) + ' retrieved!\n')
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.debug('About page request successful')
    stdout_fileno.write('About page request successful\n')
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()

            app.logger.debug('A new article is created')
            stdout_fileno.write('A new article is created\n')

            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def healthcheck():
    posts = getPosts()
    if len(posts) > 0:
        response = app.response_class(
            response=json.dumps({"result": "OK - healthy"}),
            status=200,
            mimetype='application/json'
        )
        app.logger.info('Healthz request successful')
        return response
    else:
        response = app.response_class(
            response=json.dumps({"result": "ERROR - unhealthy"}),
            status=500,
            mimetype='application/json'
        )
        app.logger.info('Healthz request successful - but service is not healthy')
        stderr_fileno.write('Healthz request successful - but service is not healthy!\n')
        app.logger.debug('DEBUG message')
        return response


@app.route('/metrics')
def metrics():
    posts = getPosts()

    response = app.response_class(
        response=json.dumps({"db_connection_count": connectionCount, "post_count": len(posts)}),
        status=200,
        mimetype='application/json'
    )
    app.logger.debug('Metrics request successful')
    return response


# start the application on port 3111
if __name__ == "__main__":
    # logging.basicConfig(filename='app.log', level=logging.DEBUG)
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0', port='3111')

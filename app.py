import sqlite3
import logging
import sys

from flask import Flask, jsonify, render_template, request, url_for, redirect, flash

# ------------------------------------------------------------
# Logging configuration (STDOUT + STDERR + timestamp + DEBUG)
# - DEBUG/INFO/WARNING -> STDOUT
# - ERROR/CRITICAL     -> STDERR
# ------------------------------------------------------------
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

log_format = logging.Formatter(
    fmt="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    datefmt="%m/%d/%Y, %H:%M:%S"
)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(log_format)
stdout_handler.addFilter(lambda record: record.levelno < logging.ERROR)

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)
stderr_handler.setFormatter(log_format)

# Avoid duplicate handlers if reloaded
if not logger.handlers:
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
else:
    logger.handlers = []
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

logging.getLogger("werkzeug").setLevel(logging.INFO)

# ------------------------------------------------------------
# Metrics counter
# ------------------------------------------------------------
db_connection_count = 0

# ------------------------------------------------------------
# Database helpers
# ------------------------------------------------------------
def get_db_connection():
    global db_connection_count
    db_connection_count += 1

    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute(
        'SELECT * FROM posts WHERE id = ?',
        (post_id,)
    ).fetchone()
    connection.close()
    return post


# ------------------------------------------------------------
# Flask app
# ------------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# ------------------------------------------------------------
# Healthcheck endpoint
# ------------------------------------------------------------
@app.route('/healthz')
def healthz():
    return jsonify(result="OK - healthy"), 200


# ------------------------------------------------------------
# Metrics endpoint
# ------------------------------------------------------------
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.close()

    return jsonify(
        db_connection_count=db_connection_count,
        post_count=post_count
    ), 200


# ------------------------------------------------------------
# Main routes
# ------------------------------------------------------------
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        # ERROR -> STDERR (required by reviewer)
        app.logger.error(f"Article with id {post_id} not found (404)")
        return render_template('404.html'), 404
    else:
        app.logger.info(f'Article "{post["title"]}" retrieved')
        return render_template('post.html', post=post)


@app.route('/about')
def about():
    app.logger.info("About page retrieved")
    return render_template('about.html')


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute(
                'INSERT INTO posts (title, content) VALUES (?, ?)',
                (title, content)
            )
            connection.commit()
            connection.close()

            app.logger.info(f'New article "{title}" created')
            return redirect(url_for('index'))

    return render_template('create.html')


# ------------------------------------------------------------
# Start application
# ------------------------------------------------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3111)

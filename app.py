from flask import Flask, render_template, url_for, request, redirect, send_from_directory, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['UPLOAD_FOLDER'] = 'songs'
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(200), nullable=False)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/view-all', methods=['GET'])
def viewAll():
    songs = Todo.query.order_by(Todo.title).all()
    return render_template('view_all.html', songs=songs)


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        id = str(uuid.uuid4())
        title = request.form['title']
        artist = request.form['artist']
        album = request.form['album']
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], id + '.mp3'))
        new_task = Todo(id=id, title=title, artist=artist, album=album)

        try:
            db.session.add(new_task)
            db.session.commit()
            flash("Song added successfully")
            return render_template('upload.html')
        except:
            flash("There was an error adding the song")

    else:
        songs = Todo.query.order_by(Todo.title).all()
        return render_template('upload.html')


@app.route('/delete/<string:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], id + '.mp3'))
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/view-all')
    except:
        return 'There was a problem deleting that task'


@app.route('/play/<string:id>')
def play(id):
    song = Todo.query.filter_by(id=id).first()
    return render_template('play.html', id=id, songTitle=song.title)


@app.route('/song/<string:id>')
def song(id):
    return send_from_directory(app.config['UPLOAD_FOLDER'], id + '.mp3')


@app.route('/download/<string:id>')
def download(id):
    return send_from_directory(app.config['UPLOAD_FOLDER'], id + '.mp3', as_attachment=True)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        album = request.form['album']
        new_task = Todo(id=id, title=title, artist=artist, album=album)

        try:
            songs = Todo.query
            if title == '' and artist == '' and album == '':
                flash("Please fill any field to search")
                return render_template('search.html')
            if title != '':
                songs = songs.filter_by(title=title)
            if artist != '':
                songs = songs.filter_by(artist=artist)
            if album != '':
                songs = songs.filter_by(album=album)
            songs = songs.all()
            return render_template('search.html', songs=songs, result=True)
        except Exception as e:
            return str(e)
            # return 'There was an issue adding your task'
    else:
        return render_template('search.html')


if __name__ == "__main__":
    app.run(debug=True)

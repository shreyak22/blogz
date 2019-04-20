from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:12356790@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.String(255))

    def __init__(self, title, text):
        self.title = title
        self.text = text


@app.route('/', methods=['GET'])
def index():

    posts = Post.query.all()
    
    return render_template('index.html',title="Build A Blog!", posts=posts)




if __name__ == '__main__':
    app.run()
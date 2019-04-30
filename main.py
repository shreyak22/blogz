from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12356790@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'wertyuiop1234'


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, text):
        self.title = title
        self.text = text

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Post', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password



@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        # getting the user of that email from  database
        if users.count() == 1:
            user = users.first()
            if check_pw_hash(password, user.pw_hash):
                session['user'] = user.username
                flash('welcome back, ' + user.username)
                return redirect("/")
        flash('bad username or password')
        return redirect("/login")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if not is_email(username):
            flash('zoiks! "' + username + '" no user')
            return redirect('/signup')
        email_db_count = User.query.filter_by(username=username).count()
        if email_db_count > 0:
            flash('yikes! "' + username + '" is already taken and password reminders are not implemented')
            return redirect('/register')
        if password != verify:
            flash('passwords should match')
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect("/")
    else:
        return render_template('signup.html')

def is_email(string):
    
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >=0 
        return domain_dot_present
        
@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/")


@app.route('/', methods=['GET'])
def index():
    
    posts = Post.query.all()
    

    return render_template('index.html',title="Blogz", posts=posts)


@app.route('/newpost', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        title_name = request.form['title']
        post = request.form['post']   
        if title_name == "" or post == "" :
            return render_template('add.html', title_error="This field is required", 
            body_error="This field is required", post_value=post, title_value=title_name)
        
        
        else:
            new_post = Post(title_name, post)
            db.session.add(new_post)
            db.session.commit()
            return render_template('add-post.html', post=new_post)

    
    return render_template('add.html')


@app.route('/blog', methods=['GET'])
def single_user():
        
    user_name = request.args.get('username')
    post = Post.query.get(user_name)   
    return render_template('singleUser.html',post=post)



@app.route('/blog-list', methods=['GET','POST'])
def blog_list():
    return render_template('add-post.html', title="blog-post")

# @app.route('/post-title', methods=['GET'])
# def post_title():
        
#     post_id = int(request.args.get('id'))
#     post = Post.query.get(post_id)   
#     return render_template('add-post.html',post=post)


if __name__ == '__main__':
    app.run()
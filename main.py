from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

from hashutils import check_pw_hash, make_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12356790@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'qerfgthbfvdcswfrnfekffd'


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, text, owner):
        self.title = title
        self.text = text
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Post', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = make_pw_hash(password)

@app.before_request
def require_login():
    
    allowed_routes = ['login', 'signup', 'index', 'single_user']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



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
            if check_pw_hash(password, user.password):
                session['username'] = user.username
                flash('welcome back, ' + user.username)
                return redirect("/")
        flash('bad username or password')
        return redirect("/login")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify_password']
        
        user_db_count = User.query.filter_by(username=username).count()
        
        if user_db_count > 0:
            flash('yikes! "' + username + '" is already taken')
            return redirect('/signup')
        if password == "":
            flash('password is required')
            return redirect('/signup')
        if password != verify:
            flash('password should match')
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        return redirect('/')
    else:
        return render_template('signup.html')
        
# @app.route("/logout", methods=['GET'])
# def logout():
#     del session['username']
#     return redirect('/blog')
@app.route('/logout')
def logout():

   session.pop('username', None)
   return redirect('blog')


@app.route('/', methods=['GET'])
def index():
    #owner = User.query.filter_by(user_name=session['username']).first()
    blog_users = User.query.all()

    

    return render_template('index.html',title="Blogz", users=blog_users)
    
def logged_in_user():
    owner = User.query.filter_by(username=session['username']).first()
    return owner


        


@app.route('/newpost', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        title_name = request.form['title']
        post = request.form['post'] 
        user_name = session['username']
        if title_name == "" or post == "" or user_name == "" :
            return render_template('add.html', title_error="This field is required", 
            body_error="This field is required", post_value=post, title_value=title_name)
        
        else:
            new_post = Post(title_name, post, logged_in_user())
            db.session.add(new_post)
            db.session.commit()
            return render_template('blog_page.html', post=new_post)

    
    return render_template('add.html')


@app.route('/blog', methods=['GET'])
def single_user():
        
    # 
    # post = Post.query.get(user_name)   
    all_posts = Post.query.all()
    user_id = request.args.get('user')
    if user_id is not None:
        all_posts = Post.query.filter_by(owner_id=user_id).all()
    return render_template('singleUser.html', posts = all_posts)



@app.route('/blog_page', methods=['GET'])
def blog_list():
    post_id = request.args.get('id')
    if post_id is not None:
        post = Post.query.get(post_id)
        return render_template('blog_page.html', title="blog-post", post = post)
    else:
        return redirect('/blog')




if __name__ == '__main__':
    app.run()
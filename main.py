from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'f8wv3w2f>v9j4sEuhcNYydAGMzzZJgkGgyHE9gUqaJcCk^f*^o7fQyBT%XtTvcYM'

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    created = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.created = datetime.utcnow()
        self.owner = owner


@app.route('/', methods=['GET'])
def index():
    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def main_page():
    post_id = request.args.get('id')
    if (post_id):
        post = Post.query.get(post_id)
        return render_template('new_post.html', title="Blog Post", post=post)
    sort = request.args.get('sort')
    if(sort == 'newest'):
        all_posts = Post.query.order_by(Post.created.desc()).all()
    else:
        all_posts = Post.query.all()
    return render_template('all_posts.html', title='All Posts', all_posts=all_posts)

@app.route('/newpost', methods= ['GET','POST'])
def new_post():
    title_error_message = ""
    body_error_message = ""
    if request.method == "POST":
   
        new_post_title = request.form["title_field"]
        new_post_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        new_post = Post(new_post_title, new_post_body, owner)
        
        if len(new_post_title) < 1:
            title_error_message = 'Please provide a post title.'
        if len(new_post_body) < 1:
            body_error_message ='Please provide a post body.'


        if not (title_error_message or body_error_message):
            db.session.add(new_post)
            db.session.commit()
            url = '/blog?id=' + str(new_post.id)
            return redirect(url)

        
    
    return render_template('new_post_form.html', title = "Make a new blog post." , title_error_message = title_error_message , body_error_message = body_error_message) 


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Post', backref='owner')



@app.route('/login', methods= (['GET','POST']))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username 
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    valid_username  = ''
    valid_password = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:

            if len(username) < 3:
                valid_username = "Not a valid username"
            
            if len(password) < 3 or password != verify:
                valid_password = "Not a valid password"

            if valid_username=="" and valid_password=="":
                new_user = User(username = username, password = password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
                
            else:
           
                valid_username = 'Duplicate user'

    return render_template('signup.html', username=username, valid_username=valid_username, valid_password=valid_password)


    
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'main_page']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


if __name__ == '__main__':
    app.run() 
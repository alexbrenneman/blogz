from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog-2:buildablog@localhost:8889/build-a-blog-2'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'f8wv3w2f>v9j4sEuhcNYydAGMzzZJgkGgyHE9gUqaJcCk^f*^o7fQyBT%XtTvcYM'

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    created = db.Column(db.DateTime)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.created = datetime.utcnow()


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
        new_post = Post(new_post_title, new_post_body)
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

if __name__ == '__main__':
    app.run()
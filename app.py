
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from datetime import datetime
from flask_bootstrap5 import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.config["SECRET_KEY"] = "labexam"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///labexam.db"

bootstrap = Bootstrap(app)


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    user = relationship("User", back_populates="posts")
    comments: Mapped[list['Comment']] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class Comment(db.Model):
    id : Mapped[int] = mapped_column(primary_key=True, unique=True)
    content : Mapped[str]
    user_id :Mapped[int] = mapped_column(ForeignKey('user.id'))
    post_id : Mapped[int] = mapped_column(ForeignKey('post.id'))
    post = relationship("Post", back_populates="comments")

class User(db.Model):
    id : Mapped[int] = mapped_column(primary_key=True, unique=True)
    username : Mapped[str]
    email : Mapped[str]
    password : Mapped[str]

    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")


@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    posts = Post.query.all()
    comments = Comment.query.all()
    users = User.query.all()
    return render_template('home.html', 
                           posts=posts, 
                           comments=comments, 
                           users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        
        flash("Invalid username or password.", "danger")
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route("/createpost", methods=['GET', 'POST'])
def createpost():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if 'user_id' not in session:
            flash("You must be logged in to create a post.", "warning")
            return redirect(url_for('login'))

        new_post = Post(title=title, content=content, user_id=session['user_id'])
        db.session.add(new_post)
        db.session.commit()
        
        flash("Post created successfully!", "success")
        return redirect(url_for('home'))

    return render_template('createpost.html')

@app.route("/viewpost/<int:Post_id>", methods=['GET', 'POST'])
def viewpost(Post_id):
    if "user_id" not in session:  # Ensure user is logged in
        flash("You must be logged in to comment.", "warning")
        return redirect(url_for("login"))
    
    post = Post.query.get_or_404(Post_id)

    if request.method == 'POST': 
        comment_content = request.form.get('comment', '').strip()
        user_id = session["user_id"]  

        if not comment_content:
            flash("Comment cannot be empty!", "danger")
            return redirect(url_for('viewpost', Post_id=Post_id))

        new_comment = Comment(content=comment_content, user_id=user_id, post_id=Post_id)

        db.session.add(new_comment)
        db.session.commit()

        flash("Comment added successfully!", "success")
        return redirect(url_for('viewpost', Post_id=Post_id))

    return render_template('viewpost.html', post=post)

@app.route("/edit_post/<int:Post_id>", methods=['GET', 'POST'])
def edit_post(Post_id):


    post = Post.query.get_or_404(Post_id)

    if session.get('user_id') != post.user_id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('viewpost', Post_id=Post_id))

    if request.method == 'POST':
        new_title = request.form.get('title', '').strip()
        new_content = request.form.get('content', '').strip()

        if not new_title or not new_content:
            flash("Title and content cannot be empty!", "danger")
            return redirect(url_for('edit_post', Post_id=Post_id))

        post.title = new_title
        post.content = new_content
        db.session.commit()
        flash("Post updated successfully!", "success")
        return redirect(url_for('viewpost', Post_id=Post_id))

    return render_template('editpost.html', post=post)

@app.route("/about")
def about():
    pass

@app.route('/edit_comment/<int:comment_id>', methods=['GET', 'POST'])
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    # Ensure only the comment owner can edit
    if session.get('user_id') != comment.user_id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('viewpost', Post_id=comment.post.id))

    if request.method == 'POST':
        # ✅ Fix: Use .get() to prevent KeyError
        new_content = request.form.get('content', '').strip()
        
        if not new_content:  # Prevent saving empty content
            flash("Comment cannot be empty!", "danger")
            return redirect(url_for('edit_comment', comment_id=comment.id))

        comment.content = new_content
        db.session.commit()
        flash("Comment updated successfully!", "success")
        return redirect(url_for('viewpost', Post_id=comment.post.id))

    return render_template("edit_comment.html", comment=comment, post=comment.post)


@app.post('/comments/<int:comment_id>/delete')
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post.id
    db.session.delete(comment)
    db.session.commit()
    flash (f'Successfully Deleted')
    return redirect(url_for('viewpost', Post_id=post_id))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))



with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)

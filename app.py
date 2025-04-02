from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from flask_bootstrap import Bootstrap5


app = Flask(__name__)

app.config["SECRET_KEY"] = "labexam"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///labexam.db"

Bootstrap5(app)
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Post(db.Model):
    id :Mapped[int] = mapped_column(primary_key=True, unique=True)
    title :Mapped[str]
    content :Mapped[str]
    comments :Mapped[list['Comment']]  = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

class Comment(db.Model):
    id : Mapped[int] = mapped_column(primary_key=True, unique=True)
    content : Mapped[str]
    post_id : Mapped[int] = mapped_column(ForeignKey('post.id'))
    post = relationship("Post", back_populates="comments")


@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route("/")
def createPost():
    pass

@app.route('/<int:Post_id>/', methods=('GET', 'Post'))
def post(Post_id):
    Post = Post.query(Post_id)
    if request.method == 'Post':
        comment = Comment(content=request.form['content'], Post=Post)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('viewPost', Post_id=Post.id))
    return render_template('viewPost.html', Post=Post)

@app.route('/comments/')
def comments():
    comments = Comment.query.order_by(Comment.id.desc()).all()
    return render_template('comments.html', comments=comments)

@app.post('/comments/<int:comment_id>/delete')
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post.id
    db.session.delete(comment)
    db.session.commit()
    flash (f'Successfully Deleted')
    return redirect(url_for('post', post_id=post_id))











with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
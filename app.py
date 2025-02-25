from flask import Flask, render_template, url_for, redirect, request, flash
from flask_bootstrap import Bootstrap5
from flask_hashing import Hashing
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

app = Flask(__name__)
app.config["SECRET_KEY"] = "acitivity3"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ITMajor.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

bootstrap = Bootstrap5(app)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

hashing = Hashing(app)


class Profile(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    firstname: Mapped[str]
    lastname: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    def hash_pass(password):
        return hashing.hash_value(password, salt="abcd")


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    title: Mapped[str]
    content: Mapped[str]
    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.id"), nullable=False)

@app.route("/home")
def home():
    profiles = Profile.query.all()
    return render_template("home.html", profiles=profiles)

@app.route("/view/<int:id>")
def profile(id):
    profile = Profile.query.get(id)
    return render_template("profile.html", profile=profile)

@app.route("/create_account", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        username = request.form["username"]
        password = request.form["password"]
        profile = Profile(firstname=firstname,
                        lastname=lastname,
                        username=username,
                        password=Profile.hash_pass(password))
        db.session.add(profile)
        db.session.commit()
        flash(f"{username} added successfully")
    return render_template("create.html")

@app.route("/update_account/<int:id>", methods=["GET", "POST"])
def update(id):
    profile = Profile.query.get(id)
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        profile.firstname = firstname
        profile.lastname = lastname
        db.session.commit()
        flash(f"{profile.username} editted successfully")
    return render_template("update.html", profile=profile)

@app.route("/delete_account/<int:id>")
def remove(id):
    Profile.query.filter_by(id=id).delete()
    db.session.commit()
    flash(f"Deleted successfully")
    return redirect(url_for("home"))

@app.route("/create_post/<int:id>", methods=["GET", "POST"])
def create_post(id):
    profile = Profile.query.get(id)
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        profile_id = request.form["profile_id"]
        post = Post(title=title,
                    content=content,
                    profile_id=profile_id)
        db.session.add(post)
        db.session.commit()
        flash(f"Created a post successfully")
    return render_template("create_post.html", profile=profile)

@app.route("/view_all_post")
def view_all_post():
    pass

@app.route("/view_post")
def view_post():
    pass

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)

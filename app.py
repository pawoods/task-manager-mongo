import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_tasks")
def get_tasks():
    tasks = list(mongo.db.tasks.find())
    return render_template("tasks.html", tasks=tasks)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    tasks = list(mongo.db.tasks.find({"$text": {"$search": query}}))
    return render_template("tasks.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username")})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        user_id = 1
        existing_id = True

        while existing_id:
            if not mongo.db.users.find_one({"user_id": user_id}):
                existing_id = False
                break
            user_id += 1

        register = {
            "user_id": user_id,
            "username": request.form.get("username"),
            "password": generate_password_hash(request.form.get("password")),
            "is_super": False,
            "is_admin": False
        }
        mongo.db.users.insert_one(register)

        # put new user into "session" cookie
        session["user"] = request.form.get("username")
        flash("Registration successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/bogin", methods=["GET", "POST"])
def bogin():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username")})

        if existing_user:
            # check hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username")
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect username and/or password")
                return redirect(url_for("bogin"))

        else:
            # username doesn't exist
            flash("Incorrect username and/or password")
            return redirect(url_for("bogin"))
    return render_template("bogin.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # Grab session user's username from database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    if session["user"]:
        tasks = mongo.db.tasks.find({"likes": username})
        return render_template("profile.html", username=username, tasks=tasks)

    return redirect(url_for("bogin"))


@app.route("/bogout")
def bogout():
    # Remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("bogin"))


@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        # form.getlist() to get list of submmissions with same name
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        category = mongo.db.categories.find_one(
            {"category_name": request.form.get("category_name")}
        )
        task = {
            "category": category,
            "task_name": request.form.get("task_name"),
            "test_input": request.form.getlist("test_input"),
            "task_description": request.form.get("task_description"),
            "due_date": request.form.get("due_date"),
            "is_urgent": is_urgent,
            "created_by": session["user"],
            "likes": []
        }
        mongo.db.tasks.insert_one(task)
        flash("Task successfully added")
        return redirect(url_for("get_tasks"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_task.html", categories=categories)


@app.route("/edit_task/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        category = mongo.db.categories.find_one(
            {"category_name": request.form.get("category_name")})
        mongo.db.tasks.update_one({"_id": ObjectId(task_id)}, {
            "$set": {
                "category": category,
                "task_name": request.form.get("task_name"),
                "test_input": request.form.getlist("test_input"),
                "task_description": request.form.get("task_description"),
                "due_date": request.form.get("due_date"),
                "is_urgent": is_urgent,
                "created_by": session["user"]
            }})
        flash("Task successfully updated")
        return redirect(url_for("get_tasks"))

    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_task.html", task=task, categories=categories)


@app.route("/delete_task/<task_id>")
def delete_task(task_id):
    mongo.db.tasks.delete_one({"_id": ObjectId(task_id)})
    flash("Task successfully deleted")
    return redirect(url_for("get_tasks"))


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name"),
            "category_color": request.form.get("category_color")
        }
        mongo.db.categories.insert_one(category)
        flash("New category added")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        edit = {
            "category_name": request.form.get("category_name"),
            "category_color": request.form.get("category_color")
        }
        mongo.db.categories.update_one({"_id": ObjectId(category_id)}, {
            "$set": edit})
        mongo.db.tasks.update_many({"category._id": ObjectId(category_id)}, {
            "$set": {
                "category.category_name": request.form.get("category_name"),
                "category.category_color": request.form.get("category_color")
            }})
        flash("Category successfully updated")
        return redirect(url_for("get_categories"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.delete_one({"_id": ObjectId(category_id)})
    flash("Category successfully deleted")
    return redirect(url_for("get_categories"))


@app.route("/add_like/<task_id>")
def add_like(task_id):
    likes = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})["likes"]
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    if username in likes:
        mongo.db.tasks.update_one({"_id": ObjectId(task_id)}, {
            "$pull": {"likes": username}})
        return redirect(url_for("get_tasks"))
    mongo.db.tasks.update_one({"_id": ObjectId(task_id)}, {
        "$push": {"likes": username}})
    return redirect(url_for("get_tasks"))


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True
    )

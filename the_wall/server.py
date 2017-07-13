from flask import Flask, redirect, request, session, flash, render_template
from mysqlconnection import MySQLConnector
import re
import md5

app = Flask(__name__)
app.secret_key = "5203945872309457"
mysql = MySQLConnector(app, "the_wall")

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------

@app.route("/login_attempt",methods=["POST"])
def login_attempt():

    server_email = request.form["email"]
    server_password = request.form["password"]
    hashed_password = md5.new(server_password).hexdigest()

    query = "SELECT * FROM users WHERE email = :test_email"

    data = {
        "test_email": server_email
    }

    db_check = mysql.query_db(query, data)

    if len(db_check) == 0:
        flash("That email does not have an account. Please register.")
        return redirect("/")

    elif db_check[0]["password"] == hashed_password:
        session["email"] = server_email
        session["id"] = db_check[0]["id"]
        return redirect("/the_wall")

    else:
        flash("Incorrect password")
        return redirect("/")

#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------

@app.route("/registration_attempt", methods=["POST"])
def registration_attempt():
    
    server_email = request.form["email"]
    server_first_name = request.form["first_name"]
    server_last_name = request.form["last_name"]
    server_password = request.form["password"]
    server_confirm_password = request.form["confirm_password"]

    if len(server_email) < 1 or len(server_first_name) < 1 or len(server_last_name) < 1 or len(server_password) < 1 or len(server_confirm_password) < 1:
        flash("All fields are required")
        return redirect("/")
    elif not (server_first_name.isalpha() or server_last_name.isalpha()):
        flash("First name and last name can only contain letters")
        return redirect("/")
    elif not EMAIL_REGEX.match(server_email):
        flash("Invalid Email Address!")
        return redirect("/")
    elif server_password != server_confirm_password:
        flash("Password confirmation must match password")
        return redirect("/")
    elif len(server_password) < 8:
        flash("Password must be 8 characters.")
        return redirect("/")
    else:
        hashed_password = md5.new(server_password).hexdigest()
        insert = "INSERT INTO users (email, first_name, last_name, password, created_at) VALUES (:email, :first_name, :last_name, :password, NOW())"
        data = {
            "email": server_email,
            "first_name": server_first_name,
            "last_name": server_last_name,
            "password": hashed_password,
        }
        mysql.query_db(insert, data)
        flash("You are now registered. You may now log in.")
        return redirect("/")

#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------

@app.route("/the_wall")
def the_wall():

    query_string = "SELECT first_name, last_name, messages.created_at, message, messages.id as 'message_id' FROM users JOIN messages ON users.id=user_id ORDER BY messages.created_at DESC"
    
    results_list = mysql.query_db(query_string)


    comment_query_string = "SELECT first_name, last_name, users.id as the_id_of_the_user, comment, comments.id as comment_id, comments.created_at, messages.id as dog, message FROM comments JOIN messages ON comments.message_id = messages.id JOIN users ON comments.user_id = users.id"
    
    comment_list = mysql.query_db(comment_query_string)

    print "-"*50
    #print results_list[0]["message_id"]
    print comment_list[0]["dog"]
    print "-"*50


    return render_template("wall.html", results_list=results_list, comment_list=comment_list)

#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------

@app.route("/message", methods=["POST"])
def message():

    query = "SELECT * FROM users WHERE email = :email"
    data1 = {
        "email": session["email"]
    }
    poster_id = mysql.query_db(query, data1)

    new_message = request.form["new_message"]
    insert = "INSERT INTO messages (message, created_at, user_id) VALUES (:message, NOW(), :user_id)"
    data2 = {
        "message": new_message,
        "user_id": poster_id[0]["id"]
    }

    mysql.query_db(insert, data2)

    return redirect("/the_wall")


#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------



@app.route("/comment/<message_id>", methods=["POST"])
def comment(message_id):
    
    commentor_id = session["id"]

    comment = request.form["new_comment"]

    insert_string = "INSERT INTO comments (user_id, created_at, message_id, comment) VALUES (:user, NOW(), :message_id, :comment_text)"

    data3 = {
        "user": commentor_id,
        "message_id": message_id,
        "comment_text": comment
    }

    mysql.query_db(insert_string, data3)




    return redirect("/the_wall")


#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------



@app.route("/logout", methods=["POST"])
def logout():
    
    session = {}
    
    return redirect("/")





#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------

app.run(debug=True)
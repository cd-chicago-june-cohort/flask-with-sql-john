from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import MySQLConnector
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
mysql = MySQLConnector(app, "emails")
app.secret_key = "50923845709"



@app.route("/")
def index():

    query = "SELECT * FROM emails"

    my_emails = mysql.query_db(query)

    return render_template("index.html", all_emails=my_emails)



@app.route("/email", methods=["POST"])
def validate():
    
    new_email = request.form["email"]

    validation_query = "SELECT email FROM emails WHERE email=(:test_email)"
    data = {"test_email": new_email}

    my_email = mysql.query_db(validation_query, data)

    if len(new_email) < 1:
        flash("Please enter an email.")
        return redirect("/")

    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Email address must be of valid form.")
        return redirect("/")

    elif (my_email):
        flash("That email already exists in our database.")
        return redirect("/")

    else:
        
        new_query = "INSERT INTO emails (email, created_at) VALUES (:validated_email, NOW())"

        new_data = {
            "validated_email": new_email
        }

        mysql.query_db(new_query, new_data)

        final_query = "SELECT * FROM emails"
        email_list = mysql.query_db(final_query)

        return render_template("success.html", new_email=new_email, email_list=email_list)
    


app.run(debug=True)
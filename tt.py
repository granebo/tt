from flask import Flask, render_template, request
import mysql.connector
import json


def open_db():
    # Import Credentials
    with open('credentials.json') as creds:
        credentials = json.load(creds)

    cnx = mysql.connector.connect(user=credentials['DB_USER'], password=credentials['DB_PASSWORD'], host=credentials['DB_HOST'], database=credentials['DB_DATABASE'])
    return(cnx)

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html', name = 'Kalle')


@app.route('/kids.html')
def kids():
    connection = open_db()
    cursor = connection.cursor()

    query = ("SELECT firstname, username FROM users WHERE child=1")
    cursor.execute(query)

    kidslist = cursor.fetchall() # [(firstname,username), ...]
    cursor.close()
    connection.close()
    return render_template('kids.html', kids = kidslist)



@app.route('/kid.html')
def kid():
    username = request.values.get('kid')
    return render_template('kid.html', kid = username)







app.run(host='0.0.0.0', port=81)

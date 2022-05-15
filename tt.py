from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html', name = 'Kalle')


@app.route('/kids.html')
def kids():
    kidslist = [('Kalle','kalle'),('Lisa','lisa')]
    return render_template('kids.html', kids = kidslist)



@app.route('/kid.html')
def kid():
    username = request.values.get('kid')
    return render_template('kid.html', kid = username)







app.run(host='0.0.0.0', port=81)

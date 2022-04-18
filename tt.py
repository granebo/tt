from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html', name = 'Kalle')


app.run(host='0.0.0.0', port=81)

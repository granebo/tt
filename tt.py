from flask import Flask, render_template, request
import mysql.connector
import json


def open_db():
    # Import Credentials
    with open('credentials.json') as creds:
        credentials = json.load(creds)

    cnx = mysql.connector.connect(user=credentials['DB_USER'],
                                  password=credentials['DB_PASSWORD'],
                                  host=credentials['DB_HOST'],
                                  database=credentials['DB_DATABASE'],
                                  )
    return (cnx)


app = Flask(__name__)


@app.route('/')
def login():
    return render_template('login.html', name='Kalle')


@app.route('/kids.html')
def kids():
    connection = open_db()
    cursor = connection.cursor()

    # query = "SELECT firstname, username FROM users WHERE child=1"
    query = "select u.username as user, u.firstname as name, SEC_TO_TIME(a.seconds) as remaining, act.description as activity, TIMEDIFF(now(),o.timeStarted) as ongoing from availabletime as a, users as u left join ongoing as o on u.ID = o.userID left join activities as act on o.activityID = act.ID where u.ID = a.userID"
    cursor.execute(query)

    kidslist = cursor.fetchall()  # [(user,name,remaining,activity,ongoing), ...]
    cursor.close()
    connection.close()
    return render_template('kids.html', kids=kidslist)


@app.route('/kid.html', methods=['GET', 'POST'])
def kid():
    username = request.values.get('username')
    # Username required
    if not username:
        return render_template('error.html', error_msg='No username')

    try:
        backdate = request.values.get('backdate')
    except:
        backdate = 0

    connection = open_db()
    cursor = connection.cursor()

    try:
        # Getting user basics
        query = f"SELECT id, firstname FROM users WHERE child=1 and username='{username}'"
        cursor.execute(query)
        row = cursor.fetchone()

        # User with given username does not exist in database
        if not row:
            return render_template('error.html', error_msg=f"No user: {username}")
        (userID, name) = row

        if 'action' in request.values:
            action = request.values.get('action')
            if action == 'stop':
                cursor.execute(f"call EndActivity({userID},{backdate});")
                connection.commit()
            elif action == 'start':
                activity = request.values.get('activities')
                backdate = int(backdate) * -1
                query = f"INSERT INTO ongoing (userID, activityID, timeStarted) VALUES ({userID},{activity},DATE_ADD(now(),INTERVAL {backdate} MINUTE))"
                cursor.execute(query)
                connection.commit()
            else:
                return render_template('error.html', error_msg=f"Invalid action: {action}")

        # Getting user remaining time
        query = f"SELECT seconds FROM availabletime WHERE userID='{userID}'"
        cursor.execute(query)
        (remainingseconds,) = cursor.fetchone()

        prettyRemaining = ""

        if remainingseconds >= 3600:
            hours = remainingseconds // 3600
            prettyRemaining += str(hours) + "h "
            remainingseconds -= hours * 3600

        if remainingseconds >= 60:
            minutes = remainingseconds // 60
            prettyRemaining += str(minutes) + "min "
            remainingseconds -= minutes * 60

        prettyRemaining += str(remainingseconds) + "sec "

        # Getting current activity
        query = f"SELECT a.description as activity, o.timeStarted as started FROM activities as a, ongoing as o WHERE a.ID = o.activityID and o.userID = '{userID}'"
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            # There is an ongoing activity
            (activity, started) = row
            return render_template('kid.html', username=username, remaining=prettyRemaining, ongoing='True', name=name,
                                   activity=activity, started=started)
        else:
            # There is no ongoing activity
            # Getting list of activities
            query = f"SELECT ID, description FROM activities"
            cursor.execute(query)
            activities = cursor.fetchall()

            return render_template('kid.html', username=username, remaining=prettyRemaining, ongoing='False', name=name,
                                   activities=activities)

    finally:
        cursor.close()
        connection.close()


app.run(host='0.0.0.0', port=81)

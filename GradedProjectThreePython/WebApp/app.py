# importing necessary libraries and functions
from flask import Flask, request, render_template, redirect, url_for, session

from flaskext.mysql import MySQL

import pickle, numpy as np, sklearn, re

app = Flask(__name__)

app.secret_key = 'simpleSecretKey'

mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'loanusers'

mysql.init_app(app)

model = pickle.load(open('modelFile.pkl', 'rb'))  # loading the trained model

@app.route('/', methods = ['GET'])
def homePage():
    return render_template('index.html')

@app.route('/login', methods = ['GET','POST'])
def loginPage():

    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        dbConnection = mysql.connect()
        cursor = dbConnection.cursor()
        cursor.execute('SELECT * FROM users WHERE user_name = % s AND user_password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedIn'] = True
            print(account[1])
            session['id'] = int(account[0])
            session['username'] = str(account[1])
            message = 'Logged in successfully !'
            return redirect(url_for('prediction'))
            #render_template('predict.html', message = message)
        else:
            message = 'Incorrect username / password !'
    return render_template('login.html', message = message)

@app.route('/register', methods = ['GET','POST'])
def registerPage():

    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        dbConnection = mysql.connect()
        cursor = dbConnection.cursor()
        # cursor = mysql.get_db().cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users u WHERE u.user_name = % s', (username, ))
        account = cursor.fetchone()
        if account:
            message = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            message = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            message = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO users (user_name, user_password, email) VALUES ( % s, % s, % s)', (username, password, email, ))
            dbConnection.commit()
            message = 'You have successfully registered !'
            return render_template('login.html', message = message)
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template('register.html',message = message)

@app.route('/predict', methods = ['GET','POST'])
def prediction():

    if request.method == 'POST':
        Gender = int(request.form['Gender'])
        Married = int(request.form['Married'])
        Dependents = int(request.form['Dependents'])
        Education = int(request.form['Education'])
        Self_Employed = int(request.form['Self_Employed'])
        Income = float(request.form['Income'])
        Loan_Amount = float(request.form['Loan_Amount'])
        Loan_Term = int(request.form['Loan_Term'])
        Credit_History = int(request.form['Credit_History'])
        Property_Area = int(request.form['Property_Area'])
        CoApplicantIncome = 0;

        prediction = model.predict([[Gender, Married, Dependents, Education, Self_Employed, Income, CoApplicantIncome, Loan_Amount,
                                     Loan_Term, Credit_History, Property_Area]])
        isEligible = False
        if prediction[0] >= 0.50:
            isEligible = True
            message = "Congratulation!!! You are eligible for the Loan" + str(prediction[0])
        else:
            message = "Sorry!!! Not eligible for the loan" + str(prediction[0])

        return render_template('predict.html', message=message, isEligible = isEligible)

    return render_template('predict.html')

@app.route('/logout', methods=['GET'])
def logoutPage():
    session.pop('id',None)
    session.pop('loggedIn',None)
    session.pop('username',None)
    return redirect(url_for('homePage'))

if __name__ == '__main__':
    app.run(debug=True)

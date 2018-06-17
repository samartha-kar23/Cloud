#from __future__ import print_function
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, jsonify
#import sys
#from data import Articles
import requests
from flask_mysqldb import MySQL
import pymysql.cursors
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import subprocess
import time
app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = '10.14.88.224'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sensor_cloud'
app.config['MYSQL_DB'] = 'Registration'
#app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)

#connect to database two
conn = pymysql.connect(host='10.14.88.224', user='root', password='sensor_cloud', db='SENSORS')

# Index
@app.route('/')
def index():
    return render_template('home.html')


# Register Form Class
class RegisterForm(Form):
    Firstname = StringField('Firstname', [validators.Length(min=1, max=50)])
#    username = StringField('Username', [validators.Length(min=4, max=25)])
    Email = StringField('Email', [validators.Length(min=6, max=50)])
    Password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        Firstname = form.Firstname.data
        Email = form.Email.data
#        username = form.username.data
        Password = sha256_crypt.encrypt(str(form.Password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO Users (Firstname, Email, Password) VALUES(%s, %s, %s)", (Firstname, Email, Password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')
	subprocess.call('python /home/devstack/Desktop/login/instance.py',shell=True)
	time.sleep(3)
	flash('Cloud instance initiated','success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        Firstname = request.form['Firstname']
        password_candidate = request.form['Password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM Users WHERE Firstname = %s", [Firstname])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            Password = data[2]

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, Password):
                # Passed
                session['logged_in'] = True
                session['Firstname'] = Firstname

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/results', methods=['GET', 'POST'])
@is_logged_in
def results():
	data = None
	if request.method == 'POST':
#		selected_users = request.form.getlist("users")
		data = request.form['data']
		mid = data.find(":")
		region = str(data[1:mid-1])
		senType = str(data[mid+2:len(data)-1])
#		params=(region,senType)
	#	return str(len(senType))
#		return data

		try:
			with conn.cursor() as cur2:
				sql = "SELECT DATA FROM SENSOR WHERE Region=%s AND Type=%s"
				result = cur2.execute(sql,(region,senType))
				result = cur2.fetchall()
				conn.commit()
				for res in result:
					for r in res:
						value = r					
				
				
			if(result > 1):
				return str(value)		
			else:
				return "error"
		finally:
			return str(value)			
			
		
					

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
#    cur = mysql.connection.cursor()
	selected_sensors = request.form.getlist('r')
	
    # Get articles
#    result = cur.execute("SELECT * FROM Users")

#    articles = cur.fetchall()
#	flash("hello","success")
    	try:
		with conn.cursor() as cur1:
			#read a single record
				sql = "SELECT DISTINCT Region FROM SENSOR"
				res1 = cur1.execute(sql)
				conn.commit()
				Regions=cur1.fetchall()
				X=[]
				Y=[]
				Z=[]
				print Regions
				for Reg in Regions:
					for R in Reg:
						X.append(R)
				for Reg in Regions:
					sql = "SELECT Type FROM SENSOR WHERE Region=%s"
					res2 = cur1.execute(sql,(Reg))
					conn.commit()
					sensors=cur1.fetchall()
					Y.append(Reg)
					Y.append(sensors)
#					for sen in sensors:
#						for s in sen:
#							Y.append(s)

#				for y in Y:
#					for i in y:
#						Z.append(i)

#		print(len(Y), file=sys.stderr)
		if res1 > 0:	
		        return render_template('dashboard.html', Regions=Y)
#, sel_sensors=selected_sensors)
		else:
		        msg = 'No Articles Found'
			return render_template('dashboard.html', msg=msg)
	finally:
		if 'logged_in' in session:		
			flash('Your session is active','success')
		else:
			conn.close()	



#@app.route('/process', methods=['POST'])
#@is_logged_in
#def worker():
	# read json + reply
#	data = request.get_json()
#	result = ''

#	for item in data:
		# loop over every row
#		result += str(item['region']) + '\n'

#	return result


#def process():

#	return request.form
#	for reg in data:
#		email = request.form['email']
#		name = request.form['name']

#	if name and email:
#		newName = name[::-1]

#		return jsonify({'name' : newName})

#	return jsonify({'error' : 'Missing data!'})

	
####################################################################################

#	try:
#		with conn.cursor() as cursor:
			#read a single record
#				sql = "SELECT Name,Type,Region, CAST(Status AS UNSIGNED) AS Status FROM SENSOR ORDER BY Type"
#				result = cursor.execute(sql)
#				articles=cursor.fetchall()

#		if result > 0:	
#		        return render_template('dashboard.html', articles=articles)
#		else:
#		        msg = 'No Articles Found'
#			return render_template('dashboard.html', msg=msg)
#	finally:
#		if 'logged_in' in session:		
#			flash('Your session is active','success')
#		else:
#			conn.close()	        

##################################################################################		
    # Close connection
#    cur.close()

# Article Form Class
#class ArticleForm(Form):
#    title = StringField('Title', [validators.Length(min=1, max=200)])
#    body = TextAreaField('Body', [validators.Length(min=30)])

# Add Article
#@app.route('/add_article', methods=['GET', 'POST'])
#@is_logged_in
#def add_article():
#    form = ArticleForm(request.form)
#    if request.method == 'POST' and form.validate():
#        title = form.title.data
#        body = form.body.data

        # Create Cursor
#        cur = mysql.connection.cursor()

        # Execute
#        xo= cur.execute("SELECT * FROM Users")

        # Commit to DB
#        mysql.connection.commit()

        #Close connection
#        cur.close()

#        flash('Article Created', 'success')

#        return redirect(url_for('dashboard'))

#    return render_template('add_article.html', form=form)


# Edit Article
#@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
#@is_logged_in
#def edit_article(id):
    # Create cursor
#    cur = mysql.connection.cursor()

    # Get article by id
#    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

#    article = cur.fetchone()
#   # Get form
#    form = ArticleForm(request.form)

    # Populate article form fields
#    form.title.data = article['title']
#    form.body.data = article['body']

#    if request.method == 'POST' and form.validate():
#        title = request.form['title']
#        body = request.form['body']

        # Create Cursor
#        cur = mysql.connection.cursor()
#        app.logger.info(title)
        # Execute
#        cur.execute ("UPDATE articles SET title=%s, body=%s WHERE id=%s",(title, body, id))
        # Commit to DB
#        mysql.connection.commit()

        #Close connection
#       cur.close()

#        flash('Article Updated', 'success')

#        return redirect(url_for('dashboard'))

#    return render_template('edit_article.html', form=form)

# Delete Article
#@app.route('/delete_article/<string:id>', methods=['POST'])
#@is_logged_in
#def delete_article(id):
    # Create cursor
#    cur = mysql.connection.cursor()

    # Execute
#    cur.execute("DELETE FROM articles WHERE id = %s", [id])

    # Commit to DB
#    mysql.connection.commit()

    #Close connection
#    cur.close()

#    flash('Article Deleted', 'success')

#    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run('0.0.0.0','9001',debug=True)

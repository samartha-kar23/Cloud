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
#conn = pymysql.connect(host='10.14.88.224', user='root', password='sensor_cloud', db='SENSORS')
fip = pymysql.connect(host='10.14.88.224', user='root', password='sensor_cloud', db='neutron')
k=""
ip=""
"""
def floatip():

	try:
		with fip.cursor() as curs:
			sql = "select status,floating_ip_address from floatingips where status=%s"
			ip1 = curs.execute(sql,('DOWN'))
			ip2=curs.fetchone()
			ip=str(ip2[1])
			return ip

	finally:

		conn.close()
"""		
# Index
@app.route('/')
def index():
    return render_template('home.html')


# Register Form Class
class RegisterForm(Form):
	Firstname = StringField('Firstname', [validators.Length(min=1, max=50)])
	Lastname = StringField('Lastname', [validators.Length(min=1, max=50)])
#    username = StringField('Username', [validators.Length(min=4, max=25)])
	Email = StringField('Email', [validators.Length(min=6, max=50)])
	Password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Passwords do not match')])
	confirm = PasswordField('Confirm Password')
	Address = StringField('Address', [validators.Length(min=6, max=200)])
	Phone = StringField('Phone', [validators.Length(min=10, max=11)])

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        Firstname = form.Firstname.data
	Lastname = form.Lastname.data
        Email = form.Email.data
#        username = form.username.data
        Password = sha256_crypt.encrypt(str(form.Password.data))
	Address = form.Address.data
	Phone = form.Phone.data
        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO Users (Firstname,Lastname, Email, Password, Add1, Cell) VALUES(%s, %s, %s, %s, %s, %s)", (Firstname, Lastname, Email, Password, Address, Phone))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()
	time.sleep(2)
	subprocess.call(["python","/home/devstack/Desktop/Sensor_login/test.py"])
	#test.myfunction()
	time.sleep(2)
        flash('You are now registered and can log in', 'success')
	#subprocess.call('python /home/devstack/Desktop/login/instance.py',shell=True)
	#k= str(subprocess.check_output(["bash","/home/devstack/Desktop/login/create.sh"]))	
	
	#ip=floatip()
	#time.sleep(3)
	
	
	flash('Cloud instance initiated','success')
	#flash(k)
	#flash(ip)
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
		if Firstname == 'admin':
			return redirect(url_for('admin'))
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

	conn = pymysql.connect(host='10.14.88.224', user='root', password='sensor_cloud', db='SENSORS')
	data = None
	value = None
	if request.method == 'POST':
#		selected_users = request.form.getlist("users")
		data = request.form['data']
		mid = data.find(":")
		region = str(data[1:mid-1])
		senType = str(data[mid+2:len(data)-1])
#		params=(region,senType)
#		return str(len(senType))
#		return data
#		value = 1
		
		try:
			with conn.cursor() as cur2:
				sql = "SELECT Data FROM SENSOR WHERE Region=%s AND Id=%s"
				result = cur2.execute(sql,(region,senType))
				result = cur2.fetchone()
				print(region+':'+senType+'>'+result[0])				
				print result
#				time.sleep(0.3)
#				cur2.close()
				return result[0]
#				conn.commit()
				for res in result:
					value = res
										
				
										
#			conn.close()
#		finally:
#			return "session is okay"
#			return str(value)
			if(result > 1):
#				conn.close()
				return str(value)
#			return "success"		
			else:
				return "error"			
			
		finally:
#			
			conn.close()	
#			flash('Your session is active','success')	
#			conn.close()			
#			print str(value)
#			return str(value)

#######ADMIN#######
@app.route('/admin',methods=['GET', 'POST'])
@is_logged_in
def admin():
	conn = pymysql.connect(host='10.14.88.224', user='root', password='sensor_cloud', db='SENSORS')
	conn1 = pymysql.connect(host='10.14.88.224', user='root', password='sensor_cloud', db='Registration')	
	try: 		
		with conn.cursor() as cur2, conn1.cursor() as cur3:
			sql = "SELECT COUNT(DISTINCT Region) FROM SENSOR"
			rest1 = cur2.execute(sql)
			conn.commit()
			Regions = cur2.fetchall()
			sql2 = "SELECT DISTINCT Type FROM SENSOR"
			rest2 = cur2.execute(sql2)
			conn.commit()
			Types = cur2.fetchall()	
			sql3 = "select cast(Status as unsigned) as Status from SENSOR"
			rest3 = cur2.execute(sql3)
			conn.commit()
			count=0
			Status = cur2.fetchall()
			for status in Status:
				for s in status:
					if s!=1:
						count+=1
					else:
						continue
			sql4 = "select count(Id) from Users"
			rest4 = cur3.execute(sql4)
			conn1.commit()
			Idno = cur3.fetchall()	
						
			return render_template('admin.html',region=Regions[0][0], types=Types, status=count, idno=Idno[0][0])	
	finally: 
		conn.close()
		conn1.close()




@app.route('/about')
def about():
	return render_template('about.html')



# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	conn = pymysql.connect(host='10.14.88.224', user='root', password='sensor_cloud', db='SENSORS')
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
					sql = "SELECT Id,Type FROM SENSOR WHERE Region=%s"
					res2 = cur1.execute(sql,(Reg))
					conn.commit()
					sensors=cur1.fetchall()
					print sensors
					Y.append(Reg)
					Y.append(sensors)
#					for S in sensors:
#						print S
#					for sen in sensors:
#						for s in sen:
#							Y.append(s)
#				for Reg in Regions:
#					sql = "SELECT Id FROM SENSOR WHERE Region=%s"
					
#				for y in Y:
#					for i in y:
#						Z.append(i)

#		print(len(Y), file=sys.stderr)
		if res1 > 0:	
			print Y
		        return render_template('dashboard.html', Regions=Y)
#, sel_sensors=selected_sensors)
		else:
		        msg = 'No Articles Found'
			return render_template('dashboard.html', msg=msg)
	finally:
#		cur1.close()
		if 'logged_in' in session:		
			flash('Your session is active','success')
		else:
#			cur1.close()	
			flash('Your session is inactive','danger')
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

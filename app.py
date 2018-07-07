from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, jsonify
import requests
from flask_mysqldb import MySQL
import pymysql.cursors
from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField, validators, RadioField, SelectMultipleField, widgets
from wtforms.widgets import ListWidget, CheckboxInput
from passlib.hash import sha256_crypt
from functools import wraps
import subprocess
import time
#entry point of applications.
app = Flask(__name__) 

# Config MySQL
app.config['MYSQL_HOST'] = '10.14.88.224'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sensor_cloud'
app.config['MYSQL_DB'] = 'Registration'
# init MYSQL
mysql = MySQL(app)

k=""
ip=""
Service_Modes = [('Manual','Manual'),('Automatic','Automatic')]	
Data_Services = [('Images', 'Images'),('Temparature', 'Temparature'),('Humidity', 'Humidity'),('Moisture', 'Moisture'),('Water Level', 'Water Level'),('History','History')]

# Index
@app.route('/home')
@app.route('/')
def index():
    return render_template('home.html')


# Register Form Class
class MultiCheckboxField(SelectMultipleField):
    		widget = widgets.ListWidget(prefix_label=False)
    		option_widget = widgets.CheckboxInput()

class RegisterForm(Form):
	Firstname = StringField('Firstname', [validators.Length(min=1, max=50),validators.DataRequired(message='Firstname is required'),validators.Regexp('^\w+$',message='must be alphanumeric')])

	Lastname = StringField('Lastname', [validators.Length(min=1, max=50, message='Lastname is required'),validators.DataRequired(message='Password is required')])
#    username = StringField('Username', [validators.Length(min=4, max=25)])

	Email = StringField('Email', [validators.Length(min=6, max=50,message='Email is too short'),validators.Email(message='Please enter a valid email address'),validators.DataRequired(message='Email is required')])

	Password = PasswordField('Password', [validators.DataRequired(message='Password is required'), validators.EqualTo('confirm', message='Passwords do not match'),validators.Regexp('^\w+$',message='must be alphanumeric')])

	confirm = PasswordField('Confirm Password')

	Address = StringField('Address', [validators.DataRequired(message='Address is required'),validators.Length(min=6, max=200, message='Address is too short')])

	Phone = StringField('Phone', [validators.DataRequired(message='Phone number required'),validators.Length(min=10, max=11, message='Please enter a valid phone number.')])

    	Service_Modes = MultiCheckboxField('Service_Modes', choices=Service_Modes)
	Data_Services = MultiCheckboxField('Data_Services', choices=Data_Services)
	
	#AService = SelectMultipleField('Automatic Service', choices =AVAILABLE_CHOICES)



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
	Service_Modes = form.Service_Modes.data
	Data_Services = form.Data_Services.data
	mode = None
	Image = 0
	Temp = 0
	Humid = 0
	Mois = 0
	Waterl = 0
	Hist = 0
	if len(Service_Modes) > 0:
		if len(Service_Modes) == 2:
			mode = 3
		elif len(Service_Modes) == 1:
			if Service_Modes[0] == "Manual":
				mode = 1
			else:
				mode = 2
	else:
		mode = 0
		
	
	if len(Data_Services) > 0:
		for i in range(len(Data_Services)):
			if Data_Services[i] == "Images":
				Image = 1
			if Data_Services[i] == "Temparature":
				Temp = 1
			if Data_Services[i] == "Humidity":
				Humid = 1
			if Data_Services[i] == "Moisture":
				Mois = 1
			if Data_Services[i] == "Water Level":
				Waterl = 1
			if Data_Services[i] == "History":
				Hist = 1


        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO Users (Firstname,Lastname, Email, Password, Add1, Cell, mode, Hist, Waterl, Mois, Humid, Temp, Image) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (Firstname, Lastname, Email, Password, Address, Phone,mode, Hist, Waterl, Mois, Humid, Temp, Image ))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()
#	time.sleep(2)
	#subprocess call for instance creation by command line
###################
#	subprocess.call(["python","/home/devstack/Desktop/Sensor_login/test.py"])
###################	
	#test.myfunction()
#	time.sleep(2)
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
@app.route('/login/', methods=['GET', 'POST'])
@app.route('/login/<apptype>',methods=['GET', 'POST'])
def login(apptype=None):
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
		elif apptype == 'irrigation':
			return redirect(url_for('irrigation'))
		elif apptype == 'health':
			return redirect(url_for('health'))
		elif apptype == 'security':
			return redirect(url_for('security'))
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
		flash('Invalid login credentials', 'danger')
                return render_template('login.html')
		
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
	    flash('User not registered, kindly register', 'danger')
            return redirect(url_for('register'))
	    
    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)  #decorator-refer glossary
    def wrap(*args, **kwargs):
        if 'logged_in' in session:	#session check for logged in user
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
    #flash('You are now logged out', 'success')
    return redirect(url_for('index'))

@app.route('/results', methods=['GET', 'POST'])
@is_logged_in
def results():
	#connection creation to database SENSORS
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
			#will return no. of (regions, sensor types, active sensor count, and users registered)	
				
			return render_template('admin.html',region=Regions[0][0], types=Types, status=count, idno=Idno[0][0])	
	finally: 
		conn.close()
		conn1.close()

################ADMIN CLOSE###########################################################

################# ADMIN CONSOLE #####################################################
@app.route('/console',methods=['GET', 'POST'])
@is_logged_in
def console():
	data = None;
	if request.method == 'POST':
#		selected_users = request.form.getlist("users")
		data = request.form['data']
		code = "123"
		try:
		
			print code
			return code	
		finally:
			return "success"
################# ADMIN CONSOLE CLOSE ###############################################


###############IRRIGATION ############################################################

@app.route('/irrigation',methods=['GET', 'POST'])
@is_logged_in
def irrigation():
	value1 = [0]*10  #stores region 2 value
	value2 = [0]*5  #stores region 1 value
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
			sql4 = "SELECT Type,Id,cast(Status as unsigned) as Status,Data FROM SENSOR WHERE Region in ('R1','R2') order by Region"
			rest4 = cur2.execute(sql4)
			conn.commit()
			data = cur2.fetchall()	
			for i in range(len(data)):
#				if i > 4:
					for j in data[i]:
						if data[i].index(j) == 3:
							value1[i] = int(float(j))
#				else:
#					for k in data[i]:
#						if data[i].index(k) == 3:
#							value2[i] = int(float(k))
					
			#will return no. of (regions, sensor types, active sensor count, and users registered)	
			sql5 = "SELECT mode, Image, Temp, Humid, Mois, Waterl, Hist FROM Users WHERE Firstname=%s"
			rest5 = cur3.execute(sql5,(session['Firstname']))
			info = cur3.fetchall()			
						
			print info	
			return render_template('irrigation.html',region=Regions[0][0], types=Types, status=count, data=data, value1=value1, info=info[0])	
	finally: 
		conn.close()
		conn1.close()



##############IRRIGATION CLOSE #######################################################

############### HEALTH ############################################################

@app.route('/health',methods=['GET', 'POST'])
@is_logged_in
def health():
	value1 = [0]*10  #stores region 2 value
	value2 = [0]*5  #stores region 1 value
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
			sql4 = "SELECT Type,Id,cast(Status as unsigned) as Status,Data FROM SENSOR WHERE Region in ('R1','R2') order by Region"
			rest4 = cur2.execute(sql4)
			conn.commit()
			data = cur2.fetchall()	
			for i in range(len(data)):
#				if i > 4:
					for j in data[i]:
						if data[i].index(j) == 3:
							value1[i] = int(float(j))
#				else:
#					for k in data[i]:
#						if data[i].index(k) == 3:
#							value2[i] = int(float(k))
					
			#will return no. of (regions, sensor types, active sensor count, and users registered)	
			print value1	
			return render_template('health.html',region=Regions[0][0], types=Types, status=count, data=data, value1=value1)	
	finally: 
		conn.close()
		conn1.close()



##############HEALTH CLOSE #######################################################

###############SECURITY ############################################################

@app.route('/security',methods=['GET', 'POST'])
@is_logged_in
def security():
	value1 = [0]*10  #stores region 2 value
	value2 = [0]*5  #stores region 1 value
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
			sql4 = "SELECT Type,Id,cast(Status as unsigned) as Status,Data FROM SENSOR WHERE Region in ('R1','R2') order by Region"
			rest4 = cur2.execute(sql4)
			conn.commit()
			data = cur2.fetchall()	
			for i in range(len(data)):
#				if i > 4:
					for j in data[i]:
						if data[i].index(j) == 3:
							value1[i] = int(float(j))
#				else:
#					for k in data[i]:
#						if data[i].index(k) == 3:
#							value2[i] = int(float(k))
					
			#will return no. of (regions, sensor types, active sensor count, and users registered)	
			print value1	
			return render_template('security.html',region=Regions[0][0], types=Types, status=count, data=data, value1=value1)	
	finally: 
		conn.close()
		conn1.close()



##############SECURITY CLOSE #######################################################
################### Downloads ######################################################
@app.route('/download')
def download():
	return render_template('download.html')


#################### Downloads end #################################################

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
				Y=[] #will store regions and sensors as tuples
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
					print sensors # use this for console debug
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


#the flask __name__ is the main for this application
if __name__ == '__main__':
    app.secret_key='secret123'
    app.run('0.0.0.0','9001',debug=True)

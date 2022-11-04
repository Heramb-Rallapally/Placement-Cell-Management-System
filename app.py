from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_session import Session
import os
import psycopg2
import psycopg2 #pip install psycopg2
import psycopg2.extras
import re
import time
from werkzeug.security import generate_password_hash, check_password_hash
from common import cache


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


app.secret_key = "cairocoders-ednalan"
cache.init_app(app=app, config={"CACHE_TYPE": "SimpleCache"})


Session(app)


DB_NAME="flask_db"
DB_USER=os.environ['DB_USERNAME']
DB_PASS=os.environ['DB_PASSWORD']
DB_HOST="localhost"
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)


@app.route('/job')
def Ind():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = "SELECT * FROM job;"
    cur.execute(s) # Execute the SQL
    list_users = cur.fetchall()
    return render_template('job.html', list_users = list_users)


@app.route('/add_job', methods=['POST'])
def add_job():
    if request.method == 'POST':
        job_id = request.form['job_Id']
        company = request.form['Company']
        position = request.form['Position']
        eligibility = request.form.getlist('Eligibility')
        streligible=' '.join(eligibility)
        cgpa = float(request.form['CGPA'])
        loc = request.form['Location']
        type = request.form['type']
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO job (job_id, company, position, eligibility, cgpa, loc, type)'
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (job_id, company, position, streligible, cgpa, loc, type))
        except:
            flash("Job Id alreay exists")
            return redirect(url_for('Ind'))
        conn.commit()
        cache.set("my_value", job_id)
        if type == 'Fulltime':
            return redirect(url_for('fulltime'))
        else :
            return redirect(url_for('intern'))
        return redirect(url_for('Ind'))

    return render_template('job.html')

@app.route('/fulltime/', methods=('GET', 'POST'))
def fulltime():
    if request.method == 'POST':
        bond = request.form['bond']
        package = request.form['package']
        cur = conn.cursor()
        job_id=cache.get("my_value")
        cache.clear()
        cur.execute('INSERT INTO fulltime (job_id, bond, package)'
                    'VALUES (%s, %s, %s)',
                    (job_id, bond, package))
        conn.commit()
        return redirect(url_for('Ind'))
    return render_template('fulltime.html')


@app.route('/intern/', methods=('GET', 'POST'))
def intern():
    if request.method == 'POST':
        ppo = request.form['ppo']
        duration = request.form['duration']
        salary = request.form['salary']
        cur = conn.cursor()
        job_id=cache.get("my_value")
        cache.clear()
        cur.execute('INSERT INTO internship (job_id, duration, ppo, salary)'
                    'VALUES (%s, %s, %s, %s)',
                    (job_id, duration, ppo, salary))
        conn.commit()
        cur.close()
        return redirect(url_for('Ind'))
    return render_template('intern.html')


@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:

        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))



@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                #session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')

    return render_template('login.html')




@app.route('/loginadmin/', methods=['GET', 'POST'])
def loginadmin():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                #session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('adminHome'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('1Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')

    return render_template('loginadmin.html')


@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_student(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute('DELETE FROM job WHERE job_id = %s',
                (id,))
    cur.execute('DELETE FROM fulltime WHERE job_id = %s',
                (id,))
    cur.execute('DELETE FROM internship WHERE job_id = %s',
                (id,))
    conn.commit()
    flash('Job Removed Successfully')
    return redirect(url_for('Ind'))





@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        _hashed_password = generate_password_hash(password)

        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register.html')


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))



@app.route('/logoutadmin')
def logoutAdmin():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('loginadmin'))


@app.route('/profile')
def profile():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if user is loggedin
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))




@app.route('/home')
def studentHome():
    return render_template('home.html')



@app.route('/adminhome')
def adminHome():
    return render_template('adminhome.html')



@app.route('/db/')
def index():
    #conn = get_db_connection()
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1")

    cur.execute('SELECT * FROM Student;')
    students = cur.fetchall()
    cur.execute('SELECT * FROM UG;')
    ugs = cur.fetchall()
    cur.execute('SELECT * FROM PG;')
    pgs = cur.fetchall()
    cur.close()
    return render_template('index.html', students=students, ugs=ugs, pgs=pgs)


# ...

@app.route('/create/', methods=('GET', 'POST'))
def create():

    if session.get("username") == None:
       return redirect(url_for('login'))
    
    cur = conn.cursor()

    existt=cur.execute('SELECT *  FROM Student WHERE EXISTS(SELECT 1 FROM Student WHERE regNo= (%s))',(session['username'],))
    
    if request.method == 'POST':

        regno = request.form['regno']
        fname = request.form['fname']
        lname = request.form['lname']
        year = time.strptime(request.form['year'],"%Y-%m-%d")

        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        gender = request.form['gender']

        typee = request.form['type']
        cgpa = request.form['cgpa']
        fa = request.form['fa']
       

        #conn = get_db_connection()
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("SELECT 1")

        existt=cur.execute('SELECT *  FROM Student WHERE EXISTS(SELECT 1 FROM Student WHERE regNo= (%s))',(session['username'],))
    
        if existt==True:
           flash("Already exist")
           return render_template('home.html')
        else :
          cur.execute('INSERT INTO Student (regNo, firstName, lastName, dob, email, phoneNo, address, gender, type, cgpa, fa)' 'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (regno,
             fname,lname,str(year[0])+'-'+str(year[1])+'-'+str(year[2]),email,
             phone,address,gender,
             typee,cgpa,fa)
            )

          if typee=='UG':
           ch1=regno[0]
           ch2=regno[-2]
           ch3=regno[-1]
           ch1=ch1+ch2+ch3
           branch=""
           if ch1=="BME":
              branch="Bachelor of Technology, Mechanical Engineering"
           elif ch1=="BCE":
              branch="Bachelor of Technology, Chemical Engineering"
           elif ch1=="BCS":
              branch="Bachelor of Technology, Computer Science Engineering"
           elif ch1=="BEE":
              branch="Bachelor of Technology, Electrical Engineering"
           elif ch1=="BEC":
              branch="Bachelor of Technology, Electronics and Communication Engineering"

           cur.execute('INSERT INTO UG (regNo, branch, semester)' 'values (%s, %s, %s)',
		        (regno, branch, sem
		        )
		      )

          else:
           ch1=regno[0]
           ch2=regno[-2]
           ch3=regno[-1]
           ch1=ch1+ch2+ch3
           branch=""

           if ch1=="MCA":
              branch="Master in Computer Applications"
           elif ch1=="MME":
              branch="Master of Technology, Mechanical Engineering"
           elif ch1=="MCE":
              branch="Master of Technology, Chemical Engineering"
           elif ch1=="MCS":
              branch="Master of Technology, Computer Science Engineering"
           elif ch1=="MEE":
              branch="Master of Technology, Electrical Engineering"
           elif ch1=="MEC":
              branch="Master of Technology, Electronics and Communication Engineering"

           cur.execute('INSERT INTO PG (regNo, branch, semester)' 'values (%s, %s, %s)',
                 (regno, branch, sem
                 )
               )


          conn.commit()
          cur.close()
          return render_template('home.html')
    return render_template('create.html')





@app.route('/my-link/')
def my_link():
   cururl = request.url
   s2="?"
   regno=cururl[cururl.index(s2) + len(s2):]
   regno=str(regno)

   #conn = get_db_connection()
   conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
   cur = conn.cursor()
   cur.execute("SELECT 1")

   cur.execute('SELECT type from Student WHERE regNo = (%s)',(regno,))
   typee=cur.fetchall()
   #return typee
   typ=typee[0][0]

   if typ=='UG':
      cur.execute('DELETE FROM UG WHERE regNo = (%s)',
                (regno,))
   else:
      cur.execute('DELETE FROM PG WHERE regNo = (%s)',
                (regno,))

   cur.execute('DELETE FROM Student WHERE regNo = (%s)',
                (regno,))
   conn.commit()
   return redirect(url_for('index'))




@app.route('/view/')
def view():
    if session.get("username") == None:
       return redirect(url_for('login'))
    
    cur = conn.cursor()
    cur.execute("SELECT 1")
    
    cur.execute('SELECT * from Student WHERE regNo = (%s)',(session['username'],))
    details=cur.fetchall()
    
    cur.execute('SELECT type from Student WHERE regNo = (%s)',(session['username'],))
    typee=cur.fetchall()
    #return typee
    typ=typee[0][0]

    if typ=='UG':
       cur.execute('SELECT * from UG WHERE regNo = (%s)',(session['username'],))
       ugdetails=cur.fetchall()
       return render_template('view.html',details=details,ugdetails=ugdetails)
    else:
       cur.execute('SELECT * from PG WHERE regNo = (%s)',(session['username'],))
       pgdetails=cur.fetchall()
       return render_template('view.html',details=details,pgdetails=pgdetails)
    

@app.route('/edit/')
def edit():
    cur = conn.cursor()
    cur.execute("SELECT 1")
    
    cur.execute('SELECT * from Student WHERE regNo = (%s)',(session['username'],))
    details=cur.fetchall()
    
    cur.execute('SELECT type from Student WHERE regNo = (%s)',(session['username'],))
    typee=cur.fetchall()
    #return typee
    typ=typee[0][0]

    if typ=='UG':
       cur.execute('SELECT * from UG WHERE regNo = (%s)',(session['username'],))
       ugdetails=cur.fetchall()
       return render_template('editprofile.html',details=details,ugdetails=ugdetails)
    else:
       cur.execute('SELECT * from PG WHERE regNo = (%s)',(session['username'],))
       pgdetails=cur.fetchall()
       return render_template('editprofile.html',details=details,pgdetails=pgdetails)
       




@app.route('/update/', methods=('GET', 'POST'))
def update():

    if session.get("username") == None:
       return redirect(url_for('login'))
    
    cur = conn.cursor()
    #return request.method
    if request.method == 'POST':
        cgpa = request.form['cgpa']
        cursem = request.form['cursem']
        
        #return cgpa+cursem
        
        cur.execute('SELECT type from Student WHERE regNo = (%s)',(session['username'],))
        typee=cur.fetchall()
        typ=typee[0][0]

        #conn = get_db_connection()
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("SELECT 1")

        cur.execute("Update Student set cgpa = %s where regNo = %s",(cgpa,session['username'],))
    
        if typ=='UG': 
           cur.execute("Update UG set semester = %s where regNo = %s",(cursem,session['username'],))
    
        else:
           cur.execute("Update PG set semester = %s where regNo = %s",(cursem,session['username'],))
    
        conn.commit()
      
    cur.execute('SELECT * from Student WHERE regNo = (%s)',(session['username'],))
    details=cur.fetchall()
    
    cur.execute('SELECT type from Student WHERE regNo = (%s)',(session['username'],))
    typee=cur.fetchall()
    #return typee
    typ=typee[0][0]

    if typ=='UG':
       cur.execute('SELECT * from UG WHERE regNo = (%s)',(session['username'],))
       ugdetails=cur.fetchall()
       flash("Profile Updated")
       return render_template('view.html',details=details,ugdetails=ugdetails)
    else:
       cur.execute('SELECT * from PG WHERE regNo = (%s)',(session['username'],))
       pgdetails=cur.fetchall()
       flash("Profile Updated")
       return render_template('view.html',details=details,pgdetails=pgdetails)
    
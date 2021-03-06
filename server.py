from flask import Flask, render_template, request, redirect, url_for, session
from flask.ext.mail import Message, Mail
import MySQLdb, utils, os, unicodedata, datetime

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "tutoringscheduler@gmail.com"
MAIL_PASSWORD = "umwtutoringscheduler"

app = Flask(__name__)
app.config.from_object(__name__)
mail = Mail(app)

app.secret_key = os.urandom(24).encode('hex')

@app.route('/editAppointment', methods=['GET', 'POST'])
def editAppointment():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  apptime=request.args.get('apptime')
  numId=request.args.get('numId')
  datenum=request.args.get('datenum')
  subject=request.args.get('class')

  appquery = "SELECT studentId FROM appointments WHERE numId = '%s'" % (numId)
  cur.execute(appquery)
  app = cur.fetchone()
  sId = app['studentId']
  query = "SELECT firstname, lastname FROM users WHERE numId = '%s'" % (sId)
  cur.execute(query)
  student = cur.fetchone()
  fname=student['firstname']
  lname=student['lastname']
  name=fname + " " + lname
  sname=" "
  d= " "
  DEL = " "
  if request.method == 'POST':
    newTime = request.form['newTime']
    newDay = request.form['newDay']
    part = request.form['part']
    if 'delete' in request.form:
      query2 = "DELETE FROM appointments WHERE numId = '%s';" % (numId)
      cur.execute(query2)
      db.commit()
      return redirect(url_for('index'))
    else:
      upTime = newTime + part
      updatequery = "UPDATE appointments SET apptime = '%s', datenum = '%s' WHERE numId = '%s'" % (upTime, newDay, numId)
      cur.execute(updatequery)
      db.commit()
      d="done"
      datenum = newDay
      apptime = upTime
  return render_template('editAppointment.html',numId=numId, day=datenum, time=apptime, sub=subject, sname=name, done=d)

@app.route('/time')
def time():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  b=[]
  username = session['username']
  IDquery = "SELECT numId FROM users WHERE email = '%s'" % (username)
  cur.execute(IDquery)
  user = cur.fetchone()
  numId = user['numId']
  appQuery = "SELECT dayofweek, hourof FROM times WHERE studentId = '%s'" % (numId)
  cur.execute(appQuery)
  apps = cur.fetchall()
  for thing in apps:
    time = thing['hourof']
    day = thing['dayofweek']
    app = time + day
    b.append(app)
  return render_template('time.html',a=b)
  
@app.route('/editTime', methods=['GET', 'POST'] )
def editTime():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  username = session['username']
  error = "error"
  if request.method == 'POST':
    date = request.form.getlist('hour')
    query = "SELECT numId,classes FROM users WHERE email = '%s'" % (username)
    cur.execute(query)
    tutor = cur.fetchone()
    Id = tutor['numId']
    subjects = tutor['classes']
    query2 = "DELETE FROM times WHERE studentId = '%s';" % (Id)
    cur.execute(query2)
    db.commit();
    if date:
      for h in date:
        hour = h[:2]
        day = h[2:]
        if hour == "06":
          hour = "6:00AM"
        elif hour == "07":
          hour = "7:00AM"
        elif hour == "08":
          hour = "8:00AM"
        elif hour == "09":
          hour = "9:00AM"
        elif hour == "10":
          hour = "10:00AM"
        elif hour == "11":
          hour = "11:00AM"
        elif hour == "12":
          hour = "12:00PM"
        elif hour == "13":
          hour = "1:00PM"
        elif hour == "14":
          hour = "2:00PM"
        elif hour == "15":
          hour = "3:00PM"
        elif hour == "16":
          hour = "4:00PM"
        elif hour == "17":
          hour = "5:00PM"
        elif hour == "18":
          hour = "6:00PM"
        elif hour == "19":
          hour = "7:00PM"
        elif hour == "20":
          hour = "8:00PM"
        elif hour == "21":
          hour = "9:00PM"
        query3 = "INSERT INTO times (studentId,classes,dayofweek,hourof,available) VALUES('%s','%s','%s','%s',1);" % (Id,subjects,day,hour)
        cur.execute(query3)
        db.commit()
        error = "sucess"
  return render_template('editTime.html', errors = error)

@app.route('/index')
def index():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  curUser = session['username']
  query2 = "SELECT numId, firstname, lastname FROM users WHERE email = \'"+curUser+"\'"
  cur.execute(query2)
  user = cur.fetchone()
  userID = user['numId']
  fname = user['firstname']
  lname = user['lastname']
  name = fname + " " + lname
  adminName = ""
  adminQuery = "SELECT * FROM users WHERE accountStatus = 1;"
  cur.execute(adminQuery)
  row = cur.fetchone()
  fname = row['firstname']
  lname = row['lastname']
  username = fname + " " + lname
  searchQuery = "SELECT class, numId, datenum, apptime, tutorId FROM appointments WHERE studentId='%s'" % (userID)
  cur.execute(searchQuery)
  sresult = cur.fetchall()
  if not sresult:
    sresult = "Nothing"
  searchQuery2 = "SELECT class, numId, datenum, apptime, studentId FROM appointments WHERE tutorId='%s'" % (userID)
  cur.execute(searchQuery2)
  tresult = cur.fetchall()
  if not tresult:
    tresult = "Nothing"
  queryStat = "SELECT accountStatus FROM users WHERE email = '" + session['username'] + "' AND password = '" + session['password'] + "';"
  cur.execute(queryStat)
  row = cur.fetchone()
  Fullname = " "
  if row['accountStatus'] == 1:
    session['Status'] = "admin"
  elif row['accountStatus'] == 2:
    session['Status'] = "tutor"
  elif row['accountStatus'] == 3:
    session['Status'] = "student"
  return render_template('index.html', row=row, Fullname=name, sresults=sresult, tresults=tresult, adminName=username)

@app.route('/logout')
def logout():
  session.pop('logged_in',None)
  session.pop('username', None)
  session.pop('password', None)
  session.pop('Status', None)
  session.pop('logged_in', None)
  return redirect(url_for('login'))

@app.route('/edit', methods=['GET', 'POST'])
def edit():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  error = " "
  if request.method == 'POST':
    password = session['password']
    oldP = request.form['oldpassword']
    newPass = request.form['password']
    email = session['username']
    level = session['Status']
   
    error = "notSame"
    if oldP == password:
      if level != "admin":
        if not newPass:
          error = "pass"
        else:
          query = "UPDATE users SET password = '%s' WHERE email = '%s'" % (newPass, email)
          cur.execute(query)
          db.commit()
          error = "password"
      elif level == "admin":
        query1 = "SELECT * FROM users WHERE email = '%s';" % (email)
        cur.execute(query1)
        db.commit()
        info = cur.fetchone() 
        firstname = request.form['firstName']
        lastname = request.form['lastName']
        newEmail = request.form['email']
        if not firstname and not lastname and not newEmail and not newPass:
          error = "nothing"
        elif newEmail and '@mail.umw.edu' not in newEmail:
          error = "email"
        else:
          if not firstname:
            firstname = info['firstname']
          if not lastname:
            lastname = info['lastname']
          if not newEmail:
            newEmail = email
          if not newPass:
             newPass = password
          query = "UPDATE users SET firstname = '%s', lastname = '%s', email = '%s', password = '%s' WHERE email = '%s';" % (firstname, lastname, newEmail, newPass, email)
          cur.execute(query)
          db.commit()
          error = "new"
    session['password'] = newPass
  return render_template('edit.html', errors=error)

@app.route('/createTutor', methods=['GET', 'POST'])
def createTutor():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  created = " "
  if request.method == 'POST':
      row = []
      first = request.form['firstName']
      last = request.form['lastName']
      email = request.form['email']
      course = request.form['course']
      password = request.form['password']
      query2 = "SELECT * FROM users WHERE email = '%s';" % (email)
      cur.execute(query2)
      test = cur.fetchone()
      if test:
        if test['accountStatus'] == 1:
          created = "admin"
        elif test['accountStatus'] == 2:
          created = "no"
        elif test['accountStatus'] == 3:
          created = "updated"
          #if the query here does not activate, take out classes + and leave it '%s'
          query3 = "UPDATE users SET accountStatus = 2, classes = classes + '%s' WHERE email = '%s';" % (course, email)
          cur.execute(query3)
      else:
        created = "yes"
        query = "INSERT INTO users (firstname,lastname,email,password,accountStatus,classes) VALUES('%s','%s','%s','%s',2, '%s');" % (first,last,email,password, course)
        cur.execute(query)
        db.commit()
  return render_template('createTutor.html', created=created)

@app.route('/editTutor', methods=['GET', 'POST'])
def editTutor():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  created = request.args.get('created')
  if request.method == 'POST':
      first = request.form['firstname']
      last = request.form['lastname']
      email = request.form['email']
      query2 = "SELECT * FROM users WHERE email = '%s';" % (email)
      cur.execute(query2)
      test = cur.fetchone()
      if test:
        if test['accountStatus'] == 1:
          created = "admin"
        elif test['accountStatus'] == 2:
          query = "SELECT classes FROM users WHERE email = '%s';" % (email)
          cur.execute(query)
          classes = cur.fetchone()
          return redirect(url_for('editTutor2', classes=classes['classes'], email=email, first=first,last=last))
        elif test['accountStatus'] == 3:
          created = "student"
      else:
        created = "no"
  return render_template('editTutor.html', created=created)

@app.route('/add_courses', methods = ['GET','POST'])
def AdminDash():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  exist = ""
  results = ""
  if request.method == 'POST':
    subject = request.form['subject']
    num = request.form['number']
    course = subject + "-" + num
    search = "SELECT class, subject FROM classes WHERE class = '" + course + "';"
    result = cur.execute(search)
    if result:
      exist = "yes"
    elif not num:
      exist = "noNum"
    else:
      exist = "no"
      query = "INSERT INTO classes (class, subject) VALUES('" + course +"', '" + subject + "');"
      results = cur.execute(query)
      db.commit();
  return render_template('add_courses.html', exist = exist, results = results)

@app.route('/editTutor2', methods=['GET', 'POST'])
def editTutor2():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  classes = request.args.get('classes')
  tempClass = classes.split(',')
  first = request.args.get('first')
  last = request.args.get('last')
  created=""
  line = ""
  email = request.args.get('email')
  if request.method == "POST":
    num = request.form['CourseNum']
    subject = request.form['Subject']
    if num and subject:
      course = subject + "-" + num
      query = "SELECT classes FROM users WHERE email = '" + email + "' AND classes LIKE '%" + course + "%';"
      cur.execute(query)
      test = cur.fetchone()
    else:
      course = ""
      test = None
    delete = request.form['tutorCourse']
    if test:
      created="exist"
    else:
      if course and not delete:
        created = "updated"
        query3 = "UPDATE users SET classes = CONCAT(classes, ',%s') WHERE email = '%s';" % (course, email)
        cur.execute(query3)
        db.commit()
      elif course and delete:
        created = "both"
        for data in tempClass:
          if data != delete:
            if line == "":
              line = data
            else:
              line = line + "," + data
        query3 = "UPDATE users SET classes = '%s' WHERE email = '%s';" % (line, email)
        cur.execute(query3)
        db.commit()
        query3 = "UPDATE users SET classes = CONCAT(classes, ',%s') WHERE email = '%s';" % (course, email)
        cur.execute(query3)
        db.commit()
      elif not course and delete:
        created = "deleted"
        for data in tempClass:
          if data != delete:
            if line == "":
              line = data
            else:
              line = line + "," + data
        query3 = "UPDATE users SET classes = '%s' WHERE email = '%s';" % (line, email)
        cur.execute(query3)
        db.commit()
      elif not course and not delete:
        created = "nothing"
      return redirect(url_for('editTutor', created = created))
  return render_template('editTutor2.html', classes = tempClass, created=created, first=first, last=last)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  exist = " "
  if request.method == 'POST':
    firstname = request.form['firstName']
    lastname = request.form['lastName']
    email = request.form['email']
    reason = request.form['reason']
    query = "SELECT * FROM users WHERE firstname = '%s' AND lastname = '%s' AND email = '%s';" % (firstname, lastname, email)
    cur.execute(query)
    account = cur.fetchone()
    if email == session['username']:
      exist = "admin"
    elif account:
      exist = "yes"
      query2 = "DELETE FROM users WHERE firstname = '%s' AND lastname = '%s' AND email = '%s';" % (firstname, lastname, email)
      cur.execute(query2)
      db.commit();
    else:
      exist = "no"
  return render_template('delete.html', exists=exist)

@app.route('/', methods=['GET', 'POST'])
def login():
    db = utils.db_connect()
    cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    error = ""
    if request.method == 'POST':
      row = []
      email = request.form['email']
      password = request.form['password']
      query = "SELECT * FROM users WHERE email = '%s' AND password = '%s'" % (email, password) 
      cur.execute(query)
      login = cur.fetchone()
      db.commit()
      if login:
        session['username'] = email
        session['password'] = password
        session['logged_in'] = "yes"
        return redirect(url_for('index'))
      else:
        error = "true"
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET','POST'])
def register():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  errorMail = ""
  errorFirst = ""
  errorLast = ""
  errorPass = ""
  error = ""
  if request.method == 'POST':
    firstname=request.form['firstname']
    lastname=request.form['lastname']
    email=request.form['email']
    password=request.form['password']
    if "mail.umw.edu" in email and firstname and lastname and password:
      query = "INSERT INTO users (firstname,lastname,email,password,accountStatus) VALUES('%s','%s','%s','%s',3);" % (firstname,lastname,email,password)
      cur.execute(query)
      db.commit()
      return redirect(url_for('login'))
    else:
      error = "true"
      if "mail.umw.edu" or "umw.edu" not in email or not email:
        errorMail = "true"
      if not firstname:
        errorFirst = "true"
      if not lastname:
        errorLast = "true"
      if not password:
        errorPass = "true"
  return render_template('register.html', errorMail=errorMail, errorFirst=errorFirst, errorLast=errorLast, errorPass=errorPass, error=error)

@app.route('/Schedule')
def Schedule():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

  query = "SELECT DISTINCT subject FROM classes"
  cur.execute(query)
  db.commit()

  results=cur.fetchall()

  return render_template('schedule.html', subjects=results)

@app.route('/appoint2', methods=['GET', 'POST'])
def appointment2():
  subject = request.form['subject']
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

  query = "SELECT class FROM classes WHERE subject=\'" + subject + "\'"
  cur.execute(query)
  db.commit()

  classes = cur.fetchall()

  return render_template('schedule2.html', classes=classes)

@app.route('/hours',methods=['GET','POST'])
def hours():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  fname=request.args.get('firstname')
  lname=request.args.get('lastname')
  classes=request.args.get('subject')
  username=session['username']
  query = "SELECT numId FROM users WHERE email='%s'" % (username)
  cur.execute(query)
  student = cur.fetchone()
  sId = student['numId']
  username = fname + " " + lname
  b=[]
  IDquery = "SELECT numId FROM users WHERE firstname = '%s' AND lastname = '%s'" % (fname, lname)
  cur.execute(IDquery)
  user = cur.fetchone()
  numId = user['numId']
  appQuery = "SELECT dayofweek, hourof FROM times WHERE studentId = '%s' AND available = '0'" % (numId)
  cur.execute(appQuery)
  apps = cur.fetchall()
  for thing in apps:
    time = thing['hourof']
    day = thing['dayofweek']
    app = time + day
    b.append(app)
  return render_template('hours.html', name=username, a=b, tutorId=numId, studentId=sId, course=classes)


@app.route('/sched3', methods=['GET','POST'])
def sched3():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  selClass = request.form['class']
  query = "SELECT firstname, lastname, numId FROM users WHERE classes LIKE '%" + selClass + "%';"
  cur.execute(query)
  tutors = cur.fetchall()
  return render_template('sched3.html', results = tutors, course=selClass)  

@app.route('/appoint4', methods=['GET', 'POST'])
def appointment4():
  selClass=request.args.get('selClass')
  dayofweek=request.args.get('dayofweek')
  studentId=request.args.get('studentId')
  hourof=request.args.get('hourof')

  if(dayofweek == 'Monday'):
    dayNum = 0
  elif(dayofweek == 'Tuesday'):
    dayNum = 1
  elif(dayofweek == 'Wednesday'):
    dayNum = 2
  elif(dayofweek == 'Thursday'):
    dayNum = 3
  elif(dayofweek == 'Friday'):
    dayNum = 4
  elif(dayofweek == 'Saturday'):
    dayNum = 5
  else:
    dayNum = 6

  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  query = "SELECT firstname, lastname FROM users WHERE numId=\'"+studentId+"\'" # ORDERBY dayofweek"
  cur.execute(query)
  db.commit()

  tutor = cur.fetchone()

  tutorFirst = tutor['firstname']
  tutorLast = tutor['lastname']
  name = tutorFirst + " " + tutorLast

  date = datetime.date.today()
  currentDate = datetime.date.today().weekday()
  if(currentDate <= dayNum):
    newDateNum = dayNum - currentDate
    d = datetime.timedelta(days=newDateNum)
    dayofweekhour = date + d
    nextorlast = "This"
  else:
    nextorlast = "Next"
    
  appDay = nextorlast + " " + dayofweek
  results = {'class':selClass, 'dayofweek':dayofweek, 'nextorlast':nextorlast, 'tutorFirst':tutorFirst, 'tutorLast':tutorLast, 'hourof':hourof}
  
  return render_template('schedule4.html', results=results)

@app.route('/bookapp', methods=['GET','POST'])
def booking():
  tutorName = request.form['name']
  selClass = request.form['class']
  day = request.form['dayofweek']
  time = request.form['time']

  names = tutorName.split(" ")
  firstname = names[0]
  lastname = names[1]

  actDay = day.split(" ")
  day = actDay[1]

  curUser = session['username']

  db= utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  curUserQuery = "SELECT numId FROM users WHERE email=\""+curUser+"\""

  cur.execute(curUserQuery)
  db.commit()

  userIDDict = cur.fetchone()
  userID = userIDDict['numId']

  tutorQuery = "SELECT numId FROM users WHERE firstname=\""+firstname+"\" AND lastname=\"" + lastname + "\""

  cur.execute(tutorQuery)
  db.commit()

  tutorIDDict = cur.fetchone()
  tutorID = tutorIDDict['numId']
  
  bookquery = "UPDATE times SET available = 1 WHERE studentId = '%s' AND hourof = '%s' AND dayofweek = '%s';" % (tutorID, time, day)
  cur.execute(bookquery)
  db.commit()
  
  appointQuery = "INSERT INTO appointments (datenum,apptime,class,studentId,tutorId) VALUES('%s','%s','%s','%d','%d');" % (day,time,selClass,userID,tutorID)
  
  cur.execute(appointQuery)
  db.commit()

  emailSubject = "UMW %s Tutoring Appointment" % (selClass)
  emailToStudent = "Hi There! Your appointment for tutoring in %s with %s %s has been made for %s at %s. Thank you for using the UMW Tutoring Scheduler!" % (selClass, firstname, lastname, day, time)
  emailToTutor = "blah"
  mail.connect()
  studentmsg = Message('Hello', sender='tutoringscheduler@gmail.com', recipients=[session['username']])
  studentmsg.subject = emailSubject
  studentmsg.body = emailToStudent
  mail.send(studentmsg)

  return render_template('booked.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
  db = utils.db_connect()
  cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
  adminName = ""
  adminQuery = "SELECT * FROM users WHERE accountStatus = 1;"
  cur.execute(adminQuery)
  row = cur.fetchone()
  fname = row['firstname']
  lname = row['lastname']
  username = fname + " " + lname
  stuff = ""
  results = ""
  queryType = ""
  a=""
  if request.method == 'POST':
    queryType = "yes"
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    subject = request.form['Subject']
    course = request.form['CourseNum']
    a = subject+"-"+course
    if firstname and lastname and not course:
      query = "SELECT firstname, lastname, classes FROM users WHERE firstname LIKE '" + firstname + "' AND lastname LIKE '" + lastname + "' AND accountStatus = 2 AND classes LIKE '%" + subject + "%';"
      cur.execute(query)
      results = cur.fetchall()
      db.commit()
    elif (firstname or lastname) and not course:
      query = "SELECT firstname, lastname, classes FROM users WHERE (firstname LIKE '" + firstname + "' OR lastname LIKE '" + lastname + "') AND accountStatus = 2 AND classes LIKE '%" + subject + "%';"
      cur.execute(query)
      results = cur.fetchall()
      db.commit()
    elif firstname and lastname and course:
      query = "SELECT firstname, lastname, classes FROM users WHERE firstname LIKE '" + firstname + "' AND lastname LIKE '" + lastname + "' AND accountStatus = 2 AND classes LIKE '%" + subject + "-" + course + "%';"
      cur.execute(query)
      results = cur.fetchall()
      db.commit()
    elif (firstname or lastname) and course:
      query = "SELECT firstname, lastname, classes FROM users WHERE (firstname LIKE '" + firstname + "' OR lastname LIKE '" + lastname + "') AND accountStatus = 2 AND classes LIKE '%" + subject + "-" + course + "%';"
      cur.execute(query)
      results = cur.fetchall()
      db.commit()
    elif not firstname and not lastname: #Search by course
      if subject and not course:
        query = "SELECT firstname, lastname, classes FROM users WHERE classes LIKE '%" + subject + "%';"
        cur.execute(query)
        results = cur.fetchall()
        db.commit()
      elif subject and course:
        query = "SELECT firstname, lastname, classes FROM users WHERE classes LIKE '%" + subject + "-" + course + "%';"
        cur.execute(query)
        results = cur.fetchall()
        db.commit()
  return render_template('search.html', stuff = stuff, selectedMenu='search', results=results, queryType=queryType, adminName=username, a=a)
  

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)


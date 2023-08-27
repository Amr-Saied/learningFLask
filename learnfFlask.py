from sqlite3 import IntegrityError
from flask import Flask, request, url_for, redirect, render_template, session, flash
from datetime import timedelta , datetime
import utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import db , validators
app = Flask(__name__)
app.secret_key = "more123_sexiness"
app.permanent_session_lifetime = timedelta(days=5)
connection = db.connect_to_database()
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["50 per minute"])


@app.route("/")
def index():
   return "This is Web Application of Team8/Amr006 xD"

@app.route("/home")
def home():
    check_login = session.get('logged_in', False)
    check_register = session.get('registered', False)
    if check_login and check_register:
        return render_template("index.html", gadgets = db.get_all_gadgets(connection))
    elif check_register and not check_login :
        return redirect(url_for('login'))
    else:
        return redirect(url_for('register'))

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per minute") 
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if not utils.is_strong_password(password):
            flash("Sorry You Entered a weak Password Please Choose a stronger one", "danger")
            return render_template('register.html')
        token = db.get_user_by_username(connection, username)

        if not token : 
            hashedPassword = utils.hash_password(password)
            db.add_user(connection, username, hashedPassword) # if username in database already in database it will return an error to terminate the server
            
            session['username'] = username
            session['logged_in'] = True
            session['registered'] = True
            session['user_id'] = db.get_user_by_username(connection, username)[0]
            return redirect(url_for('home'))
        else: 
            flash('User already exists!')
            session['registered'] = True
            return redirect(url_for('login'))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute") 
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = db.get_user_by_username(connection, username)
        if user:
            real_password = user[2]
            if utils.is_password_match(password , real_password):
                session['logged_in'] = True
                session['username'] = username
                session['user_id'] = user[0]
                return redirect(url_for('home'))
            else:
                flash('Incorrect Password. Please try again.')
        else:
            flash('User does not exist. Please register!')
            return redirect(url_for('register'))
    return render_template("login.html")


@app.route("/upload-gadget", methods = ["GET", "POST"])
@limiter.limit("10 per minute") 
def uploadGadget():

    check_login = session.get('logged_in', False)
    check_register = session.get('registered', False)

    if check_register and not check_login :
        return redirect(url_for('login'))
    elif not check_register and not check_login:
        return redirect(url_for('register'))

    if request.method == "POST":
        image_for_gadget = request.files['image']                   

        if not image_for_gadget or image_for_gadget.filename == '':
            flash('Nothing was Selected, please Choose something')
            return render_template('upload-gadget.html')
    
        if not validators.allowed_file(image_for_gadget.filename) or not validators.allowed_file_size(image_for_gadget):
            flash("Invalid File is Uploaded", "danger")
            return render_template("upload-gadget.html")

        title_of_gadget = request.form['title']
        description_to_gadget = request.form['description']
        price_of_gadget = request.form['price']
        
        image_url = f"uploads/{image_for_gadget.filename}"+ datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        image_for_gadget.save("static/" + image_url)
        user_id = session['user_id']
        db.add_gadget(connection, user_id, title_of_gadget, description_to_gadget, price_of_gadget, image_url)
        return redirect(url_for('home'))

    return render_template("upload-gadget.html")

@app.route('/gadget/<gadget_id>')
def getGadget(gadget_id):
	# Retrieve gadget information and comments from the database
  try:
      gadget = db.get_gadget(connection, gadget_id)
      comments = db.get_comments_for_gadget(connection,gadget_id)
  except IntegrityError:
      flash('Not Found')
      return redirect(url_for('home'))

  return render_template("gadget.html", gadget=gadget, comments=comments)


@app.route('/add-comment/<gadget_id>', methods=['POST'])
@limiter.limit("10 per minute") 
def addComment(gadget_id):
	text = request.form['comment']
	user_id = session['user_id']
	db.add_comment(connection, gadget_id, user_id, text)
	return redirect(url_for("getGadget", gadget_id=gadget_id))


@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('logged_in', None)
    flash('Logged Out Successfully!')
    return redirect(url_for("login"))

if __name__ == "__main__":
    db.init_db(connection)
    db.init_gadgdet_db(connection)
    db.init_comments_table(connection)
    app.run(debug=True)

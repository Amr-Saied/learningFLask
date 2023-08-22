from sqlite3 import IntegrityError
from flask import Flask, request, url_for, redirect, render_template, session, flash
from datetime import timedelta
import db , validators
app = Flask(__name__)
app.secret_key = "more123_sexiness"
app.permanent_session_lifetime = timedelta(days=5)
connection = db.connect_to_database()



@app.route("/")
def index():
   return "This is Web Application of Team8/more123 :D"

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
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        token = db.get_user_by_username(connection, username)

        try:
            db.add_user(connection, username, password)
            session['username'] = username
            session['logged_in'] = True
            session['registered'] = True
            session['user_id'] = db.get_user_by_username(connection, username)[0]
            return redirect(url_for('home'))
        except IntegrityError:
            flash('User already exists!')
            return redirect(url_for('login'))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = db.get_user_by_username(connection, username)
        if user:
            real_password = user[2]
            if password == real_password:
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

@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('logged_in', None)
    flash('Logged Out Successfully!')
    return redirect(url_for("login"))

@app.route("/upload-gadget", methods = ["GET", "POST"])
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
    
        # if validators.allowed_file(image_for_gadget.filename) or not validators.allowed_file_size(image_for_gadget):
        #     flash("Invalid File is Uploaded", "danger")
        #     return render_template("upload-gadget.html")

        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        
        image_url = f"uploads/{image_for_gadget.filename}"
        image_for_gadget.save("static/" + image_url)
        user_id = session['user_id']
        db.add_gadget(connection, user_id, title, description, price, image_url)
        return redirect(url_for('home'))

    return render_template("upload-gadget.html")

if __name__ == "__main__":
    db.init_db(connection)
    db.init_gadgdet_db(connection)
    app.run(debug=True)

from flask_app import app
from flask import render_template, redirect, request, session, flash, url_for
from flask_app.models.user import User
from flask_app.models.company import Company
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)


@app.route('/')
def home():
    return render_template('landing.html')
@app.route('/dashboard') #Only accessed once a user is logged in.
def dash():
    return render_template('index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = { 'email' : request.form['email']}
        user_in_db = User.get_email(data)
        if not user_in_db:
            flash("Invalid Email/Password. Please try again.")
        elif not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
            flash("Invalid Email/Password. Please try again.")
        else:
            session['user_id'] = user_in_db.id
            session['first_name'] = user_in_db.first_name
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/create_user')
def register():
    return render_template('create_user.html')

@app.route('/registration/process', methods=['POST'])
def registered():
    is_valid = User.validate_user(request.form)
    if not is_valid:
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "role": request.form["role"],
        "email": request.form["email"],
        "password": pw_hash,
        "confirm_password": request.form["confirm_password"]
    }
    User.save(data)
    return redirect("/")

@app.route("/customers")
def all_customers():
    return render_template('my-customers.html')

@app.route("/new/company") #This displays a form for adding 
def creating_company():
    return render_template("company_creation.html")

@app.route("/new/company/create", methods=['POST'])
def company_submission():
    if "user_id" not in session:
        return redirect('/login')
    if not Company.validate_company(request.form):
        return redirect('/new/company')
    user_id=session["user_id"]
    session["company_name"]= request.form["company_name"]
    session["physical_address"]= request.form["physical_address"]
    session["phone_number"]= request.form["phone_number"]
    data = {
        "company_name": request.form["company_name"],
        "physical_address": request.form["physical_address"],
        "phone_number": request.form["phone_number"],
        "user_id": user_id
    }
    Company.create_company(data)
    return redirect("/dashboard")
@app.route('/edit/<int:id>')
def edit_post(id):
    if "user_id" not in session:
        return redirect('/')
    single_company=Company.get_one(id)
    return render_template("edit_post.html", single_company= single_company,id=id)

@app.route('/edit/<int:id>/finalize', methods=["POST"])
def finalize_edit(id):
    if not Company.validate_post(request.form):
        return redirect('/edit/<int:id>')
    data = {
        "company_name": request.form["company_name"],
        "physical_address": request.form["physical_address"],
        "phone_number": request.form["phone_number"],
        "id": id
    }
    Company.edit_company(data)
    return redirect('/index')

@app.route('/company/delete/<int:id>')
def delete(id):
    if "user_id" not in session:
        return redirect(url_for('login'))
    Company.delete(id)
    return redirect('/')


@app.route('/logout')
def logging_out():
    session.clear()
    return redirect('/')

@app.route('/csv')
def upload_csv():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        df = pd.read_csv(filename)
        html_table = df.to_html(classes='table table-striped', escape=False, index=False)
        return render_template('index.html', html_table=html_table)

#------------------------------------------------------------------------------------
@app.route('/new_note')
def note_template():
    return render_template('notes.html')
    
#------------------------------------------------------------------------------------
# from flask_app import app
# from flask import Flask, render_template, redirect, request
# from flask_app.models.user import User
# from flask_bcrypt import Bcrypt
# bcrypt = Bcrypt(app)

# app = Flask(__name__)    
# @app.route('/')
# def landing_page():
#     return render_template('landing.html')
# @app.route('/dashboard')         
# def hello_world():
#     return render_template('index.html')
# @app.route('/registration')
# def register():
#     return render_template('create_user.html')

# @app.route('/registration/process', methods=['POST'])
# def registered():
#     is_valid = User.validate_user(request.form)
#     if not is_valid:
#         return redirect('/')
#     pw_hash = bcrypt.generate_password_hash(request.form['password'])
#     data = {
#         "first_name": request.form["first_name"],
#         "last_name": request.form["last_name"],
#         "email": request.form["email"],
#         "password": pw_hash,
#         "confirm_password": request.form["confirm_password"]
#     }
#     User.save(data)
#     return redirect("/")

if __name__=="__main__":   # Ensure this file is being run directly and not from a different module    
    app.run(debug=True)    # Run the app in debug mode.

###### Imports ##########
import os
from flask import Flask,render_template,redirect, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_required,login_user,logout_user,UserMixin,current_user
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
####### app start as flask and template ##############
app = Flask(__name__, template_folder='templates')
####### requirments of database setup ########
app.config['UPLOAD_FOLDER'] = "D:\\flask-login\\internship\\upload_files"
app.config['SECRET_KEY'] = '69565'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)
######### Login set up ################
login_manager = LoginManager()
login_manager.init_app(app)
#############Data base ############

class User(UserMixin,db.Model):
    __tablename__ = 'User'
     
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    
    def __init__(self,name,email,password):
        self.name = name
        self.email = email
        self.password = password
    
class Uploder(db.Model):
    __tablename__ = 'Uploader'
    
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    description = db.Column(db.String(100))
    image =  db.Column(db.String(120), nullable=False)
    
    def __init__(self,description,image):
        self.description = description
        self.image = image

################# data base commands ##############
# 1 => flask db init          to start database
# 2 => flask db migrate        to migrate database
#3  => flask db upgrade        if you make changes then perform it
######### With out login routes ###############

@login_manager.user_loader
def get(id):
    return User.query.get(id)


@app.route('/')
def index():
    return render_template('index.html')


# ############ Here is the Authentication ########
@app.route('/handlesignup')
def handlesignup():
    return render_template("signup.html")

@app.route('/handlelogin')
def handlelogin():
    return render_template("login.html")

############# Sign up #####################
@app.route("/signup", methods=["POST"])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('uname')
        password = request.form.get('pass')
        user = User.query.filter_by(email=email).first()
        if user:
            return redirect('handlesignup')
        new_user = User(email=email,name=name,password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect('/dashboard')
    return redirect('handlesignup')


@app.route('/login',methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return redirect('handlelogin')
        if user or check_password_hash(user.password, password):
            login_user(user)
            return redirect('/dashboard')
    return redirect('handlelogin')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')



############### User Routes ############
@app.route('/dashboard')
@login_required
def dashboard():
    
    users = User.query.all()
    n = len(users)
    return render_template('dashboard.html',name=current_user.name,users=users,n=n)

@app.route('/uploader',methods=['GET','POST'])
@login_required
def uploader():
    if request.method == 'POST':
        img = request.files['file1']
        desc = request.form.get('desc')
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(img.filename)))
        new_upload = Uploder(description=desc,image=img.filename)
        db.session.add(new_upload)
        db.session.commit()
        return render_template('upload.html')
    return render_template('upload.html')
    

app.run(debug=True)

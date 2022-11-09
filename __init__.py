from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from werkzeug.utils import secure_filename
import os
import string
import random

title="Market"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///market.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "KSLJDFLKJSD"
db = SQLAlchemy(app)

class User(db.Model):
    u_id = db.Column(db.Integer,primary_key=True)
    u_name = db.Column(db.String(100),nullable=False,unique=True)
    u_pass = db.Column(db.String(100),nullable=False)
    u_email = db.Column(db.String(100),nullable=False,unique=True)

class Product(db.Model):
    p_id = db.Column(db.Integer, primary_key=True)
    p_name = db.Column(db.String(100), nullable=False)
    p_category = db.Column(db.Integer,db.ForeignKey('category.c_id'))
    p_status = db.Column(db.String(80), nullable=False)
    p_manuf = db.Column(db.String(80), nullable=False)
    p_image = db.Column(db.String(100), nullable=False)
    # p_image = db.Column(db.DateTime(timezone=True),server_default=func.now())
    p_desc = db.Column(db.Text)

    def __repr__(self):
        return f'<Product {self.p_name}>'

class Category(db.Model):
    c_id = db.Column(db.Integer, primary_key=True)
    c_product = db.relationship('Product',backref='category')
    c_name = db.Column(db.String(100),nullable=False,unique=True)
    
# Product.p_category = relationship("Category", order_by = c_id, back_populates = "customer")


def insert_product(p_name, p_category, p_status, p_manuf, p_image, p_desc):
    pro_ins = Product(p_name=p_name,p_category=p_category,p_status=p_status,p_manuf=p_manuf,p_image=p_image,p_desc=p_desc)
    db.session.add(pro_ins)
    db.session.commit()
    if pro_ins.p_id:
        print(pro_ins.p_id)
        return True
    else:
        return False
     

@app.route("/",methods=["GET","POST"])
def index():
    if request.method == "POST":
        products = ""
        products = Product.query.filter(Product.p_name.like('%'+request.form['item_search']+'%'))
    else:
        products = Product.query.join(Category, Product.p_category==Category.c_id).add_columns(Product.p_id,Product.p_name,Product.p_desc,Product.p_image,Category.c_name).filter(Product.p_category == Category.c_id)
    print(products)
    return render_template("index.html",title=title,products = products)

@app.route('/admin/add-category',methods=["POST"])
def add_category():
    if request.method == "POST":
        category_name = request.form['category_name']
        category_orm = Category(c_name=category_name)
        db.session.add(category_orm)
        db.session.commit()
        if category_orm.c_id:
            print("Added with id: "+str(category_orm.c_id))
            return redirect('/')
        else:
            return redirect('/admin')


@app.route('/admin',methods=["POST","GET"])
def admin():
    if request.method == "POST":
        print(request.form)
        try:
            p_status = request.form['active_status']
        except:
            p_status = "off"
        p_image = "images/user_upload/"
        image_file = request.files['product_image']
        random_name = res = ''.join(random.choices(string.ascii_letters, k=10))
        image_name = secure_filename(random_name+""+image_file.filename)
        image_file.save("./static/images/user_upload/"+image_name)
        print("Image name:"+image_name)
        p_name = request.form['product_name']
        p_category = request.form['product_category']
        p_desc = request.form['product_description']
        p_image = p_image+""+image_name
        p_manuf = request.form['product_manufacturer']
        if insert_product(p_name,int(p_category),p_status,p_manuf,p_image,p_desc) == True:
            print("\nSuccess")
        else:
            print("\nError occured")
    # print(request.form)
    return render_template("admin.html",title="Admin Panel",categories = Category.query.all())

@app.route('/profile',methods=["POST","GET"])
def profile():
    if not session.get("logged_user"):
        return redirect("login")
    else:
        print(session["logged_user"])
        return render_template("profile.html",title=session.get("logged_user"))

@app.route('/products/id/<pid>')
def product_detail(pid):
    try:
        product_detail = Product.query.join(Category, Product.p_category==Category.c_id).add_columns(Product.p_id,Product.p_name,Product.p_desc,Product.p_image,Category.c_name).filter(Product.p_id == pid).one()
        print(product_detail.p_id)
        return render_template("product_detail.html",title="Product",product=product_detail)
    except:
        return redirect("/")

@app.route('/login',methods=["POST","GET"])
def login():
    if request.method == "POST":
        
        username = request.form['username']
        password = request.form['userpass']
        # user_value = User(u_name=username,u_email=useremail,u_pass = password)
        auth_response = User.query.filter(User.u_name == username,User.u_pass == password).count()
        if auth_response == 1:
            session["logged_user"] = username
            flash("Log in success","success")
            return redirect("profile")
        else:
            flash("Username or Password is incorrect","error")
            return render_template("login.html",title="login")
        # print(auth_response)
        # if username=="admin" and password == "admin":
        #     return render_template("admin.html",title="Admin Panel")
        # else:
        #     return render_template("login.html",title="login")
    else:
        return render_template("login.html",title="login")
@app.route('/logout')
def logout():
    session.pop("logged_user")
    return redirect('/')
@app.route('/register',methods=["POST","GET"])
def register():
    if request.method == "POST":
        useremail = request.form['useremail']
        username = request.form['username']
        password = request.form['userpass']
        user_value = User(u_name=username,u_email=useremail,u_pass = password)
        try:
            db.session.add(user_value)
            db.session.commit()
        except exc.SQLAlchemyError as error:
            print("Username or Email already exist"+error)
        return redirect("profile")
    else:
        return render_template("register.html",title="Register")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True) #default port is 5000
    



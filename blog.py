from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt

# Kullanici Kayit Formu
class RegisterForm(Form):
    name = StringField("Isim Soyisim", validators=[validators.Length(min=4, max=30)])
    username = StringField("Kullanici adi", validators=[validators.Length(min=5, max=35)])
    email = StringField("Email Adresi", validators=[validators.Email(message="Lutfen Gecerli Email Adresi Girin")])
    password = PasswordField("Parola:", validators=[
        validators.DataRequired(message="Lutfen Parola belirleyin"),
        validators.EqualTo(fieldname = "confirm",message="Parolaniz Uyusmuyor")
    ])
    confirm = PasswordField("Parola Dogrula")
# Login Formu
class LoginForm(Form):
    username =  StringField("Kullanici Adi")
    password = PasswordField("Parola")


app = Flask(__name__)
app.secret_key = "adilblog"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "AdilBlog"
app.config["MYSQL_CURSORCLASS"]= "DictCursor"

mysql = MySQL(app)

@app.route("/")
def index():
    articles =[
        {"id":1,"title":"Deneme1","content":"deneme 1 icerik"},
        {"id":2,"title":"Deneme2","content":"deneme 2 icerik"},
        {"id":3,"title":"Deneme3","content":"deneme 3 icerik"}
    ]
    return render_template("index.html", articles = articles)

@app.route("/about")
def about():
    return render_template("about.html")


# Kayit olma
@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password =sha256_crypt.encrypt(form.password.data)
        cursor = mysql.connection.cursor()
        
        sorgu = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()
        flash("Basariyla Kayit oldunuz...","success")
        return redirect(url_for("login"))
    else: 
        return render_template("register.html",form=form)
#Login islemi
@app.route("/login", methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()
        
        sorgu = "Select * From users where username = %s"

        result = cursor.execute(sorgu,(username,))
        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered, real_password):
                flash("Basariyla Giris Yaptiniz....", "success")
                return redirect(url_for("index"))
            else:
                flash("Parolanizi Yanlis Girdiniz...", "danger")
                return redirect(url_for("login"))
        else:
            flash("Boyle bir Kullanici adi bulunmuyor...", "danger")
            return redirect(url_for("login"))
    return render_template("login.html",form = form)

if __name__ == "__main__":
    app.run(debug=True)
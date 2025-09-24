from flask import Flask, render_template, url_for, request, redirect, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizza.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # потом понять, что это
app.secret_key = 'f9c8307a7ec441477937cb35c6303b01c1f8b6b285bfa989c11bdc2eed2bd5b3' # Его так никогда нельзя хранить, всегда в других файлах
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Users(db.Model): 
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False) 
    email = db.Column(db.String(50), nullable=False, unique=True)    
    pswd = db.Column(db.Text(200), nullable=False)
    
    def repr(self):
        return '<Users %r>' % self.id_user

@app.before_request
def load_user():
    if "user_id" in session:
        g.user = Users.query.get(session["user_id"])
    else:
        g.user=None

# Главная страница
@app.route("/")
def index():
    return render_template("index.html")
  
# Регистрация
@app.route("/reg", methods=["GET", "POST"])
def reg():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        pswd = bcrypt.generate_password_hash(request.form['pswd']).decode('utf-8')

        if Users.query.filter_by(email=email).first():
            return "Эта почта уже зарегестрирована", 400

        new_user = Users(username=username, email=email, pswd=pswd)

        try:
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id_user
            return redirect(url_for('MyProfile', id=new_user.id_user))
        except:
            return 'Ошибка при регистрации'
        
    return render_template("reg.html")
  
# Вход
@app.route("/sign", methods=["GET", "POST"])
def sign():
    if request.method == "POST":
        email = request.form["email"]
        pswd = request.form["pswd"]

        user = Users.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.pswd, pswd):
            session["user_id"] = user.id_user
            return redirect(url_for("MyProfile", id=user.id_user))  
        else:
            return "Неверный email или пароль", 401  

    return render_template("sign.html")

  
# Корзина
@app.route("/Purchases")
def Purchases():
    return render_template("Purchases.html")
  
# Мой профиль
@app.route("/MyProfile/<int:id>")
def MyProfile(id):
    if "user_id" not in session or session["user_id"] != id:
        return redirect(url_for("sign"))

    user= Users.query.get(id)
    if user:
        return render_template("MyProfile.html", user=user)


# Если страница не найдена
@app.errorhandler(404)
def pageNotFount(error):
  return render_template('page404.html')
  

if __name__=="__main__":
    app.run(debug=True)
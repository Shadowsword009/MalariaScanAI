import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from PIL import Image
import numpy as np
import bcrypt
import classify

# ==========================================
# FLASK CONFIG
# ==========================================
app = Flask(__name__)
app.secret_key = '1A2bc4s'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Model.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==========================================
# DATABASE MODELS
# ==========================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False, index=True)
    email = db.Column(db.String(128), unique=True, nullable=False, index=True)
    password = db.Column(db.LargeBinary, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    image = db.Column(db.String(256), nullable=False)
    result = db.Column(db.String(256), nullable=False)
    model_used = db.Column(db.String(128))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'image': self.image,
            'result': self.result,
            'model_used': self.model_used,
            'date_created': self.date_created
        }

with app.app_context():
    db.create_all()

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def getUser():
    if 'userId' not in session:
        return None, None
    user = User.query.get(session['userId'])
    if not user:
        return None, None

    history_data = History.query.filter_by(userId=user.id) \
        .order_by(History.date_created.desc()).all()

    history = [h.to_dict() for h in history_data]
    return user.to_dict(), history

# ==========================================
# ROUTES
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/model')
def model():
    if 'userId' not in session:
        return redirect('/login')
    return render_template('model.html')

# ==========================================
# FORGOT PASSWORD
# ==========================================
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'GET':
        return render_template('forgot.html')
    
    username = request.form.get('username')
    if not username:
        return render_template('forgot.html', error="Please enter username/email")

    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()

    if not user:
        return render_template('forgot.html', error="User not found")

    return redirect(f'/reset/{user.id}')

@app.route('/reset/<int:user_id>', methods=['GET', 'POST'])
def reset(user_id):
    user = User.query.get(user_id)
    if not user:
        return "Invalid user"

    if request.method == 'GET':
        return render_template('reset.html')

    new_password = request.form.get('password')
    confirm = request.form.get('confirm')

    if not new_password or not confirm:
        return render_template('reset.html', error="All fields required")

    if new_password != confirm:
        return render_template('reset.html', error="Passwords do not match")

    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed
    db.session.commit()

    return redirect('/login')

# ==========================================
# OTHER ROUTES
# ==========================================
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/profile')
def profile():
    details, history = getUser()
    if not details:
        return redirect('/login')
    return render_template('profile.html', details=details, history_items=history)

# ==========================================
# MODEL PREDICTION
# ==========================================
@app.route('/output', methods=['GET', 'POST'])
def output():
    if 'userId' not in session:
        return redirect('/login')
    
    image_path = ''
    model_name_str = ''
    result = None

    if request.method == 'POST':
        image_file = request.files.get("imagefile")
        if not image_file:
            return render_template("output.html", result="No image uploaded.", image='', model_used='')

        modelNo = int(request.form.get('model'))
        model_names = {0: "EfficientNet", 1: "DenseNet", 2: "MobileNet"}
        model_name_str = model_names.get(modelNo, "Unknown Model")

        os.makedirs('static/images/test/', exist_ok=True)
        image_path = os.path.join('static/images/test/', image_file.filename)
        image_file.save(image_path)

        image = Image.open(image_path)
        prediction = classify.predict(image, modelNo)

        if prediction.shape[1] == 1:
            prob = prediction[0][0]
            if prob > 0.5:
                label = "Parasitized"
                confidence = prob * 100
            else:
                label = "Uninfected"
                confidence = (1 - prob) * 100
        else:
            class_names = ['Parasitized', 'Uninfected']
            index = np.argmax(prediction)
            label = class_names[index]
            confidence = np.max(prediction) * 100

        result = f"{label} with a {confidence:.2f}% Confidence."

        new_history = History(
            userId=session['userId'],
            result=result,
            image=image_path,
            model_used=model_name_str
        )
        db.session.add(new_history)
        db.session.commit()

    return render_template("output.html", result=result, image=image_path, model_used=model_name_str)

# ==========================================
# AUTHENTICATION
# ==========================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form.get('name')
    email = request.form.get('email')
    newPass = request.form.get('newPass')
    confPass = request.form.get('confPass')

    if not username or not email or not newPass or not confPass:
        return render_template('login.html', regError="Please enter all required fields")

    if newPass != confPass:
        return render_template('login.html', regError="Passwords do not match")

    try:
        password_hash = bcrypt.hashpw(newPass.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=username, email=email, password=password_hash)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    except IntegrityError:
        db.session.rollback()
        return render_template('login.html', regError="Username or email already exists")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return render_template('login.html', loginError="Please provide username and password")

    user = User.query.filter_by(username=username).first()

    if not user:
        return render_template('login.html', loginError="No User Found")

    if bcrypt.checkpw(password.encode('utf-8'), user.password):
        session['userId'] = user.id
        return redirect('/output')
    else:
        return render_template('login.html', loginError="Password Incorrect")

# ==========================================
# RUN SERVER
# ==========================================
if __name__ == '__main__':
    app.run(debug=True, port=3000)
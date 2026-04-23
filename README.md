# 🦠 MalaraScanAI

MalaraScanAI is a web-based AI application that detects malaria from blood smear images using deep learning. It combines a trained model with an interactive Flask interface for easy testing and analysis.

---

## 🚀 Features

* AI-based malaria detection from images
* Simple web interface for uploading and testing
* Stores tested images locally
* User authentication system
* Sample test images included

---

## 🔐 Default Login Credentials

* **Username:** `admin`
* **Password:** `admin`

---

## 📂 Project Structure

```id="c8s9q2"
MalaraScanAI/
│── app.py
│── env/
│── instance/
│── static/
│   └── images/
│       └── test/
│── templates/
│── Test Samples/
│── requirements.txt
│── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Activate Virtual Environment

```bash id="zpld8a"
env\Scripts\activate
```

---

### 2️⃣ Install Dependencies

```bash id="8qf3ye"
pip install -r requirements.txt
```

---

### 3️⃣ Run the Application

```bash id="1rl4m0"
python app.py
```

Open in browser:

```id="9p2f4d"
http://127.0.0.1:5000/
```

---

## 🖼️ Image Storage

* All user-tested images are stored in:

  ```
  /static/images/test/
  ```

---

## 🧪 Test Samples

* Sample images are available in:

  ```
  /Test Samples/
  ```
* Use them to quickly verify model predictions

---

## 🗄️ Database Reset (Important)

If the database becomes corrupted or stops working:

1. Delete the `/instance` folder
2. Remove all images inside:

   ```
   /static/images/test/
   ```
3. Restart the application

⚠️ **Warning:**
This will permanently delete all stored user data and uploaded images.

---

## 📦 Requirements

Install all dependencies using:

```bash id="qk2d4c"
pip install -r requirements.txt
```

Main libraries used:

* TensorFlow
* Keras
* Flask
* SQLAlchemy
* NumPy
* scikit-image

---

## ⚠️ Notes

* Ensure Python 3.12 is installed
* Virtual environment is pre-created in `env/`
* Do not upload large model files to GitHub

---

## 🔮 Future Improvements

* Cloud deployment
* Better UI/UX
* Real-time detection
* Improved model accuracy

---

## 👨‍💻 Author

**Siva Charan**
B.Tech AI & ML

---

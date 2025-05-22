import pyrebase
import firebase_admin
from firebase_admin import credentials, auth

# Pyrebase configuration
firebaseConfig = {
    'apiKey': "AIzaSyCvmAvDemplqCPjbsruVx2-ODH-CMT6qSQ",
    'authDomain': "stdf-3e47b.firebaseapp.com",
    'databaseURL': "https://stdf-3e47b-default-rtdb.firebaseio.com",
    'projectId': "stdf-3e47b",
    'storageBucket': "stdf-3e47b.firebasestorage.app",
    'messagingSenderId': "71173546680",
    'appId': "1:71173546680:web:02422d9e4b3f71c7cf0a4d",
    'measurementId': "G-JBR9FEFM60"
}

# Initialize Pyrebase
firebase = pyrebase.initialize_app(firebaseConfig)
pyrebase_auth = firebase.auth()
pyrebase_db = firebase.database()

# Firebase Admin SDK configuration
cred = credentials.Certificate("D:\Final_project\project\credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://stdf-3e47b-default-rtdb.firebaseio.com"
})

# Export objects
auth = pyrebase_auth  # For signup compatibility
db = pyrebase_db
admin_auth = firebase_admin.auth  # For token verification
admin_db = db
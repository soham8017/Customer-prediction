This project is a Flask-based web application that provides user authentication (registration, login) and integrates a machine learning model (model.pkl) for inference. It is structured using Flask-SQLAlchemy for database management and Flask-Login for user session handling.

 **Features**
User registration and login

Secure password hashing with Werkzeug

Persistent user storage using SQLite (via SQLAlchemy)

Integration of a trained ML model (model.pkl)

Docker-friendly setup (localhost on port 5000)

 **Project Structure**
bash
Copy
Edit
.
├── main.py             # Entry point for the Flask app
├── models.py           # SQLAlchemy models (User)
├── model.pkl           # Trained ML model
├── app/                # (Expected) Application package (Flask app)
│   ├── __init__.py     # App factory
│   ├── routes.py       # Routes and views
│   └── templates/      # HTML templates
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
 Installation
Clone the repository:

bash
Copy
Edit
git clone https://github.com/soham8017/Cusomer-prediction.git
cd Customer-prediction
Set up a virtual environment:

bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Run the application:

bash
Copy
Edit
python main.py
App will be available at http://localhost:5000.

** Machine Learning Model**
The model.pkl file is a pre-trained machine learning model used for inference in the app. Ensure it is loaded properly within your route/view functions.

 **Security Notes**
Passwords are hashed before storing using Werkzeug.security.

Use HTTPS and environment variables in production.

Consider using Flask-Migrate and Flask-WTF for more robust setups.


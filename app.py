# app.py
import os
import logging
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, chi2

from models import User, db
from forms import LoginForm, RegisterForm, PredictionForm
from utils import prepare_data_for_prediction

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-for-development")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///churn_app.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load pre-trained model
try:
    with open("model.pkl", "rb") as model_file:
        model_data = pickle.load(model_file)
        rf_model = model_data["model"]
        scaler = model_data["scaler"]
        selected_cat_features = model_data["selected_cat_features"]
        label_encoders = model_data["label_encoders"]
        app.logger.debug("Model loaded successfully")
except Exception as e:
    app.logger.error(f"Error loading model: {e}")
    # Create dummy objects for development if model fails to load
    rf_model = RandomForestClassifier()
    scaler = StandardScaler()
    selected_cat_features = ["Geography", "Gender", "Card Type"]
    label_encoders = {col: LabelEncoder() for col in ["Geography", "Gender", "Card Type"]}

@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('Username already exists', 'danger')
        elif existing_email:
            flash('Email already exists', 'danger')
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """Prediction form route"""
    form = PredictionForm()
    if form.validate_on_submit():
        try:
            # Prepare data from form
            data = prepare_data_for_prediction(form, label_encoders)
            
            # Standardize numerical features
            numerical_cols = ["CreditScore", "Age", "Balance", "EstimatedSalary", "Tenure", "NumOfProducts"]
            data[numerical_cols] = scaler.transform(data[numerical_cols])
            
            # Select important categorical features
            X_cat = data[selected_cat_features]
            X_selected = pd.concat([X_cat.reset_index(drop=True), data[numerical_cols].reset_index(drop=True)], axis=1)
            
            # Make predictions
            prediction = rf_model.predict(X_selected)[0]
            probability = rf_model.predict_proba(X_selected)[0, 1] * 100
            
            # Save results in session
            session['prediction'] = int(prediction)
            session['probability'] = float(probability)
            session['customer_name'] = form.surname.data
            
            return redirect(url_for('result'))
            
        except Exception as e:
            app.logger.error(f"Prediction error: {e}")
            flash(f'Error during prediction: {str(e)}', 'danger')
    
    return render_template('predict.html', form=form)

@app.route('/predict_file', methods=['POST'])
@login_required
def predict_file():
    """Batch prediction from file route"""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('predict'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('predict'))
    
    try:
        data = pd.read_csv(file)
        
        # Preprocessing
        data.drop(columns=["RowNumber", "CustomerId", "Complain"], errors='ignore', inplace=True)
        
        # Add Point Earned column if missing
        if "Point Earned" not in data.columns:
            data["Point Earned"] = 500  # Default value
        
        # Encode categorical variables
        categorical_cols = ["Geography", "Gender", "Card Type"]
        for col in categorical_cols:
            if col in data.columns:
                le = label_encoders[col]
                data[col] = le.transform(data[col])
        
        # Standardize numerical features
        numerical_cols = ["CreditScore", "Age", "Balance", "EstimatedSalary", "Tenure", "NumOfProducts"]
        data[numerical_cols] = scaler.transform(data[numerical_cols])
        
        # Select important categorical features
        X_cat = data[selected_cat_features]
        X_selected = pd.concat([X_cat.reset_index(drop=True), data[numerical_cols].reset_index(drop=True)], axis=1)
        
        # Make predictions
        predictions = rf_model.predict(X_selected)
        probabilities = rf_model.predict_proba(X_selected)[:, 1]
        
        # Prepare results
        data['Prediction'] = predictions
        data['Churn Probability'] = probabilities * 100
        
        result_file = "static/results.csv"
        data.to_csv(result_file, index=False)
        
        return render_template('result.html', result_file=result_file, batch_prediction=True)
        
    except Exception as e:
        app.logger.error(f"File prediction error: {e}")
        flash(f'Error processing file: {str(e)}', 'danger')
        return redirect(url_for('predict'))

@app.route('/result')
@login_required
def result():
    """Display prediction results"""
    prediction = session.get('prediction')
    probability = session.get('probability')
    customer_name = session.get('customer_name', 'Customer')
    
    if prediction is None or probability is None:
        flash('No prediction data found', 'warning')
        return redirect(url_for('predict'))
    
    return render_template('result.html', 
                           prediction=prediction, 
                           probability=probability,
                           customer_name=customer_name,
                           batch_prediction=False)

# Create database tables within application context
with app.app_context():
    db.create_all()
    app.logger.info("Database tables created")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

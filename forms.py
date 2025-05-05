from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, FloatField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange

class LoginForm(FlaskForm):
    """Form for user login"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class PredictionForm(FlaskForm):
    """Form for customer churn prediction"""
    surname = StringField('Surname', validators=[DataRequired(), Length(max=100)])
    credit_score = IntegerField('Credit Score', validators=[DataRequired(), NumberRange(min=300, max=900)])
    geography = SelectField('Geography', choices=[('France', 'France'), ('Spain', 'Spain'), ('Germany', 'Germany')], validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=18, max=100)])
    tenure = IntegerField('Tenure (Years)', validators=[DataRequired(), NumberRange(min=0, max=20)])
    balance = FloatField('Balance', validators=[DataRequired(), NumberRange(min=0)])
    num_of_products = IntegerField('Number of Products', validators=[DataRequired(), NumberRange(min=1, max=4)])
    has_credit_card = SelectField('Has Credit Card', choices=[('1', 'Yes'), ('0', 'No')], validators=[DataRequired()])
    is_active_member = SelectField('Is Active Member', choices=[('1', 'Yes'), ('0', 'No')], validators=[DataRequired()])
    estimated_salary = FloatField('Estimated Salary', validators=[DataRequired(), NumberRange(min=0)])
    card_type = SelectField('Card Type', choices=[
        ('SILVER', 'Silver'), 
        ('GOLD', 'Gold'), 
        ('PLATINUM', 'Platinum'), 
        ('DIAMOND', 'Diamond')
    ], validators=[DataRequired()])
    satisfaction_score = IntegerField('Satisfaction Score (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    point_earned = IntegerField('Points Earned', validators=[DataRequired(), NumberRange(min=0, max=1000)], default=500)
    
    # File upload for batch predictions
    file = FileField('Upload CSV File for Batch Prediction')
    
    submit = SubmitField('Predict Churn')

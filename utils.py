import pandas as pd
import numpy as np

def prepare_data_for_prediction(form, label_encoders):
    """Prepare form data for prediction by the model"""
    # Create a dataframe with a single row
    data = pd.DataFrame({
        'CreditScore': [form.credit_score.data],
        'Geography': [form.geography.data],
        'Gender': [form.gender.data],
        'Age': [form.age.data],
        'Tenure': [form.tenure.data],
        'Balance': [form.balance.data],
        'NumOfProducts': [form.num_of_products.data],
        'HasCrCard': [int(form.has_credit_card.data)],
        'IsActiveMember': [int(form.is_active_member.data)],
        'EstimatedSalary': [form.estimated_salary.data],
        'Card Type': [form.card_type.data],
        'Satisfaction Score': [form.satisfaction_score.data],
        'Point Earned': [form.point_earned.data]
    })
    
    # Encode categorical features
    for col in ['Geography', 'Gender', 'Card Type']:
        le = label_encoders[col]
        data[col] = le.transform(data[col])
    
    return data

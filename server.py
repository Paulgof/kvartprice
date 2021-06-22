import pandas as pd
import joblib
from flask import Flask, jsonify, request, render_template
from tensorflow import keras

app = Flask(__name__)
model = keras.models.load_model('price_regressor.h5')
transformer = joblib.load('data_transformer.joblib')
categories = joblib.load('categories_lists.joblib')


@app.route('/')
@app.route('/index')
def index():
    for category_list in categories.values():
        category_list.sort()

    return render_template('index.html', categories=categories)


@app.route('/prediction', methods=['POST'])
def prediction():
    form = request.form
    df = pd.DataFrame({
        'Price': [1],
        'Rooms': [int(form.get('rooms'))],
        'Square': [float(form.get('square'))],
        'Floor': [int(form.get('flat_floor'))],
        'Total Floors': [int(form.get('total_floors'))],
        'District': [form.get('district')],
        'Microdistrict': [form.get('microdistrict')],
        'Flat Type': [form.get('flat_type')],
        'Toilet': [form.get('toilet')],
        'Balcony': [form.get('balcony')],
        'Repair': [form.get('repair')],
        'House Type': [form.get('house_type')],
        'Lifts': [form.get('lifts')]
    })
    df = transformer.transform(df)
    pred = model.predict(df.A[:, 1:])
    pred_price = int(pred.flatten()[0]) // 100000 * 100000
    return render_template('result.html', price=pred_price)

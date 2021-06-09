import pandas as pd
import joblib
from flask import Flask, jsonify, request
from tensorflow import keras
app = Flask(__name__)
model = keras.models.load_model('price_regressor.h5')
transformer = joblib.load('data_transformer.joblib')

@app.route('/')
@app.route('/index')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
    <meta charset="UTF-8">
    <title>Index</title>
    </head>
    <body>
    
    
    
    <form action="prediction" method="post">
        <p>
        <label for="rooms">Количество комнат</label>
        <input type="number" name="rooms" value="1">
    </p>
    <p>
        <label for="square">Площадь</label>
        <input type="number" name="square" step="0.01" value="20.5">
    </p>
    <p>
        <label for="flat_floor">Этаж квартиры</label>
        <input type="number" name="flat_floor" value="1">
    </p>
    <p>
        <label for="total_floors">Всего этажей</label>
        <input type="number" name="total_floors" value="5">
    </p>
        <label for="district">Район</label>
        <select name="district" size="1">
            <option value="Прикубанский">Прикубанский</option>
            <option value="Карасунский">Карасунский</option>
            <option value="Центральный">Центральный</option>
            <option value="Западный">Западный</option>
            <option value="Афипский пгт">Афипский пгт</option>
            <option value="Белозерный поселок">Белозерный поселок</option>
            <option value="Ленина хутор">Ленина хутор</option>
            <option value="Российский поселок">Российский поселок</option>
            <option value="Знаменский поселок">Знаменский поселок</option>
            <option value="Краснодарский поселок">Краснодарский поселок</option>
            <option value="Южный поселок">Южный поселок</option>
            <option value="Березовый поселок">Березовый поселок</option>
        </select>
    <p>
    <p>
        <label for="microdistrict">Микрорайон</label>
        <select name="microdistrict" size="1">
            <option value="Не известно">Не известно</option>
            <option value="мкр. ЗИП">мкр. ЗИП</option>
            <option value="мкр. ХБК">мкр. ХБК</option>
            <option value="мкр. РИП">мкр. РИП</option>
            <option value="мкр. Фестивальный">мкр. Фестивальный</option>
            <option value="мкр. Гидростроителей">мкр. Гидростроителей</option>
            <option value="Алый жилмассив">Алый жилмассив</option>
            <option value="мкр. Дубинка">мкр. Дубинка</option>
            <option value="мкр. Центральный">мкр. Центральный</option>
            <option value="мкр. Славянский">мкр. Славянский</option>
            <option value="мкр. Аврора">мкр. Аврора</option>
            <option value="мкр. Кожзавод">мкр. Кожзавод</option>
            <option value="мкр. Восточно-Кругликовский">мкр. Восточно-Кругликовский</option>
            <option value="мкр. Московский">мкр. Московский</option>
            <option value="мкр. Комсомольский">мкр. Комсомольский</option>
            <option value="мкр. 40 лет Победы">мкр. 40 лет Победы</option>
            <option value="мкр. Школьный">мкр. Школьный</option>
            <option value="мкр. СХИ">мкр. СХИ</option>
            <option value="мкр. Юбилейный">мкр. Юбилейный</option>
            <option value="мкр. Черемушки">мкр. Черемушки</option>
            <option value="мкр. Пашковский">мкр. Пашковский</option>
            <option value="мкр. КСК">мкр. КСК</option>
            <option value="мкр. Табачная фабрика">мкр. Табачная фабрика</option>
            <option value="Пашковский жилмассив">Пашковский жилмассив</option>
            <option value="мкр. Калинино">мкр. Калинино</option>
            <option value="проезд 1-й Лиговский">проезд 1-й Лиговский</option>
            <option value="мкр. ККБ">мкр. ККБ</option>
            <option value="мкр. Горхутор">мкр. Горхутор</option>
            <option value="Казанский микрорайон">Казанский микрорайон</option>
            <option value="мкр. Покровка">мкр. Покровка</option>
            <option value="мкр. Новознаменский">мкр. Новознаменский</option>
            <option value="проезд 1-й Сахалинский">проезд 1-й Сахалинский</option>
            <option value="мкр. Краснодарский">мкр. Краснодарский</option>
            <option value="Урожай садовое товарищество">Урожай садовое товарищество</option>
            <option value="мкр. Новые дома">мкр. Новые дома</option>
            <option value="мкр. 9-й километр">мкр. 9-й километр</option>
            <option value="Центральный микрорайон">Центральный микрорайон</option>
            <option value="Транспортник садовое товарищество">Транспортник садовое товарищество</option>
            <option value="Новознаменский жилой район">Новознаменский жилой район</option>
            <option value="мкр. Немецкая Деревня">мкр. Немецкая Деревня</option>
            <option value="мкр. Ипподром">мкр. Ипподром</option>
            <option value="Новый микрорайон">Новый микрорайон</option>
            <option value="Британия 2 жилой комплекс">Британия 2 жилой комплекс</option>
            <option value="мкр. Северный">мкр. Северный</option>
            <option value="мкр. РМЗ">мкр. РМЗ</option>
            <option value="Табачная Фабрика микрорайон">Табачная Фабрика микрорайон</option>
            <option value="Зеленодар жилой комплекс">Зеленодар жилой комплекс</option>
            <option value="проезд 1-й Краснодарский">проезд 1-й Краснодарский</option>
            <option value="Черемушки микрорайон">Черемушки микрорайон</option>
            <option value="Губернский микрорайон">Губернский микрорайон</option>
            <option value="мкр. Авиагородок">мкр. Авиагородок</option>
            <option value="Завод Измерительных Приборов микрорайон">Завод Измерительных Приборов микрорайон</option>
            <option value="Имени Н.И. Вавилова микрорайон">Имени Н.И. Вавилова микрорайон</option>
            <option value="Школьный микрорайон">Школьный микрорайон</option>
            <option value="мкр. имени Жукова">мкр. имени Жукова</option>
            <option value="2-я Площадка микрорайон">2-я Площадка микрорайон</option>
            <option value="Юбилейный микрорайон">Юбилейный микрорайон</option>
            <option value="14">14</option>
            <option value="Сады Калинина микрорайон">Сады Калинина микрорайон</option>
            <option value="Родные Просторы микрорайон">Родные Просторы микрорайон</option>
            <option value="66к2">66к2</option>
            <option value="мкр. Знаменский">мкр. Знаменский</option>
            <option value="Бавария коттеджный поселок">Бавария коттеджный поселок</option>
            <option value="Рублевский СНТ">Рублевский СНТ</option>
            <option value="Знаменский ДНТ">Знаменский ДНТ</option>
            <option value="Прогресс поселок">Прогресс поселок</option>
            <option value="Радужный коттеджный поселок">Радужный коттеджный поселок</option>
            <option value="66к1">66к1</option>
        </select>
    </p>
    <p>
        <label for="toilet">Туалет</label>
        <select name="toilet" size="1">
            <option value="1 совмещенный">1 совмещенный</option>
            <option value="1 раздельный">1 раздельный</option>
            <option value="1 совмещенный, 1 раздельный">1 совмещенный, 1 раздельный</option>
            <option value="2 совмещенных">2 совмещенных</option>
            <option value="3 совмещенных">3 совмещенных</option>
            <option value="2 раздельных">2 раздельных</option>
            <option value="1 совмещенный, 2 раздельных">1 совмещенный, 2 раздельных</option>
            <option value="3 раздельных">3 раздельных</option>
            <option value="2 совмещенных, 1 раздельный">2 совмещенных, 1 раздельный</option>
            <option value="2 совмещенных, 3 раздельных">2 совмещенных, 3 раздельных</option>
            <option value="2 совмещенных, 2 раздельных">2 совмещенных, 2 раздельных</option>
            <option value="3 совмещенных, 1 раздельный">3 совмещенных, 1 раздельный</option>
            <option value="4 раздельных">4 раздельных</option>
            <option value="3 совмещенных, 3 раздельных">3 совмещенных, 3 раздельных</option>
            <option value="2 совмещенных, 4 раздельных">2 совмещенных, 4 раздельных</option>
        </select>
    </p>
    <p>
        <label for="balcony">Балкон</label>
        <select name="balcony" size="1">
            <option value="1 балкон">1 балкон</option>
            <option value="1 лоджия">1 лоджия</option>
            <option value="Нет">Нет</option>
            <option value="1 балкон, 1 лоджия">1 балкон, 1 лоджия</option>
            <option value="2 лоджии">2 лоджии</option>
            <option value="2 балкона">2 балкона</option>
            <option value="2 балкона, 2 лоджии">2 балкона, 2 лоджии</option>
            <option value="3 лоджии">3 лоджии</option>
            <option value="1 балкон, 2 лоджии">1 балкон, 2 лоджии</option>
            <option value="2 балкона, 1 лоджия">2 балкона, 1 лоджия</option>
            <option value="3 балкона, 3 лоджии">3 балкона, 3 лоджии</option>
            <option value="3 балкона">3 балкона</option>
            <option value="4 балкона">4 балкона</option>
            <option value="4 лоджии">4 лоджии</option>
            <option value="4 балкона, 4 лоджии">4 балкона, 4 лоджии</option>
            <option value="1 балкон, 3 лоджии">1 балкон, 3 лоджии</option>
            <option value="4 балкона, 2 лоджии">4 балкона, 2 лоджии</option>
        </select>
    </p>
    <p>
        <label for="lifts">Лифт</label>
        <select name="lifts" size="1">
            <option value="Нет">Нет</option>
            <option value="Есть">Есть</option>
            <option value="1 пасс., 1 груз.">1 пасс., 1 груз.</option>
            <option value="3 пасс.">3 пасс.</option>
            <option value="2 пасс.">2 пасс.</option>
            <option value="9 всего">9 всего</option>
            <option value="6 всего">6 всего</option>
            <option value="3 всего">3 всего</option>
            <option value="2 пасс., 1 груз.">2 пасс., 1 груз.</option>
            <option value="4 всего">4 всего</option>
            <option value="Есть грузовой">Есть грузовой</option>
            <option value="3 пасс., 1 груз.">3 пасс., 1 груз.</option>
            <option value="8 всего">8 всего</option>
            <option value="2 всего">2 всего</option>
            <option value="12 всего">12 всего</option>
            <option value="4 пасс.">4 пасс.</option>
            <option value="2 пасс., 2 груз.">2 пасс., 2 груз.</option>
            <option value="5 всего">5 всего</option>
            <option value="7 всего">7 всего</option>
            <option value="16 всего">16 всего</option>
            <option value="10 всего">10 всего</option>
            <option value="2 груз.">2 груз.</option>
            <option value="1 пасс., 2 груз.">1 пасс., 2 груз.</option>
            <option value="14 всего">14 всего</option>
            <option value="29 всего">29 всего</option>
            <option value="20 всего">20 всего</option>
            <option value="17 всего">17 всего</option>
            <option value="3 пасс., 2 груз.">3 пасс., 2 груз.</option>
            <option value="4 пасс., 1 груз.">4 пасс., 1 груз.</option>
            <option value="13 всего">13 всего</option>
            <option value="4 пасс., 2 груз.">4 пасс., 2 груз.</option>
        </select>
    </p>
    <p>
        <label for="repair">Ремонт</label>
        <select name="repair" size="1">
            <option value="Не известно">Не известно</option>
            <option value="Без ремонта">Без ремонта</option>
            <option value="Евроремонт">Евроремонт</option>
            <option value="Дизайнерский">Дизайнерский</option>
            <option value="Косметический">Косметический</option>
        </select>
    </p>
    <p>
        <label for="flat_type">Тип квартиры</label>
        <select name="flat_type" size="1">
            <option value="Вторичка">Вторичка</option>
            <option value="Вторичка Пентхаус">Вторичка Пентхаус</option>
            <option value="Новостройка">Новостройка</option>
            <option value="Вторичка Апартаменты">Вторичка Апартаменты</option>
        </select>
    </p>
    <p>
        <label for="house_type">Тип дома</label>
        <select name="house_type" size="1">
            <option value="Монолитный">Монолитный</option>
            <option value="Кирпичный">Кирпичный</option>
            <option value="Монолитно кирпичный">Монолитно кирпичный</option>
            <option value="Не известно">Не известно</option>
            <option value="Панельный">Панельный</option>
            <option value="Блочный">Блочный</option>
            <option value="Старый фонд">Старый фонд</option>
            <option value="Сталинский">Сталинский</option>
        </select>
    </p>    
        <input type="submit">
    </p>
    </form>
    
    </body>
    </html>
    '''


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
    print(df.keys())
    print(transformer)
    df = transformer.transform(df)
    pred = model.predict(df.A[:, 1:])
    pred_price = pred.flatten()[0]
    return 'Стоимость квартиры = {}'.format(pred_price)

import flask
from flask import Flask, request, redirect, url_for

from flask_sqlalchemy import SQLAlchemy

DB_USERNAME = 'postgres'
DB_PASSWORD = 'postgres'
DB_NETWORK = 'localhost'
DB_DATABASE = 'comment'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_NETWORK}/{DB_DATABASE}'
db = SQLAlchemy(app)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(512), nullable=False)
    rate = db.Column(db.Integer, nullable=False)

    def __init__(self, text, rate):
        self.text = text
        self.rate = rate


# Путь к домашней странице (на основе файла templates/index.html)
@app.route('/', methods=['GET'])
def index():
    # получить "error» из "args», если она присутствует, она будет напечатана красным цветом, иначе ничего не будет отображаться
    error = request.args.get('error', '')
    # передать «comments»  (список всех комментариев) и «error»  (взято из аргументов выше в templates/index.html)
    return flask.render_template('index.html', comments=Comment.query.all(), error=error)


# Возвращает список «comments» (в формате Json)
@app.route('/comment', methods=['GET'])
def get_all_comments():
    # Возвращает все (all) строки в таблице comments
    # Не нужно «commit», потому что я только что прочитал это, не меняйте его.
    return Comment.query.all()


# Добавить новый «comment»  (в формате Json)
@app.route('/comment', methods=['POST'])
def create_new_comment():
    # Если нет «text» или «rate» -> вернуть ошибку «Пожалуйста, введите комментарий и количество звезд»
    if request.form['text'] == '' or request.form['rate'] == '':
        return redirect(url_for('index', error='Пожалуйста, введите комментарий и количество звезд'))

    # получить «text» из вновь созданного «comment»
    text = request.form['text']
    # получить «rate» из вновь созданного «комментария»
    rate = int(request.form['rate'])

    # Если «rate» (количество звезд) меньше 1 или больше 5 -> вернуть ошибку "Звезды должны быть от 1 до 5"
    if rate < 1 or rate > 5:
        return redirect(url_for('index', error='Количество звезд должно быть от 1 до 5'))

    # Добавить в базу данных 1 новый комментарий (с опубликованным текстом и оценкой)
    db.session.add(Comment(text, rate))
    # Получил фиксацию, потому что изменил таблицу (добавил 1 новый комментарий)
    db.session.commit()

    # Вернуться на главную страницу
    return redirect(url_for('index'))


# Удалить все комментарии
@app.route('/comment', methods=['DELETE'])
def delete_all_comments():
    # Очистить доску
    Comment.query.delete()
    # Должен иметь коммит для выполнения
    db.session.commit()
    return "Success"


with app.app_context():
    # создать таблицу, если она еще не создана
    db.create_all()
app.run()

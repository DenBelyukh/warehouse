
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, session
import sqlite3
from FDataBase import FDataBase  # FDataBase клас для роботи з БД, прописуємо в окремому файлі
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin


#   конфігурація
DATABASE = 'warehouse.db'
DEBUG = True
SECRET_KEY = 'qwerty'

# створення застосунку "flapp"
flapp = Flask(__name__)
flapp.config.from_object(__name__)

login_manager = LoginManager(flapp)
login_manager.login_view = 'foo_login'
login_manager.login_message = "Будь ласка, авторизуйтесь для перегляду сторінки"
login_manager.login_message_category = 'success'


# після авторизації користувача,
# цей декоратор відпрацьовує при кожному запиті,
# і повертає інформацію про користувача з БД (з доп. методу FDataBase.getUser)
# по його user_id, яке береться з session
@login_manager.user_loader
def load_user(user_id):
    print("load_user works>>>", user_id)

    # userload (екз. класу UserLogin), отриманий методом UserLogin.fromDB
    userload = UserLogin().fromDB(user_id, dbase)
    return userload

# Допоміжні функції


# Викликається з функції get_db(), якщо немає зв'язку з БД
def connect_db():
    """ Для встановлення зв'язку з БД """
    conn = sqlite3.connect(flapp.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


# def create_db():
#     """ Для створення початкової БД з необхідними таблицями
#      використовується тільки для початкового створення БД, в роботі
#      участі не приймає"""
#     db = connect_db()
#     with flapp.open_resource('sq_db.sql', mode='r') as f:
#         db.cursor().executescript(f.read())


def get_db_link():
    """ Повертає активний зв'язок з БД """
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@flapp.before_request
def before_request():
    """ Встановлення зв'язку з БД перед виконанням запита"""
    global dbase
    db_link = get_db_link()           # отримання зв'язку з базою даних (g.link_db)
    dbase = FDataBase(db_link)   # екземпляр класу FDataBase з переданим йому зв'язком з базою даних


# Функції - обробники (foo_)

@flapp.route("/base")
def foo_base():
    """ Пуста сторінка "/base" """

    return render_template('base.html', menu=dbase.getMenu())


@flapp.route("/")
def foo_index():
    """ Для головної сторінки "/" """
    menu = dbase.getMenu()

    return render_template('index.html',
                           menu=menu)


@flapp.route("/main")
@login_required
def foo_main():
    """ Для першої сторінки користувача"""
    menu = dbase.getMenu()
    boxes = dbase.getBoxes()    # "комірки" з товарами
    if not boxes:
        abort(404)

    return render_template('main.html',
                           menu=menu,
                           boxes=boxes)


@flapp.route("/total")
@login_required
def foo_pageTotal():
    """ Для показу всіх запасів в комірці "/total" """
    menu = dbase.getMenu()
    conf_total = dbase.getTotal()
    if not conf_total:
        abort(404)

    return render_template('total.html',
                           title='Загальні запаси',
                           menu=menu,
                           conf_total=conf_total)


#    для показу по сортах
@flapp.route("/getSort", methods=["POST", "GET"])
@login_required
def foo_getSort():
    """ Для показу по сорту """
    menu = dbase.getMenu()
    conf_sort = dbase.getSort(request.form['sort'])
    for i in conf_sort:
        print(i)
    return render_template('sort.html',
                           title='По сорту '+request.form['sort'],
                           menu=menu,
                           conf_sort=conf_sort)


@flapp.route("/item_edit", methods=["POST", "GET"])
@login_required
def foo_itemEdit():
    """ Для редагування запису "/item_edit" """
    menu = dbase.getMenu()
    item = dbase.getItem(request.form['wh_Id'])

    return render_template('item_edit.html',
                           title='Редагувати запис',
                           menu=menu,
                           item=item)


@flapp.route("/addNewData", methods=["POST", "GET"])
@login_required
def foo_addNewData():
    """ Для зміни запису в БД """
    menu = dbase.getMenu()

    new_data = dbase.addNewData(request.form['wh_Id'], request.form['conf_name'], request.form['volume'], request.form['amount'])
    if not new_data:
        abort(404)

    item = dbase.getItem(request.form['wh_Id'])

    return render_template('item_edit.html',
                           title='Редагувати запис',
                           menu=menu,
                           item=item)


# Функції-обробники для взаємодії з користувачем

@flapp.route("/register", methods=["POST", "GET"])
def foo_register():
    """ Для сторінки реєстрації """
    menu = dbase.getMenu()

    if request.method == "POST":
        if len(request.form['name']) > 2 and len(request.form['email']) > 3 \
                and len(request.form['psw']) > 3 and request.form['psw'] == request.form['psw2']:
            psw_hash = generate_password_hash(request.form['psw'])
            new_user = dbase.addUser(request.form['name'], request.form['email'], psw_hash)
            # new_storage тут треба створити БД для користувача і прив'язатись до неї
            if new_user:
                flash('Ви успішно зареєстровані в кооперативі', 'success')
                return redirect(url_for('foo_login'))
            else:
                flash('Помилка при додаванні в БД', 'error')
        else:
            flash('Неправильно заповнені поля форми реєстрації', 'error')

    return render_template('register.html',
                           title='Реєстрація',
                           menu=menu)


@flapp.route("/login", methods=["POST", "GET"])
def foo_login():
    """ Для сторінки авторизації """
    menu = dbase.getMenu()
    # перевіряємо чи користувач авторизований
    if current_user.is_authenticated:
        return redirect(url_for('foo_profile'))

    if request.method == "POST":
        # user - дані користувача з БД (мінімально потрібні 'id' та 'psw')
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            # Створюємо userlogin (екз. класу UserLogin)
            # і передаємо його функції login_user,
            # а вона записує його в session
            userlogin = UserLogin().create(user)
            remainme_button = True if request.form.get('remainme') else False
            login_user(userlogin, remember=remainme_button)

            return redirect(request.args.get("next") or url_for('foo_main'))

        flash("Неправильний email або пароль", "error")

    return render_template('login.html',
                           title='Авторизація',
                           menu=menu)


@flapp.route('/logout')
@login_required
def foo_logout():
    """ Для виходу з акаунту """
    logout_user()
    flash("Ви вийшли з акаунту", "success")
    return redirect(url_for('foo_login'))


@flapp.route('/profile')
@login_required
def foo_profile():
    """ Акаунт користувача """
    menu = dbase.getMenu()

    return render_template('profile.html',
                           title=f"Кабінет {current_user.get_name()}",
                           menu=menu)


# Запуск програми (app)
if __name__ == '__main__':
    flapp.run(debug=True)

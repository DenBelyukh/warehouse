class UserLogin:

    # метод, що використовується на етапі "login"
    # щоб створити екз. UserLogin і передати його
    # функції login_user для занесення в session
    # user - дані користувача, які витягнули з БД
    # з допомогою методу .getUserByEmail
    # по email з форми авторизації
    def create(self, user):
        self.__user = user
        return self

    # метод, що використовується на етапі "load"
    # дані користувача беруться з БД по його id
    def fromDB(self, user_id, dbase):
        self.__user = dbase.getUser(user_id)

        # print('fromDB >>>', dict(self.__user))
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user['id'])

    def get_name(self):
        return str(self.__user['name'])





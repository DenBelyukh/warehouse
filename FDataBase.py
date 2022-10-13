import sqlite3
import time
import math


# клас для роботи з БД
class FDataBase:
    def __init__(self, db_link):  # передаємо зв'язок з БД
        self.__db = db_link
        self.__cur = db_link.cursor()  # екземпляр класу курсор. через нього працюємо з таблицями в БД

    # ############################### головне меню
    def getMenu(self):
        sql = "SELECT * FROM mainmenu"
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print("Помилка")
        return []

    # ############################### новий склад користувача
    def makeNewStorage(self):
        pass

    # ############################### отримання boxes ('комірок')
    def getBoxes(self):
        sql = "SELECT * FROM boxes"
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print("Помилка")
        return []

    # ############################### отримання всіх запасів з БД (сорт-банка-кількість)
    def getTotal(self):
        sql = "SELECT wh_Id, conf_name, volume, amount FROM warehouse GROUP BY conf_name,volume"
        try:
            self.__cur.execute(sql)     # запит в БД
            total = self.__cur.fetchall()  # повернення результату вибірки
            if total:
                return total  # якщо є - повертаємо
        except sqlite3.Error as e:
            print("Помилка" + str(e))

        return []

        #  ############################### отримання запису з БД по Id
    def getItem(self, wh_Id):
        sql = "SELECT wh_Id, conf_name, volume, amount  FROM warehouse WHERE wh_Id LIKE :1"
        try:
            self.__cur.execute(sql, wh_Id)     # запит в БД
            item = self.__cur.fetchall()     # повернення результату вибірки
            if item:
                return item  # якщо є запис - повертаємо його
        except sqlite3.Error as e:
            print("Помилка" + str(e))

        return []

        # ############################### змінюємо запис в БД
    def addNewData(self, wh_Id, conf_name, volume, amount):
        sql = "UPDATE warehouse SET amount = :1, conf_name= :2, volume= :3  WHERE wh_Id= :4"
        try:
            self.__cur.execute(sql, (amount, conf_name, volume, wh_Id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Помилка" + str(e))
            return False

        return True

    # ############################### отримання зведених запасів з БД
    def getWarehouse(self):
        sql = "SELECT conf_name, SUM(volume*amount) FROM warehouse GROUP BY conf_name"
        try:
            self.__cur.execute(sql)  # запит в БД
            res = self.__cur.fetchall()  # повернення результату вибірки
            if res:
                return res  # якщо є - повертаємо
        except sqlite3.Error as e:
            print("Помилка" + str(e))

        return []

    # отримання запасів з БД (по сорту)
    def getSort(self, sort):
        sql = "SELECT conf_name, volume, amount FROM warehouse WHERE conf_name LIKE :1"
        # print(sort)
        try:
            self.__cur.execute(sql, (sort,))   # запит в БД кількість по сорту
            per_sort = self.__cur.fetchall()  # повернення результату вибірки
            if per_sort:
                return per_sort  # якщо є допис - повертаємо його
        except sqlite3.Error as e:
            print("Помилка" + str(e))

        return []

    # ############################### змінюємо кількість банок в БД (по сорту)
    # def addNewCount(self, conf_name, volume, new_count):
    #     try:
    #         self.__cur.execute(
    #             f"UPDATE warehouse SET amount = {new_count} WHERE conf_name='{conf_name}' AND volume={volume} ")
    #         self.__db.commit()
    #     except sqlite3.Error as e:
    #         print("Помилка" + str(e))
    #         return False
    #
    #     return True

    # ############################### додаємо користувача
    def addUser(self, name, email, psw_hash):
        try:
            self.__cur.execute("SELECT * FROM users WHERE email == :1", (email,))
            res = self.__cur.fetchone()
            if res is not None:
                # print("Користувач з таким email вже існує")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, :1, :2, :3, :4)", (name, email, psw_hash, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Помилка:" + str(e))
            return False

        return True

    # для етапу "load", при кожному запиті
    # забираємо інфу про користувача з БД
    # це для методу UserLogin().fromDB(),
    # використовується в декораторі @login_manager.user_loader
    # в функції load_user()
    def getUser(self, user_id):
        try:
            self.__cur.execute("SELECT * FROM users WHERE id = :1 LIMIT 1", (user_id,))
            res = self.__cur.fetchone()
            if not res:
                print("Користувач не знайдений")
                return False
            return res

        except sqlite3.Error as e:
            print("Помилка " + str(e))

        return False

    # для етапу "login", під час авторизації для запису в session
    # повертаємо користувача (мін. 'id', пароль) по його email
    def getUserByEmail(self, email):
        try:
            self.__cur.execute("SELECT id, psw, name FROM users WHERE email = :1 LIMIT 1", (email,))
            res = self.__cur.fetchone()
            if not res:
                print("Користувач не знайдений")
                return False

            return res
        except sqlite3.Error as e:
            print("Помилка " + str(e))

        return False


    # def addUser(self, name, email, psw_hash):
    #     try:
    #         self.__cur.execute("SELECT COUNT() as `count` FROM users WHERE email LIKE :1", (email,))
    #         res = self.__cur.fetchone()
    #         if res['count'] > 0:
    #             print("Користувач з таким email вже існує")
    #             return False
    #
    #         tm = math.floor(time.time())
    #         self.__cur.execute("INSERT INTO users VALUES(NULL, :1, :2, :3, :4)", (name, email, psw_hash, tm))
    #         self.__db.commit()
    #     except sqlite3.Error as e:
    #         print("Помилка:" + str(e))
    #         return False
    #
    #     return True
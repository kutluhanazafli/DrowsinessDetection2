from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.toast import toast
from datetime import datetime
import configparser
import mysql.connector

from GUI import MainApp


class Login(Screen):
    pass

    def connect(self):
        # get email and password from Screen
        app = App.get_running_app()
        input_email = app.manager.get_screen('login').ids['input_email'].text
        input_password = app.manager.get_screen('login').ids['input_password'].text
        # load credentials from config.ini
        config = configparser.ConfigParser()
        config.read('config.ini')
        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        dbname = config['mysql']['db']
        # connect to MySQL
        db = mysql.connector.connect(host=str(host), user=str(user), password=str(password), database=str(dbname))
        cursor = db.cursor()
        # run query to check email/password
        query = "SELECT count(*) FROM users where email='" + str(input_email) + "' and password='" + str(
            input_password) + "'"
        cursor.execute(query)
        data = cursor.fetchone()
        count = data[0]
        # verif login/email
        # if invalid
        if count == 0:
            toast('Invalid Login/Password')
        # else, if valid
        else:
            toast('Login and Password are correct!')
            # update last_login column
            now = datetime.now()
            query = "update users set last_login='" + str(now.strftime("%Y-%m-%d %H:%M:%S")) + "' where email='" + str(
                input_email) + "' and password='" + str(input_password) + "'"
            cursor.execute(query)
            db.commit()
            self.clear_widgets()
            app.stop()
            MainApp().run()
        db.close()
        pass

    def register(self):
        # get email and password from Screen
        app = App.get_running_app()
        input_email = app.manager.get_screen('login').ids['input_email'].text
        input_password = app.manager.get_screen('login').ids['input_password'].text
        # load credentials from config.ini
        config = configparser.ConfigParser()
        config.read('config.ini')
        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        dbname = config['mysql']['db']
        # connect to MySQL
        db = mysql.connector.connect(host=str(host), user=str(user), password=str(password), database=str(dbname))
        cursor = db.cursor()
        # run query to check email/password
        now = datetime.now()
        query = f"INSERT INTO users (email, password) VALUES ({input_email}, {input_password})"
        cursor.execute(query)
        db.commit()
        toast('Succesfully Registered!')

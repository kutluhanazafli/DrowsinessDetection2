import os, sys
import configparser
from datetime import datetime
import kivy


kivy.require('1.0.8')
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.app import MDApp
from login import Login


# Login Screen
class LoginApp(MDApp):
    def build(self):
        self.manager = ScreenManager(transition=NoTransition())
        self.manager.add_widget(Login(name='login'))
        return self.manager


# python main function
if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    LoginApp().run()

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from datetime import datetime
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from threading import Thread
import socket
import json
import socket
import os
import sys
from kivy.core.window import Window



class ScreenManagement(ScreenManager):
    main_screen = ObjectProperty(None)
    error_screen = ObjectProperty(None)
    dev_screen = ObjectProperty(None)
    raw_data_screen = ObjectProperty(None)
    settings_screen = ObjectProperty(None)


class NavigationBar(AnchorLayout):
    time = StringProperty(0)
    current_screen = StringProperty(False)

    # update StringProperty time -- 1 second intervals
    def update_time(self, *args):
        self.time = datetime.now().strftime('%H:%M:%S')

    def update_screen(self, current_screen):
        print(current_screen)
        image = StringProperty('./static/close.png')
        # set previous screen - (Settings - Main, Error, Dev, Raw-Data)
        if current_screen != 'settings_screen_name':
            self.previous_screen = current_screen
            self.ids.generate_btn.selected = True
            self.ids.screen_management.current = 'settings_screen_name'
        else:
            self.ids.screen_management.current = self.previous_screen
            self.ids.generate_btn.selected = False

class MainScreen(Screen):
    def __init__(self, **kwargs):   
        super(MainScreen, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.speed = '0'
        self.host = '127.0.0.1'
        self.port = 25000
        self.sock = socket.socket()
        self.data = {}
        Thread(target=self.connect).start()
    def connect(self):
        self.sock.connect((self.host, self.port))
        while True:
            data = self.sock.recv(4096)
            if not data:
                break
            self.data = json.loads(data.decode())

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == '1':
            self.manager.current = 'settings_screen_name'
        elif keycode[1] == '2':
            self.manager.current = 'main_screen_name'
        elif keycode[1] == '3':
            self.manager.current = 'dev_screen_name'
        elif keycode[1] == '4':
            self.manager.current = 'raw_data_screen_name'
        elif keycode[1] == '5':
            self.manager.current = 'error_screen_name'
        return True

    def update(self, data):
        self.manager.raw_data_screen.populate(data)
        self.manager.dev_screen.update(data)




class ErrorScreen(Screen, RecycleView):
    pass




class DevScreen(Screen):
    list = ListProperty([])
    def update(self, data):
        list[0] = 1
        print(list)




class RawDataScreen(Screen):
    data = ListProperty()
    def __init__(self, **kwargs):
        super(RawDataScreen, self).__init__(**kwargs)
    def populate(self, data):
        self.ids.rv.data = [{'value': str(x) + " : " + str(y)} for x, y in sorted(data.items())]


class SettingsScreen(Screen):

    pass


class DashUIApp(App):
    def build(self):
        nav = NavigationBar()
        Clock.schedule_interval(nav.update_time, 1)
        return nav

if __name__ == "__main__":
    DashUIApp().run()
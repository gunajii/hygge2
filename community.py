from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Ellipse, RoundedRectangle
from kivy.uix.behaviors import ButtonBehavior
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

KV = """
BoxLayout:
    orientation: "vertical"
    canvas.before:
        Color:
            rgba: 0.94, 0.91, 0.85, 1
        Rectangle:
            pos: self.pos
            size: self.size

    MDBoxLayout:
        size_hint_y: 0.1
        padding: 10
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Line:
                points: self.x, self.y, self.right, self.y
                width: 2
        MDLabel:
            text: "Community"
            font_style: "H5"
            halign: "center"
        MDIconButton:
            icon: "account-plus"
            on_release: app.show_add_friend_dialog()

    IconGrid:
        size_hint_y: 0.3

    MDBoxLayout:
        size_hint_y: 0.2
        padding: 10
        spacing: 10

    MDBoxLayout:
        size_hint_y: 0.1
        padding: 10
        spacing: 10

        MDBoxLayout:
            size_hint_x: 0.85
            radius: [25, 25, 25, 25]
            MDTextField:
                id: message_input
                hint_text: "How are you feeling?"
                mode: "rectangle"
                size_hint_x: 0.9
                background_color: 0, 0, 0, 0
                font_size: 18
                hint_text_color: 0.6, 0.6, 0.6, 1

        MDIconButton:
            size_hint_x: 0.15
            md_bg_color: 0.8, 1, 0.8, 1
            icon: "arrow-up-bold-circle"
            font_size: 24
            on_release: app.send_message()
            radius: [25, 25, 25, 25]

    MDBoxLayout:
        size_hint_y: 0.1
        padding: 10
        spacing: 20
        MDIconButton:
            icon: "home"
            on_release: app.change_screen("home")
        MDIconButton:
            icon: "chat"
            on_release: app.change_screen("chat")
        MDIconButton:
            icon: "chart-bar"
            on_release: app.change_screen("stats")
        MDIconButton:
            icon: "account"
            on_release: app.change_screen("profile")
"""

class CustomIcon(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.update_graphics()

    def update_graphics(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0, 0, 0, 1)
            size = (50, 50)
            RoundedRectangle(pos=self.pos, size=size, radius=[15])
            Ellipse(pos=(self.x + 40, self.y - 10), size=(20, 20))

    def on_press(self):
        self.show_user_info()

    def show_user_info(self):
        user_info_layout = MDBoxLayout(orientation="vertical", spacing=10, padding=20)
        close_button = MDRaisedButton(text="Close", on_release=lambda x: self.dialog.dismiss())

        self.dialog = MDDialog(
            title="User Information",
            type="custom",
            content_cls=user_info_layout,
            buttons=[close_button],
        )
        self.dialog.open()

class IconGrid(MDGridLayout):
    def __init__(self, **kwargs):
        super().__init__(cols=3, rows=2, **kwargs)
        for _ in range(6):
            self.add_widget(CustomIcon())

class KivyAndroidApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def send_message(self):
        message = self.root.ids.message_input.text
        if message.strip():
            print(f"User: {message}")
            self.root.ids.message_input.text = ""

    def change_screen(self, screen_name):
        print(f"Switching to {screen_name} screen")

    def show_add_friend_dialog(self):
        self.friend_input = MDTextField(hint_text="Enter friend's name")
        add_button = MDRaisedButton(text="Add", on_release=self.add_friend)
        close_button = MDRaisedButton(text="Close", on_release=lambda x: self.dialog.dismiss())

        self.dialog = MDDialog(
            title="Add Friend",
            type="custom",
            content_cls=self.friend_input,
            buttons=[add_button, close_button],
        )
        self.dialog.open()

    def add_friend(self, instance):
        friend_name = self.friend_input.text.strip()
        if friend_name:
            print(f"Added friend: {friend_name}")
            self.dialog.dismiss()

if __name__ == "__main__":
    KivyAndroidApp().run()
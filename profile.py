from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        with self.canvas.before:
            Color(229/255, 219/255, 197/255, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        self.top_bar = BoxLayout(orientation='horizontal', size_hint=(1, None), height=100, padding=10, spacing=10)
        self.profile_pic = Image(source="profileimg.png", size_hint=(None, 1), width=80)
        self.top_bar.add_widget(self.profile_pic)

        self.username_label = MDLabel(text="User ID", halign='left', font_style="H6")
        self.top_bar.add_widget(self.username_label)

        self.settings_btn = MDIconButton(icon="cog", user_font_size="32sp")
        self.settings_btn.bind(on_press=self.open_settings)
        self.top_bar.add_widget(self.settings_btn)

        self.layout.add_widget(self.top_bar)

        self.streak_label = MDLabel(text="🔥 Streak", halign='center', font_style="H5")
        self.layout.add_widget(self.streak_label)

        self.streak_img = Image(source="streakimg.png", size_hint=(None, None), size=(100, 100))
        self.layout.add_widget(self.streak_img)

        self.add_widget(self.layout)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def open_settings(self, instance):
        self.popup = Popup(title="Settings", content=SettingsPopup(self), size_hint=(0.8, 0.8))
        self.popup.open()

    def update_profile(self, user_id, profile_pic):
        self.username_label.text = user_id if user_id else "User ID"
        if profile_pic:
            self.profile_pic.source = profile_pic

class SettingsPopup(BoxLayout):
    def __init__(self, profile_screen, **kwargs):
        super(SettingsPopup, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.profile_screen = profile_screen

        self.profile_button = Button(text="Edit Profile")
        self.profile_button.bind(on_press=self.open_profile_popup)
        self.add_widget(self.profile_button)

        self.change_password_button = Button(text="Change Password")
        self.change_password_button.bind(on_press=self.open_password_popup)
        self.add_widget(self.change_password_button)

        self.logout_button = Button(text="Logout")
        self.logout_button.bind(on_press=self.logout_user)
        self.add_widget(self.logout_button)

        notifications_layout = BoxLayout(orientation='horizontal')
        notifications_label = MDLabel(text="Notifications")
        self.notifications_toggle = ToggleButton(text="OFF")
        self.notifications_toggle.bind(on_press=self.toggle_notifications)
        notifications_layout.add_widget(notifications_label)
        notifications_layout.add_widget(self.notifications_toggle)
        self.add_widget(notifications_layout)

    def open_profile_popup(self, instance):
        self.popup = Popup(title="Profile Settings", content=ProfileEditPopup(self.profile_screen), size_hint=(0.8, 0.8))
        self.popup.open()

    def open_password_popup(self, instance):
        self.popup = Popup(title="Change Password", content=PasswordPopup(), size_hint=(0.8, 0.8))
        self.popup.open()

    def logout_user(self, instance):
        self.profile_screen.update_profile("", "")

    def toggle_notifications(self, instance):
        instance.text = "ON" if instance.state == "down" else "OFF"

class ProfileEditPopup(BoxLayout):
    def __init__(self, profile_screen, **kwargs):
        super(ProfileEditPopup, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.profile_screen = profile_screen

        self.profile_pic = Image(source="profileimg.png", size_hint=(None, None), size=(100, 100))
        self.add_widget(self.profile_pic)

        self.choose_btn = Button(text="Choose Picture")
        self.choose_btn.bind(on_press=self.open_file_chooser)
        self.add_widget(self.choose_btn)

        self.user_id_input = TextInput(hint_text="Enter User ID")
        self.add_widget(self.user_id_input)

        self.save_btn = Button(text="Save")
        self.save_btn.bind(on_press=self.save_profile)
        self.add_widget(self.save_btn)

    def open_file_chooser(self, instance):
        layout = BoxLayout(orientation='vertical')
        self.file_chooser = FileChooserListView()
        select_btn = Button(text="Select")
        select_btn.bind(on_press=self.select_image)
        layout.add_widget(self.file_chooser)
        layout.add_widget(select_btn)
        self.file_popup = Popup(title="Select Image", content=layout, size_hint=(0.9, 0.9))
        self.file_popup.open()

    def select_image(self, instance):
        if self.file_chooser.selection:
            self.profile_pic.source = self.file_chooser.selection[0]
            self.file_popup.dismiss()

    def save_profile(self, instance):
        self.profile_screen.update_profile(self.user_id_input.text, self.profile_pic.source)
        self.parent.parent.dismiss()

class PasswordPopup(BoxLayout):
    def __init__(self, **kwargs):
        super(PasswordPopup, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.old_pw = TextInput(hint_text="Old Password", password=True)
        self.new_pw = TextInput(hint_text="New Password", password=True)
        self.confirm_pw = TextInput(hint_text="Confirm Password", password=True)
        self.status = MDLabel(text="")
        self.save = Button(text="Change")
        self.save.bind(on_press=self.change_pw)

        self.add_widget(self.old_pw)
        self.add_widget(self.new_pw)
        self.add_widget(self.confirm_pw)
        self.add_widget(self.status)
        self.add_widget(self.save)

    def change_pw(self, instance):
        if self.new_pw.text != self.confirm_pw.text:
            self.status.text = "Passwords don't match"
        else:
            self.status.text = "Password changed!"
            Clock.schedule_once(lambda dt: self.parent.parent.dismiss(), 2)

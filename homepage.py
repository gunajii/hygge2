from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.lang import Builder
import requests
from datetime import datetime
from functools import partial

Window.size = (dp(360), dp(640))  
Window.softinput_mode = "below_target"

class HomePageScreen(Screen):  
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", size_hint=(1, 1))  
        self.create_ui(layout)
        self.add_widget(layout)  

    def create_ui(self, layout):
        with self.canvas.before:
            Color(0.96, 0.92, 0.88, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        header = BoxLayout(size_hint_y=0.15, padding=20, spacing=15)
        header.add_widget(Image(source="profile_icon.png", size_hint=(None, None), size=(50, 50)))

        self.greeting_label = Label(text="Hello, Name!", font_size=22, bold=True, color=(0, 0, 0, 1))
        header.add_widget(self.greeting_label)
        layout.add_widget(header)

        text_box = BoxLayout(size_hint_y=0.3, padding=20)
        with text_box.canvas.before:
            Color(0, 0, 0, 1)
            self.border_rect = Rectangle(pos=text_box.pos, size=text_box.size)
        text_box.bind(pos=self.update_border, size=self.update_border)

        affirmations = ["You are enough!", "Today is a fresh start!", "Believe in yourself!", "You can do hard things!"]
        today_index = datetime.now().day % len(affirmations)
        self.affirmation_label = Label(text=affirmations[today_index], font_size=20, color=(0, 0, 0, 1))
        text_box.add_widget(self.affirmation_label)
        layout.add_widget(text_box)

        mood_layout = BoxLayout(size_hint_y=0.15, padding=20, orientation='vertical')
        self.mood_label = Label(text="Select your mood", font_size=18, color=(0, 0, 0, 1))
        self.mood_slider = Slider(min=0, max=100, value=50)
        self.mood_slider.bind(value=self.update_mood_label)
        
        mood_layout.add_widget(self.mood_label)
        mood_layout.add_widget(self.mood_slider)
        layout.add_widget(mood_layout)
        
        save_btn = Button(text="Save Mood", size_hint=(None, None), size=(150, 50), pos_hint={'center_x': 0.5})
        save_btn.bind(on_press=self.save_mood)
        layout.add_widget(save_btn)

        nav_bar = BoxLayout(size_hint_y=0.1, padding=10, spacing=20)
        home_btn = Button(text="🏠", font_size=30, size_hint_x=0.25)
        community_btn = Button(text="💬", font_size=30, size_hint_x=0.25)
        activity_btn = Button(text="📊", font_size=30, size_hint_x=0.25)
        profile_btn = Button(text="👤", font_size=30, size_hint_x=0.25)

        nav_bar.add_widget(home_btn)
        nav_bar.add_widget(community_btn)
        nav_bar.add_widget(activity_btn)
        nav_bar.add_widget(profile_btn)

        layout.add_widget(nav_bar)

    def update_mood_label(self, instance, value):
        if value < 33:
            self.mood_label.text = "😊 Happy"
        elif value < 66:
            self.mood_label.text = "😐 Neutral"
        else:
            self.mood_label.text = "😢 Sad"

    def save_mood(self, instance):
        user = self.greeting_label.text.replace("Hello, ", "").strip()
        if user == "Name!":
            self.greeting_label.text = "Please enter your name first!"
            return
        
        mood = self.mood_label.text.split(" ")[1]  # Extract the mood word
        data = {"user": user, "mood": mood}
        response = requests.post("http://localhost:3000/log_mood", json=data)
        
        if response.status_code == 200:
            print("Mood saved successfully!")
        else:
            print("Error saving mood.")
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update_border(self, *args):
        self.border_rect.pos = args[0].pos
        self.border_rect.size = args[0].size

class MindfulApp(MDApp):  
    def build(self):
        Builder.load_file("mindfultracker.kv")
        sm = ScreenManager()
        sm.add_widget(HomePageScreen(name="homepage"))
        return sm

if __name__ == "__main__":
    MindfulApp().run()
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

LESSONS = [
    {
        "title":"Insurance Policy",
        "text": (
            "The beneficiary shall receive the policy benefits"
            "Upon the death of the policyholder."
        ),
        "question": "Who recieves the money?",
        "answer": "The beneficiary receives the money."
    },
    {
        "title": "Basic Arithmetic",
        "text": "Solve the following: 12 + 8",
        "question": "What is 12 plus 8?",
        "answer": "The answer is 20."
    },
    {
        "title":"Multiplication",
        "text":"Calculate : 7 X 6?",
        "question":" What is "
    }
]


class EnglishScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.lesson_index = 0

        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        self.title_label = Label(font_size=22)
        self.text_label  = Label(font_size=16)
        self.question_label = Label(font_size=16)
        self.answer_label = Label(
            font_size=16,
            color=(0, 1, 0, 1)
        )

        layout.add_widget(self.title_label)
        layout.add_widget(self.text_label)
        layout.add_widget(self.question_label)
        layout.add_widget(self.answer_label)

        btn_show = Button(text="Show Explanation", size_hint=(1, 0.15))
        btn_show.bind(on_press=self.show_answer)
        btn_next = Button(text="Next Example", size_hint=(1, 0.15))
        btn_next.bind(on_press=self.next_lesson)
        btn_back = Button(text="Back", size_hint=(1,0.15))
        btn_back.bind(on_press=self.go_back)
        
        layout.add_widget(btn_show)
        layout.add_widget(btn_next)
        layout.add_widget(btn_back)

        self.add_widget(layout)
        self.load_lesson()
    
    def load_lesson(self):
        lesson = LESSONS[self.lesson_index]
        self.title_label.text = lesson["title"]
        self.text_label.text = lesson["text"]

        self.question_label.text = lesson["question"]
        self.answer_label.text =""
        self.answer_label.opacity = 0


    def show_answer(self, instance):
        self.answer_label.text =  LESSONS[self.lesson_index]["answer"]
        self.answer_label.opacity =1
        
    def next_lesson(self,instance):
        self.lesson_index = (self.lesson_index + 1) % len(LESSONS)
        self.load_lesson()

    def go_back(self, instance):
        self.manager.current = "home"


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        btn = Button(text="Go to English Comprehension")
        btn.bind(on_press=self.go_to_english)
        layout.add_widget(btn)
        self.add_widget(layout)

    def go_to_english(self, instance):
        self.manager.current = "english"


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(EnglishScreen(name="english"))
        return sm


if __name__ == "__main__":
    MyApp().run()

import os
import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp
from kivy.core.window import Window

# ── Ultra Clean Brand Colors ────────────────────────────────
BLUE         = (0.30, 0.76, 0.91, 1)
BLUE_DARK    = (0.18, 0.55, 0.72, 1)
BLUE_LIGHT   = (0.88, 0.96, 0.99, 1)
GREY_BLUE    = (0.48, 0.61, 0.69, 1)
WHITE        = (1.0,  1.0,  1.0,  1)
GREY_TEXT    = (0.30, 0.33, 0.38, 1)
GREY_LIGHT   = (0.92, 0.94, 0.96, 1)
GREEN_OK     = (0.15, 0.68, 0.38, 1)
ORANGE       = (0.95, 0.55, 0.10, 1)
RED          = (0.82, 0.18, 0.18, 1)
BG           = (0.97, 0.99, 1.00, 1)

OWNER_PIN = "1234"

SERVICES = [
    ("Mobile Car Washing",
     "Professional car wash at your location"),
    ("Couch / Mattress / Rugs /\nCurtain / Chair Cleaning",
     "Deep clean for all your soft furnishings"),
    ("Built-in Carpet Cleaning",
     "Thorough in-place carpet cleaning"),
    ("Specialized Upholstery Cleaning",
     "Expert care for delicate fabrics"),
    ("Ottoman Cleaning",
     "Restore your ottomans to like-new"),
]


# ── Helpers ─────────────────────────────────────────────────
def bg(widget, color):
    with widget.canvas.before:
        Color(*color)
        rect = Rectangle(size=widget.size, pos=widget.pos)
    widget.bind(size=lambda i, v: setattr(rect, 'size', v))
    widget.bind(pos=lambda i, v: setattr(rect, 'pos', v))


def lbl(text, size=16, bold=False, color=GREY_TEXT,
        halign='left', valign='middle', height=None):
    h = height or dp(36)
    l = Label(
        text=text, font_size=sp(size), bold=bold, color=color,
        halign=halign, valign=valign,
        size_hint_y=None, height=h
    )
    l.bind(size=l.setter('text_size'))
    return l


def inp(hint, filter=None, password=False):
    t = TextInput(
        hint_text=hint, multiline=False,
        background_color=WHITE,
        foreground_color=(0.1, 0.1, 0.15, 1),
        hint_text_color=(0.60, 0.65, 0.70, 1),
        cursor_color=BLUE_DARK,
        font_size=sp(15),
        padding=[dp(12), dp(12)],
        password=password,
        size_hint_y=None,
        height=dp(52)
    )
    if filter:
        t.input_filter = filter
    return t


def divider(color=GREY_LIGHT):
    d = BoxLayout(size_hint_y=None, height=dp(1))
    bg(d, color)
    return d


def make_scroll():
    return ScrollView(
        scroll_type=['bars', 'content'],
        bar_width=dp(3),
        scroll_distance=dp(10),
        bar_color=BLUE,
        bar_inactive_color=GREY_LIGHT
    )


def action_btn(text, color, on_press=None, height=None):
    h = height or dp(54)
    b = Button(
        text=text,
        background_color=color,
        color=WHITE,
        bold=True,
        font_size=sp(15),
        size_hint_y=None,
        height=h,
        always_release=True
    )
    if on_press:
        b.bind(on_press=on_press)
    return b


def show_popup(title, message, btn_color=None, on_dismiss=None):
    btn_color = btn_color or BLUE_DARK
    content = BoxLayout(orientation='vertical',
                        padding=[dp(16), dp(12)], spacing=dp(10))
    msg = Label(
        text=message, color=GREY_TEXT,
        halign='center', valign='middle',
        font_size=sp(14)
    )
    msg.bind(size=msg.setter('text_size'))
    content.add_widget(msg)
    ok = Button(
        text="OK", size_hint_y=None, height=dp(48),
        background_color=btn_color, color=WHITE,
        bold=True, font_size=sp(15), always_release=True
    )
    content.add_widget(ok)
    p = Popup(
        title=title, content=content,
        size_hint=(0.88, 0.40),
        title_color=BLUE_DARK,
        separator_color=BLUE,
        title_size=sp(16)
    )
    def _dismiss(x):
        p.dismiss()
        if on_dismiss:
            on_dismiss()
    ok.bind(on_press=_dismiss)
    p.open()


def header_bar(title, back_screen=None, right_text=None, right_action=None):
    bar = BoxLayout(size_hint_y=None, height=dp(60),
                    padding=[dp(8), dp(8)])
    bg(bar, BLUE_DARK)

    # Left
    if back_screen:
        back = Button(
            text="< Back", size_hint_x=None, width=dp(80),
            background_color=(0, 0, 0, 0), color=WHITE,
            font_size=sp(14), bold=True, always_release=True
        )
        back.bind(on_press=lambda x: setattr(
            App.get_running_app().root, 'current', back_screen))
        bar.add_widget(back)
    else:
        bar.add_widget(Label(size_hint_x=None, width=dp(80)))

    # Centre
    bar.add_widget(lbl(title, size=17, bold=True, color=WHITE,
                        halign='center', height=dp(44)))

    # Right
    if right_text and right_action:
        r = Button(
            text=right_text, size_hint_x=None, width=dp(80),
            background_color=(0, 0, 0, 0), color=WHITE,
            font_size=sp(13), bold=True, always_release=True
        )
        r.bind(on_press=right_action)
        bar.add_widget(r)
    else:
        bar.add_widget(Label(size_hint_x=None, width=dp(80)))

    return bar


# ════════════════════════════════════════════════════════════
#  SCREEN 1 — HOME
# ════════════════════════════════════════════════════════════
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical')
        bg(root, BG)

        # Hero
        hero = BoxLayout(orientation='vertical', size_hint_y=None,
                         height=dp(110), padding=[dp(16), dp(12)])
        bg(hero, BLUE_DARK)
        hero.add_widget(lbl("ULTRA CLEAN", size=22, bold=True,
                             color=WHITE, halign='center', height=dp(40)))
        hero.add_widget(lbl("Mobile Services (PTY) Ltd", size=12,
                             color=GREY_LIGHT, halign='center', height=dp(24)))
        hero.add_widget(lbl("We come to you — anytime, anywhere.", size=12,
                             color=BLUE_LIGHT, halign='center', height=dp(22)))
        root.add_widget(hero)

        # Services label
        root.add_widget(lbl("Our Services", size=15, bold=True,
                             color=BLUE_DARK, halign='center',
                             height=dp(40)))

        # Services scroll
        scroll = make_scroll()
        sbox = BoxLayout(orientation='vertical', padding=[dp(12), dp(4)],
                         spacing=dp(10), size_hint_y=None)
        sbox.bind(minimum_height=sbox.setter('height'))

        for i, (name, desc) in enumerate(SERVICES):
            card = BoxLayout(orientation='vertical',
                             size_hint_y=None, height=dp(72),
                             padding=[dp(12), dp(8)])
            bg(card, BLUE_DARK if i % 2 == 0 else BLUE)

            name_lbl = Label(
                text=name, color=WHITE, bold=True,
                font_size=sp(14), halign='center', valign='middle',
                size_hint_y=0.55
            )
            name_lbl.bind(size=name_lbl.setter('text_size'))

            desc_lbl = Label(
                text=desc, color=BLUE_LIGHT,
                font_size=sp(11), halign='center', valign='middle',
                size_hint_y=0.45
            )
            desc_lbl.bind(size=desc_lbl.setter('text_size'))

            card.add_widget(name_lbl)
            card.add_widget(desc_lbl)

            # Make whole card tappable
            btn = Button(
                text="", size_hint=(1, 1),
                background_color=(0, 0, 0, 0),
                always_release=True
            )
            btn.bind(on_press=lambda x, n=name: self.go_book(n))

            wrapper = BoxLayout(size_hint_y=None, height=dp(72))
            wrapper.add_widget(card)
            wrapper.add_widget(btn)
            # Overlap trick — use FloatLayout style
            from kivy.uix.floatlayout import FloatLayout
            fl = FloatLayout(size_hint_y=None, height=dp(72))
            card.pos_hint = {'x': 0, 'y': 0}
            card.size_hint = (1, 1)
            btn2 = Button(
                background_color=(0, 0, 0, 0),
                size_hint=(1, 1), pos_hint={'x': 0, 'y': 0},
                always_release=True
            )
            btn2.bind(on_press=lambda x, n=name: self.go_book(n))
            fl.add_widget(card)
            fl.add_widget(btn2)
            sbox.add_widget(fl)

        scroll.add_widget(sbox)
        root.add_widget(scroll)

        # Bottom nav
        nav = BoxLayout(size_hint_y=None, height=dp(56),
                        spacing=dp(2), padding=[dp(4), dp(4)])
        bg(nav, BLUE_DARK)

        for label, screen in [("About Us", "about"),
                               ("Why Us", "why"),
                               ("Owner Login", "owner_login")]:
            btn = Button(
                text=label,
                background_color=BLUE,
                color=WHITE,
                font_size=sp(13),
                bold=True,
                always_release=True
            )
            btn.bind(on_press=lambda x, s=screen: setattr(
                self.manager, 'current', s))
            nav.add_widget(btn)

        root.add_widget(nav)
        self.add_widget(root)

    def go_book(self, service):
        self.manager.get_screen('booking').set_service(service)
        self.manager.current = 'booking'


# ════════════════════════════════════════════════════════════
#  SCREEN 2 — BOOKING
# ════════════════════════════════════════════════════════════
class BookingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_service = SERVICES[0][0]

        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header_bar("Book a Service", back_screen='home'))

        scroll = make_scroll()
        form = BoxLayout(orientation='vertical',
                         padding=[dp(16), dp(14)],
                         spacing=dp(10), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        self.service_lbl = lbl("", size=14, bold=True,
                                color=BLUE_DARK, halign='center',
                                height=dp(40))
        form.add_widget(self.service_lbl)
        form.add_widget(divider(BLUE_LIGHT))

        def field(label_text, widget):
            form.add_widget(lbl(label_text, size=13, bold=True,
                                 color=GREY_BLUE, height=dp(30)))
            form.add_widget(widget)
            form.add_widget(BoxLayout(size_hint_y=None, height=dp(4)))

        self.name_input    = inp("Your full name")
        self.phone_input   = inp("e.g. 071 234 5678")
        self.address_input = inp("Street address for the visit")
        self.date_input    = inp("YYYY-MM-DD  e.g. 2026-09-25")
        self.time_spinner  = Spinner(
            text="09:00",
            values=("07:00", "08:00", "09:00", "10:00", "11:00",
                    "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"),
            background_color=BLUE, color=WHITE,
            font_size=sp(15),
            size_hint_y=None, height=dp(52),
            always_release=True
        )
        self.notes_input = TextInput(
            hint_text="Any special instructions? (optional)",
            background_color=WHITE,
            foreground_color=(0.1, 0.1, 0.15, 1),
            hint_text_color=(0.60, 0.65, 0.70, 1),
            font_size=sp(14),
            padding=[dp(12), dp(10)],
            size_hint_y=None, height=dp(90)
        )

        field("Full Name:", self.name_input)
        field("Phone Number:", self.phone_input)
        field("Address:", self.address_input)
        field("Preferred Date:", self.date_input)
        field("Preferred Time:", self.time_spinner)
        form.add_widget(lbl("Notes:", size=13, bold=True,
                             color=GREY_BLUE, height=dp(30)))
        form.add_widget(self.notes_input)
        form.add_widget(BoxLayout(size_hint_y=None, height=dp(12)))
        form.add_widget(action_btn("CONFIRM BOOKING", GREEN_OK,
                                   self.submit_booking, height=dp(58)))
        form.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))

        scroll.add_widget(form)
        root.add_widget(scroll)
        self.add_widget(root)

    def set_service(self, service):
        self.selected_service = service
        self.service_lbl.text = f"Selected: {service}"

    def submit_booking(self, instance):
        name    = self.name_input.text.strip()
        phone   = self.phone_input.text.strip()
        address = self.address_input.text.strip()
        date    = self.date_input.text.strip()
        time    = self.time_spinner.text
        notes   = self.notes_input.text.strip()

        if not (name and phone and address and date):
            show_popup("Missing Info",
                       "Please fill in your name,\nphone, address and date.",
                       btn_color=RED)
            return

        now = datetime.now().isoformat()
        app = App.get_running_app()
        app.cursor.execute("""
            INSERT INTO bookings
            (customer_name, phone, address, service,
             date, time, notes, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
        """, (name, phone, address, self.selected_service,
              date, time, notes, now))
        app.conn.commit()

        self.name_input.text    = ""
        self.phone_input.text   = ""
        self.address_input.text = ""
        self.date_input.text    = ""
        self.notes_input.text   = ""

        show_popup(
            "Booking Received!",
            f"Thank you {name}!\n\nWe will confirm your booking shortly.\nUltra Clean will be in touch!",
            btn_color=GREEN_OK,
            on_dismiss=lambda: setattr(self.manager, 'current', 'home')
        )


# ════════════════════════════════════════════════════════════
#  SCREEN 3 — ABOUT US
# ════════════════════════════════════════════════════════════
class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header_bar("About Us", back_screen='home'))

        scroll = make_scroll()
        content = BoxLayout(orientation='vertical',
                            padding=[dp(16), dp(14)],
                            spacing=dp(12), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(lbl("Who We Are", size=17, bold=True,
                                color=BLUE_DARK, halign='center',
                                height=dp(40)))
        content.add_widget(divider(BLUE))

        about_text = (
            "At Ultra Clean Mobile Services, we are dedicated to bringing "
            "professional-grade care directly to your doorstep.\n\n"
            "We specialize in comprehensive mobile cleaning solutions designed "
            "to revitalize your most-loved spaces and assets — from expert car "
            "washing to the deep cleaning of couches, mattresses, rugs, "
            "curtains, and chairs.\n\n"
            "Our team utilizes specialized techniques for built-in carpets, "
            "ottomans, and delicate upholstery, ensuring every fiber is treated "
            "with precision and care.\n\n"
            "Whether at home or on the go, we combine convenience with "
            "uncompromising quality to help you maintain a pristine, healthy, "
            "and brilliant environment."
        )

        about_lbl = Label(
            text=about_text, color=GREY_TEXT,
            font_size=sp(14), halign='left', valign='top',
            size_hint_y=None,
            text_size=(Window.width - dp(32), None)
        )
        about_lbl.bind(texture_size=lambda i, v: setattr(i, 'height', v[1]))
        about_lbl.bind(width=lambda i, v: setattr(
            i, 'text_size', (v, None)))
        content.add_widget(about_lbl)

        content.add_widget(BoxLayout(size_hint_y=None, height=dp(16)))
        content.add_widget(lbl("Our Services", size=16, bold=True,
                                color=BLUE_DARK, halign='center',
                                height=dp(36)))
        content.add_widget(divider(BLUE))

        for name, desc in SERVICES:
            scard = BoxLayout(orientation='vertical',
                              size_hint_y=None, height=dp(64),
                              padding=[dp(12), dp(8)])
            bg(scard, BLUE_LIGHT)
            scard.add_widget(lbl(f"  {name.replace(chr(10), ' ')}",
                                  size=13, bold=True, color=BLUE_DARK,
                                  height=dp(28)))
            scard.add_widget(lbl(f"  {desc}", size=11,
                                  color=GREY_BLUE, height=dp(22)))
            content.add_widget(scard)
            content.add_widget(BoxLayout(size_hint_y=None, height=dp(4)))

        content.add_widget(BoxLayout(size_hint_y=None, height=dp(16)))
        content.add_widget(action_btn(
            "Book Now", BLUE,
            lambda x: setattr(self.manager, 'current', 'home'),
            height=dp(54)
        ))
        content.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)


# ════════════════════════════════════════════════════════════
#  SCREEN 4 — WHY CHOOSE US
# ════════════════════════════════════════════════════════════
class WhyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header_bar("Why Choose Us", back_screen='home'))

        scroll = make_scroll()
        content = BoxLayout(orientation='vertical',
                            padding=[dp(16), dp(14)],
                            spacing=dp(12), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(lbl("Why Choose Us", size=17, bold=True,
                                color=BLUE_DARK, halign='center',
                                height=dp(40)))
        content.add_widget(divider(BLUE))

        why_text = (
            "What sets Ultra Clean Mobile Services apart is our commitment "
            "to bringing professional-grade results directly to your doorstep.\n\n"
            "We understand that your time is your most valuable asset, which is "
            "why our fully mobile service is designed to fit seamlessly into your "
            "busy schedule.\n\n"
            "Whether refreshing your home or office, or handling your car wash "
            "on-site, we prioritize your comfort and convenience.\n\n"
            "With us, you don't just get a cleaner space — you gain the freedom "
            "to focus on what matters most."
        )

        why_lbl = Label(
            text=why_text, color=GREY_TEXT,
            font_size=sp(14), halign='left', valign='top',
            size_hint_y=None,
            text_size=(Window.width - dp(32), None)
        )
        why_lbl.bind(texture_size=lambda i, v: setattr(i, 'height', v[1]))
        why_lbl.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        content.add_widget(why_lbl)

        content.add_widget(BoxLayout(size_hint_y=None, height=dp(16)))

        reasons = [
            ("We Come To You",       "No travel needed — we come to you"),
            ("Professional Grade",   "Industry-level equipment & techniques"),
            ("Saves Your Time",      "Book in minutes, we handle the rest"),
            ("All Services In One",  "Car, carpets, couches & more"),
            ("Precision & Care",     "Every fiber treated with expert attention"),
        ]

        for title, desc in reasons:
            rcard = BoxLayout(orientation='vertical',
                              size_hint_y=None, height=dp(64),
                              padding=[dp(14), dp(8)])
            bg(rcard, BLUE_LIGHT)
            rcard.add_widget(lbl(title, size=14, bold=True,
                                  color=BLUE_DARK, height=dp(28)))
            rcard.add_widget(lbl(desc, size=12, color=GREY_TEXT,
                                  height=dp(22)))
            content.add_widget(rcard)
            content.add_widget(BoxLayout(size_hint_y=None, height=dp(4)))

        content.add_widget(BoxLayout(size_hint_y=None, height=dp(16)))
        content.add_widget(action_btn(
            "Book Now", BLUE,
            lambda x: setattr(self.manager, 'current', 'home'),
            height=dp(54)
        ))
        content.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)


# ════════════════════════════════════════════════════════════
#  SCREEN 5 — OWNER LOGIN
# ════════════════════════════════════════════════════════════
class OwnerLoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header_bar("Owner Login", back_screen='home'))
        root.add_widget(Label(size_hint_y=0.12))

        card = BoxLayout(orientation='vertical',
                         padding=[dp(24), dp(20)],
                         spacing=dp(14),
                         size_hint=(0.90, None),
                         height=dp(240),
                         pos_hint={'center_x': 0.5})
        bg(card, WHITE)

        card.add_widget(lbl("Enter your PIN", size=16, bold=True,
                             color=BLUE_DARK, halign='center', height=dp(36)))
        self.pin_input = inp("PIN", password=True)
        card.add_widget(self.pin_input)
        card.add_widget(action_btn("LOGIN", BLUE_DARK,
                                    self.check_pin, height=dp(54)))
        root.add_widget(card)
        root.add_widget(Label())
        self.add_widget(root)

    def check_pin(self, instance):
        if self.pin_input.text == OWNER_PIN:
            self.pin_input.text = ""
            self.manager.current = 'owner_dashboard'
        else:
            self.pin_input.text = ""
            show_popup("Access Denied",
                       "Incorrect PIN.\nPlease try again.",
                       btn_color=RED)


# ════════════════════════════════════════════════════════════
#  SCREEN 6 — OWNER DASHBOARD
# ════════════════════════════════════════════════════════════
class OwnerDashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_filter = "All"
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation='vertical')
        bg(root, BG)

        logout_btn = Button(
            text="Logout", size_hint_x=None, width=dp(80),
            background_color=(0, 0, 0, 0), color=WHITE,
            font_size=sp(13), bold=True, always_release=True
        )
        logout_btn.bind(on_press=lambda x: setattr(
            self.manager, 'current', 'home'))

        root.add_widget(header_bar(
            "Dashboard",
            right_text="Logout",
            right_action=lambda x: setattr(self.manager, 'current', 'home')
        ))

        # Stats bar
        self.stats_bar = BoxLayout(
            size_hint_y=None, height=dp(70),
            padding=[dp(8), dp(8)], spacing=dp(4))
        bg(self.stats_bar, BLUE_LIGHT)
        root.add_widget(self.stats_bar)

        # Filter row — 2 rows of filters to avoid cramping
        filter_box = BoxLayout(orientation='vertical',
                               size_hint_y=None, height=dp(88),
                               spacing=dp(4), padding=[dp(6), dp(4)])
        bg(filter_box, WHITE)

        row1 = BoxLayout(spacing=dp(4), size_hint_y=0.5)
        row2 = BoxLayout(spacing=dp(4), size_hint_y=0.5)

        self.filter_btns = {}
        filters = ["All", "Pending", "Confirmed", "Completed", "Cancelled"]

        for i, status in enumerate(filters):
            btn = Button(
                text=status,
                font_size=sp(13), bold=True,
                background_color=BLUE if status == "All" else GREY_LIGHT,
                color=WHITE if status == "All" else GREY_TEXT,
                always_release=True
            )
            btn.bind(on_press=lambda x, s=status: self.filter_bookings(s))
            self.filter_btns[status] = btn
            if i < 3:
                row1.add_widget(btn)
            else:
                row2.add_widget(btn)

        filter_box.add_widget(row1)
        filter_box.add_widget(row2)
        root.add_widget(filter_box)

        # Bookings list
        self.scroll = make_scroll()
        self.bookings_box = BoxLayout(
            orientation='vertical',
            padding=[dp(10), dp(8)],
            spacing=dp(10),
            size_hint_y=None
        )
        self.bookings_box.bind(
            minimum_height=self.bookings_box.setter('height'))
        self.scroll.add_widget(self.bookings_box)
        root.add_widget(self.scroll)

        self.add_widget(root)

    def on_enter(self):
        self.filter_bookings("All")

    def _update_stats(self):
        app = App.get_running_app()
        self.stats_bar.clear_widgets()

        for label, query, color in [
            ("Total",     "SELECT COUNT(*) FROM bookings", BLUE_DARK),
            ("Pending",   "SELECT COUNT(*) FROM bookings WHERE status='Pending'", ORANGE),
            ("Confirmed", "SELECT COUNT(*) FROM bookings WHERE status='Confirmed'", BLUE),
            ("Completed", "SELECT COUNT(*) FROM bookings WHERE status='Completed'", GREEN_OK),
        ]:
            app.cursor.execute(query)
            count = app.cursor.fetchone()[0]

            box = BoxLayout(orientation='vertical')
            box.add_widget(lbl(str(count), size=22, bold=True,
                                color=color, halign='center', height=dp(34)))
            box.add_widget(lbl(label, size=11, color=GREY_BLUE,
                                halign='center', height=dp(20)))
            self.stats_bar.add_widget(box)

    def filter_bookings(self, status):
        self.current_filter = status

        for s, btn in self.filter_btns.items():
            btn.background_color = BLUE if s == status else GREY_LIGHT
            btn.color = WHITE if s == status else GREY_TEXT

        app = App.get_running_app()
        if status == "All":
            app.cursor.execute("""
                SELECT id, customer_name, phone, service,
                       date, time, address, status, notes
                FROM bookings ORDER BY date DESC, time
            """)
        else:
            app.cursor.execute("""
                SELECT id, customer_name, phone, service,
                       date, time, address, status, notes
                FROM bookings WHERE status=?
                ORDER BY date DESC, time
            """, (status,))

        bookings = app.cursor.fetchall()
        self.bookings_box.clear_widgets()
        self._update_stats()

        if not bookings:
            self.bookings_box.add_widget(
                lbl(f"No {status.lower()} bookings found.",
                    halign='center', color=GREY_BLUE, height=dp(60)))
            return

        for booking in bookings:
            self.bookings_box.add_widget(self._booking_card(booking))

    def _booking_card(self, booking):
        bid, name, phone, service, date, time, address, status, notes = booking

        status_colors = {
            "Pending":   ORANGE,
            "Confirmed": BLUE,
            "Completed": GREEN_OK,
            "Cancelled": RED
        }
        s_color = status_colors.get(status, GREY_TEXT)

        c = BoxLayout(orientation='vertical',
                      padding=[dp(14), dp(12)],
                      spacing=dp(6),
                      size_hint_y=None,
                      height=dp(220))
        bg(c, WHITE)

        # Name + status
        top = BoxLayout(size_hint_y=None, height=dp(34))
        top.add_widget(lbl(name, size=16, bold=True,
                            color=BLUE_DARK, height=dp(34)))
        s_lbl = Label(
            text=status, color=s_color, bold=True,
            font_size=sp(13), size_hint_x=None, width=dp(100),
            halign='right', valign='middle'
        )
        s_lbl.bind(size=s_lbl.setter('text_size'))
        top.add_widget(s_lbl)
        c.add_widget(top)

        c.add_widget(divider(BLUE_LIGHT))

        for text in [
            f"Service: {service[:40]}",
            f"Date: {date}   Time: {time}",
            f"Phone: {phone}",
            f"Address: {address}",
        ]:
            c.add_widget(lbl(text, size=13, color=GREY_TEXT, height=dp(24)))

        if notes:
            c.add_widget(lbl(f"Notes: {notes}", size=12,
                              color=GREY_BLUE, height=dp(22)))

        # Action buttons
        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        for label, new_status, color in [
            ("Confirm",  "Confirmed", BLUE),
            ("Complete", "Completed", GREEN_OK),
            ("Cancel",   "Cancelled", RED),
        ]:
            btn = Button(
                text=label, background_color=color,
                color=WHITE, font_size=sp(13), bold=True,
                always_release=True
            )
            btn.bind(on_press=lambda x, i=bid, s=new_status:
                     self.update_status(i, s))
            btn_row.add_widget(btn)
        c.add_widget(btn_row)

        # Bottom accent
        accent = BoxLayout(size_hint_y=None, height=dp(3))
        bg(accent, BLUE_LIGHT)
        c.add_widget(accent)

        return c

    def update_status(self, booking_id, new_status):
        app = App.get_running_app()
        app.cursor.execute(
            "UPDATE bookings SET status=? WHERE id=?",
            (new_status, booking_id))
        app.conn.commit()
        self.filter_bookings(self.current_filter)
        show_popup("Updated",
                   f"Booking marked as {new_status}.",
                   btn_color=BLUE)


# ════════════════════════════════════════════════════════════
#  MAIN APP
# ════════════════════════════════════════════════════════════
class UltraCleanApp(App):
    def build(self):
        self.title = "Ultra Clean Mobile Services"
        self._setup_db()
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(BookingScreen(name='booking'))
        sm.add_widget(AboutScreen(name='about'))
        sm.add_widget(WhyScreen(name='why'))
        sm.add_widget(OwnerLoginScreen(name='owner_login'))
        sm.add_widget(OwnerDashboardScreen(name='owner_dashboard'))
        return sm

    def _setup_db(self):
        data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(data_dir, exist_ok=True)
        self.conn = sqlite3.connect(
            os.path.join(data_dir, "ultraclean.db"))
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                service TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                notes TEXT DEFAULT '',
                status TEXT DEFAULT 'Pending',
                created_at TEXT
            )
        """)
        self.conn.commit()


if __name__ == "__main__":
    UltraCleanApp().run()

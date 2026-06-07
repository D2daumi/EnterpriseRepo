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

# ── Frequency Cafe Brand Colors ─────────────────────────────
DARK        = (0.10, 0.10, 0.14, 1)   # Near black — modern base
PURPLE      = (0.45, 0.20, 0.80, 1)   # Vibrant purple — cool accent
PINK        = (0.95, 0.25, 0.55, 1)   # Hot pink — fun pop
ORANGE      = (0.98, 0.60, 0.10, 1)   # Warm orange — energy
YELLOW      = (0.98, 0.85, 0.10, 1)   # Bright yellow — fun
TEAL        = (0.10, 0.78, 0.70, 1)   # Teal — cool modern
WHITE       = (1.0,  1.0,  1.0,  1)
OFF_WHITE   = (0.96, 0.96, 0.98, 1)
GREY_TEXT   = (0.55, 0.55, 0.60, 1)
GREY_LIGHT  = (0.20, 0.20, 0.26, 1)   # Dark grey for cards
GREEN_OK    = (0.15, 0.80, 0.45, 1)
RED         = (0.90, 0.20, 0.20, 1)
BG          = (0.10, 0.10, 0.14, 1)   # Dark background

OWNER_PIN = "1234"

# ── Menu Data ───────────────────────────────────────────────
MUFFIN_FLAVOURS = [
    "Vanilla", "Chocolate", "Chocolate Mint",
    "Cappuccino", "Carrot Cake"
]

MENU = {
    "Muffins": {
        "type": "unit_and_bulk",
        "unit_price": 20,
        "flavours": MUFFIN_FLAVOURS,
        "bulk": {
            "2L":  180, "5L":  350,
            "10L": 390, "20L": 450
        },
        "emoji": "🧁"
    },
    "Biscuits": {
        "type": "bulk_only",
        "flavours": [],
        "bulk": {
            "2L":  250, "5L":  380,
            "10L": 450, "20L": 500
        },
        "emoji": "🍪"
    },
    "Scones": {
        "type": "bulk_only",
        "flavours": [],
        "bulk": {
            "2L":  150, "5L":  300,
            "10L": 400, "20L": 450
        },
        "emoji": "🥐"
    },
}


# ── Helpers ─────────────────────────────────────────────────
def bg(widget, color):
    with widget.canvas.before:
        Color(*color)
        rect = Rectangle(size=widget.size, pos=widget.pos)
    widget.bind(size=lambda i, v: setattr(rect, 'size', v))
    widget.bind(pos=lambda i, v: setattr(rect, 'pos', v))


def lbl(text, size=15, bold=False, color=WHITE,
        halign='left', valign='middle', height=36):
    l = Label(text=text, font_size=sp(size), bold=bold, color=color,
              halign=halign, valign=valign,
              size_hint_y=None, height=dp(height))
    l.bind(size=l.setter('text_size'))
    return l


def inp(hint, filter=None, password=False):
    t = TextInput(
        hint_text=hint, multiline=False,
        background_color=GREY_LIGHT,
        foreground_color=WHITE,
        hint_text_color=GREY_TEXT,
        cursor_color=PURPLE,
        font_size=sp(15), padding=[dp(12), dp(12)],
        password=password, size_hint_y=None, height=dp(52)
    )
    if filter:
        t.input_filter = filter
    return t


def make_scroll():
    return ScrollView(
        scroll_type=['bars', 'content'],
        bar_width=dp(3),
        scroll_distance=dp(10),
        bar_color=PURPLE,
        bar_inactive_color=GREY_LIGHT
    )


def action_btn(text, color, on_press=None, height=54):
    b = Button(
        text=text, background_color=color, color=WHITE,
        bold=True, font_size=sp(15),
        size_hint_y=None, height=dp(height),
        always_release=True
    )
    if on_press:
        b.bind(on_press=on_press)
    return b


def show_popup(title, message, btn_color=None, on_dismiss=None):
    btn_color = btn_color or PURPLE
    content = BoxLayout(orientation='vertical',
                        padding=[dp(16), dp(12)], spacing=dp(10))
    bg(content, DARK)
    msg = Label(text=message, color=WHITE, halign='center',
                valign='middle', font_size=sp(14))
    msg.bind(size=msg.setter('text_size'))
    content.add_widget(msg)
    ok = Button(text="OK", size_hint_y=None, height=dp(48),
                background_color=btn_color, color=WHITE,
                bold=True, always_release=True)
    content.add_widget(ok)
    p = Popup(title=title, content=content,
              size_hint=(0.88, 0.42),
              title_color=PURPLE,
              separator_color=PINK,
              title_size=sp(16),
              background_color=DARK)
    def _dismiss(x):
        p.dismiss()
        if on_dismiss:
            on_dismiss()
    ok.bind(on_press=_dismiss)
    p.open()


def header_bar(title, back_screen=None, right_text=None, right_action=None):
    bar = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(8), dp(8)])
    bg(bar, DARK)
    if back_screen:
        b = Button(text="< Back", size_hint_x=None, width=dp(80),
                   background_color=(0, 0, 0, 0), color=PURPLE,
                   font_size=sp(14), bold=True, always_release=True)
        b.bind(on_press=lambda x: setattr(
            App.get_running_app().root, 'current', back_screen))
        bar.add_widget(b)
    else:
        bar.add_widget(Label(size_hint_x=None, width=dp(80)))
    bar.add_widget(lbl(title, size=17, bold=True, color=WHITE,
                        halign='center', height=44))
    if right_text and right_action:
        r = Button(text=right_text, size_hint_x=None, width=dp(80),
                   background_color=(0, 0, 0, 0), color=PINK,
                   font_size=sp(13), bold=True, always_release=True)
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
                         height=dp(130), padding=[dp(16), dp(12)])
        bg(hero, DARK)
        hero.add_widget(lbl("FREQUENCY", size=26, bold=True,
                             color=PURPLE, halign='center', height=44))
        hero.add_widget(lbl("CAFE & BAKERY", size=14, bold=True,
                             color=PINK, halign='center', height=26))
        hero.add_widget(lbl("Fresh baked. Always on point.", size=12,
                             color=GREY_TEXT, halign='center', height=22))

        # Accent line
        accent = BoxLayout(size_hint_y=None, height=dp(3))
        bg(accent, PURPLE)
        hero.add_widget(accent)
        root.add_widget(hero)

        # Menu label
        root.add_widget(lbl("  What are you craving?", size=14, bold=True,
                             color=ORANGE, height=38))

        # Menu cards
        scroll = make_scroll()
        sbox = BoxLayout(orientation='vertical',
                         padding=[dp(12), dp(6)],
                         spacing=dp(10), size_hint_y=None)
        sbox.bind(minimum_height=sbox.setter('height'))

        card_colors = [PURPLE, PINK, TEAL]
        icons = ["🧁", "🍪", "🥐"]
        subtitles = [
            "5 flavours • Single or bulk orders",
            "Bulk orders only • 4 size options",
            "Bulk orders only • 4 size options"
        ]

        for i, (item, data) in enumerate(MENU.items()):
            card = BoxLayout(orientation='vertical',
                             size_hint_y=None, height=dp(80),
                             padding=[dp(16), dp(10)])
            bg(card, card_colors[i % 3])

            top = BoxLayout(size_hint_y=0.55)
            top.add_widget(lbl(f"{icons[i]}  {item}", size=16, bold=True,
                                color=WHITE, height=32))
            card.add_widget(top)
            card.add_widget(lbl(subtitles[i], size=11,
                                 color=OFF_WHITE, height=20))

            btn = Button(background_color=(0, 0, 0, 0),
                         size_hint=(1, 1), always_release=True)
            btn.bind(on_press=lambda x, n=item: self.go_order(n))

            from kivy.uix.floatlayout import FloatLayout
            fl = FloatLayout(size_hint_y=None, height=dp(80))
            card.size_hint = (1, 1)
            card.pos_hint = {'x': 0, 'y': 0}
            btn.size_hint = (1, 1)
            btn.pos_hint = {'x': 0, 'y': 0}
            fl.add_widget(card)
            fl.add_widget(btn)
            sbox.add_widget(fl)

        scroll.add_widget(sbox)
        root.add_widget(scroll)

        # Bottom nav
        nav = BoxLayout(size_hint_y=None, height=dp(56),
                        spacing=dp(2), padding=[dp(4), dp(4)])
        bg(nav, DARK)

        nav_items = [
            ("My Orders", "order_history", PURPLE),
            ("About Us", "about", PINK),
            ("Owner", "owner_login", GREY_LIGHT),
        ]
        for label, screen, color in nav_items:
            btn = Button(text=label, background_color=color,
                         color=WHITE, font_size=sp(12),
                         bold=True, always_release=True)
            btn.bind(on_press=lambda x, s=screen: setattr(
                self.manager, 'current', s))
            nav.add_widget(btn)

        root.add_widget(nav)
        self.add_widget(root)

    def go_order(self, item):
        self.manager.get_screen('order').set_item(item)
        self.manager.current = 'order'


# ════════════════════════════════════════════════════════════
#  SCREEN 2 — ORDER
# ════════════════════════════════════════════════════════════
class OrderScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_item = "Muffins"
        self.order_type = "unit"
        self.total = 0

        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header_bar("Place Your Order", back_screen='home'))

        scroll = make_scroll()
        self.form = BoxLayout(orientation='vertical',
                              padding=[dp(16), dp(12)],
                              spacing=dp(10), size_hint_y=None)
        self.form.bind(minimum_height=self.form.setter('height'))

        self.item_lbl = lbl("", size=18, bold=True,
                             color=PURPLE, halign='center', height=44)
        self.form.add_widget(self.item_lbl)

        # Order type toggle
        type_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        self.unit_btn = Button(text="Single Units", background_color=PURPLE,
                               color=WHITE, bold=True, font_size=sp(13),
                               always_release=True)
        self.bulk_btn = Button(text="Bulk Order", background_color=GREY_LIGHT,
                               color=WHITE, bold=True, font_size=sp(13),
                               always_release=True)
        self.unit_btn.bind(on_press=lambda x: self.set_order_type("unit"))
        self.bulk_btn.bind(on_press=lambda x: self.set_order_type("bulk"))
        type_row.add_widget(self.unit_btn)
        type_row.add_widget(self.bulk_btn)
        self.form.add_widget(type_row)

        # Unit order section
        self.unit_section = BoxLayout(orientation='vertical',
                                      size_hint_y=None, height=dp(160),
                                      spacing=dp(8))
        self.unit_section.add_widget(lbl("Flavour:", size=13, bold=True,
                                          color=ORANGE, height=28))
        self.flavour_spinner = Spinner(
            text="Vanilla",
            values=MUFFIN_FLAVOURS,
            background_color=PURPLE, color=WHITE,
            font_size=sp(14), size_hint_y=None, height=dp(52)
        )
        self.unit_section.add_widget(self.flavour_spinner)
        self.unit_section.add_widget(lbl("Quantity:", size=13, bold=True,
                                          color=ORANGE, height=28))
        self.qty_input = inp("How many? e.g. 2", filter="int")
        self.unit_section.add_widget(self.qty_input)
        self.form.add_widget(self.unit_section)

        # Bulk order section
        self.bulk_section = BoxLayout(orientation='vertical',
                                      size_hint_y=None, height=dp(100),
                                      spacing=dp(8))
        self.bulk_section.add_widget(lbl("Bulk Size:", size=13, bold=True,
                                          color=ORANGE, height=28))
        self.bulk_spinner = Spinner(
            text="2L — R180",
            values=["2L — R180", "5L — R350", "10L — R390", "20L — R450"],
            background_color=PINK, color=WHITE,
            font_size=sp(14), size_hint_y=None, height=dp(52)
        )
        self.bulk_section.add_widget(self.bulk_spinner)
        self.form.add_widget(self.bulk_section)
        self.bulk_section.opacity = 0
        self.bulk_section.size_hint_y = None
        self.bulk_section.height = 0

        # Customer details
        self.form.add_widget(lbl("Your Details:", size=14, bold=True,
                                  color=TEAL, height=32))
        self.name_input    = inp("Your full name")
        self.phone_input   = inp("Your phone number")
        self.form.add_widget(self.name_input)
        self.form.add_widget(self.phone_input)

        # Delivery or collection
        self.form.add_widget(lbl("Delivery or Collection?", size=13,
                                  bold=True, color=ORANGE, height=28))
        dc_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        self.delivery_btn = Button(text="Delivery", background_color=TEAL,
                                   color=WHITE, bold=True, font_size=sp(13),
                                   always_release=True)
        self.collection_btn = Button(text="Collection", background_color=GREY_LIGHT,
                                     color=WHITE, bold=True, font_size=sp(13),
                                     always_release=True)
        self.delivery_choice = "Collection"
        self.delivery_btn.bind(on_press=lambda x: self.set_delivery("Delivery"))
        self.collection_btn.bind(on_press=lambda x: self.set_delivery("Collection"))
        dc_row.add_widget(self.delivery_btn)
        dc_row.add_widget(self.collection_btn)
        self.form.add_widget(dc_row)

        self.address_input = inp("Delivery address (if delivery)")
        self.form.add_widget(self.address_input)

        self.form.add_widget(lbl("Special Instructions:", size=13,
                                  bold=True, color=ORANGE, height=28))
        self.notes_input = TextInput(
            hint_text="Any special requests? (optional)",
            background_color=GREY_LIGHT,
            foreground_color=WHITE,
            hint_text_color=GREY_TEXT,
            font_size=sp(14), padding=[dp(12), dp(10)],
            size_hint_y=None, height=dp(80)
        )
        self.form.add_widget(self.notes_input)
        self.form.add_widget(BoxLayout(size_hint_y=None, height=dp(10)))
        self.form.add_widget(action_btn("PLACE ORDER", GREEN_OK,
                                         self.submit_order, height=58))
        self.form.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))

        scroll.add_widget(self.form)
        root.add_widget(scroll)
        self.add_widget(root)

    def set_item(self, item):
        self.selected_item = item
        data = MENU[item]
        self.item_lbl.text = f"{data['emoji']}  {item}"

        if data['type'] == 'bulk_only':
            self.set_order_type("bulk")
            self.unit_btn.disabled = True
            self.unit_btn.background_color = GREY_LIGHT
        else:
            self.unit_btn.disabled = False
            self.set_order_type("unit")

        # Update bulk prices
        bulk_data = data['bulk']
        self.bulk_spinner.values = [f"{k} — R{v}" for k, v in bulk_data.items()]
        self.bulk_spinner.text = self.bulk_spinner.values[0]

        # Update flavours
        if data['flavours']:
            self.flavour_spinner.values = data['flavours']
            self.flavour_spinner.text = data['flavours'][0]

    def set_order_type(self, order_type):
        self.order_type = order_type
        if order_type == "unit":
            self.unit_btn.background_color = PURPLE
            self.bulk_btn.background_color = GREY_LIGHT
            self.unit_section.opacity = 1
            self.unit_section.height = dp(160)
            self.bulk_section.opacity = 0
            self.bulk_section.height = 0
        else:
            self.bulk_btn.background_color = PINK
            self.unit_btn.background_color = GREY_LIGHT
            self.bulk_section.opacity = 1
            self.bulk_section.height = dp(100)
            self.unit_section.opacity = 0
            self.unit_section.height = 0

    def set_delivery(self, choice):
        self.delivery_choice = choice
        if choice == "Delivery":
            self.delivery_btn.background_color = TEAL
            self.collection_btn.background_color = GREY_LIGHT
        else:
            self.collection_btn.background_color = TEAL
            self.delivery_btn.background_color = GREY_LIGHT

    def submit_order(self, instance):
        name  = self.name_input.text.strip()
        phone = self.phone_input.text.strip()

        if not (name and phone):
            show_popup("Missing Info", "Please enter your name and phone number.", btn_color=RED)
            return

        if self.order_type == "unit":
            qty = self.qty_input.text.strip()
            if not qty or int(qty) < 1:
                show_popup("Missing Info", "Please enter a quantity.", btn_color=RED)
                return
            flavour = self.flavour_spinner.text
            size    = f"{qty} units"
            price   = int(qty) * MENU[self.selected_item].get('unit_price', 0)
            detail  = f"{qty}x {flavour} {self.selected_item}"
        else:
            bulk_val = self.bulk_spinner.text
            size     = bulk_val.split(" — ")[0]
            price    = int(bulk_val.split("R")[1])
            flavour  = "N/A"
            detail   = f"{size} {self.selected_item}"

        address = self.address_input.text.strip() or "Collection"
        notes   = self.notes_input.text.strip()
        now     = datetime.now().isoformat()

        app = App.get_running_app()
        app.cursor.execute("""
            INSERT INTO orders
            (customer_name, phone, item, flavour, size, price,
             delivery_type, address, notes, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
        """, (name, phone, self.selected_item, flavour, size,
              price, self.delivery_choice, address, notes, now))
        app.conn.commit()

        self.name_input.text    = ""
        self.phone_input.text   = ""
        self.qty_input.text     = ""
        self.address_input.text = ""
        self.notes_input.text   = ""

        show_popup(
            "Order Placed!",
            f"Thank you {name}!\n\n{detail}\nTotal: R{price}\n\n"
            f"{self.delivery_choice} confirmed!\nWe'll be in touch shortly.",
            btn_color=GREEN_OK,
            on_dismiss=lambda: setattr(self.manager, 'current', 'home')
        )


# ════════════════════════════════════════════════════════════
#  SCREEN 3 — ORDER HISTORY (Customer)
# ════════════════════════════════════════════════════════════
class OrderHistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header_bar("My Orders", back_screen='home'))

        # Search by phone
        search_box = BoxLayout(size_hint_y=None, height=dp(60),
                               padding=[dp(12), dp(8)], spacing=dp(8))
        bg(search_box, DARK)
        self.phone_search = inp("Enter your phone number to find orders")
        search_btn = Button(text="Find", size_hint_x=None, width=dp(80),
                            background_color=PURPLE, color=WHITE,
                            bold=True, font_size=sp(14), always_release=True)
        search_btn.bind(on_press=self.search_orders)
        search_box.add_widget(self.phone_search)
        search_box.add_widget(search_btn)
        root.add_widget(search_box)

        scroll = make_scroll()
        self.orders_box = BoxLayout(orientation='vertical',
                                    padding=[dp(10), dp(8)],
                                    spacing=dp(8), size_hint_y=None)
        self.orders_box.bind(minimum_height=self.orders_box.setter('height'))
        self.orders_box.add_widget(
            lbl("Enter your phone number above\nto view your orders.",
                halign='center', color=GREY_TEXT, height=80))
        scroll.add_widget(self.orders_box)
        root.add_widget(scroll)
        self.add_widget(root)

    def search_orders(self, instance):
        phone = self.phone_search.text.strip()
        if not phone:
            show_popup("Oops", "Please enter your phone number.", btn_color=RED)
            return
        app = App.get_running_app()
        app.cursor.execute("""
            SELECT item, flavour, size, price, delivery_type, status, created_at
            FROM orders WHERE phone=? ORDER BY created_at DESC
        """, (phone,))
        orders = app.cursor.fetchall()
        self.orders_box.clear_widgets()
        if not orders:
            self.orders_box.add_widget(
                lbl("No orders found for this number.",
                    halign='center', color=GREY_TEXT, height=60))
            return
        for item, flavour, size, price, delivery, status, created in orders:
            card = BoxLayout(orientation='vertical',
                             size_hint_y=None, height=dp(110),
                             padding=[dp(12), dp(10)], spacing=dp(4))
            bg(card, GREY_LIGHT)
            status_colors = {"Pending": ORANGE, "Confirmed": PURPLE,
                             "Completed": GREEN_OK, "Cancelled": RED}
            s_color = status_colors.get(status, WHITE)
            top = BoxLayout(size_hint_y=None, height=dp(28))
            top.add_widget(lbl(f"{item}", size=15, bold=True,
                                color=PURPLE, height=28))
            sl = Label(text=status, color=s_color, bold=True,
                       font_size=sp(12), size_hint_x=None, width=dp(90),
                       halign='right', valign='middle')
            sl.bind(size=sl.setter('text_size'))
            top.add_widget(sl)
            card.add_widget(top)
            desc = f"{size}" if flavour == "N/A" else f"{size} — {flavour}"
            card.add_widget(lbl(desc, size=12, color=WHITE, height=22))
            card.add_widget(lbl(f"Total: R{price}   {delivery}",
                                 size=12, color=ORANGE, height=22))
            date_str = created[:10] if created else ""
            card.add_widget(lbl(f"Ordered: {date_str}", size=11,
                                 color=GREY_TEXT, height=18))
            self.orders_box.add_widget(card)


# ════════════════════════════════════════════════════════════
#  SCREEN 4 — ABOUT
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
        content.add_widget(lbl("FREQUENCY CAFE", size=20, bold=True,
                                color=PURPLE, halign='center', height=44))
        content.add_widget(lbl("& BAKERY", size=14, bold=True,
                                color=PINK, halign='center', height=28))

        about = Label(
            text=(
                "At Frequency Cafe, we believe great food should hit different.\n\n"
                "We are a modern bakery and cafe dedicated to crafting fresh, "
                "flavourful baked goods that keep you coming back for more.\n\n"
                "From our signature muffins in 5 incredible flavours to our "
                "perfectly baked scones and biscuits — everything is made fresh "
                "with quality ingredients and plenty of love.\n\n"
                "Order single units or go big with our bulk options — "
                "perfect for events, offices, and celebrations."
            ),
            color=WHITE, font_size=sp(14),
            halign='left', valign='top', size_hint_y=None
        )
        about.bind(texture_size=lambda i, v: setattr(i, 'height', v[1]))
        about.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        content.add_widget(about)

        content.add_widget(lbl("Our Menu", size=16, bold=True,
                                color=ORANGE, halign='center', height=36))

        for item, data in MENU.items():
            card = BoxLayout(size_hint_y=None, height=dp(52),
                             padding=[dp(12), dp(8)])
            bg(card, GREY_LIGHT)
            card.add_widget(lbl(f"{data['emoji']}  {item}", size=14,
                                 bold=True, color=WHITE, height=36))
            bulk_str = " | ".join([f"{k}: R{v}" for k, v in data['bulk'].items()])
            card.add_widget(lbl(bulk_str, size=10, color=GREY_TEXT, height=36))
            content.add_widget(card)
            content.add_widget(BoxLayout(size_hint_y=None, height=dp(4)))

        content.add_widget(action_btn(
            "Order Now", PURPLE,
            lambda x: setattr(self.manager, 'current', 'home'),
            height=54
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
        root.add_widget(Label(size_hint_y=0.15))
        card = BoxLayout(orientation='vertical',
                         padding=[dp(24), dp(20)], spacing=dp(14),
                         size_hint=(0.90, None), height=dp(240),
                         pos_hint={'center_x': 0.5})
        bg(card, GREY_LIGHT)
        card.add_widget(lbl("Owner Access", size=16, bold=True,
                             color=PURPLE, halign='center', height=36))
        self.pin_input = inp("Enter PIN", password=True)
        card.add_widget(self.pin_input)
        card.add_widget(action_btn("LOGIN", PURPLE, self.check_pin, height=54))
        root.add_widget(card)
        root.add_widget(Label())
        self.add_widget(root)

    def check_pin(self, instance):
        if self.pin_input.text == OWNER_PIN:
            self.pin_input.text = ""
            self.manager.current = 'owner_dashboard'
        else:
            self.pin_input.text = ""
            show_popup("Access Denied", "Incorrect PIN.", btn_color=RED)


# ════════════════════════════════════════════════════════════
#  SCREEN 6 — OWNER DASHBOARD
# ════════════════════════════════════════════════════════════
class OwnerDashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_filter = "All"
        self.current_tab = "orders"
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header_bar(
            "Dashboard",
            right_text="Logout",
            right_action=lambda x: setattr(self.manager, 'current', 'home')
        ))

        # Tab switcher
        tabs = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(2))
        bg(tabs, DARK)
        self.orders_tab = Button(text="Orders", background_color=PURPLE,
                                  color=WHITE, bold=True, font_size=sp(14),
                                  always_release=True)
        self.inventory_tab = Button(text="Inventory", background_color=GREY_LIGHT,
                                     color=WHITE, bold=True, font_size=sp(14),
                                     always_release=True)
        self.orders_tab.bind(on_press=lambda x: self.switch_tab("orders"))
        self.inventory_tab.bind(on_press=lambda x: self.switch_tab("inventory"))
        tabs.add_widget(self.orders_tab)
        tabs.add_widget(self.inventory_tab)
        root.add_widget(tabs)

        # Stats
        self.stats_bar = BoxLayout(size_hint_y=None, height=dp(70),
                                   padding=[dp(8), dp(8)], spacing=dp(4))
        bg(self.stats_bar, GREY_LIGHT)
        root.add_widget(self.stats_bar)

        # Filter row
        filter_row = BoxLayout(size_hint_y=None, height=dp(44),
                               spacing=dp(3), padding=[dp(6), dp(4)])
        bg(filter_row, DARK)
        self.filter_btns = {}
        for status in ["All", "Pending", "Confirmed", "Completed", "Cancelled"]:
            btn = Button(text=status, font_size=sp(11), bold=True,
                         background_color=PURPLE if status == "All" else GREY_LIGHT,
                         color=WHITE, always_release=True)
            btn.bind(on_press=lambda x, s=status: self.filter_orders(s))
            self.filter_btns[status] = btn
            filter_row.add_widget(btn)
        root.add_widget(filter_row)

        # Content area
        self.scroll = make_scroll()
        self.content_box = BoxLayout(orientation='vertical',
                                     padding=[dp(10), dp(8)],
                                     spacing=dp(8), size_hint_y=None)
        self.content_box.bind(minimum_height=self.content_box.setter('height'))
        self.scroll.add_widget(self.content_box)
        root.add_widget(self.scroll)

        self.add_widget(root)

    def on_enter(self):
        self.switch_tab("orders")

    def switch_tab(self, tab):
        self.current_tab = tab
        if tab == "orders":
            self.orders_tab.background_color = PURPLE
            self.inventory_tab.background_color = GREY_LIGHT
            self.filter_orders("All")
        else:
            self.inventory_tab.background_color = PINK
            self.orders_tab.background_color = GREY_LIGHT
            self.show_inventory()

    def _update_stats(self):
        try:
            app = App.get_running_app()
            self.stats_bar.clear_widgets()
            for label, query, color in [
                ("Total",     "SELECT COUNT(*) FROM orders", WHITE),
                ("Pending",   "SELECT COUNT(*) FROM orders WHERE status='Pending'", ORANGE),
                ("Confirmed", "SELECT COUNT(*) FROM orders WHERE status='Confirmed'", PURPLE),
                ("Completed", "SELECT COUNT(*) FROM orders WHERE status='Completed'", GREEN_OK),
            ]:
                app.cursor.execute(query)
                count = app.cursor.fetchone()[0]
                box = BoxLayout(orientation='vertical')
                box.add_widget(lbl(str(count), size=20, bold=True,
                                    color=color, halign='center', height=32))
                box.add_widget(lbl(label, size=10, color=GREY_TEXT,
                                    halign='center', height=20))
                self.stats_bar.add_widget(box)
        except Exception as e:
            print(f"Stats error: {e}")

    def filter_orders(self, status):
        self.current_filter = status
        for s, btn in self.filter_btns.items():
            btn.background_color = PURPLE if s == status else GREY_LIGHT

        app = App.get_running_app()
        if status == "All":
            app.cursor.execute("""
                SELECT id, customer_name, phone, item, flavour, size,
                       price, delivery_type, address, notes, status
                FROM orders ORDER BY created_at DESC
            """)
        else:
            app.cursor.execute("""
                SELECT id, customer_name, phone, item, flavour, size,
                       price, delivery_type, address, notes, status
                FROM orders WHERE status=? ORDER BY created_at DESC
            """, (status,))

        orders = app.cursor.fetchall()
        self.content_box.clear_widgets()
        self._update_stats()

        if not orders:
            self.content_box.add_widget(
                lbl(f"No {status.lower()} orders.",
                    halign='center', color=GREY_TEXT, height=60))
            return

        for order in orders:
            self.content_box.add_widget(self._order_card(order))

    def _order_card(self, order):
        oid, name, phone, item, flavour, size, price, delivery, address, notes, status = order
        status_colors = {"Pending": ORANGE, "Confirmed": PURPLE,
                         "Completed": GREEN_OK, "Cancelled": RED}
        s_color = status_colors.get(status, WHITE)

        c = BoxLayout(orientation='vertical', padding=[dp(12), dp(10)],
                      spacing=dp(4), size_hint_y=None, height=dp(200))
        bg(c, GREY_LIGHT)

        top = BoxLayout(size_hint_y=None, height=dp(30))
        top.add_widget(lbl(name, size=15, bold=True, color=PURPLE, height=30))
        sl = Label(text=status, color=s_color, bold=True, font_size=sp(12),
                   size_hint_x=None, width=dp(90), halign='right', valign='middle')
        sl.bind(size=sl.setter('text_size'))
        top.add_widget(sl)
        c.add_widget(top)

        desc = f"{size} {item}" if flavour == "N/A" else f"{size} {flavour} {item}"
        c.add_widget(lbl(f"Order: {desc}", size=13, color=WHITE, height=22))
        c.add_widget(lbl(f"Total: R{price}   {delivery}", size=13,
                          color=ORANGE, height=22))
        c.add_widget(lbl(f"Phone: {phone}", size=12, color=WHITE, height=20))
        if address and address != "Collection":
            c.add_widget(lbl(f"Address: {address}", size=12,
                              color=WHITE, height=20))
        if notes:
            c.add_widget(lbl(f"Notes: {notes}", size=11,
                              color=GREY_TEXT, height=18))

        btn_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        for label, new_status, color in [
            ("Confirm",  "Confirmed", PURPLE),
            ("Complete", "Completed", GREEN_OK),
            ("Cancel",   "Cancelled", RED),
        ]:
            btn = Button(text=label, background_color=color, color=WHITE,
                         font_size=sp(12), bold=True, always_release=True)
            btn.bind(on_press=lambda x, i=oid, s=new_status:
                     self.update_status(i, s))
            btn_row.add_widget(btn)
        c.add_widget(btn_row)
        return c

    def update_status(self, order_id, new_status):
        app = App.get_running_app()
        app.cursor.execute("UPDATE orders SET status=? WHERE id=?",
                           (new_status, order_id))
        app.conn.commit()
        self.filter_orders(self.current_filter)

    def show_inventory(self):
        self.content_box.clear_widgets()
        self._update_stats()
        app = App.get_running_app()

        self.content_box.add_widget(lbl("Stock Inventory", size=16, bold=True,
                                         color=PINK, halign='center', height=36))

        app.cursor.execute("SELECT item, flavour, quantity, updated_at FROM inventory ORDER BY item")
        items = app.cursor.fetchall()

        if not items:
            self.content_box.add_widget(
                lbl("No inventory yet.\nAdd stock below.", halign='center',
                    color=GREY_TEXT, height=60))
        else:
            for item, flavour, qty, updated in items:
                card = BoxLayout(size_hint_y=None, height=dp(54),
                                 padding=[dp(12), dp(8)])
                bg(card, GREY_LIGHT)
                warn_color = RED if qty <= 5 else GREEN_OK
                label_text = f"{item}" if flavour == "N/A" else f"{item} — {flavour}"
                card.add_widget(lbl(label_text, size=13, bold=True,
                                     color=WHITE, height=36))
                qty_lbl = Label(text=f"{qty} units", color=warn_color,
                                bold=True, font_size=sp(14),
                                size_hint_x=None, width=dp(90),
                                halign='right', valign='middle')
                qty_lbl.bind(size=qty_lbl.setter('text_size'))
                card.add_widget(qty_lbl)
                self.content_box.add_widget(card)
                self.content_box.add_widget(
                    BoxLayout(size_hint_y=None, height=dp(3)))

        # Add stock form
        self.content_box.add_widget(BoxLayout(size_hint_y=None, height=dp(10)))
        self.content_box.add_widget(lbl("Add / Update Stock", size=14,
                                         bold=True, color=TEAL, height=32))

        self.inv_item_spinner = Spinner(
            text="Muffins",
            values=list(MENU.keys()),
            background_color=PURPLE, color=WHITE,
            font_size=sp(14), size_hint_y=None, height=dp(50)
        )
        self.inv_flavour_spinner = Spinner(
            text="Vanilla",
            values=MUFFIN_FLAVOURS + ["N/A"],
            background_color=GREY_LIGHT, color=WHITE,
            font_size=sp(14), size_hint_y=None, height=dp(50)
        )
        self.inv_qty_input = inp("Quantity to add", filter="int")

        self.content_box.add_widget(lbl("Item:", size=12, color=GREY_TEXT, height=24))
        self.content_box.add_widget(self.inv_item_spinner)
        self.content_box.add_widget(lbl("Flavour (N/A if not applicable):",
                                         size=12, color=GREY_TEXT, height=24))
        self.content_box.add_widget(self.inv_flavour_spinner)
        self.content_box.add_widget(lbl("Quantity:", size=12,
                                         color=GREY_TEXT, height=24))
        self.content_box.add_widget(self.inv_qty_input)
        self.content_box.add_widget(
            action_btn("ADD TO STOCK", TEAL, self.add_inventory, height=52))
        self.content_box.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))

    def add_inventory(self, instance):
        item    = self.inv_item_spinner.text
        flavour = self.inv_flavour_spinner.text
        qty     = self.inv_qty_input.text.strip()

        if not qty or not qty.isdigit():
            show_popup("Oops", "Please enter a valid quantity.", btn_color=RED)
            return

        app = App.get_running_app()
        app.cursor.execute(
            "SELECT id, quantity FROM inventory WHERE item=? AND flavour=?",
            (item, flavour))
        existing = app.cursor.fetchone()

        if existing:
            new_qty = existing[1] + int(qty)
            app.cursor.execute(
                "UPDATE inventory SET quantity=?, updated_at=? WHERE id=?",
                (new_qty, datetime.now().isoformat(), existing[0]))
        else:
            app.cursor.execute("""
                INSERT INTO inventory (item, flavour, quantity, updated_at)
                VALUES (?, ?, ?, ?)
            """, (item, flavour, int(qty), datetime.now().isoformat()))

        app.conn.commit()
        self.inv_qty_input.text = ""
        show_popup("Stock Updated", f"{qty} {flavour} {item} added to stock!",
                   btn_color=TEAL, on_dismiss=lambda: self.show_inventory())


# ════════════════════════════════════════════════════════════
#  MAIN APP
# ════════════════════════════════════════════════════════════
class FrequencyCafeApp(App):
    def build(self):
        self.title = "Frequency Cafe"
        self._setup_db()
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(OrderScreen(name='order'))
        sm.add_widget(OrderHistoryScreen(name='order_history'))
        sm.add_widget(AboutScreen(name='about'))
        sm.add_widget(OwnerLoginScreen(name='owner_login'))
        sm.add_widget(OwnerDashboardScreen(name='owner_dashboard'))
        return sm

    def _setup_db(self):
        data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(data_dir, exist_ok=True)
        self.conn = sqlite3.connect(os.path.join(data_dir, "frequency.db"))
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                item TEXT NOT NULL,
                flavour TEXT DEFAULT 'N/A',
                size TEXT NOT NULL,
                price REAL NOT NULL,
                delivery_type TEXT DEFAULT 'Collection',
                address TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                status TEXT DEFAULT 'Pending',
                created_at TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                flavour TEXT DEFAULT 'N/A',
                quantity INTEGER DEFAULT 0,
                updated_at TEXT
            )
        """)
        self.conn.commit()


if __name__ == "__main__":
    FrequencyCafeApp().run()

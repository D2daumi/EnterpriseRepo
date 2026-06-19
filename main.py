import os
import sqlite3
import json
import random
import math
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.metrics import dp, sp
from kivy.clock import Clock

# ═══════════════════════════════════════════════
#  BRAND COLORS
# ═══════════════════════════════════════════════
BLACK      = (0.05, 0.05, 0.05, 1)
MAROON     = (0.28, 0.04, 0.04, 1)
GOLD       = (0.85, 0.68, 0.10, 1)
GOLD_LIGHT = (0.96, 0.91, 0.70, 1)
GOLD_DARK  = (0.60, 0.47, 0.06, 1)
WHITE      = (1.00, 1.00, 1.00, 1)
GREY_TEXT  = (0.40, 0.42, 0.46, 1)
GREY_LIGHT = (0.93, 0.94, 0.96, 1)
GREY_CARD  = (0.97, 0.97, 0.98, 1)
GREEN      = (0.10, 0.65, 0.35, 1)
GREEN_LIGHT= (0.88, 0.97, 0.91, 1)
RED        = (0.85, 0.18, 0.18, 1)
ORANGE     = (0.95, 0.56, 0.10, 1)
BLUE       = (0.12, 0.46, 0.90, 1)
BG         = (0.96, 0.96, 0.98, 1)

APP_NAME     = "Spana Black Express"
OWNER_PIN    = "1234"
VERSION      = "2.1"
DELIVERY_FEE = 15

# 8 order steps
ORDER_STEPS = [
    (0,  "📋", "Order Placed",       BLACK),
    (1,  "✅", "Order Accepted",      GREEN),
    (2,  "🏍", "Driver Assigned",     GOLD),
    (3,  "🛒", "Driver at Shop",      ORANGE),
    (4,  "📦", "Order Collected",     ORANGE),
    (5,  "🚀", "En Route to You",     BLUE),
    (6,  "📍", "Driver Nearby",       MAROON),
    (7,  "🎉", "Delivered",           GREEN),
]

# Driver registry — online/busy state stored in app
DRIVERS = [
    {"id": 1, "name": "Sipho M.",  "bike": "Honda Wave #1", "phone": "0712345678", "rating": 4.9, "trips": 342},
    {"id": 2, "name": "Thabo K.", "bike": "Yamaha #2",     "phone": "0723456789", "rating": 4.7, "trips": 218},
]

SHOPS = [
    {"id": 1, "name": "EGkota General Store", "icon": "🛒",
     "category": "General", "rating": 4.8, "time": "15-25 min",
     "items": [
        {"id": 1, "name": "Bread (700g)",        "price": 18},
        {"id": 2, "name": "Milk (1L)",            "price": 22},
        {"id": 3, "name": "Eggs (6 pack)",        "price": 30},
        {"id": 4, "name": "Cooldrink (2L)",       "price": 28},
        {"id": 5, "name": "Washing Powder",       "price": 55},
        {"id": 6, "name": "Rice (2kg)",           "price": 42},
        {"id": 7, "name": "Cooking Oil (750ml)",  "price": 38},
        {"id": 8, "name": "Sugar (1kg)",          "price": 24},
     ]},
    {"id": 2, "name": "Mama's Vegy Shop", "icon": "🥦",
     "category": "Fresh Produce", "rating": 4.9, "time": "10-20 min",
     "items": [
        {"id": 9,  "name": "Tomatoes (1kg)",     "price": 20},
        {"id": 10, "name": "Onions (1kg)",        "price": 15},
        {"id": 11, "name": "Spinach (bunch)",     "price": 12},
        {"id": 12, "name": "Potatoes (2kg)",      "price": 35},
        {"id": 13, "name": "Carrots (500g)",      "price": 14},
        {"id": 14, "name": "Cabbage (head)",      "price": 18},
        {"id": 15, "name": "Green Pepper (3pk)",  "price": 16},
        {"id": 16, "name": "Sweet Potato (1kg)",  "price": 22},
     ]},
]

# ═══════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════
def bg(widget, color):
    with widget.canvas.before:
        Color(*color)
        rect = Rectangle(size=widget.size, pos=widget.pos)
    widget.bind(size=lambda i, v: setattr(rect, 'size', v))
    widget.bind(pos=lambda i, v: setattr(rect, 'pos', v))

def lbl(text, size=15, bold=False, color=GREY_TEXT,
        halign='left', valign='middle', height=None):
    h = height or dp(36)
    l = Label(text=text, font_size=sp(size), bold=bold, color=color,
              halign=halign, valign=valign, size_hint_y=None, height=h)
    l.bind(size=l.setter('text_size'))
    return l

def inp(hint, password=False, input_filter=None):
    t = TextInput(
        hint_text=hint, multiline=False, background_color=WHITE,
        foreground_color=(0.1,0.1,0.15,1), hint_text_color=(0.65,0.67,0.72,1),
        cursor_color=GOLD_DARK, font_size=sp(15),
        padding=[dp(14),dp(14)], password=password,
        size_hint_y=None, height=dp(52))
    if input_filter:
        t.input_filter = input_filter
    return t

def make_scroll():
    return ScrollView(scroll_type=['bars','content'], bar_width=dp(3),
                      bar_color=GOLD, bar_inactive_color=GREY_LIGHT)

def btn(text, color=BLACK, text_color=WHITE, on_press=None,
        height=None, font_size=15, bold=True):
    h = height or dp(52)
    b = Button(text=text, background_color=color, color=text_color,
               bold=bold, font_size=sp(font_size), size_hint_y=None,
               height=h, always_release=True, halign='center', valign='middle')
    b.bind(size=lambda i, v: setattr(b, 'text_size', (b.width-dp(8), b.height)))
    if on_press:
        b.bind(on_press=on_press)
    return b

def divider():
    d = BoxLayout(size_hint_y=None, height=dp(1))
    bg(d, GREY_LIGHT)
    return d

def show_popup(title, msg, color=None, on_ok=None):
    color = color or BLACK
    box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
    l = Label(text=msg, color=GREY_TEXT, halign='center', valign='middle', font_size=sp(14))
    l.bind(size=l.setter('text_size'))
    box.add_widget(l)
    ok = btn("OK", color, on_press=lambda x: (p.dismiss(), on_ok() if on_ok else None))
    box.add_widget(ok)
    p = Popup(title=title, content=box, size_hint=(0.88,0.44),
              title_color=BLACK, separator_color=GOLD, title_size=sp(16))
    p.open()

def header(title, back=None, right_text=None, right_cb=None):
    bar = BoxLayout(size_hint_y=None, height=dp(62), padding=[dp(6),dp(8)])
    bg(bar, BLACK)
    if back:
        b = btn("< Back", (0,0,0,0), GOLD, font_size=14, height=dp(46),
                on_press=lambda x: setattr(App.get_running_app().root,'current',back))
        b.size_hint_x = None; b.width = dp(80)
        bar.add_widget(b)
    else:
        bar.add_widget(Label(size_hint_x=None, width=dp(80)))
    bar.add_widget(lbl(title, size=17, bold=True, color=GOLD,
                       halign='center', height=dp(46)))
    if right_text and right_cb:
        r = btn(right_text, (0,0,0,0), GOLD, font_size=13, height=dp(46), on_press=right_cb)
        r.size_hint_x = None; r.width = dp(80)
        bar.add_widget(r)
    else:
        bar.add_widget(Label(size_hint_x=None, width=dp(80)))
    return bar

def step_info(idx):
    idx = max(0, min(idx, len(ORDER_STEPS)-1))
    return ORDER_STEPS[idx]

# ═══════════════════════════════════════════════
#  LIVE MAP
# ═══════════════════════════════════════════════
class LiveMap(BoxLayout):
    def __init__(self, moving=False, step=0, **kw):
        super().__init__(**kw)
        self.moving = moving
        self.step = step
        self.angle = 0
        self.pulse = 0
        self.size_hint_y = None
        self.height = dp(210)
        self.bind(size=self._draw, pos=self._draw)
        Clock.schedule_interval(self._tick, 0.05)

    def _draw(self, *a):
        self.canvas.clear()
        with self.canvas:
            Color(0.06,0.10,0.16,1)
            Rectangle(size=self.size, pos=self.pos)
            Color(0.12,0.18,0.26,1)
            for x in range(0, int(self.width), 50):
                Line(points=[self.x+x,self.y,self.x+x,self.y+self.height], width=1)
            for y in range(0, int(self.height), 50):
                Line(points=[self.x,self.y+y,self.x+self.width,self.y+y], width=1)
            Color(0.15,0.22,0.32,1)
            Line(points=[self.x+self.width*0.12, self.y+self.height*0.5,
                         self.x+self.width*0.88, self.y+self.height*0.5], width=10)
            sx = self.x + self.width*0.12
            sy = self.y + self.height*0.5
            Color(0.95,0.56,0.10,1)
            Ellipse(pos=(sx-13,sy-13), size=(26,26))
            Color(1,1,1,0.9)
            Ellipse(pos=(sx-5,sy-5), size=(10,10))
            dx = self.x + self.width*0.88
            dy = self.y + self.height*0.5
            Color(0.85,0.68,0.10,1)
            Ellipse(pos=(dx-13,dy-13), size=(26,26))
            Color(1,1,1,0.9)
            Ellipse(pos=(dx-5,dy-5), size=(10,10))
            progress = min(self.step/7.0, 1.0)
            drv_x = sx + (dx-sx)*progress
            drv_y = sy + math.sin(self.angle*3)*12
            if self.moving: self.angle += 0.05
            pr = 18 + math.sin(self.pulse)*5
            Color(0.28,0.04,0.04,0.3)
            Ellipse(pos=(drv_x-pr,drv_y-pr), size=(pr*2,pr*2))
            Color(0.85,0.68,0.10,1)
            Ellipse(pos=(drv_x-13,drv_y-13), size=(26,26))
            Color(0.05,0.05,0.05,1)
            Ellipse(pos=(drv_x-6,drv_y-6), size=(12,12))

    def _tick(self, dt):
        self.pulse += 0.12
        if self.moving: self._draw()

# ═══════════════════════════════════════════════
#  SPLASH
# ═══════════════════════════════════════════════
class SplashScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical')
        bg(root, BLACK)
        root.add_widget(Label(size_hint_y=0.12))
        logo = BoxLayout(orientation='vertical', size_hint_y=None,
                         height=dp(190), padding=[dp(20),dp(10)])
        logo.add_widget(lbl("🏍", size=54, halign='center', color=GOLD, height=dp(80)))
        logo.add_widget(lbl(APP_NAME, size=27, bold=True, color=GOLD,
                            halign='center', height=dp(48)))
        logo.add_widget(lbl("Work for the People  •  Express Delivery",
                            size=12, color=GOLD_LIGHT, halign='center', height=dp(28)))
        logo.add_widget(lbl(f"v{VERSION}", size=10, color=(0.35,0.37,0.42,1),
                            halign='center', height=dp(24)))
        root.add_widget(logo)
        root.add_widget(Label(size_hint_y=0.08))
        roles = BoxLayout(orientation='vertical', padding=[dp(24),dp(8)],
                          spacing=dp(12), size_hint_y=None)
        roles.bind(minimum_height=roles.setter('height'))
        roles.add_widget(lbl("Who are you?", size=14, bold=True,
                             color=GREY_TEXT, halign='center', height=dp(34)))
        for icon, label, screen, color, tc in [
            ("👤", "I'm a Customer",     "cust_home",  GOLD,  BLACK),
            ("🏢", "I'm the Dispatcher", "owner_login", MAROON,WHITE),
            ("🏍", "I'm a Driver",       "drv_login",  (0.14,0.14,0.16,1), GOLD),
        ]:
            roles.add_widget(btn(f"{icon}  {label}", color, tc, height=dp(60),
                on_press=lambda x,s=screen: setattr(
                    App.get_running_app().root,'current',s)))
        roles.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))
        sc = make_scroll()
        sc.add_widget(roles)
        root.add_widget(sc)
        self.add_widget(root)

# ═══════════════════════════════════════════════
#  CUSTOMER: HOME
# ═══════════════════════════════════════════════
class CustHomeScreen(Screen):
    def on_enter(self): self._build()
    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header("Order Now", back='splash',
                               right_text="History",
                               right_cb=lambda x: setattr(
                                   App.get_running_app().root,'current','cust_history')))
        sc = make_scroll()
        box = BoxLayout(orientation='vertical', padding=[dp(12),dp(8)],
                        spacing=dp(12), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        welcome = BoxLayout(size_hint_y=None, height=dp(70), padding=[dp(16),dp(12)])
        bg(welcome, BLACK)
        wb = BoxLayout(orientation='vertical')
        wb.add_widget(lbl("Good day! 👋", size=16, bold=True, color=GOLD, height=dp(28)))
        wb.add_widget(lbl("What can we deliver for you?", size=12, color=WHITE, height=dp(24)))
        welcome.add_widget(wb)
        box.add_widget(welcome)
        box.add_widget(lbl("🛒  Local Shops", size=14, bold=True, color=BLACK, height=dp(36)))
        for shop in SHOPS:
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(110),
                             padding=[dp(14),dp(12)])
            bg(card, WHITE)
            top = BoxLayout(size_hint_y=None, height=dp(34))
            top.add_widget(lbl(f"{shop['icon']}  {shop['name']}", size=15,
                               bold=True, color=BLACK, height=dp(34)))
            top.add_widget(lbl(f"⭐ {shop['rating']}", size=13, color=GOLD,
                               halign='right', height=dp(34)))
            card.add_widget(top)
            card.add_widget(lbl(f"🕐 {shop['time']}  •  {shop['category']}",
                               size=12, color=GREY_TEXT, height=dp(24)))
            card.add_widget(btn("Shop Now →", GOLD, BLACK, height=dp(36),
                on_press=lambda x,s=shop: self._go(s)))
            box.add_widget(card)
        note = BoxLayout(size_hint_y=None, height=dp(40), padding=[dp(12),dp(8)])
        bg(note, GOLD_LIGHT)
        note.add_widget(lbl(f"🏍  Flat delivery fee: R{DELIVERY_FEE}  •  Cash or Card",
                           size=12, color=GOLD_DARK, height=dp(24)))
        box.add_widget(note)
        box.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))
        sc.add_widget(box)
        root.add_widget(sc)
        self.add_widget(root)

    def _go(self, shop):
        App.get_running_app().active_shop = shop
        self.manager.get_screen('cust_shop').load_shop(shop)
        self.manager.current = 'cust_shop'

# ═══════════════════════════════════════════════
#  CUSTOMER: SHOP
# ═══════════════════════════════════════════════
class CustShopScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.shop = None
        self.cart = {}

    def load_shop(self, shop):
        self.shop = shop
        self.cart = {}
        self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header(self.shop['name'], back='cust_home'))
        sc = make_scroll()
        box = BoxLayout(orientation='vertical', padding=[dp(12),dp(8)],
                        spacing=dp(8), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        for item in self.shop['items']:
            qty = self.cart.get(item['id'], 0)
            card = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(72),
                             padding=[dp(14),dp(10)], spacing=dp(10))
            bg(card, WHITE)
            info = BoxLayout(orientation='vertical', size_hint_x=0.6)
            info.add_widget(lbl(item['name'], size=14, bold=True, color=BLACK, height=dp(28)))
            info.add_widget(lbl(f"R{item['price']}", size=15, color=GOLD, bold=True, height=dp(26)))
            card.add_widget(info)
            ctrl = BoxLayout(size_hint_x=0.4, spacing=dp(6))
            if qty > 0:
                m = btn("-", MAROON, height=dp(44), font_size=18,
                        on_press=lambda x,i=item: self._remove(i))
                m.size_hint_x = 0.33
                ctrl.add_widget(m)
                ql = lbl(str(qty), size=15, bold=True, color=BLACK,
                         halign='center', height=dp(44))
                ql.size_hint_x = 0.33
                ctrl.add_widget(ql)
            p = btn("+", GOLD, BLACK, height=dp(44), font_size=18,
                    on_press=lambda x,i=item: self._add(i))
            p.size_hint_x = 0.33 if qty > 0 else 1
            ctrl.add_widget(p)
            card.add_widget(ctrl)
            box.add_widget(card)
        sc.add_widget(box)
        root.add_widget(sc)
        if self.cart:
            subtotal = sum(
                self.shop['items'][i-1]['price'] * q
                for i, q in self.cart.items()
                if i-1 < len(self.shop['items'])
            )
            cbar = BoxLayout(size_hint_y=None, height=dp(60),
                             padding=[dp(12),dp(6)], spacing=dp(8))
            bg(cbar, BLACK)
            cbar.add_widget(lbl(
                f"🛒  {sum(self.cart.values())} item(s)  •  R{subtotal+DELIVERY_FEE}",
                size=14, bold=True, color=WHITE, height=dp(48)))
            cbar.add_widget(btn("Checkout →", GOLD, BLACK, height=dp(48),
                on_press=lambda x: self._checkout(subtotal)))
            root.add_widget(cbar)
        self.add_widget(root)

    def _add(self, item):
        self.cart[item['id']] = self.cart.get(item['id'], 0) + 1
        self._build()

    def _remove(self, item):
        if self.cart.get(item['id'], 0) > 0:
            self.cart[item['id']] -= 1
            if self.cart[item['id']] == 0:
                del self.cart[item['id']]
        self._build()

    def _checkout(self, subtotal):
        app = App.get_running_app()
        app.active_cart = self.cart
        self.manager.get_screen('cust_payment').load(subtotal + DELIVERY_FEE)
        self.manager.current = 'cust_payment'

# ═══════════════════════════════════════════════
#  CUSTOMER: PAYMENT
# ═══════════════════════════════════════════════
class CustPaymentScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.total = 0
        self.method = "cash"

    def load(self, total):
        self.total = total
        self._build()

    def on_enter(self):
        if self.total: self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header("Checkout", back='cust_shop'))
        sc = make_scroll()
        form = BoxLayout(orientation='vertical', padding=[dp(16),dp(14)],
                         spacing=dp(12), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))
        summ = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100),
                         padding=[dp(14),dp(12)])
        bg(summ, BLACK)
        summ.add_widget(lbl("Order Summary", size=12, color=GOLD_LIGHT, height=dp(22)))
        summ.add_widget(lbl(f"Items: R{self.total-DELIVERY_FEE}   Delivery: R{DELIVERY_FEE}",
                           size=13, color=WHITE, height=dp(26)))
        summ.add_widget(lbl(f"Total: R{self.total}", size=18, bold=True,
                           color=GOLD, height=dp(34)))
        form.add_widget(summ)
        dep = self.total / 2
        form.add_widget(lbl(f"50% Deposit: R{dep:.2f}", size=13,
                           color=MAROON, bold=True, halign='center', height=dp(30)))
        form.add_widget(divider())
        form.add_widget(lbl("Payment Method", size=13, bold=True, color=BLACK, height=dp(28)))
        mbox = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        for m, icon in [("cash","💵 Cash"),("card","💳 Card")]:
            mbox.add_widget(btn(icon,
                GOLD if m==self.method else GREY_LIGHT,
                BLACK if m==self.method else GREY_TEXT,
                height=dp(52),
                on_press=lambda x,mv=m: self._method(mv)))
        form.add_widget(mbox)
        form.add_widget(divider())
        form.add_widget(lbl("Your Name *", size=12, bold=True, color=BLACK, height=dp(24)))
        self.name_inp = inp("Full name")
        form.add_widget(self.name_inp)
        form.add_widget(lbl("Phone Number *", size=12, bold=True, color=BLACK, height=dp(24)))
        self.phone_inp = inp("e.g. 073 123 4567")
        form.add_widget(self.phone_inp)
        form.add_widget(lbl("Delivery Address *", size=12, bold=True, color=BLACK, height=dp(24)))
        self.addr_inp = inp("Street name & number")
        form.add_widget(self.addr_inp)
        form.add_widget(lbl("Special Instructions", size=12, bold=True, color=BLACK, height=dp(24)))
        self.notes_inp = inp("e.g. Gate code, landmark...")
        form.add_widget(self.notes_inp)
        form.add_widget(BoxLayout(size_hint_y=None, height=dp(14)))
        form.add_widget(btn(f"Place Order  •  Pay R{dep:.2f}", GOLD, BLACK,
                           height=dp(58), on_press=self._place))
        form.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))
        sc.add_widget(form)
        root.add_widget(sc)
        self.add_widget(root)

    def _method(self, m):
        self.method = m
        self._build()

    def _place(self, x):
        name  = self.name_inp.text.strip()
        phone = self.phone_inp.text.strip()
        addr  = self.addr_inp.text.strip()
        notes = self.notes_inp.text.strip()
        if not (name and phone and addr):
            show_popup("Missing Info", "Please fill in name, phone, and address.", RED)
            return
        app = App.get_running_app()
        otp = str(random.randint(1000, 9999))
        now = datetime.now().isoformat()
        app.cursor.execute("""
            INSERT INTO orders
            (customer_name,phone,address,notes,shop,items,total,deposit,
             status_idx,payment_method,otp,created_at)
            VALUES (?,?,?,?,?,?,?,?,0,?,?,?)
        """, (name, phone, addr, notes, app.active_shop['name'],
              json.dumps(app.active_cart), self.total, self.total/2,
              self.method, otp, now))
        app.conn.commit()
        app.current_order_id = app.cursor.lastrowid
        app.current_otp = otp
        show_popup("Order Placed! 🎉",
                   f"Order #{app.current_order_id} confirmed!\n\n"
                   f"Your OTP: {otp}\n(Share only when order arrives)",
                   GREEN,
                   on_ok=lambda: setattr(self.manager,'current','cust_track'))

# ═══════════════════════════════════════════════
#  CUSTOMER: TRACKING
# ═══════════════════════════════════════════════
class CustTrackScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.step = 0
        self._clk = None

    def on_enter(self):
        self._build()
        # Auto-refresh every 5s to pick up dispatcher/driver updates
        self._clk = Clock.schedule_interval(lambda dt: self._build(), 5)

    def on_leave(self):
        if self._clk:
            Clock.unschedule(self._clk)
            self._clk = None

    def _build(self):
        app = App.get_running_app()
        app.cursor.execute(
            "SELECT customer_name,status_idx,driver,otp FROM orders WHERE id=?",
            (app.current_order_id,))
        row = app.cursor.fetchone()
        if not row: return
        cname, sidx, driver, otp = row
        self.step = sidx

        self.clear_widgets()
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header(f"Order #{app.current_order_id}", back='cust_home'))

        si = step_info(self.step)
        notif = BoxLayout(size_hint_y=None, height=dp(46), padding=[dp(16),dp(8)])
        bg(notif, si[3])
        notif.add_widget(lbl(f"🔔  {si[1]}  {si[2]}", size=13, bold=True,
                            color=WHITE, height=dp(30)))
        root.add_widget(notif)

        sc = make_scroll()
        content = BoxLayout(orientation='vertical', padding=[dp(12),dp(8)],
                            spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(LiveMap(moving=driver is not None, step=self.step))

        eta_mins = max(2, 20 - self.step*3)
        eta = BoxLayout(size_hint_y=None, height=dp(52), padding=[dp(14),dp(8)])
        bg(eta, BLACK)
        eta.add_widget(lbl(f"🕐  ETA: {eta_mins} min", size=15, bold=True,
                          color=GOLD, height=dp(36)))
        eta.add_widget(lbl("Live estimate", size=11, color=GREY_TEXT,
                          halign='right', height=dp(36)))
        content.add_widget(eta)

        content.add_widget(lbl("Delivery Progress", size=13, bold=True,
                               color=BLACK, height=dp(30)))
        for idx, icon, label, color in ORDER_STEPS:
            done    = idx < self.step
            current = idx == self.step
            rbox = BoxLayout(size_hint_y=None, height=dp(44),
                             padding=[dp(12),dp(6)], spacing=dp(8))
            if current:
                bg(rbox, MAROON); tc = GOLD
            elif done:
                bg(rbox, GREEN_LIGHT); tc = GREEN
            else:
                bg(rbox, GREY_CARD); tc = GREY_TEXT
            dot = "●" if current else ("✓" if done else "○")
            rbox.add_widget(lbl(f"{dot}  {icon}  {label}", size=13,
                               bold=current, color=tc, height=dp(32)))
            content.add_widget(rbox)

        if driver:
            drv_data = next((d for d in DRIVERS if d['name']==driver), None)
            dcard = BoxLayout(size_hint_y=None, height=dp(88),
                              padding=[dp(14),dp(10)], spacing=dp(10))
            bg(dcard, WHITE)
            left = BoxLayout(orientation='vertical', size_hint_x=0.65)
            left.add_widget(lbl(f"🏍  {driver}", size=14, bold=True,
                               color=BLACK, height=dp(26)))
            if drv_data:
                left.add_widget(lbl(f"⭐ {drv_data['rating']}  •  "
                                   f"{drv_data['trips']} trips",
                                   size=12, color=GREY_TEXT, height=dp(22)))
                left.add_widget(lbl(drv_data['bike'], size=12,
                                   color=GREY_TEXT, height=dp(22)))
            dcard.add_widget(left)
            dcard.add_widget(btn("📞 Call", MAROON, height=dp(44),
                on_press=lambda x: show_popup("Call Driver",
                    f"Calling {driver}...", GOLD)))
            content.add_widget(dcard)
        else:
            w = BoxLayout(size_hint_y=None, height=dp(50), padding=[dp(12),dp(8)])
            bg(w, GREY_CARD)
            w.add_widget(lbl("Dispatcher is assigning a driver...",
                            size=13, color=GREY_TEXT, halign='center', height=dp(34)))
            content.add_widget(w)

        if self.step >= 6:
            ocard = BoxLayout(orientation='vertical', size_hint_y=None,
                              height=dp(90), padding=[dp(14),dp(10)])
            bg(ocard, GOLD_LIGHT)
            ocard.add_widget(lbl("Your Delivery OTP — Share with driver",
                                size=11, color=GOLD_DARK, halign='center', height=dp(22)))
            ocard.add_widget(lbl(str(otp), size=34, bold=True, color=BLACK,
                                halign='center', height=dp(52)))
            content.add_widget(ocard)

        if self.step >= 7:
            content.add_widget(btn("✅  Confirm Delivery Received", GREEN,
                                  height=dp(56), on_press=self._confirm))

        content.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))
        sc.add_widget(content)
        root.add_widget(sc)
        self.add_widget(root)

    def _confirm(self, x):
        show_popup("Thank You! 🎉",
                   "Delivery confirmed!\nThank you for using Spana Black Express.",
                   GREEN,
                   on_ok=lambda: setattr(self.manager,'current','cust_home'))

# ═══════════════════════════════════════════════
#  CUSTOMER: HISTORY
# ═══════════════════════════════════════════════
class CustHistoryScreen(Screen):
    def on_enter(self): self._build()
    def _build(self):
        self.clear_widgets()
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header("Order History", back='cust_home'))
        sc = make_scroll()
        box = BoxLayout(orientation='vertical', padding=[dp(12),dp(8)],
                        spacing=dp(8), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        app.cursor.execute(
            "SELECT id,customer_name,shop,total,status_idx,created_at "
            "FROM orders ORDER BY created_at DESC LIMIT 20")
        orders = app.cursor.fetchall()
        if not orders:
            box.add_widget(lbl("No orders yet. Go place one! 🛒",
                              halign='center', color=GREY_TEXT, height=dp(80)))
        else:
            for oid, name, shop, total, sidx, created in orders:
                si = step_info(sidx)
                card = BoxLayout(orientation='vertical', size_hint_y=None,
                                 height=dp(86), padding=[dp(14),dp(10)])
                bg(card, WHITE)
                top = BoxLayout(size_hint_y=None, height=dp(28))
                top.add_widget(lbl(f"#{oid}  {shop}", size=14, bold=True,
                                  color=BLACK, height=dp(28)))
                top.add_widget(lbl(f"R{total}", size=14, bold=True, color=GOLD,
                                  halign='right', height=dp(28)))
                card.add_widget(top)
                mid = BoxLayout(size_hint_y=None, height=dp(24))
                mid.add_widget(lbl(f"{si[1]}  {si[2]}  •  {created[:10]}",
                                  size=12, color=GREY_TEXT, height=dp(24)))
                t = btn("Track", MAROON, height=dp(24), font_size=11,
                        on_press=lambda x,o=oid: self._track(o))
                t.size_hint_x = None; t.width = dp(66)
                mid.add_widget(t)
                card.add_widget(mid)
                box.add_widget(card)
        sc.add_widget(box)
        root.add_widget(sc)
        self.add_widget(root)

    def _track(self, oid):
        App.get_running_app().current_order_id = oid
        self.manager.current = 'cust_track'

# ═══════════════════════════════════════════════
#  OWNER: LOGIN
# ═══════════════════════════════════════════════
class OwnerLoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header("Dispatcher Login", back='splash'))
        root.add_widget(Label(size_hint_y=0.2))
        card = BoxLayout(orientation='vertical', size_hint=(0.88,None),
                         height=dp(240), pos_hint={'center_x':0.5},
                         padding=[dp(20),dp(18)], spacing=dp(14))
        bg(card, WHITE)
        card.add_widget(lbl("🏢  Enter PIN", size=16, bold=True, color=BLACK,
                           halign='center', height=dp(36)))
        self.pin = inp("PIN", password=True)
        card.add_widget(self.pin)
        card.add_widget(btn("LOGIN", MAROON, height=dp(54), on_press=self._check))
        root.add_widget(card)
        root.add_widget(Label())
        self.add_widget(root)

    def _check(self, x):
        if self.pin.text == OWNER_PIN:
            self.pin.text = ""
            self.manager.current = 'owner_dash'
        else:
            self.pin.text = ""
            show_popup("Wrong PIN", "Incorrect PIN. Try again.", RED)

# ═══════════════════════════════════════════════
#  OWNER: DASHBOARD  ← FULLY REBUILT v2.1
# ═══════════════════════════════════════════════
class OwnerDashScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.filter = "All"
        self.filter_btns = {}
        self._clk = None

    def on_enter(self):
        self._build()
        # Auto-refresh every 6s
        self._clk = Clock.schedule_interval(lambda dt: self._refresh(), 6)

    def on_leave(self):
        if self._clk:
            Clock.unschedule(self._clk)
            self._clk = None

    def _refresh(self):
        self._filter(self.filter)

    def _build(self):
        self.clear_widgets()
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header(
            "Dispatcher",
            right_text="Logout",
            right_cb=lambda x: setattr(self.manager,'current','splash')))

        # Stats
        app.cursor.execute("SELECT COUNT(*) FROM orders")
        total_o = app.cursor.fetchone()[0]
        app.cursor.execute("SELECT COUNT(*) FROM orders WHERE status_idx=0")
        new_o = app.cursor.fetchone()[0]
        app.cursor.execute("SELECT COUNT(*) FROM orders WHERE status_idx BETWEEN 1 AND 6")
        active_o = app.cursor.fetchone()[0]

        stats = BoxLayout(size_hint_y=None, height=dp(82),
                          padding=[dp(8),dp(8)], spacing=dp(4))
        bg(stats, MAROON)
        for label, val, color in [
            ("Total", total_o, GOLD),
            ("New", new_o, WHITE),
            ("Active", active_o, GOLD_LIGHT),
            ("Drivers", len(DRIVERS), WHITE),
        ]:
            b = BoxLayout(orientation='vertical')
            b.add_widget(lbl(str(val), size=20, bold=True, color=color,
                            halign='center', height=dp(36)))
            b.add_widget(lbl(label, size=10, color=GOLD_LIGHT,
                            halign='center', height=dp(20)))
            stats.add_widget(b)
        root.add_widget(stats)

        # Driver availability panel
        drv_panel = BoxLayout(size_hint_y=None, height=dp(56),
                              padding=[dp(8),dp(6)], spacing=dp(6))
        bg(drv_panel, BLACK)
        drv_panel.add_widget(lbl("DRIVERS:", size=11, bold=True,
                                color=GOLD_LIGHT, height=dp(44),
                                valign='middle'))
        for drv in DRIVERS:
            online = app.driver_online.get(drv['id'], True)
            busy   = app.driver_busy.get(drv['id'], False)
            if busy:
                label = f"🟡 {drv['name']}"
                c = ORANGE
            elif online:
                label = f"🟢 {drv['name']}"
                c = GREEN
            else:
                label = f"🔴 {drv['name']}"
                c = (0.35,0.35,0.35,1)
            b = btn(label, c, height=dp(40), font_size=11,
                    on_press=lambda x,d=drv: self._toggle_driver(d))
            drv_panel.add_widget(b)
        root.add_widget(drv_panel)

        # Filter tabs
        fbar = BoxLayout(size_hint_y=None, height=dp(50),
                         spacing=dp(4), padding=[dp(6),dp(4)])
        bg(fbar, WHITE)
        self.filter_btns = {}
        for s in ["All","New","Active","Done"]:
            b = btn(s,
                    MAROON if s==self.filter else GREY_LIGHT,
                    GOLD   if s==self.filter else GREY_TEXT,
                    height=dp(42),
                    on_press=lambda x,sv=s: self._filter(sv))
            self.filter_btns[s] = b
            fbar.add_widget(b)
        root.add_widget(fbar)

        # Orders list
        sc = make_scroll()
        self.obox = BoxLayout(orientation='vertical', padding=[dp(10),dp(6)],
                              spacing=dp(8), size_hint_y=None)
        self.obox.bind(minimum_height=self.obox.setter('height'))
        sc.add_widget(self.obox)
        root.add_widget(sc)

        self._filter("All")
        self.add_widget(root)

    def _toggle_driver(self, drv):
        app = App.get_running_app()
        current = app.driver_online.get(drv['id'], True)
        app.driver_online[drv['id']] = not current
        self._build()

    def _filter(self, status):
        self.filter = status
        for s, b in self.filter_btns.items():
            b.background_color = MAROON if s==status else GREY_LIGHT
            b.color = GOLD if s==status else GREY_TEXT

        app = App.get_running_app()
        if status == "All":
            app.cursor.execute(
                "SELECT id,customer_name,phone,address,shop,total,status_idx,driver "
                "FROM orders ORDER BY created_at DESC")
        elif status == "New":
            app.cursor.execute(
                "SELECT id,customer_name,phone,address,shop,total,status_idx,driver "
                "FROM orders WHERE status_idx=0 ORDER BY created_at DESC")
        elif status == "Active":
            app.cursor.execute(
                "SELECT id,customer_name,phone,address,shop,total,status_idx,driver "
                "FROM orders WHERE status_idx BETWEEN 1 AND 6 ORDER BY created_at DESC")
        else:
            app.cursor.execute(
                "SELECT id,customer_name,phone,address,shop,total,status_idx,driver "
                "FROM orders WHERE status_idx=7 ORDER BY created_at DESC")

        rows = app.cursor.fetchall()
        self.obox.clear_widgets()
        if not rows:
            self.obox.add_widget(lbl("No orders here.", halign='center',
                                    color=GREY_TEXT, height=dp(60)))
            return
        for row in rows:
            self.obox.add_widget(self._order_card(row))

    def _order_card(self, row):
        oid, name, phone, addr, shop, total, sidx, driver = row
        si = step_info(sidx)

        # Calculate card height
        is_new = sidx == 0
        h = dp(230) if is_new else dp(148)
        card = BoxLayout(orientation='vertical', size_hint_y=None, height=h,
                         padding=[dp(14),dp(10)], spacing=dp(5))
        bg(card, WHITE)

        # Header row
        top = BoxLayout(size_hint_y=None, height=dp(26))
        top.add_widget(lbl(f"#{oid}  {name}", size=13, bold=True,
                          color=BLACK, height=dp(26)))
        top.add_widget(lbl(f"R{total}", size=13, bold=True, color=GOLD,
                          halign='right', height=dp(26)))
        card.add_widget(top)
        card.add_widget(lbl(f"📍  {addr}", size=12, color=GREY_TEXT, height=dp(20)))
        card.add_widget(lbl(f"🛒  {shop}  •  📞  {phone}", size=12,
                           color=GREY_TEXT, height=dp(20)))

        # Status badge
        sbadge = BoxLayout(size_hint_y=None, height=dp(26), spacing=dp(6))
        sbadge.add_widget(lbl(f"{si[1]}  {si[2]}", size=12, bold=True,
                             color=si[3], height=dp(26)))
        if driver:
            sbadge.add_widget(lbl(f"🏍  {driver}", size=12,
                                 color=GOLD_DARK, height=dp(26)))
        card.add_widget(sbadge)

        # ── ASSIGN DRIVER PANEL (only for new orders) ──
        if is_new:
            card.add_widget(divider())
            app = App.get_running_app()

            # Show available drivers with status
            card.add_widget(lbl("Select Driver:", size=12, bold=True,
                               color=BLACK, height=dp(24)))

            drv_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(6))
            available_any = False
            for drv in DRIVERS:
                online = app.driver_online.get(drv['id'], True)
                busy   = app.driver_busy.get(drv['id'], False)
                available = online and not busy

                if available:
                    label = f"🟢 {drv['name']}"
                    color = GOLD
                    tc    = BLACK
                    available_any = True
                elif busy:
                    label = f"🟡 {drv['name']} (Busy)"
                    color = GREY_LIGHT
                    tc    = GREY_TEXT
                else:
                    label = f"🔴 {drv['name']} (Offline)"
                    color = GREY_LIGHT
                    tc    = GREY_TEXT

                b = btn(label, color, tc, height=dp(46), font_size=11,
                        on_press=(lambda x,d=drv,o=oid: self._assign(o,d))
                        if available else None)
                drv_row.add_widget(b)
            card.add_widget(drv_row)

            if not available_any:
                card.add_widget(lbl("⚠️  No drivers available right now.",
                                   size=11, color=RED, height=dp(22)))

        return card

    def _assign(self, order_id, driver):
        app = App.get_running_app()

        # Check not already busy
        if app.driver_busy.get(driver['id'], False):
            show_popup("Driver Busy",
                       f"{driver['name']} is already on a delivery.", ORANGE)
            return

        # Assign
        app.cursor.execute(
            "UPDATE orders SET driver=?,status_idx=2 WHERE id=?",
            (driver['name'], order_id))
        app.conn.commit()

        # Mark driver as busy
        app.driver_busy[driver['id']] = True

        show_popup("Driver Assigned! ✅",
                   f"🏍  {driver['name']}\nassigned to Order #{order_id}\n\n"
                   f"Status: Driver Assigned",
                   GREEN,
                   on_ok=lambda: self._build())

# ═══════════════════════════════════════════════
#  OWNER: LIVE MONITORING SCREEN
# ═══════════════════════════════════════════════
class OwnerMonitorScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._clk = None

    def on_enter(self):
        self._build()
        self._clk = Clock.schedule_interval(lambda dt: self._build(), 5)

    def on_leave(self):
        if self._clk:
            Clock.unschedule(self._clk)
            self._clk = None

    def _build(self):
        self.clear_widgets()
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header("Live Monitor", back='owner_dash'))

        sc = make_scroll()
        box = BoxLayout(orientation='vertical', padding=[dp(12),dp(8)],
                        spacing=dp(10), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        box.add_widget(lbl("🔴  LIVE — Active Deliveries", size=14, bold=True,
                          color=MAROON, height=dp(34)))

        app.cursor.execute("""
            SELECT id,customer_name,address,shop,status_idx,driver
            FROM orders WHERE status_idx BETWEEN 1 AND 6
            ORDER BY status_idx DESC
        """)
        active = app.cursor.fetchall()

        if not active:
            empty = BoxLayout(size_hint_y=None, height=dp(80), padding=[dp(16),dp(16)])
            bg(empty, WHITE)
            empty.add_widget(lbl("No active deliveries right now.",
                               size=13, color=GREY_TEXT, halign='center', height=dp(48)))
            box.add_widget(empty)
        else:
            for oid, name, addr, shop, sidx, driver in active:
                si = step_info(sidx)
                eta = max(2, 20 - sidx*3)

                card = BoxLayout(orientation='vertical', size_hint_y=None,
                                 height=dp(130), padding=[dp(14),dp(10)], spacing=dp(5))
                bg(card, WHITE)

                top = BoxLayout(size_hint_y=None, height=dp(26))
                top.add_widget(lbl(f"#{oid}  {name}", size=13, bold=True,
                                  color=BLACK, height=dp(26)))
                top.add_widget(lbl(f"ETA: {eta} min", size=13, bold=True,
                                  color=BLUE, halign='right', height=dp(26)))
                card.add_widget(top)

                card.add_widget(lbl(f"🏍  Driver: {driver or 'Unassigned'}",
                                  size=13, bold=True, color=GOLD_DARK, height=dp(24)))
                card.add_widget(lbl(f"{si[1]}  {si[2]}", size=12, bold=True,
                                  color=si[3], height=dp(22)))
                card.add_widget(lbl(f"📍  {addr}", size=12, color=GREY_TEXT, height=dp(20)))

                # Mini map
                card.add_widget(LiveMap(moving=True, step=sidx))
                card.height = dp(340)

                box.add_widget(card)

        sc.add_widget(box)
        root.add_widget(sc)
        self.add_widget(root)

# ═══════════════════════════════════════════════
#  DRIVER: LOGIN
# ═══════════════════════════════════════════════
class DrvLoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header("Driver Login", back='splash'))
        root.add_widget(Label(size_hint_y=0.15))
        card = BoxLayout(orientation='vertical', size_hint=(0.88,None),
                         height=dp(280), pos_hint={'center_x':0.5},
                         padding=[dp(20),dp(18)], spacing=dp(14))
        bg(card, WHITE)
        card.add_widget(lbl("Select Your Profile", size=15, bold=True,
                           color=BLACK, halign='center', height=dp(36)))
        for drv in DRIVERS:
            card.add_widget(btn(f"🏍  {drv['name']}  •  {drv['bike']}",
                               BLACK, GOLD, height=dp(58),
                               on_press=lambda x,d=drv: self._login(d)))
        root.add_widget(card)
        root.add_widget(Label())
        self.add_widget(root)

    def _login(self, drv):
        App.get_running_app().current_driver = drv
        self.manager.current = 'drv_dash'

# ═══════════════════════════════════════════════
#  DRIVER: DASHBOARD  ← FULLY REBUILT v2.1
# ═══════════════════════════════════════════════
class DrvDashScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._clk = None

    def on_enter(self):
        self._build()
        # Auto-refresh every 6s to pick up new assignments
        self._clk = Clock.schedule_interval(lambda dt: self._build(), 6)

    def on_leave(self):
        if self._clk:
            Clock.unschedule(self._clk)
            self._clk = None

    def _build(self):
        self.clear_widgets()
        app = App.get_running_app()
        drv = app.current_driver
        online = app.driver_online.get(drv['id'], True)

        root = BoxLayout(orientation='vertical')
        bg(root, BG)
        root.add_widget(header(
            f"🏍  {drv['name']}",
            right_text="Logout",
            right_cb=lambda x: setattr(self.manager,'current','splash')))

        # Online/Offline toggle bar
        sbar = BoxLayout(size_hint_y=None, height=dp(54),
                         padding=[dp(12),dp(6)], spacing=dp(8))
        bg(sbar, GREEN if online else MAROON)
        sbar.add_widget(lbl(
            "🟢  ONLINE — Ready for jobs" if online
            else "🔴  OFFLINE — Not accepting jobs",
            size=13, bold=True, color=WHITE, height=dp(42)))
        tog = btn("Go Offline" if online else "Go Online",
                  BLACK, GOLD, height=dp(42), font_size=12,
                  on_press=lambda x: self._toggle(drv))
        tog.size_hint_x = None
        tog.width = dp(110)
        sbar.add_widget(tog)
        root.add_widget(sbar)

        sc = make_scroll()
        content = BoxLayout(orientation='vertical', padding=[dp(12),dp(8)],
                            spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(lbl("📋  My Active Jobs", size=14, bold=True,
                               color=BLACK, height=dp(34)))

        app.cursor.execute("""
            SELECT id,customer_name,phone,address,shop,status_idx,otp
            FROM orders WHERE driver=? AND status_idx BETWEEN 1 AND 6
            ORDER BY created_at DESC
        """, (drv['name'],))
        deliveries = app.cursor.fetchall()

        if not deliveries:
            empty = BoxLayout(size_hint_y=None, height=dp(100),
                              padding=[dp(16),dp(16)])
            bg(empty, WHITE)
            empty.add_widget(lbl(
                "No active jobs.\nStand by — dispatcher will assign you. 🏍",
                size=13, color=GREY_TEXT, halign='center', height=dp(68)))
            content.add_widget(empty)
        else:
            for oid, name, phone, addr, shop, sidx, otp in deliveries:
                si = step_info(sidx)
                card = BoxLayout(orientation='vertical', size_hint_y=None,
                                 height=dp(210), padding=[dp(14),dp(10)], spacing=dp(5))
                bg(card, BLACK if sidx<=2 else WHITE)
                tc = GOLD if sidx<=2 else BLACK

                card.add_widget(lbl(f"Order #{oid}", size=15, bold=True,
                                  color=tc, height=dp(26)))
                card.add_widget(lbl(f"👤  {name}  •  📞  {phone}",
                                  size=12, color=tc if sidx<=2 else GREY_TEXT,
                                  height=dp(22)))
                card.add_widget(lbl(f"📍  {addr}",
                                  size=12, color=tc if sidx<=2 else GREY_TEXT,
                                  height=dp(22)))
                card.add_widget(lbl(f"🛒  {shop}",
                                  size=12, color=tc if sidx<=2 else GREY_TEXT,
                                  height=dp(22)))
                card.add_widget(lbl(f"{si[1]}  {si[2]}", size=12, bold=True,
                                  color=GOLD if sidx<=2 else si[3], height=dp(22)))
                card.add_widget(divider())

                # Action button based on current step
                # Step 2=Driver Assigned → go to shop
                # Step 3=At Shop → collect
                # Step 4=Collected → en route
                # Step 5=En Route → nearby
                # Step 6=Nearby → deliver (OTP)
                brow = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
                if sidx == 2:
                    brow.add_widget(btn("🛒  Arrived at Shop", GOLD, BLACK,
                                      height=dp(50),
                                      on_press=lambda x,o=oid: self._upd(o,3)))
                elif sidx == 3:
                    brow.add_widget(btn("📦  Order Collected", ORANGE,
                                      height=dp(50),
                                      on_press=lambda x,o=oid: self._upd(o,5)))
                elif sidx == 5:
                    brow.add_widget(btn("📍  I'm Nearby", BLUE,
                                      height=dp(50),
                                      on_press=lambda x,o=oid: self._upd(o,6)))
                elif sidx == 6:
                    brow.add_widget(btn("✅  Delivered — Enter OTP", GREEN,
                                      height=dp(50),
                                      on_press=lambda x,o=oid,op=otp: self._deliver(o,op)))
                card.add_widget(brow)
                content.add_widget(card)

        sc.add_widget(content)
        root.add_widget(sc)
        self.add_widget(root)

    def _toggle(self, drv):
        app = App.get_running_app()
        current = app.driver_online.get(drv['id'], True)
        app.driver_online[drv['id']] = not current
        self._build()

    def _upd(self, order_id, new_step):
        app = App.get_running_app()
        app.cursor.execute("UPDATE orders SET status_idx=? WHERE id=?",
                          (new_step, order_id))
        app.conn.commit()
        si = step_info(new_step)
        show_popup("Status Updated ✅", f"{si[1]}  {si[2]}", GREEN,
                   on_ok=lambda: self._build())

    def _deliver(self, order_id, otp):
        app = App.get_running_app()
        box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        box.add_widget(lbl("Enter Customer OTP", size=14, bold=True,
                          color=BLACK, halign='center', height=dp(28)))
        box.add_widget(lbl("Ask customer for their 4-digit code",
                          size=12, color=GREY_TEXT, halign='center', height=dp(22)))
        otp_inp = inp("4-digit OTP", input_filter='int')
        box.add_widget(otp_inp)

        def _verify(x):
            if otp_inp.text.strip() == otp:
                p.dismiss()
                app.cursor.execute(
                    "UPDATE orders SET status_idx=7 WHERE id=?", (order_id,))
                app.conn.commit()
                # Free up driver
                drv = app.current_driver
                app.driver_busy[drv['id']] = False
                show_popup("Delivered! 🎉",
                           f"Order #{order_id} completed!\nGreat work! 🏍",
                           GREEN, on_ok=lambda: self._build())
            else:
                show_popup("Wrong OTP", "OTP does not match. Try again.", RED)

        box.add_widget(btn("Verify & Complete", GREEN, on_press=_verify))
        p = Popup(title="OTP Verification", content=box,
                  size_hint=(0.88,0.46),
                  title_color=BLACK, separator_color=GOLD)
        p.open()

# ═══════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════
class SpanaBlackV21(App):
    def build(self):
        self.title = APP_NAME
        self.active_shop    = None
        self.active_cart    = {}
        self.current_order_id = None
        self.current_otp    = None
        self.current_driver = None
        # Driver state dictionaries — keyed by driver id
        self.driver_online  = {d['id']: True  for d in DRIVERS}
        self.driver_busy    = {d['id']: False for d in DRIVERS}
        self._db()
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(CustHomeScreen(name='cust_home'))
        sm.add_widget(CustShopScreen(name='cust_shop'))
        sm.add_widget(CustPaymentScreen(name='cust_payment'))
        sm.add_widget(CustTrackScreen(name='cust_track'))
        sm.add_widget(CustHistoryScreen(name='cust_history'))
        sm.add_widget(OwnerLoginScreen(name='owner_login'))
        sm.add_widget(OwnerDashScreen(name='owner_dash'))
        sm.add_widget(OwnerMonitorScreen(name='owner_monitor'))
        sm.add_widget(DrvLoginScreen(name='drv_login'))
        sm.add_widget(DrvDashScreen(name='drv_dash'))
        return sm

    def _db(self):
        d = os.path.join(os.getcwd(), "data")
        os.makedirs(d, exist_ok=True)
        self.conn = sqlite3.connect(os.path.join(d, "spana_v21.db"))
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                notes TEXT,
                shop TEXT NOT NULL,
                items TEXT,
                total REAL NOT NULL,
                deposit REAL NOT NULL,
                status_idx INTEGER DEFAULT 0,
                driver TEXT,
                payment_method TEXT,
                otp TEXT,
                created_at TEXT
            )
        """)
        self.conn.commit()

if __name__ == "__main__":
    SpanaBlackV21().run()

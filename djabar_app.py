import os
import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

class StoreInventoryApp(App):
    def build(self):
        self.title = "Store Inventory"

        
        # DATABASE
        data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, "inventory.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()
        
        # UI
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)
        
        # INPUTS
        self.name_input = TextInput(hint_text="Product name", multiline=False)
        self.category_input = TextInput(hint_text="Category (e.g. Raw / Ready)", multiline=False)
        
        self.unit_spinner = Spinner(
            text="units",
            values=("kg", "units", "litres"),
            size_hint_y=None,
            height=44
        )
        
        self.qty_input = TextInput(hint_text="Starting quantity", input_filter="int", multiline=False)
        
        add_btn = Button(text="Add Product", size_hint_y=None, height=50)
        add_btn.bind(on_press=self.add_item)
        
        # OUTPUT
        self.output_label = Label(text=self.get_inventory_text(), size_hint_y=None, halign="left", valign="top")
        self.output_label.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        
        scroll = ScrollView()
        scroll.add_widget(self.output_label)
        
        # CONTROLS
        self.control_input = TextInput(hint_text="Enter Product ID", input_filter="int", multiline=False)
        
        plus_btn = Button(text="+ Add 1", size_hint_y=None, height=40)
        minus_btn = Button(text="- Remove 1", size_hint_y=None, height=40)
        delete_btn = Button(text="Delete Product", size_hint_y=None, height=40)
        
        plus_btn.bind(on_press=lambda x: self.adjust_quantity(1))
        minus_btn.bind(on_press=lambda x: self.adjust_quantity(-1))
        delete_btn.bind(on_press=lambda x: self.delete_product())
        
        # LAYOUT
        root.add_widget(self.name_input)
        root.add_widget(self.category_input)
        root.add_widget(self.unit_spinner)
        root.add_widget(self.qty_input)
        root.add_widget(add_btn)
        root.add_widget(scroll)
        root.add_widget(self.control_input)
        root.add_widget(plus_btn)
        root.add_widget(minus_btn)
        root.add_widget(delete_btn)
        
        return root
    
    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit TEXT NOT NULL,
            min_quantity INTEGER DEFAULT 5,
            created_at TEXT,
            updated_at TEXT
        )
        """)
        self.conn.commit()
    
    def add_item(self, instance):
        name = self.name_input.text.strip()
        category = self.category_input.text.strip()
        qty = self.qty_input.text.strip()
        unit = self.unit_spinner.text
        
        if not (name and category and qty.isdigit()):
            self.show_popup("Error", "Please fill all fields correctly!")
            return
        
        now = datetime.now().isoformat()
        self.cursor.execute("""
            INSERT INTO inventory (name, category, quantity, unit, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, category, int(qty), unit, now, now))
        
        self.conn.commit()
        self.clear_inputs()
        self.refresh_output()
    
    def adjust_quantity(self, change):
        pid = self.control_input.text.strip()
        if not pid.isdigit():
            self.show_popup("Error", "Enter a valid Product ID!")
            return
        
        self.cursor.execute("SELECT quantity FROM inventory WHERE id = ?", (pid,))
        row = self.cursor.fetchone()
        if not row:
            self.show_popup("Error", f"Product ID {pid} not found!")
            return
        
        new_qty = max(0, row[0] + change)
        now = datetime.now().isoformat()
        self.cursor.execute("""
            UPDATE inventory
            SET quantity = ?, updated_at = ?
            WHERE id = ?
        """, (new_qty, now, pid))
        self.conn.commit()
        self.refresh_output()
    
    def delete_product(self):
        pid = self.control_input.text.strip()
        if not pid.isdigit():
            self.show_popup("Error", "Enter a valid Product ID!")
            return
        
        self.cursor.execute("SELECT name FROM inventory WHERE id = ?", (pid,))
        row = self.cursor.fetchone()
        if not row:
            self.show_popup("Error", f"Product ID {pid} not found!")
            return
        
        self.cursor.execute("DELETE FROM inventory WHERE id = ?", (pid,))
        self.conn.commit()
        self.clear_inputs()
        self.refresh_output()
        self.show_popup("Deleted", f"Product {row[0]} removed successfully!")
    
    def get_inventory_text(self):
        self.cursor.execute("""
            SELECT id, category, name, quantity, unit, min_quantity
            FROM inventory
            ORDER BY category
        """)
        items = self.cursor.fetchall()
        if not items:
            return "No stock yet."
        
        text = ""
        current_cat = ""
        for id, cat, name, qty, unit, min_q in items:
            if cat != current_cat:
                text += f"\n[{cat}]\n"
                current_cat = cat
            warn = " !LOW" if qty <= min_q else ""
            text += f"{id}. {name}: {qty} {unit}{warn}\n"
        return text
    
    def refresh_output(self):
        self.output_label.text = self.get_inventory_text()
    
    def clear_inputs(self):
        self.name_input.text = ""
        self.category_input.text = ""
        self.qty_input.text = ""
        self.control_input.text = ""
    
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(300, 200))
        popup.open()

if __name__ == "__main__":
    StoreInventoryApp().run()
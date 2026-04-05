from tabulate import tabulate



"""
    Shoe Inventory Management System:
    This program allows users to manage a shoe inventory
    through a menu-driven interface.
    Features include viewing all shoes, adding new entries,
    restocking, searching by code,
    calculating item values, 
    and displaying data in a tabulated format.

"""

class Shoe:
    """Represents a shoe in the inventory."""

    def __init__(self, country, code, product, cost, quantity, size):
        self.country = country
        self.code = code
        self.product = product
        self.cost = cost
        self.quantity = quantity
        self.size = size

    def get_cost(self):
        """Return the cost of the shoe."""
        return self.cost

    def get_quantity(self):
        """Return the quantity of the shoe."""
        return self.quantity

    def get_value(self):
        """Calculate and return the total value of the shoe."""
        return self.cost * self.quantity

    def __str__(self):
        return (
            f"Country: {self.country}, Code: {self.code},\
        Product: {self.product}, "
            f"Cost: R{self.cost:.2f}, \
        Quantity: {self.quantity}, Size: {self.size}"
        )


# Global shoe list
shoe_list = []


def read_shoes_data():
    try:
        with open("inventory.txt", "r", encoding="utf-8") as file:
            next(file)  # Skip header
            for line in file:
                parts = line.strip().split(',')
                if len(parts) == 6:
                    country, code, product, cost, quantity, size = parts
                elif len(parts) == 5:
                    country, code, product, cost, quantity = parts
                    size = ""  # Default to empty string if missing
                else:
                    print(f"Skipping malformed line: {line.strip()}")
                    continue
                try:
                    shoe = Shoe(country, code, product, float(cost), int(quantity), size)
                    shoe_list.append(shoe)
                except ValueError as e:
                    print(f"Error parsing line: {line.strip()} - {e}")
    except FileNotFoundError:
        print("Error: Inventory file not found.")



def capture_shoes():
    """Prompt user to enter shoe details and add to shoe_list."""
    print("\nEnter shoe details Or(type 'e' to exit):")

    country = input("Enter country: ").strip()
    if country.lower() == "e":
        print("Capture cancelled.")
        return

    code = input("Enter code: ").strip()
    if code.lower() == "e":
        print("Capture cancelled.")
        return

    product = input("Enter product name: ").strip()
    if product.lower() == "e":
        print("Capture cancelled.")
        return

    size = input("Enter size: ").strip()
    if size.lower() == "e":
        print("Capture cancelled.")
        return

    cost_input = input("Enter cost: ").strip()
    if cost_input.lower() == "e":
        print("Capture cancelled.")
        return

    quantity_input = input("Enter quantity: ").strip()
    if quantity_input.lower() == "e":
        print("Capture cancelled.")
        return

    try:
        cost = float(cost_input)
        quantity = int(quantity_input)
    except ValueError:
        print("Invalid input for cost or quantity. Please enter numeric values.")
        return

    shoe = Shoe(country, code, product, cost, quantity, size)
    shoe_list.append(shoe)
    print("Shoe added successfully.")


def view_all():
    """Display all shoes in inventory."""
    if not shoe_list:
        print("No shoes in inventory.")
        return

    print(f"{'Country':<15}{'Code':<10}{'Product':<20}{'Cost':<10}{'Quantity':<10}{'Size':<10}")
    print("~" * 75)
    for shoe in shoe_list:
        print(
            f"{shoe.country:<15}{shoe.code:<10}{shoe.product:<20}"
            f"R{shoe.cost:<9.2f}{shoe.quantity:<10}{shoe.size:<10}"
        )


def get_quantity(shoe):
    """Return the quantity of a shoe object."""
    return shoe.quantity


def re_stock():
    """Restock the shoe with the lowest quantity and update the file."""
    lowest_qty_shoe = min(shoe_list, key=get_quantity)
    print(f"\nThe shoe with the lowest quantity is:\n{lowest_qty_shoe}")

    try:
        restock_amount = int(input("Enter quantity to add (or 0 to skip): "))
        if restock_amount > 0:
            lowest_qty_shoe.quantity += restock_amount
            print(f"Updated quantity: {lowest_qty_shoe.quantity}")

            with open("inventory.txt", "r") as file:
                lines = file.readlines()

            for i in range(1, len(lines)):
                data = lines[i].strip().split(",")
                if data[1] == lowest_qty_shoe.code:
                    data[4] = str(lowest_qty_shoe.quantity)
                    lines[i] = ",".join(data) + "\n"
                    break

            with open("inventory.txt", "w") as file:
                file.writelines(lines)

            print("Inventory file updated successfully.")
        else:
            print("No changes made to inventory.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")


def search_shoe():
    """Search for a shoe by code and display it."""
    search_code = input("Enter the shoe code to search: ").lower().strip()
    for shoe in shoe_list:
        if shoe.code.lower() == search_code:
            print("Shoe found:")
            print(shoe)
            return
    print("Shoe not found.")


def value_per_item():
    """Calculate and display the value of each shoe item."""
    for shoe in shoe_list:
        print(f"{shoe.product} - Value: R{shoe.get_value():.2f}")


def shoe_table():
    """Display shoe inventory in a tabulated format."""
    if not shoe_list:
        print("No shoes in inventory.")
        return

    table = [
        [shoe.country, shoe.code, shoe.product, f"R{shoe.cost:.2f}", shoe.quantity, shoe.size]
        for shoe in shoe_list
    ]
    headers = ["Country", "Code", "Product", "Cost", "Quantity", "Size"]
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))


def highest_quantity():
    """Display the shoe with the highest quantity and mark it as on sale."""
    if not shoe_list:
        print("No shoes in inventory.")
        return

    highest_shoe = max(shoe_list, key=get_quantity)
    print("Shoe with the highest quantity:")
    print(highest_shoe)
    print(f"{highest_shoe.product} is on SALE!")


def main_menu():
    """Display the main menu and handle user choices."""
    while True:
        
        print("\n===== Shoe Inventory Menu =====")
        print("1. View all shoes")
        print("2. Capture new shoe")
        print("3. Display shoes in table format")
        print("4. Restock shoes")
        print("5. Search shoe by code")
        print("6. Calculate value per item")
        print("7. Show product with highest quantity")
        print("8. Exit")

        choice = input("Enter your choice (1–8): ").strip()

        if choice == "1":
            view_all()
        elif choice == "2":
            capture_shoes()
        elif choice == "3":
            shoe_table()
        elif choice == "4":
            re_stock()
        elif choice == "5":
            search_shoe()
        elif choice == "6":
            value_per_item()
        elif choice == "7":
            highest_quantity()
        elif choice == "8":
            print("Exiting program......\n Goodbye!")
            break
        else:
            print("Invalid choice. Please select a number from 1 to 8.")


# Program Execution
read_shoes_data()  # Initialize shoe_list from file
main_menu()

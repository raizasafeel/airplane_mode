import frappe
import random
def execute():
    tickets = frappe.db.get_all("Airplane Ticket", filters={"seat": ["is", "not set"]})

    for ticket in tickets:
        row = random.randint(1, 100)
        seat = random.choice(['A', 'B', 'C', 'D', 'E'])
        seat_number = f"{row}{seat}"
        frappe.set_value("Airplane Ticket", ticket.name, "seat", seat_number)
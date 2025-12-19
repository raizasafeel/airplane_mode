# Copyright (c) 2025, Me! and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import random


class AirplaneTicket(Document):
	def remove_duplicate_add_ons(self):
		if not self.add_ons:
			return
		seen_ids = set()
		unique_add_ons = []
		for add_on in self.add_ons:
			if add_on.item not in seen_ids:
				unique_add_ons.append(add_on)
				seen_ids.add(add_on.item)
		self.add_ons = unique_add_ons

	def total_number_of_tickets(self):
		count = frappe.db.count(
			"Airplane Ticket",
			filters={"flight": self.flight}
		)
		return count
	
	def total_number_of_seats(self):
		flight = frappe.get_value("Airplane Flight", self.flight, "airplane")
		return frappe.get_value("Airplane", flight, "capacity")

	def is_flight_full(self):
		return self.total_number_of_tickets() >= self.total_number_of_seats()

	def generate_seat_number(self):
		if not self.seat:
			row = random.randint(1, 100)
			seat = random.choice(['A', 'B', 'C', 'D', 'E'])
			self.seat = f"{row}{seat}"
	
	def calculate_total_amount(self):
		add_ons_fee = sum(add_on.amount for add_on in self.add_ons)
		self.total_amount = self.flight_price + add_ons_fee
	
	def is_status_boarded(self):
		return self.status == "Boarded"

	def validate(self):
		self.calculate_total_amount()
		self.remove_duplicate_add_ons()

	def before_insert(self):
		self.generate_seat_number()
		if self.is_flight_full():
			frappe.throw(
				title="Flight Full",
				msg="Cannot issue ticket as the flight is already full."
			)

	def before_submit(self):
		if not self.is_status_boarded():
			frappe.throw(
				title="Invalid Status",
				msg="Cannot submit ticket unless status is 'Boarded'.")

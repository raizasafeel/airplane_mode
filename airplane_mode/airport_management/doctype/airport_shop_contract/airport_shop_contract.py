# Copyright (c) 2025, Me! and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AirportShopContract(Document):
	def get_default_configs(self):
		default_tax_rate = frappe.db.get_single_value("Airport Shop Configuration", "default_tax_rate")
		default_rent = frappe.db.get_single_value("Airport Shop Configuration", "default_rent_amount")
		return {
			"default_tax_rate": default_tax_rate,
			"default_rent": default_rent
		}
	
	def set_defaults(self):
		configs = self.get_default_configs()
		if not self.tax_rate:
			self.tax_rate = configs["default_tax_rate"]
		if not self.rent_amount:
			self.rent_amount = configs["default_rent_amount"]

	def calculate_total_amount(self):
		self.total_amount = self.rent_amount + (self.rent_amount * self.tax_rate / 100)

	def before_insert(self):
		if not self.tax_rate or not self.rent_amount:
			self.set_defaults()

	def on_submit(self):
		frappe.db.set_value("Airport Shop", self.airport_shop, "status", "Occupied")

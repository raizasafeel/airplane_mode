# Copyright (c) 2025, Me! and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AirportShopContract(Document):
	def get_default_configs(self):
		default_tax_rate = frappe.db.get_value("Airport Setting", fieldname = "default_tax_rate")
		default_rent_amount = frappe.db.get_value("Airport Setting",fieldname =  "default_rent_amount")
		return {
			"default_tax_rate": default_tax_rate,
			"default_rent_amount": default_rent_amount
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

	def before_save(self):
		self.calculate_total_amount()

	def is_shop_occupied(self):
		shop_status = frappe.db.get_value("Airport Shop", self.shop, "status")
		print("\n\n\n", shop_status, self.shop, "\n\n\n")
		if shop_status == "Occupied":
			frappe.throw(f"Shop {self.shop} is already occupied.")

	def on_submit(self):
		self.is_shop_occupied()
		frappe.db.set_value("Airport Shop", self.shop, "status", "Occupied")
		self.date = frappe.utils.nowdate()
		if self.status != "Active":
			frappe.throw("Status must be 'Active' on submission.")

	def on_cancel(self):
		frappe.db.set_value("Airport Shop", self.shop, "status", "Available")

# Copyright (c) 2025, Me! and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from airplane_mode.airplane_mode.set_airport_stats import set_shop_stats

class Airport(Document):
	def fill_in_stats(self):
		if not self.total_shops or not self.occupied_shops or not self.available_shops:
			set_shop_stats(self.name)

	def validate(self):
		self.fill_in_stats()
		

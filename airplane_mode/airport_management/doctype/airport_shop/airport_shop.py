# Copyright (c) 2025, Me! and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
from airplane_mode.airplane_mode.set_airport_stats import set_shop_stats

class AirportShop(WebsiteGenerator):
	def on_update(self):
		if not self.status: 
			self.status = "Available"
		set_shop_stats(self.airport)

	def after_delete(self):
		set_shop_stats(self.airport)
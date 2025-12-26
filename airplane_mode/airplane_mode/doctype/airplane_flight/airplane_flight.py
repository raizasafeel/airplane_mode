# Copyright (c) 2025, Me! and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

class AirplaneFlight(WebsiteGenerator):
	def calculate_eta(self):
		self.eta = self.time_of_departure + frappe.utils.time_diff_in_hours(self.flight_duration)

	def on_submit(self):
		self.status = "Completed"

	def before_save(self):
		self.calculate_eta()
	
# Copyright (c) 2025, Me! and contributors
# For license information, please see license.txt

import frappe
from datetime import timedelta
from frappe.website.website_generator import WebsiteGenerator

class AirplaneFlight(WebsiteGenerator):
	def calculate_eta(self):
		if self.time_of_departure and self.duration:
			# Duration is stored in seconds, convert to timedelta and add to time_of_departure
			duration_timedelta = timedelta(seconds=self.duration)
			# Combine date_of_departure and time_of_departure to get datetime
			departure_datetime = frappe.utils.get_datetime(
				f"{self.date_of_departure} {self.time_of_departure}"
			)
			eta_datetime = departure_datetime + duration_timedelta
			self.eta = eta_datetime.date()

	def on_submit(self):
		self.status = "Completed"

	def before_save(self):
		self.calculate_eta()
	
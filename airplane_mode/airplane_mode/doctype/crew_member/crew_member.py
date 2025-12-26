# Copyright (c) 2025, Me! and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

class CrewMember(Document):
	def set_full_name(self):
		if self.last_name:
			self.full_name = f"{self.first_name} {self.last_name}"
		else:
			self.full_name = self.first_name

	def set_age_from_dob(self):
		if self.date_of_birth:
			dob = getdate(self.date_of_birth)
			today_date = getdate(today())
			self.age = today_date.year - dob.year - ((today_date.month, today_date.day) < (dob.month, dob.day))

	def before_save(self):
		self.set_full_name()
		self.set_age_from_dob()
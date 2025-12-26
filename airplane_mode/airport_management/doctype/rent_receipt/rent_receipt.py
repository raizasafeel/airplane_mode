# Copyright (c) 2025, Me! and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RentReceipt(Document):
	def calculate_due_amount(self):
		self.amount_due = self.total_amount - self.amount_paid

	def paid_amount_is_valid(self):
		if self.amount_paid > self.total_amount:
			frappe.throw(
				title="Invalid Paid Amount",
				msg="Paid amount cannot be greater than total rent."
			)

	def on_submit(self):
		if self.status != "Paid":
			frappe.throw(
				title="Cannot Submit",
				msg="Rent receipt can only be submitted if status is 'Paid'."
			)

	def validate(self):
		self.calculate_due_amount()
		self.paid_amount_is_valid()

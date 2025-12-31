# Copyright (c) 2025, Me! and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data()
	chart = get_chart(data)
	summary = get_summary(data)
	title = get_title()
 
	return columns, data, title, chart, summary

def get_title():
	"""Return the title of the report."""
	return _("Revenue by Airline")

def get_summary(data):
	"""Return the summary of the report."""
	revenue = sum(row[1] for row in data)
	return [{
		"value": revenue,
 		"indicator": "Green" if revenue > 0 else "Red",
 		"label": _("Total Revenue"),
 		"datatype": "Currency",
 		"currency": "INR"
	}]

def get_chart(data: list[list]) -> dict:
	"""Return chart configuration for the report.

	The chart configuration is a dictionary that defines the type of chart,
	labels, datasets, and other options.
	"""
	labels = [row[0] for row in data]
	values = [row[1] for row in data]

	chart = {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": _("Revenue"),
					"values": values,
				}
			],
		},
		"type": "donut",
	}
	return chart

def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"label": _("Airline"),
			"fieldname": "airline",
			"fieldtype": "Link",
			"options": "Airline",
		},
		{
			"label": _("Revenue"),
			"fieldname": "revenue",
			"fieldtype": "Currency",
		},
	]


def get_data() -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	AirplaneTicket = frappe.qb.DocType('Airplane Ticket')
	SubmittedTicket = frappe.qb.from_(AirplaneTicket).select(AirplaneTicket.name, AirplaneTicket.total_amount, AirplaneTicket.flight).where(AirplaneTicket.docstatus == 1)
	Airplane = frappe.qb.DocType('Airplane')
	Flight = frappe.qb.DocType('Airplane Flight')
	Airline = frappe.qb.DocType('Airline')

	query = (
		frappe.qb.from_(Airline)
		.left_join(Airplane).on(Airplane.airline == Airline.name)
		.left_join(Flight).on(Flight.airplane == Airplane.name)
		.left_join(SubmittedTicket).on(SubmittedTicket.flight == Flight.name)
		.select(
			Airline.name.as_('airline'), 
			frappe.qb.functions("Coalesce", frappe.qb.functions("Sum", SubmittedTicket.total_amount), 0).as_('revenue')
			)
		.groupby(Airline.name))

	rows = query.run(as_dict=True)
	return [[r.get('airline'), r.get('revenue')] for r in rows]

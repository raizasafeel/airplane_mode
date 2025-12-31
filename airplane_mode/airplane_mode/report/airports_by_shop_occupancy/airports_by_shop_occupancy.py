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
	title = _("Airports by Shop Occupancy")
	chart = get_chart(data)
	summary = get_summary(data)

	return columns, data, title, chart, summary

def get_chart(data: list[list]) -> dict:
	"""Return chart configuration for the report.

	The chart configuration is a dictionary that defines the type of chart,
	labels, datasets, and other options.
	"""
	labels = [d.name for d in data]
	occupied_shops = [d.occupied_shop_count for d in data]
	available_shops = [d.available_shop_count for d in data]
	total_shops = [d.shop_count for d in data]

	chart = {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": _("Shop Occupancy"),
					"values": occupied_shops,
				},
				{
					"name": _("Available Shops"),
					"values": available_shops,
				},
				{
					"name": _("Total Shops"),
					"values": total_shops,
				},
			],
		},
		"type": "bar",
	}

	return chart


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"label": _("Airport Name"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Airport",
		},
		{
			"label": _("Total Shop Count"),
			"fieldname": "shop_count",
			"fieldtype": "Int",
		},
		{
			"label": _("Occupied Shop Count"),
			"fieldname": "occupied_shop_count",
			"fieldtype": "Int",
		},
		{
			"label": _("Available Shop Count"),
			"fieldname": "available_shop_count",
			"fieldtype": "Int",
		},
	]


def get_summary(data):
	"""Return the summary of the report."""
	available_shops = sum(row.available_shop_count for row in data)
	occupied_shops = sum(row.occupied_shop_count for row in data)
	total_shops = sum(row.shop_count for row in data)
	return [{
		"value": available_shops,
 		"indicator": "Green" if available_shops > 0 else "Red",
 		"label": _("Total Available Shops"),
 		"datatype": "Int",
 	},
	{
		"value": occupied_shops,
 		"indicator": "Green" if occupied_shops > 0 else "Red",
 		"label": _("Total Occupied Shops"),
 		"datatype": "Int",
 	},
	{
		"value": total_shops,
 		"indicator": "Green" if total_shops > 0 else "Red",
 		"label": _("Total Shops"),
 		"datatype": "Int",
 	}]	

def get_data() -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	Airport = frappe.qb.DocType("Airport")
	AirportShop = frappe.qb.DocType("Airport Shop")
	
	query = (
		frappe.qb.from_(AirportShop)
		.right_join(Airport)
		.on(Airport.name == AirportShop.airport)
		.select(
			Airport.name,
			frappe.qb.functions("Coalesce", frappe.qb.functions("Count", AirportShop.name), 0).as_("shop_count"),
			frappe.qb.functions("Coalesce", frappe.qb.functions("Sum", AirportShop.status == "Occupied"), 0).as_("occupied_shop_count"),
			frappe.qb.functions("Coalesce", frappe.qb.functions("Sum", AirportShop.status == "Available"), 0).as_("available_shop_count"),
		)
		.groupby(Airport.name)
	)

	rows = query.run(as_dict=True)
	return rows


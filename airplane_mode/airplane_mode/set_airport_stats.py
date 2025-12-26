import frappe

def get_shop_stats(airport_name):
	occupied_shops = frappe.db.count("Airport Shop", {"airport": airport_name, "Status": "Occupied"})
	available_shops = frappe.db.count("Airport Shop", {"airport": airport_name, "Status": "Available"})
	total_shops = frappe.db.count("Airport Shop", {"airport": airport_name})
	return {
		"occupied": occupied_shops,
		"available": available_shops,
		"total": total_shops
	}

def set_shop_stats(airport_name):
	stats = get_shop_stats(airport_name)
	frappe.db.set_value("Airport", airport_name, "occupied_shops", stats["occupied"])
	frappe.db.set_value("Airport", airport_name, "available_shops", stats["available"])
	frappe.db.set_value("Airport", airport_name, "total_shops", stats["total"])
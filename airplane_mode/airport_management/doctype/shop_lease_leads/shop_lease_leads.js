// Copyright (c) 2025, Me! and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shop Lease Leads", {
	refresh(frm) {
        frm.add_custom_button("Convert into Tenant", () => {
            frappe.new_doc("Airport Tenant", {
                first_name: frm.doc.first_name,
                last_name: frm.doc.last_name,
                phone: frm.doc.phone,
                email: frm.doc.email
            });
            frappe.set_route("Form", "Airport Tenant", frappe.get_last_doc("Airport Tenant").name);
        })
	},
});
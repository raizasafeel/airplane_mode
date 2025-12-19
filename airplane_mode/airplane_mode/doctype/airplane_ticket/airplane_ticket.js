// Copyright (c) 2025, Me! and contributors
// For license information, please see license.txt

frappe.ui.form.on("Airplane Ticket", {
	refresh(frm) {
        frm.add_custom_button("Assign Seats", () => {
            ticket_name = frm.doc.name;
            frappe.prompt({
                label: "Seat",
                fieldname: "seat",
                fieldtype: "Data",
            }, (value) => {
                    frm.set_value("seat", value.seat);
                    frappe.msgprint(`Seat ${value.seat} assigned to ticket ${ticket_name}.`);
                }, "Enter seat number to assign: ", "Submit");
        })
	},
});

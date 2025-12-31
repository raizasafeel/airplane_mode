import frappe
from frappe.utils import getdate, today, add_months

def send_rent_reminders():
    settings = frappe.get_single("Airport Setting")
    if not settings.rent_reminder:
        return
    
    curr_date = getdate(today())

    contracts = frappe.get_all(
        "Airport Shop Contract",
        filters={
            "status": "Active",
            "start_date": ["<=", curr_date],
            "end_date": [">=", curr_date],
        },
        fields=["name", "tenant", "shop", "billing_cycle", "start_date", "end_date"]
    )

    for contract in contracts:
        should_send = False

        # only monthly and yearly billing cycles are supported
        if contract.billing_cycle == "Monthly":
            add_months_count = 1
        else:
            add_months_count = 12

        next_billing_date = add_months(contract.start_date, add_months_count)
        
        if next_billing_date <= contract.end_date:
            should_send = True
        
        if should_send:
            # Get tenant email from Airport Tenant
            tenant_email = frappe.db.get_value("Airport Tenant", contract.tenant, "email")
            contract.email = tenant_email
            send_mail(contract)

def send_mail(contract):
    frappe.sendmail(
        recipients=contract.email,
        subject="Rent Payment Reminder",
        content=f"""
        Dear Tenant,

        This is a reminder that your rent for the shop {contract.shop} is due soon.
        Please ensure that the payment is made on time to avoid any late fees.
        Thank you for your prompt attention to this matter.
        Best regards,
        Airport Management
        """,
        reference_doctype="Airport Shop Contract",
        reference_name=contract.name,
        now=True)


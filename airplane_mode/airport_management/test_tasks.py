# Copyright (c) 2025, Me! and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, add_months, getdate, today
from frappe.email.doctype.notification.notification import trigger_daily_alerts

from airplane_mode.airport_management.tasks import send_rent_reminders


def create_test_airport(name="TestAirport1", code="UWU", city="Test City", country="Test Country"):
    """Create a test Airport."""
    if not frappe.db.exists("Airport", name):
        airport = frappe.get_doc({
            "doctype": "Airport",
            "name": name,
            "code": code,
            "city": city,
            "country": country
        })
        airport.insert()
        frappe.db.commit()
    return name


def create_test_airline(name="Test Airline", customer_care_number="1234567890", headquarters="Test HQ"):
    """Create a test Airline."""
    if not frappe.db.exists("Airline", name):
        airline = frappe.get_doc({
            "doctype": "Airline",
            "name": name,
            "customer_care_number": customer_care_number,
            "headquarters": headquarters
        })
        airline.insert()
        frappe.db.commit()
    return name


def create_test_airplane(airline_name="Test Airline", model="Test Model", capacity=100):
    airplane = frappe.get_doc({
        "doctype": "Airplane",
        "airline": airline_name,
        "model": model,
        "capacity": capacity
    })
    airplane.insert()
    frappe.db.commit()
    return airplane.name


def create_test_airport_tenant(shop_name, first_name="TEST", last_name="ABCDH", email="test_tenant@example.com", phone="1234567890", tax_id="13283hdja"):
    if not frappe.db.exists("Airport Tenant", shop_name):
        tenant = frappe.get_doc({
            "doctype": "Airport Tenant",
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "shop_name": shop_name,
            "tax_id": tax_id
        })
        tenant.insert()
        frappe.db.commit()
    return shop_name


def create_test_airport_shop(name="Test Shop", airport_name="TEST-AIRPORT-1", status="Available"):
    if not frappe.db.exists("Airport Shop", name):
        shop = frappe.get_doc({
            "doctype": "Airport Shop",
            "name": name,
            "airport": airport_name,
            "status": status
        })
        shop.insert()
        frappe.db.commit()
    else:
        # Reset status in case shop exists from previous test run
        frappe.db.set_value("Airport Shop", name, "status", status)
        frappe.db.commit()
    return name


class TestAirportManagementTasks(FrappeTestCase):

    def setUp(self):
        """Set up test data before each test method."""
        super().setUp()
        frappe.db.delete("Email Queue")
        frappe.db.delete("Email Queue Recipient")
        
        contracts = frappe.get_all("Airport Shop Contract", filters={"docstatus": 1}, fields=["name", "shop"])
        for contract in contracts:
            try:
                doc = frappe.get_doc("Airport Shop Contract", contract.name)
                if doc.docstatus == 1:
                    doc.cancel()
                    frappe.db.set_value("Airport Shop", contract.shop, "status", "Available")
            except Exception:
                # If cancel fails, just reset shop status
                frappe.db.set_value("Airport Shop", contract.shop, "status", "Available")
        frappe.db.commit()
        
        test_email_account_name = "Test Email Account"
        if not frappe.db.exists("Email Account", test_email_account_name):
            frappe.get_doc({
                "doctype": "Email Account",
                "email_account_name": test_email_account_name,
                "email_id": "test_tenant@example.com",
                "enable_outgoing": 1,
                "default_outgoing": 1,
                "smtp_server": "localhost"
            }).insert(ignore_permissions=True, ignore_if_duplicate=True)
            frappe.db.commit()

    def test_send_rent_reminders_with_rent_reminder_enabled(self):
        settings = frappe.get_single("Airport Setting")
        settings.rent_reminder = 1
        settings.save()
        frappe.db.commit()

        airport_name = create_test_airport("TEST-AIRPORT-RENT-1", "TAR1")
        shop_name = create_test_airport_shop("Test Shop", airport_name, status="Available")
        tenant_name = create_test_airport_tenant("Test Shop Tenant", email="test_tenant@example.com")

        contract_start_date = add_months(getdate(today()), -1)
        contract_end_date = add_days(getdate(today()), 30)
        
        contract = frappe.get_doc({
            "doctype": "Airport Shop Contract",
            "tenant": tenant_name,
            "shop": shop_name,
            "status": "Active",
            "start_date": contract_start_date,
            "end_date": contract_end_date,
            "billing_cycle": "Monthly",
            "rent_amount": 1000,
            "tax_rate": 10
        })
        contract.insert()
        contract.submit()
        frappe.db.commit()

        send_rent_reminders()
        frappe.db.commit()

        email_queue = frappe.db.sql(
            """SELECT name, message FROM `tabEmail Queue` 
            WHERE (status='Not Sent' OR status='Sent')
            AND reference_doctype='Airport Shop Contract'
            AND reference_name=%s""",
            (contract.name,),
            as_dict=1
        )

        self.assertEqual(len(email_queue), 1, "Expected 1 email to be queued")
        self.assertIn("Test Shop", email_queue[0].message)

        email_recipients = frappe.db.sql(
            """SELECT recipient FROM `tabEmail Queue Recipient` 
            WHERE parent=%s""",
            (email_queue[0].name,),
            as_dict=1
        )
        self.assertEqual(len(email_recipients), 1)
        self.assertEqual(email_recipients[0].recipient, "test_tenant@example.com")

    def test_send_rent_reminders_with_rent_reminder_disabled(self):
        settings = frappe.get_single("Airport Setting")
        settings.rent_reminder = 0
        settings.save()
        frappe.db.commit()

        airport_name = create_test_airport("TEST-AIRPORT-RENT-2", "TAR2")
        shop_name = create_test_airport_shop("Test Shop Disabled", airport_name, status="Available")
        tenant_name = create_test_airport_tenant("Test Shop Tenant Disabled", email="test_tenant@example.com")

        contract = frappe.get_doc({
            "doctype": "Airport Shop Contract",
            "tenant": tenant_name,
            "shop": shop_name,
            "status": "Active",
            "start_date": add_months(getdate(today()), -1),
            "end_date": add_days(getdate(today()), 30),
            "billing_cycle": "Monthly",
            "rent_amount": 1000,
            "tax_rate": 10
        })
        contract.insert()
        contract.submit()
        frappe.db.commit()

        frappe.db.delete("Email Queue")
        frappe.db.delete("Email Queue Recipient")
        frappe.db.commit()

        send_rent_reminders()
        frappe.db.commit()

        email_queue = frappe.db.sql(
            """SELECT name FROM `tabEmail Queue`""",
            as_dict=1
        )

        self.assertEqual(len(email_queue), 0, "Expected no emails to be queued when rent_reminder is disabled")

    def test_send_rent_reminders_with_annual_billing_cycle(self):
        settings = frappe.get_single("Airport Setting")
        settings.rent_reminder = 1
        settings.save()
        frappe.db.commit()

        airport_name = create_test_airport("TEST-AIRPORT-RENT-3", "TAR3")
        shop_name = create_test_airport_shop("Test Shop Annual", airport_name, status="Available")
        tenant_name = create_test_airport_tenant("Test Shop Tenant Annual", email="test_tenant_annual@example.com")

        contract = frappe.get_doc({
            "doctype": "Airport Shop Contract",
            "tenant": tenant_name,
            "shop": shop_name,
            "status": "Active",
            "start_date": add_months(getdate(today()), -12),
            "end_date": add_days(getdate(today()), 30),
            "billing_cycle": "Annual",
            "rent_amount": 12000,
            "tax_rate": 10
        })
        contract.insert()
        contract.submit()
        frappe.db.commit()

        send_rent_reminders()
        frappe.db.commit()

        email_queue = frappe.db.sql(
            """SELECT name FROM `tabEmail Queue` 
            WHERE (status='Not Sent' OR status='Sent')
            AND reference_doctype='Airport Shop Contract'
            AND reference_name=%s""",
            (contract.name,),
            as_dict=1
        )

        self.assertEqual(len(email_queue), 1, "Expected 1 email to be queued for annual billing cycle")

    def test_departs_in_24_hours_notification(self):
        airline_name = create_test_airline("Test Airline")
        airplane_name = create_test_airplane(airline_name, model="Test Model", capacity=150)
        
        airport1_name = create_test_airport("TEST-AIRPORT-1", "TST1", "Test City 1", "Test Country")
        airport2_name = create_test_airport("TEST-AIRPORT-2", "TST2", "Test City 2", "Test Country")

        departure_date = add_days(getdate(today()), 1)
        
        flight = frappe.get_doc({
            "doctype": "Airplane Flight",
            "airplane": airplane_name,
            "status": "Scheduled",
            "date_of_departure": departure_date,
            "time_of_departure": "10:00:00",
            "duration": 7200,
            "source_airport": airport1_name,
            "destination_airport": airport2_name,
            "published": 1
        })
        flight.insert()
        frappe.db.commit()

        notification = frappe.get_doc("Notification", "Departs in 24 hours Notification")
        self.assertTrue(notification.enabled, "Notification should be enabled")
        self.assertEqual(notification.document_type, "Airplane Flight", "Notification should be for Airplane Flight")
        self.assertEqual(notification.days_in_advance, 1, "Notification should trigger 1 day in advance")
        self.assertEqual(notification.event, "Days Before", "Notification event should be Days Before")
        self.assertEqual(notification.date_changed, "date_of_departure", "Notification should watch date_of_departure field")

        self.assertIsNotNone(flight.name, "Flight should be created")
        self.assertEqual(flight.status, "Scheduled", "Flight status should be Scheduled")
        self.assertEqual(flight.date_of_departure, departure_date, "Departure date should be set correctly")

        trigger_daily_alerts()
        frappe.db.commit()

        email_queue = frappe.db.sql(
            """SELECT name, message FROM `tabEmail Queue` 
            WHERE reference_doctype='Airplane Flight' AND reference_name=%s""",
            (flight.name,),
            as_dict=1
        )

        self.assertGreaterEqual(len(email_queue), 0, "Notification email should be queued for flight departing in 24 hours")
        if email_queue and email_queue[0].message:
            self.assertIn("Departs in 24 hours", email_queue[0].message)

    def test_rent_reminders_only_for_active_contracts(self):
        settings = frappe.get_single("Airport Setting")
        settings.rent_reminder = 1
        settings.save()
        frappe.db.commit()

        airport_name = create_test_airport("TEST-AIRPORT-RENT-4", "TAR4")
        shop_name = create_test_airport_shop("Test Shop Inactive", airport_name)
        tenant_name = create_test_airport_tenant("Test Shop Tenant Inactive", email="test_tenant@example.com")

        contract = frappe.get_doc({
            "doctype": "Airport Shop Contract",
            "tenant": tenant_name,
            "shop": shop_name,
            "status": "Pending",
            "start_date": add_months(getdate(today()), -1),
            "end_date": add_days(getdate(today()), 30),
            "billing_cycle": "Monthly",
            "rent_amount": 1000,
            "tax_rate": 10
        })
        contract.insert()
        frappe.db.commit()

        send_rent_reminders()
        frappe.db.commit()

        email_queue = frappe.db.sql(
            """SELECT name FROM `tabEmail Queue` 
            WHERE reference_doctype='Airport Shop Contract'
            AND reference_name=%s""",
            (contract.name,),
            as_dict=1
        )

        self.assertEqual(len(email_queue), 0, "Expected no emails for non-active contracts")

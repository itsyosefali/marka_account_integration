import frappe
from frappe import _
from frappe.utils import now, flt, cstr, nowdate, getdate
from frappe.frappeclient import FrappeClient
from erpnext.accounts.party import get_party_account
from erpnext.accounts.utils import get_account_currency
from erpnext.setup.utils import get_exchange_rate
import erpnext

@frappe.whitelist()
def create_customer_if_not_exists(customer_name):
    """Create customer if it doesn't exist"""
    if not frappe.db.exists("Customer", customer_name):
        customer_doc = frappe.new_doc("Customer")
        customer_doc.customer_name = customer_name
        customer_doc.customer_type = "Individual"
        customer_doc.insert()
        return customer_doc.name
    return customer_name


def create_supplier_if_not_exists(supplier_name):
    """Create supplier if it doesn't exist"""
    if not frappe.db.exists("Supplier", supplier_name):
        supplier_doc = frappe.new_doc("Supplier")
        supplier_doc.supplier_name = supplier_name
        supplier_doc.supplier_type = "Individual"
        supplier_doc.insert()
        return supplier_doc.name
    return supplier_name


def create_item_if_not_exists(item_code, item_name=None, item_group="All Item Groups"):
    """Create item if it doesn't exist"""
    if not frappe.db.exists("Item", item_code):
        item_doc = frappe.new_doc("Item")
        item_doc.item_code = item_code
        item_doc.item_name = item_name or item_code
        item_doc.item_group = item_group
        item_doc.is_stock_item = 1
        item_doc.is_sales_item = 1
        item_doc.is_purchase_item = 1
        item_doc.insert()
        return item_doc.name
    return item_code


# Sales Invoice CRUD
@frappe.whitelist()
def create_sales_invoice(customer, items, posting_date=None, due_date=None, vat_rate=None, vat_account_head=None, vat_description=None, **kwargs):
    """Create a new Sales Invoice"""
    try:
        customer = create_customer_if_not_exists(customer)
        
        doc = frappe.new_doc("Sales Invoice")
        doc.customer = customer
        doc.posting_date = posting_date or now()
        doc.due_date = due_date or now()
        
        for item in items:
            item_code = create_item_if_not_exists(
                item.get("item_code"),
                item.get("item_name"),
                item.get("item_group", "All Item Groups")
            )
            
            doc.append("items", {
                "item_code": item_code,
                "qty": item.get("qty", 1),
                "rate": item.get("rate", 0),
                "amount": flt(item.get("qty", 1)) * flt(item.get("rate", 0))
            })
        
        if vat_rate is not None:
            doc.append("taxes", {
                "charge_type": "On Net Total",
                "account_head": vat_account_head or "VAT 5% - M",
                "description": vat_description or "VAT",
                "rate": flt(vat_rate),
                "tax_amount": 0
            })
        
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        doc.insert()
        doc.submit()
        
        return {
            "status": "success",
            "message": _("Sales Invoice created successfully"),
            "name": doc.name
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def get_sales_invoice(name):
    """Get Sales Invoice by name"""
    try:
        doc = frappe.get_doc("Sales Invoice", name)
        return {
            "status": "success",
            "data": doc.as_dict()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def update_sales_invoice(name, **kwargs):
    """Update Sales Invoice"""
    try:
        doc = frappe.get_doc("Sales Invoice", name)
        
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        doc.save()
        doc.submit()
        
        return {
            "status": "success",
            "message": _("Sales Invoice updated successfully"),
            "name": doc.name
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def delete_sales_invoice(name):
    """Delete Sales Invoice"""
    try:
        doc = frappe.get_doc("Sales Invoice", name)
        
        if doc.docstatus == 1:
            doc.cancel()
        
        frappe.delete_doc("Sales Invoice", name)
        
        return {
            "status": "success",
            "message": _("Sales Invoice deleted successfully")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# Purchase Invoice CRUD
@frappe.whitelist()
def create_purchase_invoice(supplier, items, posting_date=None, due_date=None, vat_rate=None, vat_account_head=None, vat_description=None, **kwargs):
    """Create a new Purchase Invoice"""
    try:
        supplier = create_supplier_if_not_exists(supplier)
        
        doc = frappe.new_doc("Purchase Invoice")
        doc.supplier = supplier
        doc.posting_date = posting_date or now()
        doc.due_date = due_date or now()
        
        for item in items:
            item_code = create_item_if_not_exists(
                item.get("item_code"),
                item.get("item_name"),
                item.get("item_group", "All Item Groups")
            )
            
            doc.append("items", {
                "item_code": item_code,
                "qty": item.get("qty", 1),
                "rate": item.get("rate", 0),
                "amount": flt(item.get("qty", 1)) * flt(item.get("rate", 0))
            })
        
        # Add VAT if provided
        if vat_rate is not None:
            doc.append("taxes", {
                "charge_type": "On Net Total",
                "account_head": vat_account_head or "VAT - UAE",
                "description": vat_description or "VAT",
                "rate": flt(vat_rate),
                "tax_amount": 0
            })
        
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        doc.insert()
        doc.submit()
        
        return {
            "status": "success",
            "message": _("Purchase Invoice created successfully"),
            "name": doc.name
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def get_purchase_invoice(name):
    """Get Purchase Invoice by name"""
    try:
        doc = frappe.get_doc("Purchase Invoice", name)
        return {
            "status": "success",
            "data": doc.as_dict()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def update_purchase_invoice(name, **kwargs):
    """Update Purchase Invoice"""
    try:
        doc = frappe.get_doc("Purchase Invoice", name)
        
        if doc.docstatus == 1:
            doc.cancel()
            doc = frappe.get_doc("Purchase Invoice", name)
        
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        doc.save()
        doc.submit()
        
        return {
            "status": "success",
            "message": _("Purchase Invoice updated successfully"),
            "name": doc.name
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def delete_purchase_invoice(name):
    """Delete Purchase Invoice"""
    try:
        doc = frappe.get_doc("Purchase Invoice", name)
        
        if doc.docstatus == 1:
            doc.cancel()
        
        frappe.delete_doc("Purchase Invoice", name)
        
        return {
            "status": "success",
            "message": _("Purchase Invoice deleted successfully")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# Payment Entry CRUD
@frappe.whitelist()
def create_payment_entry(party_type, party, paid_amount, mode_of_payment=None, company=None, 
                        posting_date=None, reference_no=None, reference_date=None, 
                        references=None, cost_center=None, remarks=None, submit=False, **kwargs):
    """
    Create a new Payment Entry using ERPNext's utilities
    
    Args:
        party_type (str): "Customer" or "Supplier"
        party (str): Party name
        paid_amount (float): Amount to pay/receive
        mode_of_payment (str, optional): Mode of payment (required for bank account lookup)
        company (str, optional): Company name (defaults to default company)
        posting_date (str, optional): Posting date (defaults to today)
        reference_no (str, optional): Reference number
        reference_date (str, optional): Reference date
        references (list, optional): List of reference documents to allocate against
        cost_center (str, optional): Cost center
        remarks (str, optional): Remarks/notes
        submit (bool, optional): Whether to submit the payment entry (default: False)
        **kwargs: Additional fields to set on the payment entry
    """
    try:
        if party_type == "Customer":
            party = create_customer_if_not_exists(party)
        elif party_type == "Supplier":
            party = create_supplier_if_not_exists(party)
        
        if not company:
            company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
        
        if not company:
            frappe.throw(_("Company is required"))
        
        posting_date = posting_date or nowdate()
        reference_date = getdate(reference_date) if reference_date else getdate(posting_date)
        
        payment_type = "Receive" if party_type == "Customer" else "Pay"
        
        party_account = get_party_account(party_type, party, company)
        party_account_currency = get_account_currency(party_account)
        
        bank_account = None
        bank_account_currency = None
        
        if mode_of_payment:
            bank_account = frappe.db.get_value(
                "Mode of Payment Account",
                {"parent": mode_of_payment, "company": company},
                "default_account"
            )
        
        if not bank_account:
            bank_account = frappe.db.get_value(
                "Account",
                {"company": company, "account_type": "Cash", "is_group": 0},
                "name"
            )
            
        if not bank_account:
            bank_account = frappe.db.get_value(
                "Account",
                {"company": company, "account_type": "Bank", "is_group": 0},
                "name"
            )
        
        if not bank_account:
            frappe.throw(_("Please specify mode_of_payment or ensure a default Cash/Bank account exists for company {0}").format(company))
        
        bank_account_currency = get_account_currency(bank_account)
        
        company_currency = frappe.get_cached_value("Company", company, "default_currency")
        
        source_exchange_rate = 1.0
        target_exchange_rate = 1.0
        
        if payment_type == "Receive":
            paid_from_currency = party_account_currency
            paid_to_currency = bank_account_currency
            
            if party_account_currency != company_currency:
                source_exchange_rate = get_exchange_rate(party_account_currency, company_currency, posting_date)
            if bank_account_currency != company_currency:
                target_exchange_rate = get_exchange_rate(bank_account_currency, company_currency, posting_date)
                
        else: 
            paid_from_currency = bank_account_currency
            paid_to_currency = party_account_currency
            
            if bank_account_currency != company_currency:
                source_exchange_rate = get_exchange_rate(bank_account_currency, company_currency, posting_date)
            if party_account_currency != company_currency:
                target_exchange_rate = get_exchange_rate(party_account_currency, company_currency, posting_date)

        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = payment_type
        pe.company = company
        pe.posting_date = posting_date
        pe.reference_date = reference_date
        pe.mode_of_payment = mode_of_payment
        pe.party_type = party_type
        pe.party = party
        pe.cost_center = cost_center or erpnext.get_default_cost_center(company)
        
        if payment_type == "Receive":
            pe.paid_from = party_account
            pe.paid_to = bank_account
            pe.paid_from_account_currency = party_account_currency
            pe.paid_to_account_currency = bank_account_currency
        else:  # Pay
            pe.paid_from = bank_account
            pe.paid_to = party_account
            pe.paid_from_account_currency = bank_account_currency
            pe.paid_to_account_currency = party_account_currency
        
        pe.source_exchange_rate = source_exchange_rate
        pe.target_exchange_rate = target_exchange_rate
        
        pe.paid_amount = flt(paid_amount)
        pe.received_amount = flt(paid_amount)
        
        if reference_no:
            pe.reference_no = reference_no
        if remarks:
            pe.remarks = remarks
        
        if references:
            for ref in references:
                pe.append("references", {
                    "reference_doctype": ref.get("reference_doctype"),
                    "reference_name": ref.get("reference_name"),
                    "allocated_amount": flt(ref.get("allocated_amount", 0)),
                    "outstanding_amount": flt(ref.get("outstanding_amount", 0)),
                    "total_amount": flt(ref.get("total_amount", 0))
                })
        
        for key, value in kwargs.items():
            if hasattr(pe, key):
                setattr(pe, key, value)
        
        pe.setup_party_account_field()
        pe.set_missing_values()
        pe.set_amounts()
        
        pe.insert()
        
        pe.submit()
        
        return {
            "status": "success",
            "message": _("Payment Entry {0} successfully").format("created and submitted" if submit else "created"),
            "name": pe.name,
            "docstatus": pe.docstatus
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Payment Entry Creation Error"))
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def create_payment_entry_from_invoice(invoice_doctype, invoice_name, paid_amount=None, 
                                     mode_of_payment=None, submit=False, **kwargs):
    """
    Create Payment Entry from an existing Sales Invoice or Purchase Invoice
    using ERPNext's built-in get_payment_entry method
    
    Args:
        invoice_doctype (str): "Sales Invoice" or "Purchase Invoice"
        invoice_name (str): Name of the invoice
        paid_amount (float, optional): Amount to pay (defaults to outstanding amount)
        mode_of_payment (str, optional): Mode of payment
        submit (bool, optional): Whether to submit the payment entry (default: False)
        **kwargs: Additional fields to set on the payment entry
    
    Returns:
        dict: Status and payment entry details
    """
    try:
        from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry as erpnext_get_payment_entry
        
        # Validate invoice doctype
        if invoice_doctype not in ["Sales Invoice", "Purchase Invoice"]:
            frappe.throw(_("invoice_doctype must be 'Sales Invoice' or 'Purchase Invoice'"))
        
        # Check if invoice exists
        if not frappe.db.exists(invoice_doctype, invoice_name):
            frappe.throw(_("{0} {1} does not exist").format(invoice_doctype, invoice_name))
        
        # Use ERPNext's built-in method to create payment entry
        pe = erpnext_get_payment_entry(
            dt=invoice_doctype,
            dn=invoice_name,
            party_amount=paid_amount,
            bank_account=None
        )
        
        # Set mode of payment if provided
        if mode_of_payment:
            pe.mode_of_payment = mode_of_payment
            
            # Update bank account based on mode of payment
            invoice_doc = frappe.get_doc(invoice_doctype, invoice_name)
            bank_account = frappe.db.get_value(
                "Mode of Payment Account",
                {"parent": mode_of_payment, "company": invoice_doc.company},
                "default_account"
            )
            if bank_account:
                if pe.payment_type == "Receive":
                    pe.paid_to = bank_account
                    pe.paid_to_account_currency = frappe.db.get_value("Account", bank_account, "account_currency")
                else:
                    pe.paid_from = bank_account
                    pe.paid_from_account_currency = frappe.db.get_value("Account", bank_account, "account_currency")
        
        # Set additional fields from kwargs
        for key, value in kwargs.items():
            if hasattr(pe, key):
                setattr(pe, key, value)
        
        # Recalculate amounts if mode of payment changed
        if mode_of_payment:
            pe.set_amounts()
        
        # Insert the payment entry
        pe.insert()
        
        # Submit if requested
        if submit:
            pe.submit()
        
        return {
            "status": "success",
            "message": _("Payment Entry {0} successfully from {1} {2}").format(
                "created and submitted" if submit else "created",
                invoice_doctype,
                invoice_name
            ),
            "name": pe.name,
            "docstatus": pe.docstatus,
            "payment_type": pe.payment_type,
            "paid_amount": pe.paid_amount,
            "received_amount": pe.received_amount
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Payment Entry from Invoice Creation Error"))
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def get_payment_entry(name):
    """Get Payment Entry by name"""
    try:
        doc = frappe.get_doc("Payment Entry", name)
        return {
            "status": "success",
            "data": doc.as_dict()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def update_payment_entry(name, **kwargs):
    """Update Payment Entry"""
    try:
        doc = frappe.get_doc("Payment Entry", name)
        
        if doc.docstatus == 1:
            doc.cancel()
            doc = frappe.get_doc("Payment Entry", name)
        
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        doc.save()
        doc.submit()
        
        return {
            "status": "success",
            "message": _("Payment Entry updated successfully"),
            "name": doc.name
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def delete_payment_entry(name):
    """Delete Payment Entry"""
    try:
        doc = frappe.get_doc("Payment Entry", name)
        
        if doc.docstatus == 1:
            doc.cancel()
        
        frappe.delete_doc("Payment Entry", name)
        
        return {
            "status": "success",
            "message": _("Payment Entry deleted successfully")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# Report mapping for different report types
REPORT_MAPPING = {
    "general_ledger": "General Ledger",
    "profit_loss": "Profit and Loss Statement", 
    "cash_flow": "Cash Flow",
    "payables": "Accounts Payable",
    "receivables": "Accounts Receivable",
    "payables_summary": "Payables Summary",
    "receivables_summary": "Receivables Summary",
    "trial_balance": "Trial Balance",
    "balance_sheet": "Balance Sheet",
    "vat_report": "VAT Report"
}

@frappe.whitelist()
def login_and_open_general_ledger(company=None, from_date=None, to_date=None, account=None):
    """Legacy function - redirects to the new general report function"""
    return open_report(
        report_type="general_ledger",
        company=company,
        from_date=from_date,
        to_date=to_date,
        account=account
    )

@frappe.whitelist()
def open_report(report_type=None, company=None, from_date=None, to_date=None, account=None, **kwargs):
    """
    General endpoint to open any of the specified reports
    
    Args:
        report_type (str): Type of report to open. Options:
            - general_ledger: General Ledger
            - profit_loss: Gross Profit and Loss Account
            - cash_flow: Cash Flow
            - payables: Report Payables
            - receivables: Report Receivables
            - payables_summary: Report Payables Summary
            - receivables_summary: Report Receivables Summary
            - trial_balance: Trial Balance
            - balance_sheet: Balance Sheet
            - vat_report: VAT Report
        company (str, optional): Company filter
        from_date (str, optional): From date filter
        to_date (str, optional): To date filter
        account (str, optional): Account filter
        **kwargs: Additional parameters for specific reports
    """
    try:
        # Check if report_type is provided
        if not report_type:
            frappe.throw("Report type is required")
        
        # Validate report type
        if report_type not in REPORT_MAPPING:
            available_reports = ", ".join(REPORT_MAPPING.keys())
            frappe.throw(f"Invalid report type '{report_type}'. Available options: {available_reports}")
        
        settings = frappe.get_doc(
            "Merka Account Settings", "Merka Account Settings",
        )
        username = settings.user_email
        password = settings.user_password
        site_url = frappe.utils.get_url()
        
        if not frappe.db.exists("User", username):
            frappe.throw(f"User {username} does not exist in the system")
        
        if not username:
            frappe.throw("User email not found in Merka Account Settings")
        if not password:
            frappe.throw("User password not found in Merka Account Settings")
        
        client = FrappeClient(url=site_url, username=username, password=password, verify=True)
        
        sid = client.session.cookies.get('sid')
        
        if not sid:
            frappe.throw("Failed to get session ID. Please check credentials.")
        
        # Get the report name from mapping
        report_name = REPORT_MAPPING[report_type]
        
        # Determine the correct URL path based on report type
        if report_type in ["general_ledger", "profit_loss", "trial_balance", "balance_sheet"]:
            # Query reports
            report_url = f"{site_url}/app/query-report/{report_name.replace(' ', '%20')}"
        elif report_type in ["cash_flow", "payables", "receivables", "payables_summary", "receivables_summary", "vat_report"]:
            # Script reports
            report_url = f"{site_url}/app/query-report/{report_name.replace(' ', '%20')}"
        else:
            # Default to query report
            report_url = f"{site_url}/app/query-report/{report_name.replace(' ', '%20')}"
        
        # Build parameters
        params = []
        if company:
            params.append(f"company={company}")
        if from_date:
            params.append(f"from_date={from_date}")
        if to_date:
            params.append(f"to_date={to_date}")
        if account:
            params.append(f"account={account}")
        
        # Add any additional parameters (exclude cmd and sid as they shouldn't be passed to the report)
        excluded_params = ['cmd', 'sid', 'report_type']
        for key, value in kwargs.items():
            if value is not None and key not in excluded_params:
                params.append(f"{key}={value}")
        
        # Add session ID
        params.append(f"sid={sid}")
        
        if params:
            report_url += "?" + "&".join(params)
        
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = report_url
        frappe.local.response["http_status_code"] = 302
        
        return {
            "status": "success",
            "message": f"Redirecting to {report_name}",
            "report_type": report_type,
            "report_name": report_name,
            "url": report_url
        }
        
    except Exception as e:
        frappe.throw(f"Failed to login and redirect to {report_type}: {str(e)}")

# Journal Entry CRUD
@frappe.whitelist()
def create_journal_entry(company, posting_date=None, voucher_type="Journal Entry", accounts=None, user_remark=None, **kwargs):
    """
    Create a new Journal Entry with mandatory fields validation
    
    Args:
        company (str): Company name (mandatory)
        posting_date (str, optional): Posting date (defaults to current date)
        voucher_type (str, optional): Entry type (defaults to "Journal Entry")
        accounts (list): List of account entries with debit/credit amounts (mandatory)
        user_remark (str, optional): User remark
        **kwargs: Additional fields like title, reference, etc.
    
    Account entries format:
        accounts = [
            {
                "account": "Account Name",
                "debit_in_account_currency": 1000.0,  # Either debit or credit must be provided
                "credit_in_account_currency": 0.0,
                "cost_center": "Main - Company",  # Optional
                "party_type": "Customer",  # Optional for receivable/payable accounts
                "party": "Customer Name",  # Optional
                "user_remark": "Description"  # Optional
            },
            {
                "account": "Another Account",
                "debit_in_account_currency": 0.0,
                "credit_in_account_currency": 1000.0,
                "cost_center": "Main - Company"
            }
        ]
    """
    try:
        # Validate mandatory fields
        if not company:
            frappe.throw(_("Company is mandatory for Journal Entry"))
        
        if not accounts or len(accounts) < 2:
            frappe.throw(_("At least 2 account entries are required for Journal Entry"))
        
        # Validate company exists
        if not frappe.db.exists("Company", company):
            frappe.throw(_("Company {0} does not exist").format(company))
        
        # Create Journal Entry document
        doc = frappe.new_doc("Journal Entry")
        doc.company = company
        doc.posting_date = posting_date or now()
        doc.voucher_type = voucher_type
        doc.user_remark = user_remark
        
        # Set additional fields from kwargs
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        # Add account entries
        total_debit = 0
        total_credit = 0
        
        for account_entry in accounts:
            # Validate account entry
            if not account_entry.get("account"):
                frappe.throw(_("Account is mandatory for each entry"))
            
            # Validate account exists
            if not frappe.db.exists("Account", account_entry.get("account")):
                frappe.throw(_("Account {0} does not exist").format(account_entry.get("account")))
            
            debit_amount = flt(account_entry.get("debit_in_account_currency", 0))
            credit_amount = flt(account_entry.get("credit_in_account_currency", 0))
            
            # Validate that either debit or credit is provided, but not both
            if debit_amount and credit_amount:
                frappe.throw(_("Account {0}: Cannot have both debit and credit amounts").format(account_entry.get("account")))
            
            if not debit_amount and not credit_amount:
                frappe.throw(_("Account {0}: Either debit or credit amount is required").format(account_entry.get("account")))
            
            # Add to totals
            total_debit += debit_amount
            total_credit += credit_amount
            
            # Create account entry
            account_row = doc.append("accounts", {
                "account": account_entry.get("account"),
                "debit_in_account_currency": debit_amount,
                "credit_in_account_currency": credit_amount,
                "cost_center": account_entry.get("cost_center"),
                "party_type": account_entry.get("party_type"),
                "party": account_entry.get("party"),
                "user_remark": account_entry.get("user_remark"),
                "reference_type": account_entry.get("reference_type"),
                "reference_name": account_entry.get("reference_name"),
                "project": account_entry.get("project")
            })
        
        # Validate debit and credit balance
        if abs(total_debit - total_credit) > 0.01:  # Allow for small rounding differences
            frappe.throw(_("Total debit amount ({0}) must equal total credit amount ({1})").format(total_debit, total_credit))
        
        # Insert and submit the document
        doc.insert()
        doc.submit()
        
        return {
            "status": "success",
            "message": _("Journal Entry created successfully"),
            "name": doc.name,
            "total_debit": total_debit,
            "total_credit": total_credit
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def get_journal_entry(name):
    """Get Journal Entry by name"""
    try:
        doc = frappe.get_doc("Journal Entry", name)
        return {
            "status": "success",
            "data": doc.as_dict()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def update_journal_entry(name, accounts=None, **kwargs):
    """Update Journal Entry"""
    try:
        doc = frappe.get_doc("Journal Entry", name)
        
        # Cancel if submitted
        if doc.docstatus == 1:
            doc.cancel()
            doc = frappe.get_doc("Journal Entry", name)
        
        # Update accounts if provided
        if accounts:
            # Clear existing accounts
            doc.accounts = []
            
            # Validate and add new accounts
            total_debit = 0
            total_credit = 0
            
            for account_entry in accounts:
                if not account_entry.get("account"):
                    frappe.throw(_("Account is mandatory for each entry"))
                
                if not frappe.db.exists("Account", account_entry.get("account")):
                    frappe.throw(_("Account {0} does not exist").format(account_entry.get("account")))
                
                debit_amount = flt(account_entry.get("debit_in_account_currency", 0))
                credit_amount = flt(account_entry.get("credit_in_account_currency", 0))
                
                if debit_amount and credit_amount:
                    frappe.throw(_("Account {0}: Cannot have both debit and credit amounts").format(account_entry.get("account")))
                
                if not debit_amount and not credit_amount:
                    frappe.throw(_("Account {0}: Either debit or credit amount is required").format(account_entry.get("account")))
                
                total_debit += debit_amount
                total_credit += credit_amount
                
                doc.append("accounts", {
                    "account": account_entry.get("account"),
                    "debit_in_account_currency": debit_amount,
                    "credit_in_account_currency": credit_amount,
                    "cost_center": account_entry.get("cost_center"),
                    "party_type": account_entry.get("party_type"),
                    "party": account_entry.get("party"),
                    "user_remark": account_entry.get("user_remark"),
                    "reference_type": account_entry.get("reference_type"),
                    "reference_name": account_entry.get("reference_name"),
                    "project": account_entry.get("project")
                })
            
            if abs(total_debit - total_credit) > 0.01:
                frappe.throw(_("Total debit amount ({0}) must equal total credit amount ({1})").format(total_debit, total_credit))
        
        # Update other fields
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        doc.save()
        doc.submit()
        
        return {
            "status": "success",
            "message": _("Journal Entry updated successfully"),
            "name": doc.name
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
@frappe.whitelist()
def get_available_reports():
    """
    Get list of available reports with their descriptions
    """
    return {
        "status": "success",
        "reports": [
            {
                "type": "general_ledger",
                "name": "General Ledger",
                "description": "General Ledger report showing all account transactions"
            },
            {
                "type": "profit_loss", 
                "name": "Profit and Loss Statement",
                "description": "Gross Profit and Loss Account report"
            },
            {
                "type": "cash_flow",
                "name": "Cash Flow",
                "description": "Cash flow statement report"
            },
            {
                "type": "payables",
                "name": "Accounts Payable", 
                "description": "Report showing outstanding payables"
            },
            {
                "type": "receivables",
                "name": "Accounts Receivable",
                "description": "Report showing outstanding receivables"
            },
            {
                "type": "payables_summary",
                "name": "Payables Summary",
                "description": "Summary report of all payables"
            },
            {
                "type": "receivables_summary", 
                "name": "Receivables Summary",
                "description": "Summary report of all receivables"
            },
            {
                "type": "trial_balance",
                "name": "Trial Balance",
                "description": "Trial balance report"
            },
            {
                "type": "balance_sheet",
                "name": "Balance Sheet", 
                "description": "Balance sheet report"
            },
            {
                "type": "vat_report",
                "name": "VAT Report",
                "description": "VAT report for tax compliance"
            }
        ]
    }


@frappe.whitelist(allow_guest=True)
def open_hr_module():
    """
    Opens the HR module (app/hr) using HR user credentials from Merka Account Settings
    """
    try:
        # Get HR credentials from settings
        settings = frappe.get_doc(
            "Merka Account Settings", "Merka Account Settings",
        )
        hr_email = settings.hr_email
        hr_password = settings.hr_password
        site_url = frappe.utils.get_url()
        
        # Validate HR credentials
        if not hr_email:
            frappe.throw("HR email not found in Merka Account Settings")
        if not hr_password:
            frappe.throw("HR password not found in Merka Account Settings")
        
        # Validate user exists
        if not frappe.db.exists("User", hr_email):
            frappe.throw(f"User {hr_email} does not exist in the system")
        
        # Login using FrappeClient
        client = FrappeClient(url=site_url, username=hr_email, password=hr_password, verify=True)
        
        # Get session ID
        sid = client.session.cookies.get('sid')
        
        if not sid:
            frappe.throw("Failed to get session ID. Please check HR credentials.")
        
        # Build HR module URL
        hr_url = f"{site_url}/app/hr?sid={sid}"
        
        # Set redirect response
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = hr_url
        frappe.local.response["http_status_code"] = 302
        
        return {
            "status": "success",
            "message": "Redirecting to HR module",
            "url": hr_url
        }
        
    except Exception as e:
        frappe.throw(f"Failed to open HR module: {str(e)}")
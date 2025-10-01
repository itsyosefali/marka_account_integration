import frappe
from frappe import _
from frappe.utils import now, flt, cstr
from frappe.frappeclient import FrappeClient

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
def create_sales_invoice(customer, items, posting_date=None, due_date=None, **kwargs):
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
def create_purchase_invoice(supplier, items, posting_date=None, due_date=None, **kwargs):
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
def create_payment_entry(party_type, party, paid_amount, paid_from=None, paid_to=None, references=None, **kwargs):
    """Create a new Payment Entry"""
    try:
        if party_type == "Customer":
            party = create_customer_if_not_exists(party)
        elif party_type == "Supplier":
            party = create_supplier_if_not_exists(party)
        
        doc = frappe.new_doc("Payment Entry")
        doc.payment_type = "Receive" if party_type == "Customer" else "Pay"
        doc.party_type = party_type
        doc.party = party
        doc.paid_amount = flt(paid_amount)
        doc.received_amount = flt(paid_amount)
        doc.posting_date = now()
        
        if paid_from:
            doc.paid_from = paid_from
        if paid_to:
            doc.paid_to = paid_to
        
        # Add payment references
        if references:
            for ref in references:
                doc.append("references", {
                    "reference_doctype": ref.get("reference_doctype"),
                    "reference_name": ref.get("reference_name"),
                    "allocated_amount": ref.get("allocated_amount", 0),
                    "outstanding_amount": ref.get("outstanding_amount", 0)
                })
        
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        doc.insert()
        doc.submit()
        
        return {
            "status": "success",
            "message": _("Payment Entry created successfully"),
            "name": doc.name
        }
    except Exception as e:
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
def open_report(report_type, company=None, from_date=None, to_date=None, account=None, **kwargs):
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
            report_url = f"{site_url}/app/script-report/{report_name.replace(' ', '%20')}"
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
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if value is not None:
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
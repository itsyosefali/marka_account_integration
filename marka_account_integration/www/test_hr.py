import frappe

def get_context(context):
    """Allow guest access to this page"""
    context.no_cache = 1
    
    # Allow guests to view this page
    frappe.flags.ignore_permissions = True
    
    return context


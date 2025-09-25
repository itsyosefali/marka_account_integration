// Copyright (c) 2025, itsyosefali and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Merka Account Settings", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Merka Account Settings", {
    refresh(frm) {
        frm.add_custom_button("Login and Open General Ledger", function () {
            frappe.call({
                method: "marka_account_integration.api.login_and_open_general_ledger",
                callback: function (r) {
                    console.log(r);
                }
            });
        });
    }
});
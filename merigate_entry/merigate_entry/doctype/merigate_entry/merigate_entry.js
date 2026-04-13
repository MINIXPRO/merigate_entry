frappe.ui.form.on('Merigate Entry', {
    refresh(frm) {
        if (frm.doc.file_url) {
            frm.add_custom_button('View Invoice', () => {
                window.open(frm.doc.file_url, '_blank');
            });
        }
    }
});
from __future__ import unicode_literals
import frappe
from frappe import _ 
import datetime

def alaa():
    return datetime.date.today()


@frappe.whitelist()
def updateLawyerOnApprove(doc,method):
    if doc.workflow_state == "Approved":
        emp_id = frappe.get_value('Employee',{'user_id':frappe.user},'name')
        #frappe.db.set_value('PotentialService',doc.name ,'lawyer',emp_id)

        #frappe.db.sql("""update tabPotentialService set `lawyer`=`HR-EMP-00001` where `name`=`{docName}`""".format(docName=doc.name))


@frappe.whitelist()
def autoShare(doc , method):
    from frappe.share import add
    for employee in doc.employee:
        add(doc.doctype, doc.name, employee.employee, read=1, write=1, share=0, everyone=0)

@frappe.whitelist()
def deleteAttach(doc, method):
    if doc.attached_to_doctype == "Case":
        
        frappe.delete_doc('Case Attachements', doc.file_name)

    elif doc.attached_to_doctype == "Study Potential Cases":
        frappe.delete_doc('Potential Case Attachements', doc.file_name)

    elif doc.attached_to_doctype == "Miscellaneous Services":
        frappe.delete_doc('Service Attachements', doc.file_name)

@frappe.whitelist()
def createAttach(doc, method):
    if doc.attached_to_doctype == "Case":
        docc = frappe.new_doc('Case Attachements')
        docc.case = doc.attached_to_name
        docc.title = doc.file_name
        docc.attachement = doc.file_url
        docc.insert()

    elif doc.attached_to_doctype == "Study Potential Cases":
        docc = frappe.new_doc('Potential Case Attachements')
        docc.potential_case = doc.attached_to_name
        docc.title = doc.file_name
        docc.attachement = doc.file_url
        docc.insert()

    elif doc.attached_to_doctype == "Miscellaneous Services":
        docc = frappe.new_doc('Service Attachements')
        docc.service = doc.attached_to_name
        docc.title = doc.file_name
        docc.attachement = doc.file_url
        docc.insert()

@frappe.whitelist()
def lead_query(doctype, txt, searchfield, start, page_len, filters):
    user = frappe.db.get_list("User", 
        filters={
            "name":frappe.session.user
        },
        fields=['name', 'full_name'],
    )
    return frappe.db.sql("""
        SELECT name, customer
        FROM `tabLead`
        WHERE customer == {0}
    """.format(user[0].full_name))

@frappe.whitelist()
def getDocumentAttachements(doctype , docName):
    files = frappe.db.sql(f""" select name , file_url from `tabFile` where attached_to_doctype=%s and attached_to_name=%s """,(doctype,docName),as_dict=True)
    return files

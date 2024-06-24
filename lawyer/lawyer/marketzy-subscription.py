from __future__ import unicode_literals
import frappe
from frappe import _
import json
import requests

from frappe.sessions import Session, clear_sessions, delete_session

@frappe.whitelist()
def subscriptionValdition():
    
    from datetime import datetime as _d
    import datetime
    from dateutil.relativedelta import relativedelta
    import  requests
    import time
    user = frappe.session.user

    if user == "Administrator":
        return 0 

    userDoc = frappe.get_doc('User',user)
    _s = frappe.get_value('Company',{'name':userDoc.companies[0].company},['serial_number'])

    s = readSerial(_s)

    sub = ''

    if s['status'] == 'Trial':
        sub = _d.strptime(s['start_date'],'%Y-%m-%d').date() + relativedelta(days=14)
    
    elif s['status'] == 'Paid' or s['status'] == 'Not Paid':
        sub = _d.strptime(s['start_date'],'%Y-%m-%d').date() + relativedelta(months=s['time_period'])

    today = datetime.date.today()

    if sub < today:
            # check if there is new serial 
        url = 'https://wowit.sa/api/resource/Lawyer Subscription?fields=["start_date","subscription","employee_count","branch_count","time_period"]&filters=[["serial_number","=","'+s['serial']+'"]]'
        my_headers = {'Authorization':'Basic NTVlZmVlZTUxMTMwNDljOjYxM2VkYTU4OGM2MGZkZQ=='}
        response = requests.request("GET",url,headers=my_headers)

        if response.status_code == 200:
            data = response.json()['data'][0]
                
            if s['start_date'] == data['start_date']:
                url = 'https://wowit.sa/api/resource/Lawyer Subscription/' + s['serial']
                payload={'data': '{"subscription":"Not Paid"}'} 
                response = requests.request("PUT",url,headers=my_headers,data=payload)
                if response.status_code == 200:
                    s['status'] = 'Not Paid'
                    editSerial( json.dumps(readSerial(_s)) , json.dumps(s) )
                    frappe.set_user('Guest')

            else:

                s['start_date'] = data['start_date']
                s['status'] = data['subscription']
                s['employee_count'] = data['employee_count']
                s['company_count'] = data['branch_count']
                s['time_period'] = data['time_period']
                editSerial( json.dumps(readSerial(_s)) , json.dumps(s) )
                return 0

    else:
        frappe.msgprint('welcome')
        frappe.msgprint(userDoc.companies[0].company)
        frappe.defaults.set_user_default('company',userDoc.companies[0].company,user=userDoc.name)
        
        
@frappe.whitelist()
def onItemValidate(doc,method):
    if doc.item_code.startswith(doc.company + "-") == False:
        doc.item_code = doc.company + "-" + doc.item_code
        doc.name = doc.item_code


@frappe.whitelist(allow_guest=True)
def userOnDelete(doc,method):

    ori_user = frappe.session.user
    
    if ori_user == "Administrator":
        return 0

    frappe.set_user("Administrator")
    _s = frappe.get_value('Company',{'name':doc.companies[0].company},['serial_number'])
    license = readSerial(_s)
    userP = frappe.get_list('User Permission' , filters={"user":doc.email},fields=['name'])
    for p in userP:
        frappe.delete_doc('User Permission',p.name)

    
    license['employee_count'] = license['employee_count'] + 1
    editSerial(json.dumps(readSerial(_s)) , json.dumps(license))
    
    frappe.local.cookie_manager.delete_cookie(["full_name", "user_id", "sid", "user_image", "system_user"])

def toto():
    uPs = frappe.get_list('User Permission',filters={'user':'sana@gmail.com'},fields=['name'])

    for p in uPs:
        frappe.delete_doc("User Permission",p.name)
        
# Create Company
@frappe.whitelist(allow_guest=True)
def createCompany(company,cr,serial,abbr, email, tax_id=""):
    import datetime
    from dateutil.relativedelta import relativedelta
    try:
        frappe.set_user("Administrator")
        doc = frappe.new_doc('Company')
        doc.tax_id = tax_id
        doc.company_name = company
        doc.company_name_in_arabic = 'ماركتزي'
        doc.abbr = abbr
        doc.default_currency = "SAR"
        doc.country = "Saudi Arabia"
        doc.cr = cr
        doc.serial_number = serial
        doc.create_chart_of_accounts_based_on = "Standard Template"
        doc.chart_of_accounts = "Standard with Numbers"
        doc.insert()
    # createPrimaryUsers(company)
    #insertUsersSystem(company)
        return 'success'
    except:
        frappe.throw("The company is registered before")

@frappe.whitelist(allow_guest=True)
def createSuperUser(company, full_name, email, number, national_id):
    frappe.set_user("Administrator")
    ui = {'company':company}

    doc  = frappe.new_doc('User')
    doc.email = email
    doc.mobile_no = number
    doc.national_id = national_id
    doc.first_name  = full_name
    doc.language = 'ar'
    doc.role_profile_name = 'Lawyer'
    doc.module_profile = 'General Director'
    doc.user_type = 'System User'
    doc.send_welcome_email  = 1
    doc.append('companies' , ui)
    doc.insert()
    
    insertUsersSystem(email)
    #localSubscription(doc, email, "")

@frappe.whitelist(allow_guest=True)
def addUserEmail(company, email):
    frappe.set_user("Administrator")
    ui = {'company':company}
    doc = frappe.get_doc("User", email)
    doc.append('companies' , ui)
    doc.save()


# def localSubscription(user, email ,customer_name):
#     customer = frappe.get_doc("Customer", customer_name)
#     email = customer.email_id
    
#     ## Getting the subscription if exists from "e-law.sa"
#     url = f'https://wowit.sa/api/resource/Lawyer Subscription'
#     headers = {
#         "Authorization": "Basic NTVlZmVlZTUxMTMwNDljOjYxM2VkYTU4OGM2MGZkZQ==",
#     }
#     response = requests.get(f'{url}?fields=["*"]&filters=[["user","=","{email}"]]', headers=headers)
#     sucessful = response.status_code == 200
#     headers = {
#         "Authorization": "Basic NTVlZmVlZTUxMTMwNDljOjYxM2VkYTU4OGM2MGZkZQ==",
#         "Context-Type": "application/json"
#     }
#     frappe.msgprint(str(sucessful))
#     if sucessful:
#         start_date = datetime.strptime(str(self.start_date), '%Y-%m-%d')
#         if global_sub.subscription == "Trial":
#             end_date = start_date + timedelta(weeks=2)
            
#         elif global_sub.subscription == "Paid":
#             months = global_sub.time_period
#             end_date = start_date + relativedelta(months=months)
#         notif_date = end_date - timedelta(days=7)
#         subscriptions = response.json()["data"]
#         isNotEmpty = len(subscriptions) > 0

#         if isNotEmpty:
#             sub = subscriptions[0]
#             sub_name = sub["name"]

#             url = f'{url}/{sub_name}'gen
#             body = {
#                 "start_date": start_date.strftime("%Y-%m-%d"),
#                 "end_date": end_date.strftime("%Y-%m-%d"),
#                 "notif_date": notif_date.strftime("%Y-%m-%d"),
#                 "type": global_sub.subscription
#             }
#             response = requests.put(url, headers=headers, json=body)
#         else:
#             local_sub = frappe.new_doc("Lawyer Subscription")

#             local_sub.user = email
#             local_sub.company = user["companies"][0]["company"]
#             local_sub.start_date = start_date.strftime("%Y-%m-%d")
#             local_sub.end_date = end_date.strftime("%Y-%m-%d")
#             local_sub.notif_date = notif_date.strftime("%Y-%m-%d")
#             local_sub.type = global_sub.subscription

#             body = {
#                 "user": email,
#                 "company": user["companies"][0]["company"],
#                 "start_date": start_date.strftime("%Y-%m-%d"),
#                 "end_date": end_date.strftime("%Y-%m-%d"),
#                 "notif_date": notif_date.strftime("%Y-%m-%d"),
#                 "type": global_sub.subscription
#             }
#             response = requests.post(url, headers=headers, json=body)

@frappe.whitelist(allow_guest=True)
def insertUsersSystem(user):
    frappe.set_user("Administrator")
    
    doc = frappe.get_doc('User',user)
    doc.user_type = 'System User'

    doc.save()

@frappe.whitelist(allow_guest=True)
def createPrimaryUsers(company):
    frappe.set_user("Administrator")
    role = None 
    module = None
    for i in range(5):
        if i == 0:
            role = 'Manager'
            module = 'Manager'
        elif i == 1:
            role = 'Purchase'
            module = 'Purchase'
        elif i == 2:
            role = 'Sale'
            module = 'Sale'
        elif i == 3:
            role = 'Stock'
            module = 'Stock'
        elif i == 4:
            role = 'OrderCollector'
            module = 'Order Collector'
        doc = frappe.new_doc('User')
        doc.email = role + company + '@example.com'
        doc.first_name = role + company
        doc.language = 'ar'
        doc.company = company
        doc.role_profile_name = role
        doc.module_profile = module
        doc.send_welcome_email = 0
        doc.insert() 
        docP = frappe.new_doc('User Permission')
        docP.user = doc.email
        docP.allow = 'Company'
        docP.for_value = company
        docP.insert()


@frappe.whitelist(allow_guest=True)
def createUserValidition(doc,method):
    original_user = frappe.session.user

    #frappe.set_user("Administrator")
    if (original_user == "Administrator"):
        pass
        #return 0

    _s = frappe.get_value('Company',{'name':doc.companies[0].company},['serial_number'])
    license = readSerial(_s)
    if True: ##license['employee_count'] > 1:
        #check if there user permission
        #user_permissions = frappe.get_list('User Permission',filters={'user':doc.email},fields=['user','allow','for_value'])
        user_permissions = frappe.db.sql(""" select user , allow , for_value from `tabUser Permission` where user='{}' """.format(doc.email),as_dict=1)
        if len(user_permissions) > 0:
            for i in range(len(doc.companies)):
                if user_permissions[i].for_value == doc.companies[i].company:
                    continue
                else:
                    docP = frappe.new_doc('User Permission')
                    docP.user = doc.email 
                    docP.allow = 'Company'
                    docP.for_value = doc.companies[i].company
                    docP.insert(ignore_permissions=True)
        else:
            for i in range(len(doc.companies)):
                docP = frappe.new_doc('User Permission')
                docP.user = doc.email
                docP.allow = 'Company'
                docP.for_value = doc.companies[i].company
                docP.insert(ignore_permissions=True)

        license['employee_count'] = license['employee_count'] - 1   
            
        editSerial(json.dumps(readSerial(_s)) , json.dumps(license))
        #insertUsersSystem(doc.companies[0].company)
        #frappe.local.cookie_manager.delete_cookie(["full_name", "user_id", "sid", "user_image", "system_user"])
    else:
        frappe.throw("U Reached Maximum Users")
    return 'failed'

@frappe.whitelist(allow_guest=True)
def createCompanyValidition(company, abbr):
    user = frappe.session.user
    frappe.set_user("Administrator")
    userDoc = frappe.get_doc('User',user)
    _s = frappe.get_value('Company',{'name':userDoc.companies[0].company},['serial_number']
    )

    license = readSerial(_s)

    if license['company_count'] > 1:
        createCompany(company , license['serial'], abbr=abbr,email=userDoc.name)

        docP = frappe.new_doc('User Permission')
        docP.user = userDoc.email 
        docP.allow = 'Company'
        docP.for_value = company
        docP.insert()
        
        license['company_count'] = license['company_count'] - 1 
        editSerial(json.dumps(readSerial(_s)) , json.dumps(license))
        frappe.local.cookie_manager.delete_cookie(["full_name", "user_id", "sid", "user_image", "system_user"])
        return 0 
    else:
        frappe.throw("U Reached Maximum Companies")
    return 'success'

def customerValidation(id_number):
    url = 'https://wowit.sa/api/resource/Customer?filters=[[\"id_number\",\"=\","'+id_number+'"]]'
    my_headers = {'Authorization':'Basic NTVlZmVlZTUxMTMwNDljOjYxM2VkYTU4OGM2MGZkZQ=='}
    response = requests.request("GET", url, headers=my_headers)
    if (len(response.json()['data']) > 0):
        return True
    else:
        return False

@frappe.whitelist(allow_guest=True)
def createAddress(doc):
    frappe.set_user("Administrator")
    try:
        address = frappe.new_doc('Address')
        address.address_title = doc.company
        address.company = doc.company
        address.address_type = 'Office'
        address.address_line1 = doc.street_name
        address.address_line2 = doc.district
        address.state = doc.state
        address.city = doc.city
        address.country = doc.country
        address.pincode = doc.pincode
        address.building_no = doc.building_no
        address.phone = doc.phone_number
        address.vat_tax_no = doc.tax_category
        address.append('links',{"link_doctype":"Company","link_name":doc.company})
        address.insert(ignore_permissions=True)
    except:
        frappe.throw("This address exists before")
        

@frappe.whitelist(allow_guest=True)
def createHeaderLogo(doc):
    frappe.set_user("Administrator")
    letter_head = frappe.new_doc('Letter Head')
    letter_head.letter_head_name = doc.company
    letter_head.company = doc.company
    letter_head.image = doc.logo
    letter_head.image_height = 100
    letter_head.image_width = 250
    letter_head.align = 'Center'
    letter_head.insert(ignore_permissions=True)

@frappe.whitelist(allow_guest=True)
def generateMarketzySerial(doc,method):
    url = "https://wowit.sa/api/resource/Customer"
    my_headers = {'Authorization':'Basic NTVlZmVlZTUxMTMwNDljOjYxM2VkYTU4OGM2MGZkZQ=='}
    customer_id = ''
    
    if (customerValidation(doc.id_number) == True):
        customer_id  = doc.full_name
    else:
        payload={'data': '{"email_id":"'+doc.email+'","customer_name":"'+doc.full_name+'","customer_type":"Individual","customer_group":"Individual","territory":"Saudi Arabia" , "id_number":"'+doc.id_number+'"}'}
        response = requests.request("POST", url, headers=my_headers, data=payload)
        customer_id = response.json()['data']['name'] 
    url = "https://wowit.sa/api/resource/Tax Category"
    payload = {'data': '{"title":"'+doc.tax_category+'"}'}
    response = requests.request("POST",url,headers=my_headers,data=payload)
    url = "https://wowit.sa/api/resource/Address"
    payload = {'data':'{"address_title":"'+customer_id+'","address_type":"Office","address_line1":"'+doc.street_name+'","address_line2":"'+doc.district+'","city":"'+doc.city+'","country":"'+doc.country+'","pincode":"'+doc.pincode+'","building_no":"'+doc.building_no+'","phone":"'+doc.phone_number+'","tax_category":"'+doc.tax_category+'","links":[{"link_doctype":"Customer","link_name":"'+customer_id+'"}]}'}
    response = requests.request("POST",url,headers=my_headers,data=payload)
    if response.status_code == 200:
        url = "https://wowit.sa/api/method/wowit.wowit.wow_subscription.generateSerialLawyer"
        payload = {'customer':""+customer_id+"",'advertiser':""+doc.advertiser+""}
        response = requests.request("POST", url , headers=my_headers , data=payload )
        if response.status_code == 200:
            writeSerial(response.json()['message'])
            createCompany(doc.company,doc.cr, json.loads(response.json()['message'])['serial'], doc.abbr, doc.email, tax_id=doc.tax_category)
            createSuperUser(doc.company, doc.full_name, doc.email, doc.phone_number, doc.id_number)
            #addUserEmail(doc.company, doc.email)
            createAddress(doc)
            createHeaderLogo(doc)
            frappe.msgprint('Your Serial Number : ' + json.loads(response.json()['message'])['serial'] )
            #frappe.throw(response.json()['message'])
            return 0 

    else:
        return response.status_code
    
def writeSerial(serial):
    path = '/home/frappe/frappe-bench/sites/'
    f = open(path + 'auth-pass.json',"a")
    f.write(serial + '|')
    f.close()
    
def readSerial(_serial):
    path = '/home/frappe/frappe-bench/sites/'
    f = open(path + 'auth-pass.json',"r")
    serials = f.read()
    _serials = serials.split('|')    
    for serial in _serials:
        serial = json.loads(serial)
        if serial['serial'] == _serial:
            return serial
    return 'not found!'

def editSerial (_serial , _newSerial):
    path = '/home/frappe/frappe-bench/sites/'
    f = open(path + 'auth-pass.json',"r")
    filedata = f.read()
    f.close()
    
    newdata = filedata.replace(_serial , _newSerial)

    f = open(path + 'auth-pass.json',"w")
    f.write(newdata)
    f.close()

@frappe.whitelist(allow_guest=True)
def redirectRegister(advertiser):

    frappe.local.response['type'] = "redirect"
    frappe.local.response['location'] = "/register?new=1&advertiser="+advertiser

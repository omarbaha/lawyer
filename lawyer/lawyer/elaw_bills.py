from __future__ import unicode_literals
import frappe
from frappe import _
import json
import requests

import binascii
import base64



class Zakah:
    def __init__(self, invoice_bill):
        self._invoice_bill = invoice_bill

    def bin2hex(self,value):
        # if the value string convert it to binary then hex
        _out = None
        if type(value) == str:
            bytes_str = bytes(value, 'utf-8')
            _out = binascii.hexlify(bytes_str).decode('utf-8')
        else:
            res = hex(value)
            if len(str(res)) < 4:
                _out=res[2:].zfill(2)
            else:
                _out=res[2:]
        return _out


    # assemble function
    def assembleHex(self):
        assembled = ''
        for i in range(6):
            if i == 0:
                continue

            if(i == 1):
                assembled +=  self.bin2hex(i) + self.bin2hex(len(self._invoice_bill['seller_name'])) + self.bin2hex(self._invoice_bill['seller_name'])
            if (i == 2):
                assembled +=  self.bin2hex(i) + self.bin2hex(len(self._invoice_bill['vat_no'])) + self.bin2hex(self._invoice_bill['vat_no'])
            if (i == 3):
                assembled += self.bin2hex(i) + self.bin2hex(len(self._invoice_bill['time_stamp'])) + self.bin2hex(self._invoice_bill['time_stamp'])
            if (i == 4):
                assembled += self.bin2hex(i) + self.bin2hex(len(self._invoice_bill['total'])) + self.bin2hex( self._invoice_bill['total'])
            if (i == 5):
                assembled += self.bin2hex(i) + self.bin2hex(len(self._invoice_bill['vat_total'])) + self.bin2hex(self._invoice_bill['vat_total'])


        return base64.b64encode(bytearray.fromhex(assembled))


@frappe.whitelist()
def getBase64(seller_name , vat_no , time_stamp,total , vat_total):
    invoice = Zakah({
         "seller_name":seller_name,
        "vat_no":vat_no,
        "time_stamp":time_stamp,
        "total":total,
        "vat_total":vat_total
        }
    )
    print(invoice._invoice_bill)
    i = invoice.assembleHex()
    return i.decode('utf-8')
@frappe.whitelist()
def qrcodeLink(bill,pformat):
    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = "/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name="+bill+"&format="+pformat+"&no_letterhead=0&_lang=ar"


@frappe.whitelist()
def bill_address(company_name):
    _addresses = frappe.get_list('Address',fields=['name','address_title','address_line1','address_line2','city','country','pincode','additional_no','building_no','vat_tax_no'])

    for address in _addresses:
        doc = frappe.get_doc('Address',address.name)
        for link in doc.links:
            if link.link_name == company_name:
                return address

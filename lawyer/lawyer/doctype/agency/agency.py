# Copyright (c) 2023, Alaa and contributors
# For license information, please see license.txt

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import frappe
from frappe.model.document import Document


class Agency(Document):
	def validate(self):
		end_date = datetime.strptime(str(self.expiry_date), '%Y-%m-%d')
		self.notif_date1 = end_date - timedelta(days=10)
		self.notif_date2 = end_date - timedelta(days=5)
		self.notif_date3 = end_date - timedelta(days=1)

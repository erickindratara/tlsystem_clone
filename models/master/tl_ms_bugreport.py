from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models 
from datetime import datetime
 
class bugreport(models.Model): #
    _name = 'tl.ms.bugreport' #nama di db berubah jadi training_course
    _description = 'Master bug report'
    _rec_name = 'type'
    type = fields.Selection(string="type", default="improve", selection=[("bug", "bug"),("support", "support"),("improve", "improvement"),  ("new", "new module") ]) 
    dateissued =fields.Datetime(string='issued date', required=False, default=datetime.today())
    datesolved =fields.Datetime(string='solved date', required=False, default=datetime.today())
    issolved = fields.Selection(string="issolved", default="new", selection=[
        ("new", "new"), 
        ("rejected", "rejected"),
        ("approved", "approved"),
        ("pending", "pending"),
        ("onprogress", "on progress"),
        ("solved", "solved"),
        ("unable", "unable to solve") ])   
    statusproject = fields.Selection(string="statusproject",default="unct", selection=[
        ("unct", "not categorized"),
        ("act", "activityplan"),
        ("actfri", "activityplan_forFriday"),
        ("MRS", "Meeting Result")
         ]) 
    
    notes =fields.Char(string='notes', required=True)  
    result =fields.Char(string='result')  
    attachment1 = fields.Binary('attachment1')
 

  
  
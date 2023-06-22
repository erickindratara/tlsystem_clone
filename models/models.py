from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models 




'''class additionalcost(models.Model): #
    _name = 'tl.ms.additionalcost' #nama di db berubah jadi training_course
    _description = 'Transaction additionalcost'
    #_rec_name = 'fullname'   
     
    customerid = fields.Many2one('tl.ms.customer', string="Customer") 
    #customername = fields.Char(related=customerid.companyname, string="Customer name")#store=True
    chassisno = fields.Char(string='No chassis', required=True) #field di db
    engineno = fields.Char(string='No Mesin', required=True) #field di db 
    manfactureyear = fields.Char(string='tahun pembuatan', required=True) #field di db 
    color = fields.Char(string='warna', required=True) #field di db 
''' 
 
from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from xmlrpc.client import Boolean
from odoo import api, fields, models

class bankmaster(models.Model):  
    _name = 'tl.ms.bankmaster'  
    _description = 'bankmaster'
    _rec_name = 'bankid' 

    bankid = fields.Char(string='BankAccountid', default='')  
    bankname = fields.Char(string='BankAccountname', default='')
    isactive = fields.Boolean(string='isactive')  
      
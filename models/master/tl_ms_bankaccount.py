from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models

class expense(models.Model): #
    _name = 'tl.ms.bankaccount' #nama di db berubah jadi training_course
    _description = 'bankaccount'
    _rec_name = 'bankaccountid'
    
 

    bankaccountid = fields.Char(string='BankAccountid',default='', required=True)  
    bankaccountname = fields.Char(string='BankAccountname', default='', required=True)   
    pytreceivealias = fields.Char(string='bonmerah alias', default='', required=True)   
    bankid = fields.Many2one('tl.ms.bankmaster', string='bankid', required=True)  
    bankbranch = fields.Char(string='bankbranch', default='', required=True)   
    accountname = fields.Char(string='accountname', default='', required=True)   
    accountno = fields.Char(string='accountno', default='', required=True)    
    accountcode = fields.Char(string='accountcode', default='', required=True)   
    isactive = fields.Boolean(string='isactive', required=True, default=True)  
 
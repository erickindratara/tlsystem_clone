from ast import Store
import calendar
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models 
from datetime import datetime, timedelta, date
from uuid import uuid4
from odoo.exceptions import UserError, ValidationError
      

class tokenhistory(models.Model): #
    _name = 'tl.ms.tokenhistory'  
    _description = 'Master tokenhistory'
    _rec_name = 'token'  

    
    @api.model
    def action_generate_api_key(self): 
        rand_token = str(uuid4())
        rand_token = rand_token.upper() 
        return rand_token

    def getdate(param):
        result = date.today()
        if(param=="today"):
            result  = result
        if(param=="tomorrow"):
            maxday = calendar.monthrange(result.year, result.month)[1]
            tanggalbesok = result.day+1
            if(tanggalbesok > maxday):
                tanggalbesok = 1 
                result =result.replace(day=tanggalbesok) 
                result =result.replace(month=result.month+1) 
            else:
                result =result.replace(day=tanggalbesok)   
        return result   
        
    token =   fields.Char(string='token',default=action_generate_api_key, required=True) #field di db   
    clientid = fields.Selection(string="clientid", default='TUNASWEB', selection=[("X2K02YI0P1Y7LF6HXZYPDQ", "X2K02YI0P1Y7LF6HXZYPDQ")]) 
    secretkey = fields.Char(string='secretkey', required=True,default='8fMF8A5Q' )  
    
    generateddate =fields.Datetime(string='generated date', required=False, default=getdate('today'))
    expireddate =fields.Datetime(string='expired date', required=False, default=getdate('tomorrow')) 
    usedcount = fields.Char(string='usedcount', required=True,default=0 )  
    isactive = fields.Boolean(string='isactive', required=True, default=True)  
     
    def write(self, vals):
        val_usedcount = 0
        val_isactive = True
        if(vals.get('usedcount') not in (None, False)):
            val_usedcount=vals.get('usedcount') 
        if(vals.get('isactive') != None):
            val_isactive=vals.get('isactive') 
        vals = {
            'usedcount':val_usedcount,
            'isactive':val_isactive, 
        }
        res = super(tokenhistory, self).write(vals)
        return res 

    @api.model
    def create(self, vals):  
        datetoday = date.today()    
        table =self.env['tl.ms.tokenhistory'].search([('isactive', '=', True), ('expireddate','>=',datetoday)])  
        exist_token = table.token
        exist_expireddate = table.expireddate
        data_notexist_needcreateone= True
        if(table.id == True):
            data_notexist_needcreateone = False 
        if(data_notexist_needcreateone):
            querystr = """ update tl_ms_tokenhistory set isactive = false """
            self._cr.execute(querystr) 
            res = super(tokenhistory, self).create(vals)
            return res 
        else: 
            raise ValidationError("silahkan pakai token[  "+exist_token+'  ], expired hingga'+str(exist_expireddate))   


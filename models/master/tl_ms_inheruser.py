import os
from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied, UserError, ValidationError 
from odoo.tools import consteq
from werkzeug.security import safe_str_cmp
import hashlib
import passlib.context
import binascii 


class ResUsers(models.Model):  
    _inherit = 'res.users'   
    
    customtoken = fields.Char(string='customtoken'  , copy=False)
    device_id   = fields.Char(string='device_id'    , copy=False)

    @api.model
    def generate_auth_token(self, user):  
        token = self._generate(user.login) 
        import ipdb; ipdb.set_trace()
        user.write({'customtoken': token}) 
        return token
    
    @api.model
    def updatedeviceid(self, userid, device_id): 
        user = self.env['res.users'].sudo().search([('id', '=', userid)])  
        if user:  
            user.write({'device_id': device_id}) 
    @api.model
    def check_credentials(self, userid): 
        user = self.env['res.users'].sudo().search([('id', '=', userid)])  
        if not user: 
            raise AccessDenied(_('Wrong login/password'))  
        token = self._generate(user.login) 

        user.write({'customtoken': token})
        return user, token
     
    def write(self, vals):    
        return super(ResUsers, self).write(vals)
     
    @api.model
    def create(self, vals):      
        return super(ResUsers, self).create(vals)
    
    is_driver           = fields.Boolean(string='is_driver'         )
    is_useraccessgiven  = fields.Boolean(string='is_useraccessgiven')
     

    def coba(self): 
        user = self.env['res.users'].sudo().search([('id', '=', self.id)], limit=1)
        group = self.env['res.groups'].search([('name', 'in', ( 'Internal User',
                                                                'TL Master Read',
                                                                'TL Master Create',
                                                                'TL Master Update',
                                                                'TL Master Delete',
                                                                'TL change Customer Read',
                                                                'TL change Customer Create',
                                                                'TL change Customer Update',
                                                                'TL change Customer Delete',
                                                                'TL Read',
                                                                'TL Create',
                                                                'TL Update',
                                                                'TL Delete',  
                                                               )
                                                )
                                               ]) 
         
        for id in group:
            if(id not in (None, False)):
                user.write({'groups_id': [(4, id.id)]})   
        user.write({'company_ids': [(4, 1)]})   
        user.write({'is_useraccessgiven':True})     
                
         
    def _generate(self, forlogin):  
        API_KEY_SIZE = 20 
        k = binascii.hexlify(os.urandom(API_KEY_SIZE)).decode()
        mainname='MOBILEAPP_'+forlogin
        user = self.env['res.users'].sudo().search([('login', '=', forlogin)])  
        
        self.env.cr.execute("""delete from res_users_apikeys where name=%s """,[mainname])

        self.env.cr.execute("""
        INSERT INTO res_users_apikeys (name, user_id, key, index)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        [mainname, user.id, hash_api_key(k), k[:INDEX_SIZE]])
  
        print('mainname:',mainname, 'wikwik',k) 
        return k
 
    
KEY_CRYPT_CONTEXT = passlib.context.CryptContext( 
    ['pbkdf2_sha512'], pbkdf2_sha512__rounds=6000,
)
hash_api_key = getattr(KEY_CRYPT_CONTEXT, 'hash', None) or KEY_CRYPT_CONTEXT.encrypt

INDEX_SIZE = 8 # in hex digits, so 4 bytes, or 20% of the key 
  
from odoo import models, fields, api, _

class Sequence(models.Model):
    _inherit = "ir.sequence"

    #@api.multi
    def get_per_doc_code(self,doc_code, prefix):
        # doc_code = self.pool.get('wtc.branch').browse(cr, uid, branch_id).doc_code
        seq_name = '{0}/{1}'.format(prefix, doc_code)
        prefix = '/%(y)s/%(month)s/'
        prefix = seq_name + prefix

        ids = self.search([('name','=',seq_name),('prefix','=',prefix)], limit=1)
        if not ids:
            vals = {
                'name':seq_name,
                'implementation': 'standard',
                'prefix': prefix,
                'padding':5
            }
            ids = super(Sequence,self).create(vals)

        return self.get_id(ids.id)

    def get_short_master(self,doc_code, prefix):
        # doc_code = self.pool.get('wtc.branch').browse(cr, uid, branch_id).doc_code
        seq_name = '{0}/{1}'.format(prefix, doc_code)
        prefix = '/%(y)s/'
        prefix = seq_name + prefix 
        ids = self.search([('name','=',seq_name),('prefix','=',prefix)], limit=1)
        if not ids:
            vals = {
                'name':seq_name,
                'implementation': 'standard',
                'prefix': prefix,
                'padding':3
            }
            ids = super(Sequence,self).create(vals)

        return self.get_id(ids.id)
        
    def get_per_inv_code(self, prefix): 
        seq_name = prefix
        prefixyear = '/%(year)s'
        prefixmonth = '#%(month)s#'
        prefix = seq_name + prefixyear+prefixmonth

        ids = self.search([('name','=',seq_name),('prefix','=',prefix)], limit=1)
        if not ids:
            vals = {
                'name':seq_name,
                'implementation': 'standard',
                'prefix': prefix,
                'padding':5
            }
            ids = super(Sequence,self).create(vals)

        idnya =  self.get_id(ids.id)
        idnya =  idnya.replace('#01#','/I/')
        idnya =  idnya.replace('#02#','/II/')
        idnya =  idnya.replace('#03#','/III/')
        idnya =  idnya.replace('#04#','/IV/')
        idnya =  idnya.replace('#05#','/V/')
        idnya =  idnya.replace('#06#','/VI/')
        idnya =  idnya.replace('#07#','/VII/')
        idnya =  idnya.replace('#08#','/VIII/')
        idnya =  idnya.replace('#09#','/IX/')
        idnya =  idnya.replace('#10#','/X/')
        idnya =  idnya.replace('#11#','/XI/')
        idnya =  idnya.replace('#12#','/XII/') 
        return idnya
         
'''
    @api.multi
    def get_nik_per_branch(self,doc_code):
        seq_name = '{0}'.format('EMP')

        ids = self.search([('name','=',seq_name)])
        if not ids:
            prefix = '%(y)s%(month)s'
            # prefix = doc_code + prefix
            vals = {
                'name':seq_name,
                'implementation':'standard',
                'prefix':prefix,
                'padding':3
            }
            ids = super(Sequence,self).create(vals)
        return self.get_id(ids.id)

    @api.multi
    def get_code_md(self,doc_code) :
        this = self.suspend_security()
        ids = this.search([('name','=',doc_code)])
        if not ids:
            prefix = '/%(y)s/%(month)s/'
            prefix = doc_code + prefix
            vals = {
                'name':doc_code,
                'implementation':'no_gap',
                'prefix':prefix,
                'padding':5
            }
            ids = this.create(vals)
        return this.get_id(ids.id)

    @api.multi
    def get_code_transaksi_customer(self,dealer,code): 
        seq_name = '{0}/{1}'.format(dealer,code)
        ids = self.search([('name','=',seq_name)])
        if not ids:
            prefix = '/%(y)s/%(month)s/'
            prefix = str(dealer) + str(prefix) + str(code)
            vals = {
                'name':seq_name,
                'implementation':'no_gap',
                'prefix':prefix,
                'padding':4
            }
            ids = self.create(vals)
        return self.get_id(ids.id)

    @api.multi
    def get_two_doc_code(self,doc_code1, doc_code2, prefix):
        seq_name = '{0}/{1}/{2}'.format(prefix, doc_code1, doc_code2)
        ids = self.search([('name','=',seq_name)])
        if not ids:
            prefix = '/%(y)s/%(month)s/'
            prefix = seq_name + prefix
            vals = {
                'name':seq_name,
                'implementation': 'standard',
                'prefix': prefix,
                'padding':5
            }
            ids = super(Sequence,self).create(vals)
        return self.get_id(ids.id)
    
    @api.multi
    def get_code_transaksi_4(self,code,prefix):
        seq_name = '{0}/{1}'.format(code,prefix)
        ids = self.search([('name','=',seq_name)])
        if not ids:
            prefix = '/%(y)s/%(month)s/'
            prefix = seq_name + prefix
            vals = {
                'name':seq_name,
                'implementation':'no_gap',
                'prefix':prefix,
                'padding':4
            }
            ids = self.create(vals)
        return self.get_id(ids.id)

    @api.multi
    def get_transaction_month_year_code(self,doc_code, prefix):
        # doc_code = self.pool.get('wtc.branch').browse(cr, uid, branch_id).doc_code
        seq_name = '{0}/{1}'.format(prefix, doc_code)
        prefix = '/%(month)s/%(y)s/'
        prefix = seq_name + prefix

        ids = self.search([('name','=',seq_name),('prefix','=',prefix)], limit=1)
        if not ids:
            vals = {
                'name':seq_name,
                'implementation': 'standard',
                'prefix': prefix,
                'padding':5
            }
            ids = super(Sequence,self).create(vals)

        return self.get_id(ids.id)

    @api.multi
    def get_name_sequence_by_code(self,doc_code):
        seq_name = '{0}'.format(doc_code)
        prefix = '/%(y)s/%(month)s/'
        prefix = seq_name + prefix

        ids = self.search([('name','=',seq_name),('prefix','=',prefix)], limit=1)
        if not ids:
            vals = {
                'name':seq_name,
                'implementation':'standard',
                'prefix':prefix,
                'padding':5
            }
            ids = super(Sequence,self).create(vals)
        return self.get_id(ids.id)
    
    #get voucher code
    @api.multi
    def get_voucher_code(self,code):
        prefix = '/%(month)s/%(y)s/'
        prefix = code + prefix

        ids = self.search([('name','=',code)], limit=1)
        if not ids:
            vals = {
                'name': code,
                'implementation': 'no_gap',
                'prefix': prefix,
                'padding': 4
            }
            ids = super(Sequence,self).create(vals)
        
        return self.get_id(ids.id)

    @api.multi
    def get_voucher_code_voucher(self,code):
        prefix = '%(month)s%(y)s'
        prefix = code + prefix

        ids = self.search([('name','=',code)], limit=1)
        if not ids:
            vals = {
                'name': code,
                'implementation': 'standard',
                'prefix': prefix,
                'padding': 3
            }
            ids = super(Sequence,self).create(vals)
        
        return self.get_id(ids.id)'''



 
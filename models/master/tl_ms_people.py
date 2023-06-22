from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from venv import create
from weakref import ref
from odoo import api, fields, models 

class Person(models.Model): #
    _name = 'tl.ms.people' #nama di db berubah jadi training_course
    _description = 'Master People'
    _rec_name = 'fullname'
     
    type = fields.Selection(string="Tipe", selection=[("DRVFRE", "Driver Freelance"), ("DRVFIX", "Driver Fixed"), ("KORLAP", "Koordinator Lapangan"), ("OTHR", "Other") ])
    korlap = fields.Many2one('tl.ms.people', domain="[('type','=','KORLAP')]", string="Korlap")  #field di db
    fullname = fields.Char(string='Nama Lengkap', required=True) #field di db
    nickname = fields.Char(string='Nama Panggilan', required=True) #field di db
    Birthdate =fields.Datetime(string='Tgl Lahir', required=False)
    Joindate =fields.Datetime(string='Tgl Join', required=False)
    Leavedate =fields.Datetime(string='Tgl pisah', required=False)
    Phone  =fields.Char(string='Telfon/HP', required=False)
    KTP  =fields.Char(string='Tanda  Pengenal KTP', required=False)
    SIM  =fields.Char(string='Surat Izin Mengemudi', required=False) 
    file_upload = fields.Binary('File Upload')
    #def print_picking_sparepart(self):
    def print_person(self):
            datas = {
                'id': self.id,
                #'model': 'dms.stockcard',
                'model': 'tl.ms.people',
                'data': 'data' [0],
            }
            return self.env.ref('tlsystem.print_people').report_action(self, data=datas)
            ''''if self.transaction_type == 'outgoing':
                return self.env.ref('stock_card.print_picking').report_action(self, data=datas)
            else:
                return self.env.ref('stock_card.print_storing').report_action(self, data=datas)'''
 

class PrintPersonPdf(models.AbstractModel):
    #_name = 'report.stock_card.print_storing_list' 
    #_name [report/nama module/template ID]
    _name = 'report.tlsystem.print_people_list'
    _description = 'Master People Print'

    @api.model
    def _get_report_values(self, docids, data=None):   
        people_obj = self.env['tl.ms.people'].sudo().search([('id','=',data['id'])])  
        # people_obj = self.env['tl.ms.people'].sudo().search([('id','=','535')])   
        res =  {
            'docs': data['data'],
            'people_obj': people_obj,
            'date': fields.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        } 
  
        return res

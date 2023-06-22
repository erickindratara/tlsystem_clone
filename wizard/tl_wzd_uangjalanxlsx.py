from odoo import api, fields, models, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class wzduangjalanxlsx(models.TransientModel): 
    # _name           = 'uangjalan.report.wizard' 
    _name           = 'tl.wzd.uangjalanxlsx'
    _descriptions   = 'Print Laporan Uang Jalan wzd1' 
    
    # datefrom        = fields.Date(string="Date From")
    # dateto          = fields.Date(string="Date To")

    datefrom        = fields.Date(string="Date From", default=date.today().replace(day=1))
    allkorlap       = fields.Boolean(string='semua korlap', default=True)  
    korlap          = fields.Many2one('res.partner', string="Korlap", domain = [('is_korlap','=',True)])   
    datefrom        = fields.Date(string="Tanggal Pengajuan From", default=date.today().replace(day=1))
    dateto          = fields.Date(string="Tanggal Pengajuan To", default=(date.today() + relativedelta(day=1, months=+1, days=-1)).strftime('%Y-%m-%d'))
    rowestimated     = fields.Integer(string='estimasi rows')  
    
    @api.onchange('datefrom', 'allkorlap', 'korlap', 'datefrom', 'dateto', 'rowestimated')
    def gettable(self): 
        cuscon=self.env['tl.tr.draftwo'].sudo().search(self.getdomain(), limit =999999999) 
        self.rowestimated = len(cuscon) 
        
    def getdomain(self):
        domain = [('dwodate', '>=', self.datefrom),
                ('dwodate', '<=', self.dateto  )]
        if not self.allkorlap:
            domain.append(('korlap_id', '=', self.korlap.id)) 
        return domain


    def action_print_excel_report(self):  
        if(self.allkorlap == False and self.korlap.id==False):   
            raise ValidationError('korlap harus diisi')    
          
        cuscon = self.env['tl.tr.draftwo'].sudo().search_read(self.getdomain(), limit =999999999) 
        
        
        datafromwzd = {
            'form_data'      : self.read()[0],
            # 'finaldata' : cuscon.read(),
            'finaldata' : cuscon,
            'wtf'       :'tunas'
            # 'appointments': appointment_list
    } 
        # return self.env.ref('tlsystem.tl_rpt_uangjalanxlsx').report_action(self,data=data2)
        # return self.env.ref('report.tlsystem.laporan_uang_jalan_xlsx').report_action(self,data=data2) 

        # it will run tlsystem\report\tl_rpt_uangjalanxlsx.py def : generate_xlsx_report
        return self.env.ref('tlsystem.reportxml_tl_wzd_uangjalanxlsx').report_action(self,data=datafromwzd)  
         
    # def action_print_report(self):
    #     domain = []
    #     dfr=self.datefrom; dto = self.dateto
    #     if(dfr):
    #         domain +=[('','>=', dfr)]
    #     if(dto):
    #         domain +=[('','<=', dto)]
    #     data = self.env['tl.tr.draftwo'].search(domain)
    #     datalist = []
    #     for item in data:
    #         vals = ''
    #         datalist.append(vals)
    #     data2 = {
    #         'form_data': self.read()[0],
    #         'appointments': appointment_list
    #     }
        # return self.env.ref('tlsystem.laporan_uang_jalan_xlsx').report_action(self,data=data2)
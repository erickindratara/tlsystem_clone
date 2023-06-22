from ast import Store
from re import A
from traitlets import default
from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from datetime import date 
 
class AccountMove(models.Model):  
    _inherit = 'account.move'  
    namek = fields.Char(string='Namekian') #field di db +

    def print_sumberdataaccountmove(self):   
        
        selected_ids = self.id 
        datas = { 
            'id': selected_ids, 
            'model': 'account.move',
            'data': 'data' [0],
        }
        return self.env.ref('tlsystem.erick_invoice_print').report_action(self, data=datas)
    def print_sumberdataaccountmovedt(self):   
        
        selected_ids = self.id  
        datas = { 
            'id': selected_ids, 
            'model': 'account.move',
            'data': 'data' [0],
        }
        return self.env.ref('tlsystem.erick_invoicedt_print').report_action(self, data=datas)
#
    def newdefault(self):   
        int_emp = self.getdefaultcustomerid() 
        return int_emp
 
    mycompanyid= fields.Char(default=newdefault, string="mycompanyid", Store=False )  

    def action_update_invoice_date(self):
        self.write({'invoice_date': fields.Date.today()})

    @api.model_create_multi
    def create(self, vals):  
        res =super(AccountMove, self).create(vals)
        for vales in self: 
            a=1
        return res 
 
    def write(self, vals): 
        res =super(AccountMove, self).write(vals) 
        state = vals.get('state')  
        namec='[]'   
        if ('state' in vals and vals.get('state') == 'posted'):
            queryget=''
            error = True
            if(self.id!=False):
                try:
                    error = False
                    queryget = """ select name  from  account_move  where id ="""+str(self.id)+"""; """
                    self._cr.execute(queryget) 
                except ValueError:
                    error = True
            
            if(error==False):
                invno = self._cr.dictfetchone().get('name') 

                old_invno=''
                if(invno[:3] =='INV'): 
                    old_invno=invno
                    invno = self.env['ir.sequence'].get_per_inv_code('MAM')   
                    prefix =invno[0:len(invno)-5]  
                    queryhd = """ update account_move set   name='"""+str(invno)+"""' ,
                                                            payment_reference='"""+str(invno)+"""'  ,
                                                            sequence_prefix=concat(sequence_prefix,'_','"""+str(prefix)+"""') 
                                                            where id ="""+str(self.id)+"""; """
                    self._cr.execute(queryhd)
                    querydt = """ update account_move_line set move_name='"""+str(invno)+"""'  
                                                            where move_id ="""+str(self.id)+"""  """
                    self._cr.execute(querydt)
                    querydt2 = """ update account_move_line set name='"""+str(invno)+"""' 
                                                            where move_id ="""+str(self.id)+""" and
                                                            name='"""+str(old_invno)+"""' ; """
                    self._cr.execute(querydt2)
        accmove = self.env['account.move'].browse(self.id)
        accmoveline =self.env['account.move.line'].search([('move_id', '=', self.id)]) 
        if(state=='cancel'):
            lineid =''
            for id in accmoveline:
                if(lineid!=''):
                    lineid=lineid+','+str(id.id)
                else: 
                    lineid=str(id.id)
                draftwo= self.env['tl.tr.draftwo'].search([('dwoid', '=', id.dwoid)])
                for idwo in draftwo: 
                    query2 = """ update tl_tr_draftwo set stage='CIV',invoiceno =  NULL where id ="""+str(idwo.id)+"""; """
                    self._cr.execute(query2) 
            if(lineid!=''):
                querydelete1= """ delete  from account_move_line where  id in ("""+lineid+"""); """ 
                self._cr.execute(querydelete1)  
        return res
    # hapus account_move
# delete  from  account_account_tag_account_move_line_rel
# delete  from  account_analytic_tag_account_move_line_rel
# delete  from  account_move_account_resequence_wizard_rel
# delete  from  account_move_line_account_tax_rel
# delete  from  account_move 
# delete  from  account_move-line
    # hapus account_move
    def addppn(self):
        var_a = self.cekifppnexist() 
        query="""
        insert into account_tax
        (name, type_tax_use,amount_type,active,company_id,
        "sequence",amount, description,price_include,include_base_amount,
        tax_group_id,tax_exigibility,create_uid,create_date)
        values
        ('10% x 11%','sale','percent',true, 1,
        1,1.1,'11%',false,false,
        1,'on_invoice',1, CURRENT_DATE )
        """
        if(var_a==None):  
            self._cr.execute(query)    
    def cekifppnexist(self):
        query="""
        select id from account_tax where name='10% x 11x%'and active =true
        """
        self._cr.execute(query) 
        var_a = self._cr.dictfetchone()  
        if(var_a!=None):
            var_a =var_a.get('id')   
        else:
            var_a = None 
        return var_a


    @api.onchange('invoice_line_ids')         
    def _onchange_invoice_line_ids(self):
        self.addppn()
        isduplicate = False
        for rec in self:
            for line in rec.line_ids:
                dwcheck =line.dwoid
                for recdt in self:
                    dwcount=0
                    dwthatduplicate=''
                    for linedt in recdt.line_ids:
                        dwcheckdt = linedt.dwoid  
                        if(dwcheck==dwcheckdt and (dwcheck!=False and dwcheckdt!=False)):
                            dwcount=dwcount+1  
                            if(dwcount>1):
                                dwthatduplicate =linedt.dwoid
                                isduplicate=True 
                                
        if(isduplicate): 
            msg='kamu tidak boleh input duplicate DraftWO['+dwthatduplicate+']'
            raise ValidationError(msg)  
        else:  
            current_invoice_lines = self.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab) 
            others_lines = self.line_ids - current_invoice_lines
            if others_lines and current_invoice_lines - self.invoice_line_ids:
                others_lines[0].recompute_tax_line = True
            self.line_ids = others_lines + self.invoice_line_ids
            self._onchange_recompute_dynamic_lines()
        # original



    @api.model
    def getdefaultcustomerid(self):       
        str_a = self.env.user.id ; res_user  = self.env['tl.ms.user'].sudo().search([('user_id', '=', str_a)], limit=1) 
        if(res_user.id in(False,None)):  
            res_partner  = self.env['res.partner'].sudo().search([('is_logistic_customer', '=', True)], limit=1)
            datenow =fields.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vals = {'user_id'   :str_a,'defaultcustomer':res_partner.id,'create_uid':str_a,'create_date':datenow,'write_uid' :str_a,'write_date':datenow,} 
            res_user =self.env['tl.ms.user'].sudo().create(vals ) 
        defcus = res_user.defaultcustomer 
        return defcus

    partner_id = fields.Many2one( 'res.partner', default=getdefaultcustomerid, string='Partner', required=True)


    
class PrintInvoicedtAccountMovePdf(models.AbstractModel): 
    _name = 'report.tlsystem.print_invoicedt_template'    
    _description = 'Transaction invoicedt Print' 

    def extractdate(self, datenya):
        streng ='-' 
        if(datenya!= False and datenya!=None): 
            streng=str(datenya.day)+' ' +self.monthname(datenya.month)+' ' +str(datenya.year)  
        return streng

    def monthname(self, month): 
        strmonth = ''
        if(month==1): strmonth='Jan'
        if(month==2): strmonth='Feb'
        if(month==3): strmonth='Mar'
        if(month==4): strmonth='Apr'
        if(month==5): strmonth='May'
        if(month==6): strmonth='Jun'
        if(month==7): strmonth='Jul'
        if(month==8): strmonth='Aug'
        if(month==9): strmonth='Sep'
        if(month==10): strmonth='Oct'
        if(month==11): strmonth='Nov'
        if(month==12): strmonth='Dec'
        return strmonth
    @api.model
    def _get_report_values(self, docids, data=None):  
        import locale
        # selected_ids = self.env.context.get('active_ids', [])
        invoiceline_obj = self.env['account.move.line'].sudo().search([('move_id','=',data['id']),('dwoid','!=',False)])   #ini dipake sebenernya buat detail   
        dict_iline ={}
        data_iline =[] 
        sum_biayakirim=0
        sum_dpp=0
        sum_ppn=0
        sum_totalinvoice=0
        sum_pph23=0
        sum_totalinvoice_pph=0
        for h in invoiceline_obj: 
            dict_iline={'cust'      : h.tl_tr_draftwo_id.custinitial,
                        'custname'  : h.tl_tr_draftwo_id.customerid.name,
                        'brand'  : h.tl_tr_draftwo_id.qi_brand,
                        'type'  : h.tl_tr_draftwo_id.qi_brandcategory,
                        'chassis'  : h.tl_tr_draftwo_id.chassisno,
                        'engine'  : h.tl_tr_draftwo_id.engineno,
                        'dodate'  : self.extractdate(h.tl_tr_draftwo_id.dwodate)  ,
                        'senddate'  : self.extractdate(h.tl_tr_draftwo_id.senddate) ,
                        'from'  : h.tl_tr_draftwo_id.qi_locationfrom,
                        'to'  : h.tl_tr_draftwo_id.qi_locationto,
                        'nodo'  : h.tl_tr_draftwo_id.dwoid,
                        'dobill'  : h.tl_tr_draftwo_id.dwoid+'/BILL',
                        'cost'  : f"{int(h.tl_tr_draftwo_id.qi_cost):,}" ,
                        'salesprice'  : f"{int(h.tl_tr_draftwo_id.qi_salesprice):,}",
                        }
            sum_biayakirim=sum_biayakirim+h.tl_tr_draftwo_id.qi_salesprice
            data_iline.append(dict_iline)
        sum_dpp=sum_biayakirim
        sum_ppn=11*((10*sum_dpp)/100)/100
        sum_totalinvoice=sum_biayakirim+sum_ppn
        sum_pph23=(2*sum_biayakirim)/100
        sum_totalinvoice_pph=sum_totalinvoice-sum_pph23
        sum_biayakirim=f"{int(sum_biayakirim):,}" 
        sum_dpp=f"{int(sum_dpp):,}" 
        sum_ppn=f"{int(sum_ppn):,}" 
        sum_totalinvoice=f"{int(sum_totalinvoice):,}" 
        sum_pph23=f"{int(sum_pph23):,}" 
        sum_totalinvoice_pph=f"{int(sum_totalinvoice_pph):,}"   
  
         
        headertitle='makan bung'  
        cust = 'x'
        custname = 'x'
        
        for item in data_iline:
            cust = item.get('cust')
            custname = item.get('custname')
        if(cust in ('SS','DHT')):
            headertitle= "Distribusi Unit " + custname
        else:
            headertitle="Lampiran Invoice Logistic" 
        # logo_obj = self.env['res.company'].sudo().search([('id','=','1')])   
        res =  {
            'docs': data['data'],
            'invoiceline_obj': data_iline, 
            'sum_biayakirim':sum_biayakirim,
            'sum_dpp':sum_dpp,
            'sum_ppn':sum_ppn,
            'sum_totalinvoice':sum_totalinvoice,
            'sum_pph23':sum_pph23,
            'sum_totalinvoice_pph':sum_totalinvoice_pph,
            # 'logo':logo_obj.logo_web, ini bikin error
            'date': fields.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'headertitle': headertitle,
        } 
        return res 

    
class PrintInvoiceAccountMovePdf(models.AbstractModel): 
    _name = 'report.tlsystem.print_invoice_template'    
    _description = 'Transaction invoice Print' 

    def convertmonth(self, invdate):
        streng = ''
        day  =  invdate.day
        month  =  invdate.month
        strmonth = self.monthname(month)

        year  =  invdate.year
        streng =str(day)+' '+str(strmonth)+' '+str(year)
        return streng
    
    def monthname(self, month): 
        strmonth = ''
        if(month==1): strmonth='Jan'
        if(month==2): strmonth='Feb'
        if(month==3): strmonth='Mar'
        if(month==4): strmonth='Apr'
        if(month==5): strmonth='May'
        if(month==6): strmonth='Jun'
        if(month==7): strmonth='Jul'
        if(month==8): strmonth='Aug'
        if(month==9): strmonth='Sep'
        if(month==10): strmonth='Oct'
        if(month==11): strmonth='Nov'
        if(month==12): strmonth='Dec'
        return strmonth
     
    def extractdate(self, datenya):
        streng ='-' 
        if(datenya!= False and datenya!=None): 
            streng=str(datenya.day)+' ' +self.monthname(datenya.month)+' ' +str(datenya.year)  
        return streng

    @api.model
    def _get_report_values(self, docids, data=None):  
        import locale
        # selected_ids = self.env.context.get('active_ids', [])  
        invoice_obj = self.env['account.move'].sudo().search([('id','=',data['id'])])   #ini dipake sebenernya buat detail    
        logo_obj = self.env['res.company'].sudo().search([('id','=','1')])     
        dpp=invoice_obj.amount_untaxed
        ppn=invoice_obj.amount_tax 
        ppndpp =  int(dpp+ppn)
        ppndpp_desc = self.terbilang(ppndpp, 'IDR', 'id')  
        # datex = self.convertmonth() 

        
        res =  {
            'docs': data['data'],
            'invoice_obj': invoice_obj, 
            'xx': 'yyeck', 
            'customername':invoice_obj.partner_id.name,
            'customeraddress':invoice_obj.partner_id.street,
            'noinvoice':invoice_obj.name,
            'tgljatuhtempo':self.extractdate(invoice_obj.invoice_date_due),
            'dpp':f"{int(dpp):,}",
            'ppn':f"{int(ppn):,}",
            'ppndpp':f"{int(ppndpp):,}",
            'logo':logo_obj.logo_web,
            'materai':0,
            'biayapengiriman':0,
            'biayareimbursement':0,
            'subtotal':0, 
            'tanggal':self.extractdate(invoice_obj.invoice_date), 
            'terbilang':ppndpp_desc, 
            'date': fields.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'title': 'Finance & Admin SPV'
        } 
        return res
    #terbilang start 
    dic = {       
        'to_19' : ('Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'),
        'tens'  : ('Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'),
        'denom' : ('', 'Thousand', 'Million', 'Billion', 'Trillion', 'Quadrillion', 'Quintillion'),        
        'to_19_id' : ('Nol', 'Satu', 'Dua', 'Tiga', 'Empat', 'Lima', 'Enam', 'Tujuh', 'Delapan', 'Sembilan', 'Sepuluh', 'Sebelas', 'Dua Belas', 'Tiga Belas', 'Empat Belas', 'Lima Belas', 'Enam Belas', 'Tujuh Belas', 'Delapan Belas', 'Sembilan Belas'),
        'tens_id'  : ('Dua Puluh', 'Tiga Puluh', 'Empat Puluh', 'Lima Puluh', 'Enam Puluh', 'Tujuh Puluh', 'Delapan Puluh', 'Sembilan Puluh'),
        'denom_id' : ('', 'Ribu', 'Juta', 'Miliar', 'Triliun', 'Biliun')
    }
      
    def terbilang(self, number, currency, bhs):
        number = '%.2f' % number
        units_name = ' ' + self.cur_name(currency) + ' '
        lis = str(number).split('.')
        start_word = self.english_number(int(lis[0]), bhs)
        end_word = self.english_number(int(lis[1]), bhs)
        cents_number = int(lis[1])
        cents_name = (cents_number > 1) and 'Sen' or 'sen'
        final_result_sen = start_word + units_name + end_word +' '+cents_name
        final_result = start_word + units_name
        if end_word == 'Nol' or end_word == 'Zero':
            final_result = final_result
        else:
            final_result = final_result_sen
         
        return final_result[:1].upper()+final_result[1:]
    
    def _convert_nn(self, val, bhs):
        tens = self.dic['tens_id']
        to_19 = self.dic['to_19_id']
        if bhs == 'en':
            tens = self.dic['tens']
            to_19 = self.dic['to_19']
        if val < 20:
            return to_19[val]
        for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
            if dval + 10 > val:
                if val % 10:
                    return dcap + ' ' + to_19[val % 10]
                return dcap
    
    def _convert_nnn(self, val, bhs):
        word = ''; rat = ' Ratus'; to_19 = self.dic['to_19_id']
        if bhs == 'en':
            rat = ' Hundred'
            to_19 = self.dic['to_19']
        (mod, rem) = (val % 100, val // 100)
        if rem == 1:
            word = 'Seratus'
            if mod > 0:
                word = word + ' '   
        elif rem > 1:
            word = to_19[rem] + rat
            if mod > 0:
                word = word + ' '
        if mod > 0:
            word = word + self._convert_nn(mod, bhs)
        return word
    
    def english_number(self, val, bhs):
        denom = self.dic['denom_id']
        if bhs == 'en':
            denom = self.dic['denom']
        if val < 100:
            return self._convert_nn(val, bhs)
        if val < 1000:
            return self._convert_nnn(val, bhs)
        for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom))):
            if dval > val:
                mod = 1000 ** didx
                l = val // mod
                r = val - (l * mod)
                ret = self._convert_nnn(l, bhs) + ' ' + denom[didx]
                if r > 0:
                    ret = ret + ' ' + self.english_number(r, bhs)
                if bhs == 'id':
                    if val < 2000:
                        ret = ret.replace("Satu Ribu", "Seribu")
                return ret
    
    def cur_name(self, cur="idr"):
        cur = cur.lower()
        if cur=="usd":
            return "Dollars"
        elif cur=="aud":
            return "Dollars"
        elif cur=="idr":
            return "Rupiah"
        elif cur=="jpy":
            return "Yen"
        elif cur=="sgd":
            return "Dollars"
        elif cur=="usd":
            return "Dollars"
        elif cur=="eur":
            return "Euro"
        else:
            return cur
    #terbilang end

 
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line' 
    # _inherit = ['account.move.line']
  
   

    def write(self, vals): 
        res =super(AccountMoveLine, self).write(vals) 
        invoiceno=''
        dwoid=''
        lop = 0
        for record in self:  
            invoiceno=  record['move_name']
            dwoid =  record['dwoid']  
            lop= lop+1 
            if(dwoid !=False):
                getinvno = """ select move_name, move_id from account_move_line where dwoid='"""+str(dwoid)+"""'; """
                self._cr.execute(getinvno)   
                var_a = self._cr.dictfetchone()  
                invoiceno = var_a.get('move_name')
                if(invoiceno =='/'):
                    invoiceno =  'Draft Invoice(* '+str(var_a.get('move_id'))+')'
                query = """ update  tl_tr_draftwo set invoiceno =  '"""+str(invoiceno)+"""', stage='OCI'  where dwoid='"""+str(dwoid)+"""'; """
                self._cr.execute(query)   
        for update in vals: 
            state = ''
            try:
                state = update['state']
            except:
                state = False
  
            if(state!= False): 
                if(state == 'cancel'): 
                    query = """ update  tl_tr_draftwo set invoiceno =  NULL, stage='CIV'  where dwoid='"""+str(dwoid)+"""'; """
                    self._cr.execute(query)   

        return res
        
    @api.model_create_multi
    def create(self, vals): 
        invoiceno='' 
        dwoid=''
         

        res =super(AccountMoveLine, self).create(vals)
        # for vales in self: 
        #     invoiceno=  vales['move_name']
        #     dwoid =  vales['dwoid']  
        dwoid = self.dwoid
        if(dwoid == False):
            dwoid = 'babeeei'
            for vales in vals: 
                dwoid = vales.get('dwoid')
                # invoiceno = vales['move_name']
                if(dwoid != False): 
                    query = """ select move_name from account_move_line where dwoid ='"""+str(dwoid)+"""'; """
                    self._cr.execute(query) 
                    var_a = self._cr.dictfetchone()      
                    if(var_a !=False and var_a !=None):
                        try:  
                            if(var_a.get('move_name') != None):
                                var_a = var_a.get('move_name') 
                        except ValueError:
                            var_a ='null-error'
                        query2 = """ update tl_tr_draftwo set invoiceno ='"""+str(var_a)+"""' , stage='OCI' where  dwoid ='"""+str(dwoid)+"""'; """ 
                        self._cr.execute(query2)   
        return res
        
    def unlink(self):     
        query2 =  '' 
        for item in self:
            dwoid=str(item['dwoid'])
            if(dwoid!=False and dwoid!='False'):   
                query2 = """update tl_tr_draftwo set invoiceno =NULL , stage='RTI' where  dwoid ='"""+str(dwoid)+"""';""" 
                try:
                    if(query2!=''):
                        self._cr.execute(query2) 
                except ValueError: 
                    a=1 
        res= super(AccountMoveLine, self).unlink() 
        return res
          


         
    @api.onchange('tl_tr_draftwo_id')
    def cus_onchange(self):   
        self.dwoid =self.tl_tr_draftwo_id.dwoid
        self.price_unit =  self.tl_tr_draftwo_id.qi_salespriceafterdiscount
        self.price_subtotal = self.quantity * self.price_unit 
        
         
    tl_tr_draftwo_id = fields.Many2one('tl.tr.draftwo', domain = [('stage','=','RTI')],    string="draftwo")   

    dwoid = fields.Char(string ='DWO ID' )  
 
  
# -*- coding: utf-8 -*-

import base64
import io
from odoo import models


class uangjalanxlsx(models.AbstractModel):#ini berhasil di load
    # _name = 'report.tlsystem.report_uangjalan_xls'
    _name = 'report.tlsystem.tl_template_uangjalanxlsx' 
    # model_tl_rpt_uangjalanxlsx
    _inherit = 'report.report_xlsx.abstract'

    def checkfalse(self,primaryvalue, nullvalue):  
        finaldata = nullvalue
        if primaryvalue: 
            if type(primaryvalue) == list:
                finaldata = primaryvalue[1]
            else:
                finaldata = primaryvalue 
        return finaldata 

    def generate_xlsx_report(self, workbook, data, wizarddata):
    # def generate_xlsx_report(self):
        # wizarddata=patients   
        format_1 = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'yellow'})
         
        sheet = workbook.add_worksheet('makankosappo')
        bold = workbook.add_format({'bold': True})
        row = 0; colhd = 0;coldt = 0; colhd=0;    
        colhd   ;sheet.write(row, colhd, 'stage'                    , bold)   
        colhd+=1;sheet.write(row, colhd, 'activestage'   			, bold) 
        colhd+=1;sheet.write(row, colhd, 'triptype'      			, bold)
        colhd+=1;sheet.write(row, colhd, 'claimid'       			, bold) 
        colhd+=1;sheet.write(row, colhd, 'claimamount'   			, bold) 
        colhd+=1;sheet.write(row, colhd, 'claimaccountabilityamount', bold) 
        colhd+=1;sheet.write(row, colhd, 'customerid'				, bold)
        colhd+=1;sheet.write(row, colhd, 'korlap_id'				, bold)  
        colhd+=1;sheet.write(row, colhd, 'driverid'					, bold) 
        colhd+=1;sheet.write(row, colhd, 'dwoid'					, bold) 
        colhd+=1;sheet.write(row, colhd, 'wono'						, bold) 
        colhd+=1;sheet.write(row, colhd, 'invoiceno'				, bold) 
        colhd+=1;sheet.write(row, colhd, 'chassisno'				, bold) 
        colhd+=1;sheet.write(row, colhd, 'engineno'					, bold) 
        colhd+=1;sheet.write(row, colhd, 'licenseplate'				, bold) 
        colhd+=1;sheet.write(row, colhd, 'manfactureyear'			, bold) 
        colhd+=1;sheet.write(row, colhd, 'color'					, bold) 
        colhd+=1;sheet.write(row, colhd, 'peopletype'				, bold) 
        colhd+=1;sheet.write(row, colhd, 'rp_drivertype'			, bold) 
        colhd+=1;sheet.write(row, colhd, 'senddate'					, bold) 
        colhd+=1;sheet.write(row, colhd, 'dwodate'					, bold) 
        colhd+=1;sheet.write(row, colhd, 'additionalinfo'			, bold)
        colhd+=1;sheet.write(row, colhd, 'quotationitemID'			, bold) 
        colhd+=1;sheet.write(row, colhd, 'qi_brandcategory'			, bold) 
        colhd+=1;sheet.write(row, colhd, 'qi_brand'					, bold) 
        colhd+=1;sheet.write(row, colhd, 'qi_locationfrom'			, bold) 
        colhd+=1;sheet.write(row, colhd, 'qi_locationto'			, bold) 
        colhd+=1;sheet.write(row, colhd, 'qi_salesprice'			, bold) 
        colhd+=1;sheet.write(row, colhd, 'qi_cost'					, bold) 
        colhd+=1;sheet.write(row, colhd, 'qi_discount'				, bold) 
        colhd+=1;sheet.write(row, colhd,'qi_salespriceafterdiscount', bold) 
        colhd+=1;sheet.write(row, colhd, 'qi_wayoftransport'		, bold) 
        colhd+=1;sheet.write(row, colhd, 'qi_trip'					, bold) 
        colhd+=1;sheet.write(row, colhd, 'qi_jenisbarang'			, bold) 
        colhd+=1;sheet.write(row, colhd, 'qi_jenistransaksi'		, bold) 
        colhd+=1;sheet.write(row, colhd, 'qi_usingferries'			, bold) 
        colhd+=1;sheet.write(row, colhd, 'qi_jenisunit'				, bold) 
        colhd+=1;sheet.write(row, colhd, 'drivername'				, bold) 
        colhd+=1;sheet.write(row, colhd, 'donumber'					, bold) 
        colhd+=1;sheet.write(row, colhd, 'spe_number'				, bold)
        colhd+=1;sheet.write(row, colhd, 'wholesalename'			, bold) 
        colhd+=1;sheet.write(row, colhd, 'drafttype'				, bold) 
        #qi_multitrip
        for obj in data['finaldata']: 
            row += 1; coldt=0
            coldt   ;sheet.write(row, coldt, self.checkfalse(obj['stage'],''))  
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['activestage'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['triptype'],''))
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['claimid'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['claimamount'],0)) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['claimaccountabilityamount'],0)) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['customerid'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['korlap_id'],''))  
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['driverid'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['dwoid'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['wono'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['invoiceno'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['chassisno'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['engineno'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['licenseplate'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['manfactureyear'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['color'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['peopletype'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['rp_drivertype'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['senddate'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['dwodate'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['additionalinfo'],''))
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['quotationitemID'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_brandcategory'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_brand'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_locationfrom'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_locationto'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_salesprice'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_cost'],0)) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_discount'],0)) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_salespriceafterdiscount'],0)) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_wayoftransport'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_trip'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_jenisbarang'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_jenistransaksi'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_usingferries'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['qi_jenisunit'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['drivername'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['donumber'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['spe_number'],''))
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['wholesalename'],'')) 
            coldt+=1;sheet.write(row, coldt, self.checkfalse(obj['drafttype'],'')) 



            # row += 1
            # sheet.write(row, col, 'reference')
            # sheet.write(row, col+1, 'patientname')
            # row = 3
            # col = 3
            # sheet.set_column('D:D', 12)
            # sheet.set_column('E:E', 13)

        #     row += 1
        #     sheet.merge_range(row, col, row, col + 1, 'ID Card', format_1)

        #     row += 1
        #     if obj.image:
        #         patient_image = io.BytesIO(base64.b64decode(obj.image))
        #         sheet.insert_image(row, col, "image.png", {'image_data': patient_image, 'x_scale': 0.5, 'y_scale': 0.5})

        #         row += 6
        #     sheet.write(row, col, 'Name', bold)
        #     sheet.write(row, col + 1, obj.name)
        #     row += 1
        #     sheet.write(row, col, 'Age', bold)
        #     sheet.write(row, col + 1, obj.age)
        #     row += 1
        #     sheet.write(row, col, 'Reference', bold)
        #     sheet.write(row, col + 1, obj.reference)

        #     row += 2
        #     sheet.merge_range(row, col, row + 1, col + 1, '', format_1)






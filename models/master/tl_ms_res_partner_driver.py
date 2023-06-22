from ast import Store
from re import A
from traitlets import default
from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from datetime import date

class ResPartner(models.Model):  
    _inherit = 'res.partner' 
from ast import Store
from ctypes import create_unicode_buffer
from email.policy import default
from http.client import FOUND
from tracemalloc import DomainFilter
from typing_extensions import Required
from venv import create
from weakref import ref
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class wholesale(models.Model): #
    _name = 'tl.ms.wholesale' #nama di db berubah jadi training_course
    _description = 'Master wholesale list'
    _rec_name = 'wholesalename' 

    wholesalename = fields.Char(string="wholesale name", required = True)
  
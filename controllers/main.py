import functools
import openerp
from openerp import http
from openerp.http import request
from openerp.http import Response
import werkzeug.wrappers
try:
    import simplejson as json
except ImportError:
    import json
import logging
_logger = logging.getLogger(__name__)
from datetime import timedelta,datetime,date
import time
from dateutil.relativedelta import relativedelta
import hashlib
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta

ERROR_TYPE_ACCESS_DENIED = "access_denied"
ERROR_TYPE_DATA_ERROR = "data_error"
ERROR_TYPE_MANDATORY_PARAMS = "mandatory_params"
ERROR_TYPE_EMPTY_MANDATORY_PARAMS = "empty_mandatory_params"
ERROR_TYPE_DATA_NOT_FOUND = "data_not_found"
ERROR_TYPE_SERVER_ERROR = "server_error"
ERROR_TYPE_INVALID_SECRET = "invalid_client_secret"
ERROR_TYPE_TOKEN_EXPIRED = "token_expired"


# def log_api_ibes(name,type_hit,url,request_type,request_data,response_code,response_data):
#     log= {
#         'name':name,
#         'type':type_hit,
#         'url':url,
#         'request_type':request_type,
#         'request':request_data,
#         'response_code':response_code,
#         'response':response_data,
#     }
    # obj_create=request.env['teds.b2b.api.log'].sudo().create(log)

def valid_response_json(info,data,is_log,type_hit,url,request_type,request_data,validation_status=1):  
    dict ={}
    data =[]   
    dict = { "status":1,
        "validation_status":validation_status,
        "message":info,
    }
    # if is_log:
    #     print('log nya belom ada')
    #     response=True
        # log_api_ibes(info,type_hit,url,request_type,request_data,200,response)
    data.append(dict)   
    return json.dumps(data) 

def invalid_response_json(error,info,is_log,type_hit,url,request_type,request_data): 
    dict ={}
    data =[]   
    dict = { "status":0,
        "validation_status":0,
        "message":[{"error":error,"info":info }],
    }
    data.append(dict)   
    return json.dumps(data) 


def check_valid_secret(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        error=''
        api_key_id = request.httprequest.headers#.get('Authorization') #Authorization: Bearer kontji
        api_key_type =request.httprequest.headers.get('Authorization').split()
        token = ''
        if(api_key_type[0]=='Bearer'):
            token = api_key_type[1]
        else:
            api_key_id= False
        # api_key = request.httprequest.headers.get('Authorization') #Authorization: Bearer kontji  
        request_time = datetime.today()
        uid = request.session.uid #result none karena memang gak login
        end_point = request.httprequest.url #ada datanya
        request_data = request.params #ada
        method = request.httprequest.method.lower() #ada POST
        
        if not api_key_id:
            info = "Missing IBES-API-Key in request header!"
            error = 'api_key_not_found'
            _logger.error(info)
            return invalid_response_json(error,info,True,'incoming',end_point,method,request_data)
            

        if not api_key_type:
            info = "Missing IBES-API-Key in request header!"
            error = 'api_key_not_found'
            _logger.error(info)
            return invalid_response_json(error,info,True,'incoming',end_point,method,request_data)

        if not request_time:
            info = "Missing X-Request-Time in request header!"
            error = 'request_time_not_found'
            _logger.error(info)
            return invalid_response_json(error,info,True,'incoming',end_point,method,request_data)

        if not token:
            info = "Missing DGI-API-Token in request header!"
            error = 'api_token_not_found'
            _logger.error(info)
            return invalid_response_json(error,info,True,'incoming',end_point,method,request_data)
 
        tokent_history = http.request.env['tl.ms.tokenhistory'].sudo().search([('token','=',token),('isactive','=',True),('expireddate','>=',date.today())]) 
                
        if not tokent_history.id:
            info = "Token expired/not active or found !"
            error = 'api_token_not_found2'
            _logger.error(info)
            return invalid_response_json(ERROR_TYPE_TOKEN_EXPIRED,info,True,'incoming',end_point,method,request_data)
 
        # client_secret_data = request.env['res.users'].sudo().search([
        #     ('api_key_id', '=', api_key1111_id)], order='id DESC', limit=1)
        # if not client_secret_data:
        #     # Invalid Secret #
        #     return invalid_response_json(ERROR_TYPE_INVALID_SECRET,'Client Secret is invalid!',True,'incoming',end_point,method,request_data)
        
        # data_token = "%s%s%s" %(api_key_id,client_secret_data.api_secret_id,request_time)
        # token_hash = hashlib.sha256(data_token).hexdigest()
        # if (token_hash == token):
        #     request.session.uid = client_secret_data.id
        #     request.uid = client_secret_data.id
        #     return func(self, *args, **kwargs)
        # # Invalid Secret #
        # return invalid_response_json(ERROR_TYPE_INVALID_SECRET,'Client Secret is invalid!',True,'incoming',end_point,method,request_data)
        if (1 == 1): 
            return func(self, *args, **kwargs)
    return wrap
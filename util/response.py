from flask import  make_response, jsonify

def response_with(data=None, headers={},  status=200, **kwargs): 
    # result  = {}
    # if data:
    #     result.update(data)
    
    headers['Access-Control-Allow-Origin'] = '*'
    headers['server'] = 'Restaurant Management'
        
    return make_response(jsonify(data) ,status, headers)
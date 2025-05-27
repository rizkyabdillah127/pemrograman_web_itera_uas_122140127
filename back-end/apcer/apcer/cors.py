# In a file called tweens.py or in the main file
from pyramid.response import Response
from pyramid.httpexceptions import HTTPForbidden

def cors_tween_factory(handler, registry):
    def cors_tween(request):
        # Allow specific origin (not *)
        allowed_origin = 'http://localhost:5173'

        if request.method == 'OPTIONS':
            # Preflight response
            response = request.response
            response.headers['Access-Control-Allow-Origin'] = allowed_origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Max-Age'] = '3600'
            
            return response

        # Actual response
        response = handler(request)
        response.headers['Access-Control-Allow-Origin'] = allowed_origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response

    return cors_tween
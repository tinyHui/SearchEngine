import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DOWNLOAD_DIR = os.path.join(os.path.dirname(BASE_DIR), 'WebPages')
HISTORY_FIEL = os.path.join(DOWNLOAD_DIR, 'record.his')

HTTP_RESPONSE_ERROR = {
            204:"No Response", \
            400:"Bad Request", \
            401:"Unauthorized", \
            403:"Forbidden", \
            404:"Not Found", \
            405:"Method not allowed", \
            406:"Not Acceptable", \
            408:"Request Timeout", \
            409:"Conflict", \
            413:"Request Entity Too Large", \
            414:"Request URL Too Long", \
            417:"Expectition Failed", \
            444:"No Response", \
            500:"Enternal Server Error", \
            502:"Bad Gateway", \
            599:"Network Connect timeout Error" \
        }

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
import logging
import logging.config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'normal': { 
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'simple': { 
            'format': '%(levelname)s - %(message)s'
        },
        'anony_format':{
            'format': '%(asctime)s - %(message)s'
        },
    },
    'handlers': {
        'console1': {  
            'class': 'logging.StreamHandler',  
            'formatter': 'simple',  
        },
        'record': { 
            'class': 'logging.FileHandler',  
            'filename': './logs/record.log',   
            'formatter': 'normal',  
        },
        'anony_record': {
            'class': 'logging.FileHandler',  
            'filename': './logs/anony.log',   
            'formatter': 'anony_format',  
        },
    },
    'loggers': {
        'c': { 
            'handlers': ['console1'],
            'level': 'DEBUG',  
        },
        'r': { 
            'handlers': ['record'],
            'level': 'DEBUG',  
            'propagate': True,
        },
        'anony':{
            'handlers':['anony_record'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}

logging.config.dictConfig(config=LOGGING)

console_logger = logging.getLogger('c')
record_logger = logging.getLogger('r')
anony_logger = logging.getLogger('anony')
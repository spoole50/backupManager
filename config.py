def init():
    global _RunStats 
    _RunStats = {'start':0,
                'totFiles':0,
                'totSize':0,
                'hashAlgo':'crc32',
                'logFilePath': '',
                'logFile': None,
                'fileDict': {},
                'flags':{
                    'move': False,
                    'verbose': 0
                }}
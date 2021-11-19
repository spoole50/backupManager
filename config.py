def init():
    global _RunStats
    _RunStats = {'start':0,
                'totFiles':0,
                'totSize':0,
                'totFiles_trans':0,
                'totSize_trans':0,
                'hashAlgo':'crc32',
                'logFile': None,
                'fileDict': {},
                'hashDict': {},
                'src': None,
                'target': None,
                'flags':{
                    'move': False,
                    'verbose': False,
                    'yes': False,
                    'dry': False,
                    'condense': False
                }}
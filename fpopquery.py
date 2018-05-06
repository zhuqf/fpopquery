from FreedomPop import FreedomPop

def run(username, password, warning, limit, log):
    import pprint
    pp = pprint.PrettyPrinter( width=160 )
    fp = FreedomPop(username, password)
    if log is True:
        fp.enableLog()
    fp.printSummary(warning, limit)

if __name__ == "__main__":
    import configparser
    config = configparser.ConfigParser()
    config.sections()
    config.read('freedompop.cfg')
    logEnabled = False
    warningPercentage = None
    limitPercentage = None
    if config.has_option('Configure','log'):
        if config['Configure']['log'] == 'enable':
            logEnabled = True
    if config.has_option('Configure','warning'):
        warningPercentage = float( config['Configure']['warning'] )
    
    if config.has_option('Configure','limit'):
        limitPercentage = float( config['Configure']['limit'] )
            
    if 'FreedomPop' in config:
        for key in config['FreedomPop']: 
            run(key, config['FreedomPop'][key], warningPercentage, limitPercentage, logEnabled)
    



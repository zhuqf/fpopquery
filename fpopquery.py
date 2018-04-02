from FreedomPop import FreedomPop

def run(username, password):
    import pprint
    pp = pprint.PrettyPrinter( width=160 )
    fp = FreedomPop(username, password)
    fp.printSummary()

if __name__ == "__main__":
    import configparser
    config = configparser.ConfigParser()
    config.sections()
    config.read('freedompop.cfg')
    if 'FreedomPop' in config:
        for key in config['FreedomPop']: 
            run(key, config['FreedomPop'][key])
    
#    run(sys.argv[1], sys.argv[2]) 



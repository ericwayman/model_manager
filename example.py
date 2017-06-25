import sys
#sys.path.append("..")
from model_manager import ParamManager
import configparser
#import model_manager
#from model_manager import x
#model_params
CONFIG_FILE="/Users/ewayman/workspace/model_manager/config"
pm=ParamManager(CONFIG_FILE)
p = pm.param_dict


def main():
    j = pm.get_json()
    print(j)
    return ".97"

if __name__ == "__main__":
    main()
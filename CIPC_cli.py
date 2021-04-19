import json
import sys
import threading

import CIPC

with open('config.json', "r") as jsonfile:
    configs = json.loads(jsonfile.read())

def viewhelp():
    print("""
    Usage:          CIPC_cli.py mode device_names 
    Example: python CIPC_cli.py r    S1 S2 R2 S8 S3 R4
    
    Modes:
        r       read configurations - reads configurations from devices and saves them to corresponding configuration txt files
                note that encrypted passwords will be read and saved in encrypted form
        u       update configurations - reads configurations from txt files and applies them to devices
                without clearing previous configurations 
        e       erase configurations - erases configurations from devices
        w       write configurations - reads configurations from files and applies them to devices
                erasing previous configurations
        с       alternative usage, for one device with custom passwords (if there is no password type "n")
        
                Usage:          CIPC_cli.py c mode device_name user_EXEC_password priv_EXEC_password  
                Example: python CIPC_cli.py c e    S1          n                  cllass
                
    You can use "all" as a device name to order handle all devices in its device list
    Example: python CIPC_cli.py r all
    """)


if len(sys.argv) == 1:
    viewhelp()

else:
    mode = sys.argv[1]

    with open('device_list_and_configs/device_list.json', "r") as jsonfile:
        devise_list = json.loads(jsonfile.read())

    if mode == "c":
        mode = sys.argv[2]
        devise_list[sys.argv[3]]["user_password"] = sys.argv[4]
        devise_list[sys.argv[3]]["priv_password"] = sys.argv[5]
        devise_name_list = [sys.argv[3]]

    elif sys.argv[2] == "all":
        devise_name_list = devise_list.keys()  # keys() вернет имена всех девайсов

    else:
        devise_name_list = sys.argv[2:]

    if mode == "r":
        for devise_name in devise_name_list:
            threading.Thread(name=devise_name + "[read_conf]",
                             target=CIPC.read_configuration,
                             args=(devise_name,
                                   configs["devise_address"],
                                   devise_list[devise_name]["devise_port"],
                                   devise_list[devise_name]["user_password"],
                                   devise_list[devise_name]["priv_password"])).start()

    elif mode == "u":
        for devise_name in devise_name_list:
            threading.Thread(name=devise_name + "[upd_conf]",
                             target=CIPC.update_configuration,
                             args=(devise_name,
                                   configs["devise_address"],
                                   devise_list[devise_name]["devise_port"],
                                   devise_list[devise_name]["user_password"],
                                   devise_list[devise_name]["priv_password"])).start()

    elif mode == "w":
        for devise_name in devise_name_list:
            threading.Thread(name=devise_name + "[write_conf]",
                             target=CIPC.write_configuration,
                             args=(devise_name,
                                   configs["devise_address"],
                                   devise_list[devise_name]["devise_port"],
                                   devise_list[devise_name]["user_password"],
                                   devise_list[devise_name]["priv_password"])).start()

    elif mode == "e":
        for devise_name in devise_name_list:
            threading.Thread(name=devise_name + "[erase_conf]",
                             target=CIPC.erase_configuration,
                             args=(devise_name,
                                   configs["devise_address"],
                                   devise_list[devise_name]["devise_port"],
                                   devise_list[devise_name]["user_password"],
                                   devise_list[devise_name]["priv_password"])).start()


    elif mode == "/?":
        viewhelp()

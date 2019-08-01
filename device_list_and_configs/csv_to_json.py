import csv
import json

with open('device_list.csv', "r") as csv_file:
    reader = csv.reader(csv_file, delimiter=' ')
    json_devise_list = {}
    for row in reader:
        json_devise_list.update({row[0]: {"devise_port": row[1], "user_password": "", "priv_password": ""}})

with open('device_list.json', "w") as json_file:
    json.dump(json_devise_list, json_file)

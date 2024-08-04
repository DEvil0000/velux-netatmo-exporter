#!/usr/bin/env python3
import time
import os
import requests
import json
from datetime import datetime, timedelta
from prometheus_client import start_http_server, Gauge, Info, Enum

metric_prefix = "velux_netatmo_"

# Create a Prometheus metrics for the room
air_quality_metric = Gauge(metric_prefix + "room_" + 'air_quality_value', 'Air Quality value', ['id', 'name'])
co2_metric = Gauge(metric_prefix + "room_" + 'co2_ppm', 'CO2 ', ['id', 'name'])
humidity_metric = Gauge(metric_prefix + "room_" + 'humidity_percent', 'Humidity in percent', ['id', 'name'])
temperature_metric = Gauge(metric_prefix + "room_" + 'temperature_celsius', 'Temperature in degrees celsius', ['id', 'name'])
algo_status_metric = Gauge(metric_prefix + "room_" + 'algo_status_value', 'Algo status of the room', ['id', 'name'])
lux_metric = Gauge(metric_prefix + "room_" + 'lux_lux', 'Light brightness in Lux', ['id', 'name'])

# Create a Prometheus metrics for the modules
firmware_revision_netatmo_metric = Info(metric_prefix + "module" + 'firmware_revision', 'Firmware revision', ['id', 'name', 'type', 'room_id', 'room_name'])
firmware_revision_thirdparty_metric = Info(metric_prefix + "module" + 'firmware_revision_thirdparty', 'Firmware revision third party', ['id', 'name', 'type', 'room_id', 'room_name'])
hardware_version_metric = Info(metric_prefix + "module_" + 'hardware_version', 'Hardware version', ['id', 'name', 'type', 'room_id', 'room_name'])
is_raining_metric = Gauge(metric_prefix + "module_" + 'raining_bool', 'Raining state', ['id', 'name', 'type', 'room_id', 'room_name'])
locked_metric = Gauge(metric_prefix + "module_" + 'locked_bool', 'Locked state', ['id', 'name', 'type', 'room_id', 'room_name'])
locking_metric = Gauge(metric_prefix + "module_" + 'locking_bool', 'Locking in progress state', ['id', 'name', 'type', 'room_id', 'room_name'])
wifi_strength_metric = Gauge(metric_prefix + "module_" + 'wifi_strength', 'Wifi signal strength', ['id', 'name', 'type', 'room_id', 'room_name'])
battery_percent_metric = Gauge(metric_prefix + "module_" + 'battery_percent', 'Battery chare in percent', ['id', 'name', 'type', 'room_id', 'room_name'])
battery_level_metric = Gauge(metric_prefix + "module_" + 'battery_level_mV', 'Battery chare in milli Volts', ['id', 'name', 'type', 'room_id', 'room_name'])
reachable_metric = Gauge(metric_prefix + "module_" + 'reachable_bool', 'Is device reachable or offline', ['id', 'name', 'type', 'room_id', 'room_name'])
rf_strength_metric = Gauge(metric_prefix + "module_" + 'rf_strength', 'RF signal strength', ['id', 'name', 'type', 'room_id', 'room_name'])
current_position_metric = Gauge(metric_prefix + "module_" + 'current_position_percent', 'Current window position in percent open', ['id', 'name', 'type', 'room_id', 'room_name'])
mode_metric = Info(metric_prefix + "module_" + 'control_mode', 'Control mode in use', ['id', 'name', 'type', 'room_id', 'room_name'])
secure_position_metric = Gauge(metric_prefix + "module_" + 'secure_position', 'Secure window position', ['id', 'name', 'type', 'room_id', 'room_name'])
target_position_metric = Gauge(metric_prefix + "module_" + 'target_position_percent', 'Target window position', ['id', 'name', 'type', 'room_id', 'room_name'])
silent_metric = Gauge(metric_prefix + "module_" + 'silent_bool', 'Winodw silent mode on', ['id', 'name', 'type', 'room_id', 'room_name'])

def getBaseUrl():
    return "https://app.velux-active.com"

def getMail():
    return os.environ['MAIL']

def getPassword():
    return os.environ['PASSWORD']

def getClientID():
    return os.environ['CLIENTID']

def getClientSecret():
    return os.environ['CLIENTSECRET']

def getToken():
    data = {
        'grant_type': 'password',
        'client_id': getClientID(),
        'client_secret': getClientSecret(),
        'username': getMail(),
        'password': getPassword(),
        'user_prefix': 'velux',
    }
    response = requests.post(getBaseUrl() + '/oauth2/token', data=data)
    token = response.json()
    t = datetime.now() + timedelta(seconds=token['expires_in'])
    token['expieres_at'] = t.isoformat()
    return token

def readToken():
    try:
        f = open("/var/lib/velux-netatmo-exporter/token.json", "r")
        token = json.load(f)
        tdelata = datetime.fromisoformat(token['expieres_at']) - datetime.now()
        token['expires_in'] = round(tdelata.total_seconds()) -1
        token['expire_in'] = token['expires_in']
        f.close()
        if token['expires_in'] > 0:
            #only return still valid tokens
            return token
        else:
            print("token from file was expired")
            return None
    except:
        print("token file read failed")
        return None

def writeToken(token):
    try:
        f = open("/var/lib/velux-netatmo-exporter/token.json", "w")
        json.dump(token, f)
        f.close()
    except:
        print("token file write failed")

def refreshToken(refresh_token):
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': getClientID(),
        'client_secret': getClientSecret(),
    }
    response = requests.post(getBaseUrl() + '/oauth2/token', data=data)
    return response.json()

def getHomeData(access_token):
    data = {
        'access_token': access_token
    }
    response = requests.post(getBaseUrl() + '/api/gethomedata', data=data)
    return response.json()

def getHomeId(home_data):
    return home_data['body']['homes'][0]['id']

def getHomesData(access_token):
    data = {
        'access_token': access_token,
    }
    response = requests.post(getBaseUrl() + '/api/homesdata', data=data)
    return response.json()

def getModulesNames(homes_data):
    # type, id, name
    return homes_data['body']['homes'][0]['modules']

def getRoomsNames(homes_data):
    # type, id, name
    return homes_data['body']['homes'][0]['rooms']

def getHomeStatus(access_token, home_id):
    data = {
        'access_token': access_token,
        'home_id': home_id,
    }
    response = requests.post(getBaseUrl() + '/api/homestatus', data=data)
    return response.json()

def getModulesDetails(home_status):
    return home_status['body']['home']['modules']

def getRoomsDetails(home_status):
    return home_status['body']['home']['rooms']

#def getModuleMeassurements(access_token, device_id, module_id):
#    data = {
#        'access_token': access_token,
#        'device_id': device_id,
#        'module_id': module_id,
#        'scale': '30min',
#        'type': 'CO2,Humidity', # min_hum,max_hum
#        'date_end': 'last',
#        #date_begin=1561834800'
#    }
#    response = requests.post(getBaseUrl() + '/api/getmeasure', data=data)
#    return response.json()

def getAndRestructureData(access_token, home_id):
    rooms = {
        'global': {
            # pseudo room for devices without room
            'id': 'global',
            'name': 'global',
            'modules': [],
        },
    }
    modules = {
        'NXG': {}, #GW
        'NXO': {}, #WINDOW
        'NXS': {}, #SENSOR
        'NXD': {}, #LOCK
    }
    home_status_raw = getHomeStatus(access_token, home_id)
    home_status_modules_raw = getModulesDetails(home_status_raw)
    for module in home_status_modules_raw:
        modules[module['type']][module['id']] = module

    home_status_rooms_raw = getRoomsDetails(home_status_raw)
    for room in home_status_rooms_raw:
        rooms[room['id']] = room
        rooms[room['id']]['modules'] = []

    homes_data_raw = getHomesData(access_token)
    modules_mapping_raw = getModulesNames(homes_data_raw)
    for module in modules_mapping_raw:
        modules[module['type']][module['id']]['name'] = module['name']
        if 'room_id' in module:
            rooms[module['room_id']]['modules'].append(modules[module['type']][module['id']])
        else:
            rooms['global']['modules'].append(modules[module['type']][module['id']])

    rooms_mapping_raw = getRoomsNames(homes_data_raw)
    for room in rooms_mapping_raw:
        rooms[room['id']]['name'] = room['name']

    return rooms

if __name__ == '__main__':
    # Start the Prometheus HTTP server on port 9211
    start_http_server(9211)

    sleep_time = 60

    # read token
    token = readToken()
    # if token not okay get new token
    if token == None:
        print("getting new token")
        token = getToken()
        writeToken(token)

    home_id = getHomeId(getHomeData(token['access_token']))

    while True:
        # maybe refresh
        if token['expires_in'] < sleep_time:
            print("refreshing token")
            token = refreshToken(token['refresh_token'])
            writeToken(token)
        
        # get data
        rooms = getAndRestructureData(token['access_token'], home_id)
        for room_id, room in rooms.items():
            if 'air_quality' in room:
                air_quality_metric.labels(room['id'], room['name']).set(room['air_quality'])
            if 'co2' in room:
                co2_metric.labels(room['id'], room['name']).set(room['co2'])
            if 'humidity' in room:
                humidity_metric.labels(room['id'], room['name']).set(room['humidity'])
            if 'temperature' in room:
                temperature_metric.labels(room['id'], room['name']).set(room['temperature'])
            if 'algo_status' in room:
                #TODO should maybe be enum
                algo_status_metric.labels(room['id'], room['name']).set(room['algo_status'])
            if 'lux' in room:
                lux_metric.labels(room['id'], room['name']).set(room['lux'])
            for module in room['modules']:
                if 'firmware_revision_netatmo' in module:
                    firmware_revision_netatmo_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).info({'firmware_revision_netatmo': str(module['firmware_revision_netatmo'])})
                elif 'firmware_revision' in module:
                    firmware_revision_netatmo_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).info({'firmware_revision_netatmo': str(module['firmware_revision'])})
                if 'firmware_revision_thirdparty' in module:
                    firmware_revision_thirdparty_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).info({'firmware_revision_thirdparty': str(module['firmware_revision_thirdparty'])})
                if 'hardware_version' in module:
                    hardware_version_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).info({'hardware_version': str(module['hardware_version'])})
                if 'is_raining' in module:
                    is_raining_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(module['is_raining'])
                if 'locked' in module:
                    locked_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(module['locked'])
                if 'locking' in module:
                    locking_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(module['locking'])
                if 'wifi_strength' in module:
                    wifi_strength_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(module['wifi_strength'])
                if 'battery_percent' in module:
                    battery_percent_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(module['battery_percent'])
                elif 'battery_state' in module:
                    # windows do not report battery_percent or battery_level sadly
                    if module['battery_state'] == "high":
                        battery_percent_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(80)
                    elif module['battery_state'] == "full":
                        battery_percent_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(90)
                    else:
                        #TODO add other label mappings maybe
                        battery_percent_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(0)
                if 'battery_level' in module:
                    battery_level_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(module['battery_level'])
                if 'reachable' in module:
                    reachable_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(module['reachable'])
                if 'rf_strength' in module:
                    rf_strength_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(module['rf_strength'])
                if 'current_position' in module:
                    current_position_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(module['current_position'])
                if 'mode' in module:
                    #TODO should maybe be enum
                    mode_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).info({'mode': str(module['mode'])})
                if 'secure_position' in module:
                    secure_position_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(module['secure_position'])
                if 'target_position' in module:
                    target_position_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(module['target_position'])
                if 'silent' in module:
                    silent_metric.labels(module['id'], module['name'], module['type'], room['id'], room['name']).set(module['silent'])
        
        # Sleep for 60 sec
        time.sleep(sleep_time)
        token['expires_in'] -= sleep_time -1

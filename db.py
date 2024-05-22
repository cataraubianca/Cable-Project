from datetime import datetime
from aslookup import get_as_data
from ripe.atlas.cousteau import MeasurementRequest, AtlasResultsRequest
import pickle
import os.path
import ipaddress
import subprocess
import sys 
from flask import Flask, request, jsonify
from flask_cors import CORS
import json



app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
def get_info(msm, start_year, start_month, start_day, stop_year, stop_month, stop_day, id):
    def call_withdrawals_source(timestamp, source, destination):
        command = f"wsl python3 withdrawals_source.py {timestamp} {source} {destination}"
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print("Command output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error executing command:", e)
            print("Command output:", e.output)
            print("Command stderr:", e.stderr)

    def call_withdrawals_destination(timestamp, source, destination):
        command = f"wsl python3 withdrawals_destination.py {timestamp} {source} {destination}"
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print("Command output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error executing command:", e)
            print("Command output:", e.output)
            print("Command stderr:", e.stderr)
    def call_announcements(timestamp, source, destination):
        command = f"wsl python3 announcements.py {timestamp} {source} {destination}"
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print("Command output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error executing command:", e)
            print("Command output:", e.output)
            print("Command stderr:", e.stderr)

    def call_graph(timestamp, source, destination):
        command = f"wsl python3 as_mapping.py {timestamp} {source} {destination}"
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print("Command output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error executing command:", e)
            print("Command output:", e.output)
            print("Command stderr:", e.stderr)

    anomaly_file = 'anomalies.json'

    if os.path.isfile('./results1.pkl'):
        with open( './results1.pkl','rb') as openfile:
            results=pickle.load(openfile)
        is_success=True
    else:
        kwargs = {
            "msm_id":int(msm),
            "start": datetime(int(start_year), int(start_month), int(start_day)),
            "stop": datetime(int(stop_year), int(stop_month), int(stop_day))
        }
        is_success, results = AtlasResultsRequest(**kwargs).create()
    src_dict=dict()
    anomaly_dict=dict()
    timeordered_dict=dict()
    i=0
    if is_success:
        with open('results.pkl', 'wb') as file:
            pickle.dump(results, file)
        alpha=0.4 #moving average coefficient
        beta=0.4 #moving standard deviation coefficient
        for res in results:
            if i == 0:
                print(res)
            i = i + 1
            epoch=res['stored_timestamp']//(5*60)*5*60
            if (epoch in timeordered_dict):
                timeordered_dict[epoch].append(res)
            else:
                timeordered_dict[epoch]= [res]

            if res['src_addr'] in src_dict:
                src_dict[res['src_addr']]['rtt'].append((res['stored_timestamp'],res['avg']))
                if (res['avg']>-1):
                    if (res['avg']>1.20*src_dict[res['src_addr']]['mavg']) and (src_dict[res['src_addr']]['mavg']>100) :
                        ip = res['src_addr']
                        if (not ipaddress.ip_address(ip).is_private):
                            as_data=get_as_data(ip)
                            if (res['stored_timestamp']//(5*60)*5*60 in anomaly_dict):
                                anomaly_dict[epoch].append((res['src_addr'],res['dst_addr'],res['avg'],src_dict[res['src_addr']]['mavg'],res['stored_timestamp'], as_data.asn,as_data.as_name,as_data.cc))
                            else:
                                    anomaly_dict[epoch]=[(res['src_addr'],res['dst_addr'],res['avg'],src_dict[res['src_addr']]['mavg'],res['stored_timestamp'], as_data.asn,as_data.as_name,as_data.cc)]
                    src_dict[res['src_addr']]['mstd']=(1-beta)*src_dict[res['src_addr']]['mstd']+beta*abs(src_dict[res['src_addr']]['mavg']-res['avg'])
                    src_dict[res['src_addr']]['mavg']=(1-alpha)*src_dict[res['src_addr']]['mavg']+alpha*res['avg']
            else:
                src_dict[res['src_addr']]={'rtt':[(res['stored_timestamp'],res['avg'])],'mavg':res['avg'],'mstd':res['avg']}
        with open('src_dict.pkl', 'wb') as file:
            pickle.dump(src_dict, file)
        with open(anomaly_file, 'wb') as file:
            pickle.dump(anomaly_dict, file)
        with open('ordered1.pkl', 'wb') as file:
            pickle.dump(timeordered_dict, file)

    idx = 0  
    anomaly_source_ = None
    anomaly_address_ = None
    anomaly_timestamp_ = None

    with open(anomaly_file, 'w') as file:
        anomalies_list = []
        for timestamp, anomalies in anomaly_dict.items():
            for anomaly in anomalies:
                anomalies_list.append({
                    'anomaly_source': anomaly[0],
                    'anomaly_address': anomaly[1],
                    'anomaly_avg': anomaly[2],
                    'anomaly_mavg': anomaly[3],
                    'anomaly_timestamp': anomaly[4],
                    'asn': anomaly[5],
                    'as_name': anomaly[6],
                    'country_code': anomaly[7]
                })
                if idx == id-1: 
                    anomaly_source_ = anomaly[0]
                    anomaly_address_ = anomaly[1]
                    anomaly_timestamp_ = anomaly[4]
                idx += 1
        json.dump(anomalies_list, file, indent=4)
    print("Anomaly Source:", anomaly_source_)
    print("Anomaly Address:", anomaly_address_)
    print("Anomaly Timestamp:", anomaly_timestamp_)
    call_withdrawals_source(int(anomaly_timestamp_), str(anomaly_source_), str(anomaly_address_))
    call_withdrawals_destination(int(anomaly_timestamp_), str(anomaly_source_), str(anomaly_address_))
    call_announcements(int(anomaly_timestamp_), str(anomaly_source_), str(anomaly_address_))
    call_graph(int(anomaly_timestamp_), str(anomaly_source_), str(anomaly_address_))
#get_info(23046934, 2024, 2, 23, 2024, 2, 24, 205)  # msm_id, date of start, date of end, id of the row in the table that we want to run the functions on as example -> 179
@app.route('/run', methods=['POST'])
def run():
    data = request.json
    print("Received data:", data)
    msm = data.get('measurement_id')
    start_year = data.get('start_year')
    start_month = data.get('start_month')
    start_day = data.get('start_day')
    stop_year = data.get('end_year')
    stop_month = data.get('end_month')
    stop_day = data.get('end_day')
    id = data.get('id')

    if None in (msm, start_year, start_month, start_day, stop_year, stop_month, stop_day, id):
        return jsonify({'error': 'Missing data in request'}), 400

    try:
        msm = int(msm)
        start_year = int(start_year)
        start_month = int(start_month)
        start_day = int(start_day)
        stop_year = int(stop_year)
        stop_month = int(stop_month)
        stop_day = int(stop_day)
        id = int(id)
        print("Parameters:", msm, start_year, start_month, start_day, stop_year, stop_month, stop_day, id)
    except ValueError:
        return jsonify({'error': 'Invalid parameter types'}), 400

    get_info(msm, start_year, start_month, start_day, stop_year, stop_month, stop_day, id)

    return jsonify({'message': 'Process started successfully'}), 200




def get_delays_withdrawals(msm, start_year, start_month, start_day, stop_year, stop_month, stop_day, id):
    def call_withdrawals_source(timestamp, source, destination):
        command = f"wsl python3 withdrawals_source_dw.py {timestamp} {source} {destination}"
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print("Command output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error executing command:", e)
            print("Command output:", e.output)
            print("Command stderr:", e.stderr)

    def call_withdrawals_destination(timestamp, source, destination):
        command = f"wsl python3 withdrawals_destination_dw.py {timestamp} {source} {destination}"
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print("Command output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error executing command:", e)
            print("Command output:", e.output)
            print("Command stderr:", e.stderr)


    anomaly_file = 'anomalies_dw.json'

    if os.path.isfile('./results1_dw.pkl'):
        with open( './results1_dw.pkl','rb') as openfile:
            results=pickle.load(openfile)
        is_success=True
    else:
        kwargs = {
            "msm_id":int(msm),
            "start": datetime(int(start_year), int(start_month), int(start_day)),
            "stop": datetime(int(stop_year), int(stop_month), int(stop_day))
        }
        is_success, results = AtlasResultsRequest(**kwargs).create()
    src_dict=dict()
    anomaly_dict=dict()
    timeordered_dict=dict()
    if is_success:
        with open('results_dw.pkl', 'wb') as file:
            pickle.dump(results, file)
        alpha=0.4
        beta=0.4
        for res in results:
            epoch=res['stored_timestamp']//(5*60)*5*60
            if (epoch in timeordered_dict):
                timeordered_dict[epoch].append(res)
            else:
                timeordered_dict[epoch]= [res]

            if res['src_addr'] in src_dict:
                src_dict[res['src_addr']]['rtt'].append((res['stored_timestamp'],res['avg']))
                if (res['avg']>-1):
                    if (res['avg']>1.20*src_dict[res['src_addr']]['mavg']) and (src_dict[res['src_addr']]['mavg']>100) :
                        ip = res['src_addr']
                        if (not ipaddress.ip_address(ip).is_private):
                            as_data=get_as_data(ip)
                            if (res['stored_timestamp']//(5*60)*5*60 in anomaly_dict):
                                anomaly_dict[epoch].append((res['src_addr'],res['dst_addr'],res['avg'],src_dict[res['src_addr']]['mavg'],res['stored_timestamp'], as_data.asn,as_data.as_name,as_data.cc))
                            else:
                                    anomaly_dict[epoch]=[(res['src_addr'],res['dst_addr'],res['avg'],src_dict[res['src_addr']]['mavg'],res['stored_timestamp'], as_data.asn,as_data.as_name,as_data.cc)]
                    src_dict[res['src_addr']]['mstd']=(1-beta)*src_dict[res['src_addr']]['mstd']+beta*abs(src_dict[res['src_addr']]['mavg']-res['avg'])
                    src_dict[res['src_addr']]['mavg']=(1-alpha)*src_dict[res['src_addr']]['mavg']+alpha*res['avg']
            else:
                src_dict[res['src_addr']]={'rtt':[(res['stored_timestamp'],res['avg'])],'mavg':res['avg'],'mstd':res['avg']}
        with open('src_dict_dw.pkl', 'wb') as file:
            pickle.dump(src_dict, file)
        with open(anomaly_file, 'wb') as file:
            pickle.dump(anomaly_dict, file)
        with open('ordered1_dw.pkl', 'wb') as file:
            pickle.dump(timeordered_dict, file)

    idx = 0  
    anomaly_source_ = None
    anomaly_address_ = None
    anomaly_timestamp_ = None

    with open(anomaly_file, 'w') as file:
        anomalies_list = []
        for timestamp, anomalies in anomaly_dict.items():
            for anomaly in anomalies:
                anomalies_list.append({
                    'anomaly_source': anomaly[0],
                    'anomaly_address': anomaly[1],
                    'anomaly_avg': anomaly[2],
                    'anomaly_mavg': anomaly[3],
                    'anomaly_timestamp': anomaly[4],
                    'asn': anomaly[5],
                    'as_name': anomaly[6],
                    'country_code': anomaly[7]
                })
                if idx == id-1: 
                    anomaly_source_ = anomaly[0]
                    anomaly_address_ = anomaly[1]
                    anomaly_timestamp_ = anomaly[4]
                idx += 1 
        json.dump(anomalies_list, file, indent=4)
    print("Anomaly Source:", anomaly_source_)
    print("Anomaly Address:", anomaly_address_)
    print("Anomaly Timestamp:", anomaly_timestamp_)
    call_withdrawals_source(int(anomaly_timestamp_), str(anomaly_source_), str(anomaly_address_))
    call_withdrawals_destination(int(anomaly_timestamp_), str(anomaly_source_), str(anomaly_address_))
#get_info(23046934, 2024, 2, 23, 2024, 2, 24, 205)  # msm_id, date of start, date of end, id of the row in the table that we want to run the functions on as example -> 179
@app.route('/dw', methods=['POST'])
def run_get_delays():
    data = request.json
    print("Received data:", data)
    msm = data.get('measurement_id')
    start_year = data.get('start_year')
    start_month = data.get('start_month')
    start_day = data.get('start_day')
    stop_year = data.get('end_year')
    stop_month = data.get('end_month')
    stop_day = data.get('end_day')
    id = data.get('id')

    if None in (msm, start_year, start_month, start_day, stop_year, stop_month, stop_day, id):
        return jsonify({'error': 'Missing data in request'}), 400

    try:
        msm = int(msm)
        start_year = int(start_year)
        start_month = int(start_month)
        start_day = int(start_day)
        stop_year = int(stop_year)
        stop_month = int(stop_month)
        stop_day = int(stop_day)
        id = int(id)
        print("Parameters:", msm, start_year, start_month, start_day, stop_year, stop_month, stop_day, id)
    except ValueError:
        return jsonify({'error': 'Invalid parameter types'}), 400

    get_delays_withdrawals(msm, start_year, start_month, start_day, stop_year, stop_month, stop_day, id)

    return jsonify({'message': 'Process started successfully'}), 200








def get_anomalies(msm, start_year, start_month, start_day, stop_year, stop_month, stop_day):
    anomaly_file = 'anomalies_d.json'

    if os.path.isfile('./results1_d.pkl'):
        with open( './results1_d.pkl','rb') as openfile:
            results=pickle.load(openfile)
        is_success=True
    else:
        kwargs = {
            "msm_id":int(msm),
            "start": datetime(int(start_year), int(start_month), int(start_day)),
            "stop": datetime(int(stop_year), int(stop_month), int(stop_day))
        }
        is_success, results = AtlasResultsRequest(**kwargs).create()
    src_dict=dict()
    anomaly_dict=dict()
    timeordered_dict=dict()
    if is_success:
        with open('results_d.pkl', 'wb') as file:
            pickle.dump(results, file)
        alpha=0.4
        beta=0.4
        for res in results:
            epoch=res['stored_timestamp']//(5*60)*5*60
            if (epoch in timeordered_dict):
                timeordered_dict[epoch].append(res)
            else:
                timeordered_dict[epoch]= [res]

            if res['src_addr'] in src_dict:
                src_dict[res['src_addr']]['rtt'].append((res['stored_timestamp'],res['avg']))
                if (res['avg']>-1):
                    if (res['avg']>1.20*src_dict[res['src_addr']]['mavg']) and (src_dict[res['src_addr']]['mavg']>100) :
                        ip = res['src_addr']
                        if (not ipaddress.ip_address(ip).is_private):
                            as_data=get_as_data(ip)
                            if (res['stored_timestamp']//(5*60)*5*60 in anomaly_dict):
                                anomaly_dict[epoch].append((res['src_addr'],res['dst_addr'],res['avg'],src_dict[res['src_addr']]['mavg'],res['stored_timestamp'], as_data.asn,as_data.as_name,as_data.cc))
                            else:
                                    anomaly_dict[epoch]=[(res['src_addr'],res['dst_addr'],res['avg'],src_dict[res['src_addr']]['mavg'],res['stored_timestamp'], as_data.asn,as_data.as_name,as_data.cc)]
                    src_dict[res['src_addr']]['mstd']=(1-beta)*src_dict[res['src_addr']]['mstd']+beta*abs(src_dict[res['src_addr']]['mavg']-res['avg'])
                    src_dict[res['src_addr']]['mavg']=(1-alpha)*src_dict[res['src_addr']]['mavg']+alpha*res['avg']
            else:
                src_dict[res['src_addr']]={'rtt':[(res['stored_timestamp'],res['avg'])],'mavg':res['avg'],'mstd':res['avg']}
        with open('src_dict_d.pkl', 'wb') as file:
            pickle.dump(src_dict, file)
        with open(anomaly_file, 'wb') as file:
            pickle.dump(anomaly_dict, file)
        with open('ordered1_d.pkl', 'wb') as file:
            pickle.dump(timeordered_dict, file)


    with open(anomaly_file, 'w') as file:
        anomalies_list = []
        for timestamp, anomalies in anomaly_dict.items():
            for anomaly in anomalies:
                anomalies_list.append({
                    'anomaly_source': anomaly[0],
                    'anomaly_address': anomaly[1],
                    'anomaly_avg': anomaly[2],
                    'anomaly_mavg': anomaly[3],
                    'anomaly_timestamp': anomaly[4],
                    'asn': anomaly[5],
                    'as_name': anomaly[6],
                    'country_code': anomaly[7]
                })
        json.dump(anomalies_list, file, indent=4)
#get_info(23046934, 2024, 2, 23, 2024, 2, 24, 205)  # msm_id, date of start, date of end, id of the row in the table that we want to run the functions on as example -> 179
@app.route('/d', methods=['POST'])
def run_d():
    print("Endpoint /d was called")
    data = request.json
    print("Received data:", data)
    msm = data.get('measurement_id')
    start_year = data.get('start_year')
    start_month = data.get('start_month')
    start_day = data.get('start_day')
    stop_year = data.get('end_year')
    stop_month = data.get('end_month')
    stop_day = data.get('end_day')

    if None in (msm, start_year, start_month, start_day, stop_year, stop_month, stop_day):
        return jsonify({'error': 'Missing data in request'}), 400

    try:
        msm = int(msm)
        start_year = int(start_year)
        start_month = int(start_month)
        start_day = int(start_day)
        stop_year = int(stop_year)
        stop_month = int(stop_month)
        stop_day = int(stop_day)
        print("Parameters:", msm, start_year, start_month, start_day, stop_year, stop_month, stop_day)
    except ValueError:
        return jsonify({'error': 'Invalid parameter types'}), 400

    get_anomalies(msm, start_year, start_month, start_day, stop_year, stop_month, stop_day)

    return jsonify({'message': 'Process started successfully'}), 200




if __name__ == "__main__":
    app.run(debug=True)
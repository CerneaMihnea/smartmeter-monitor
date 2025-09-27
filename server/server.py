from flask import Flask, request, jsonify, render_template, redirect, url_for
import requests
from datetime import datetime

app = Flask(__name__)
current_hour = 0

data = {}

def format_hours(hours_float):
    total_seconds = int(hours_float * 3600)  # convertim ore în secunde
    days = total_seconds // (24 * 3600)
    remainder = total_seconds % (24 * 3600)
    hrs = remainder // 3600
    remainder %= 3600
    mins = remainder // 60
    secs = remainder % 60
    return f"{days} zile, {hrs} ore, {mins} minute, {secs} secunde"



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', devices=data, ora = current_hour)

@app.route('/add_device', methods=['POST'])
def add_device():
    device_id = request.form.get('device_id')
    slave_id = request.form.get('slave_id')
    baudrate=request.form.get('baudrate')
    data_bits=request.form.get('data_bits')
    stop_bits=request.form.get('stop_bits')
    parity=request.form.get('parity')
    if device_id and device_id not in data:
        data[device_id] = {
            "slave_id" : slave_id,
            "serial_nb": 0,
            "import_energy": 0.0,
            "export_energy": 0.0,
            "hour_first_entry": 0.0,
            "run_hour" : 0.0,
            "last_time_update": None,
            "last_time_entry": None,
            "first_time_update": None,
            "status" : 0
        }
    pico_payload = {
    'device_id': device_id,
    'slave_id': slave_id,
    'baudrate': baudrate,
    'data_bits': data_bits,
    'stop_bits': stop_bits,
    'parity': parity
    }
    print(pico_payload)
    try:
        pico_url = "http://10.10.28.25:5001/device_config"
        r = requests.post(pico_url, json=pico_payload, timeout=2)
        print(f"Trimis configurare la Pico, status: {r.status_code}")
    except Exception as e:
        print(f"Eroare la trimiterea configurarii catre Pico: {e}")


    return redirect(url_for('index'))

@app.route('/data', methods=['POST'])
def update_data():
    try:
        json_data = request.get_json()
        #print(data)
        device_id = json_data.get("device_id")
        if not device_id:
            return "Missing device_id", 400
        if not int(json_data.get("serial_nb", data[device_id]["serial_nb"])):
            raise Exception("Nu exitsa conexiune")
        data[device_id]["serial_nb"] = int(json_data.get("serial_nb", data[device_id]["serial_nb"]))
        data[device_id]["import_energy"] = float(json_data.get("import_energy", data[device_id]["import_energy"]))
        data[device_id]["export_energy"] = float(json_data.get("export_energy", data[device_id]["export_energy"]))
        data[device_id]["last_time_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not data[device_id]["first_time_update"]:
            hour_float_value = float(json_data.get("run_hour", data[device_id]["run_hour"]))
            data[device_id]["hour_first_entry"] = format_hours(hour_float_value)
            data[device_id]["first_time_update"] = datetime.today().timestamp()
        else:
            diff_time = (datetime.today().timestamp() - data[device_id]["first_time_update"])
            hour_float_value = float(json_data.get("run_hour", data[device_id]["run_hour"])) + (1/3600) * diff_time 
        data[device_id]["run_hour"] = format_hours(hour_float_value)
        #print(data)
        return 'OK', 200
    except Exception as e:
        print(e)
        data[device_id]['status'] = 0
        return f"Error: {e}", 400


@app.route('/runtime')
def runtime():
    device_id = request.args.get("device_id")
    if not device_id or device_id not in data:
        return jsonify({"error": "Device not found"}), 404
    #print(data)
    return jsonify(data[device_id])

@app.route('/runtime_index')
def runtime_index():
    global ora_curenta, data
    ora_curenta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({'ora': ora_curenta, 'devices' : data})


@app.route('/device/<device_id>')
def device_detail(device_id):
    if device_id not in data:
        return "Device not found", 404
    return render_template(
        'device_detail.html',
        device_id=device_id,
        device=data[device_id]
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

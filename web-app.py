from flask import Flask, render_template, request, redirect, url_for, jsonify
import subprocess
import re
import os

app = Flask(__name__)

# Store device information (replace with persistent storage if needed)
devices = {}

@app.route('/')
def index():
    return render_template('index.html', devices=devices)

@app.route('/scan')
def scan_devices():
    """Scans for Bluetooth devices and returns the results."""
    try:
        output = subprocess.check_output(['python', 'app.py', '--scan'], stderr=subprocess.STDOUT).decode('utf-8')
        print(output)
        device_name_pattern = re.compile(r"found device ([\dA-F:]+) with name (\S+)")
        matches = device_name_pattern.findall(output)
        found_devices = [{'mac_address': mac, 'device_name': name} for mac, name in matches]
        return jsonify(found_devices)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add_device', methods=['POST'])
def add_device():
    """Adds a new device to the list."""
    data = request.get_json()
    friendly_name = data.get('friendly_name')
    mac_address = data.get('mac_address')
    if friendly_name and mac_address:
        devices[mac_address] = {'friendly_name': friendly_name}
        return jsonify({'message': 'Device added successfully!'}), 201
    else:
        return jsonify({'error': 'Invalid device data'}), 400

@app.route('/device/<mac_address>')
def device_page(mac_address):
    """Renders the device control page."""
    device = devices.get(mac_address)
    if device:
        return render_template('device.html', device=device, mac_address=mac_address)
    else:
        return jsonify({'error': 'Device not found'}), 404

@app.route('/device/<mac_address>/command', methods=['POST'])
def run_command(mac_address):
    """Executes a command on the specified device."""
    command = request.form.get('command')
    if command:
        try:
            # Construct the command with arguments
            command_args = ['python', 'app.py']
            command_args.extend(command.split())  # Split command into arguments
            command_args.extend(['--address', mac_address])

            # Execute the command
            output = subprocess.check_output(command_args).decode('utf-8')
            return jsonify({'output': output}), 200
        except subprocess.CalledProcessError as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'No command provided'}), 400

if __name__ == '__main__':
    port = os.environ.get('PORT', 8080)
    app.run(debug=True, host='0.0.0.0', port=port)

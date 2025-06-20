from flask import Flask, request, jsonify
from flask_cors import CORS
import paramiko
import time

# ✅ Define the Flask app first
app = Flask(__name__)
CORS(app)  # Enable CORS for browser access

@app.route('/control', methods=['POST'])
def control_pdu():
    data = request.get_json()
    ip = data.get('ip')
    outlet = data.get('outlet')
    action = data.get('action')

    username = 'user'
    password = 'pass'  # Replace with actual

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)

        shell = ssh.invoke_shell()
        time.sleep(1)
        shell.recv(1000)

        # Send power command
        shell.send(f'power outlets {outlet} {action}\n')
        time.sleep(1)

        output = shell.recv(2000).decode()

        # Check if confirmation is required
        if "Do you wish to turn outlet" in output:
            shell.send('y\n')
            time.sleep(2)
            output += shell.recv(5000).decode()

        ssh.close()

        return jsonify({
            'status': 'success',
            'message': f'Success: Outlet {outlet} turned {action.upper()}.\nOutput:\n{output}'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

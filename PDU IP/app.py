from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import paramiko
import time

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control_pdu():
    data = request.get_json()
    ip = data['ip']
    outlet = data['outlet']
    action = data['action']

    # Hardcoded credentials (only in backend)
    username = 'user'
    password = 'pass'

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)

        shell = ssh.invoke_shell()
        time.sleep(3)
        shell.recv(1000)

        shell.send(f'power outlets {outlet} {action}\n')
        time.sleep(1)
        output = shell.recv(3000).decode()

        if "Do you wish" in output or "[y/n]" in output:
            shell.send("y\n")
            time.sleep(2)
            output += shell.recv(5000).decode()

        ssh.close()

        # Print SSH output in terminal for debugging
        print(f"\n--- SSH Output for {ip}, outlet {outlet}, action {action} ---")
        print(output)
        print("-------------------------------------------------------------\n")

        return jsonify({'status': 'success', 'message': f'Outlet {outlet} turned {action.upper()} successfully.'})

    except Exception as e:
        print(f"❌ Error during SSH session: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
import pandas as pd
import paramiko
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'})

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    results = []
    try:
        df = pd.read_excel(filepath)

        for index, row in df.iterrows():
            ip = str(row['PDU IP Addresses']).strip()
            outlet = str(row['PDU Outlet Numbers']).strip()
            action = str(row['Action']).strip().lower()

            username = 'user'
            password = 'pass'

            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username=username, password=password, timeout=10)

                shell = ssh.invoke_shell()
                time.sleep(3)  # wait for shell to be ready

                # Clear initial banner/output
                if shell.recv_ready():
                    shell.recv(1000)

                # Send command as single line
                shell.send(f'power outlets {outlet} {action}\n')
                time.sleep(1)

                output = ''
                if shell.recv_ready():
                    output = shell.recv(3000).decode(errors='ignore')

                # Check if confirmation prompt is present
                if "Do you wish" in output or "[y/n]" in output:
                    shell.send("y\n")
                    time.sleep(2)
                    if shell.recv_ready():
                        output += shell.recv(5000).decode(errors='ignore')

                ssh.close()

                # Print SSH output in terminal for debugging
                print(f"\n--- SSH Output for {ip}, outlet {outlet}, action {action} ---")
                print(output)
                print("-------------------------------------------------------------\n")

                results.append({
                    'ip': ip,
                    'outlet': outlet,
                    'action': action.upper(),
                    'status': 'success',
                    'message': f'Outlet {outlet} turned {action.upper()} successfully.',
                    'output': output.splitlines()[-10:]
                })

            except Exception as e:
                results.append({
                    'ip': ip,
                    'outlet': outlet,
                    'action': action.upper(),
                    'status': 'error',
                    'message': f'{ip} outlet {outlet} {action.upper()} failed: {str(e)}'
                })

        os.remove(filepath)
        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    app.run(debug=True)

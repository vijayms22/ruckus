import paramiko
import time

# === USER INPUT ===
hosts = []
print("Enter details of hosts (leave IP blank to stop):")
while True:
    ip = input("Enter IP address: ").strip()
    if not ip:
        break
    username = ("root").strip()
    password = ("WW!3iNfR@1").strip()
    hosts.append({"ip": ip, "username": username, "password": password})

# === CONFIGURATION ===
INSTALLER_URL = "http://10.177.22.50:8080/Ubuntu-falcon-sensor_7.11.0-16407_amd64.deb"
INSTALLER_NAME = INSTALLER_URL.split("/")[-1]
CID = "E2A9E4AA36BA492982C5C31D652FD5E3-12"

INSTALL_COMMANDS = f"""
curl -O {INSTALLER_URL}
echo {{password}} | sudo -S dpkg -i {INSTALLER_NAME}
echo {{password}} | sudo -S /opt/CrowdStrike/falconctl -s --cid={CID}
echo {{password}} | sudo -S systemctl start falcon-sensor || echo {{password}} | sudo -S service falcon-sensor start
ps -e | grep falcon-sensor
"""

STATUS_COMMAND = "systemctl status falcon-sensor --no-pager"

def install_on_host(ip, username, password):
    print(f"\n[🔗] Connecting to {ip}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ip, username=username, password=password, timeout=10)
        print(f"[+] Connected to {ip}, running install commands...")

        commands = INSTALL_COMMANDS.replace("{{password}}", password)
        stdin, stdout, stderr = ssh.exec_command(commands)
        time.sleep(3)  # Increased sleep for installation commands to complete
        output = stdout.read().decode()
        error = stderr.read().decode()

        if "falcon-sensor" in output:
            print(f"[✔] Falcon Sensor installed successfully on {ip}")
        else:
            print(f"[✘] Check output for {ip}:\n{output}\n{error}")

        # Check Falcon Sensor service status
        print(f"[🔍] Checking Falcon Sensor service status on {ip}...")
        status_cmd = f"echo {password} | sudo -S {STATUS_COMMAND}"
        stdin, stdout, stderr = ssh.exec_command(status_cmd)
        status_output = stdout.read().decode()
        status_error = stderr.read().decode()

        if "Active: active (running)" in status_output:
            print(f"[✔] Falcon Sensor service is running on {ip}")
            lines = output.splitlines()
            for line in lines[:10]:
                print(line)
        else:
            print(f"[⚠] Falcon Sensor service might not be running on {ip}")

        print("------ SERVICE STATUS ------")
        print(status_output)
        if status_error:
            print("------ SERVICE ERROR ------")
            print(status_error)

    except Exception as e:
        print(f"[❌] Failed to connect or install on {ip}: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    for host in hosts:
        install_on_host(host["ip"], host["username"], host["password"])

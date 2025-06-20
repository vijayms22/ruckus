import paramiko
import time
import getpass

def control_pdu(ip, username, password, outlet, action):
    try:
        print(f"\n🔌 Connecting to {ip}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)

        shell = ssh.invoke_shell()
        time.sleep(1)
        shell.recv(1000)  # Clear login banner
        time.sleep(1)     # ✅ Wait 1 seconds after login

        # ✅ Send full command
        full_command = f'power outlets {outlet} {action}\n'
        print(f"📤 Sending command: {full_command.strip()}")
        shell.send(full_command)
        time.sleep(1)

        output = shell.recv(3000).decode()
        print(output)

        # ✅ Send 'y' only if prompted
        if "Do you wish to turn outlet" in output or "[y/n]" in output:
            print("✅ Confirming with 'y'")
            shell.send('y\n')
            time.sleep(2)
            output += shell.recv(5000).decode()

        ssh.close()
        print(f"\n✅ Outlet {outlet} turned {action.upper()} successfully.")
       # print("📋 Output:\n", output)

    except Exception as e:
        print(f"\n❌ Error: {e}")

# === INTERACTIVE MODE ===
if __name__ == "__main__":
    print("🔧 Intelligent PDU Control via SSH\n")

    pdu_ip = input("Enter PDU IP Address: ").strip()
    outlet = input("Enter Outlet Number: ").strip()
    action = input("Enter Action (on / off / cycle): ").strip().lower()

    if action not in ['on', 'off', 'cycle']:
        print("❌ Invalid action. Must be: on / off / cycle")
        exit(1)

    username = ("user")
    password = ("pass")

    control_pdu(pdu_ip, username, password, outlet, action)

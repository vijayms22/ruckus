import paramiko
import time

def enable_root_ssh(ip, user, password, root_password, port=22):
    try:
        print(f"[🔗] Connecting to {ip} as {user}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port=port, username=user, password=password, timeout=10)

        shell = client.invoke_shell()

        def send(cmd, wait=1):
            shell.send(cmd + '\n')
            time.sleep(wait)

        # Switch to root user
        send('sudo -i')
        send(password)  # In case it prompts for sudo password

        # Enable root login via SSH
        send("sed -i 's/^#*PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config")
        send("sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config")

        # Set root password
        send(f'echo "root:{root_password}" | chpasswd')

        # Restart SSH service
        send('systemctl restart ssh || systemctl restart sshd')

        print(f"[✅] Root SSH access enabled for {ip}")
        client.close()

    except Exception as e:
        print(f"[❌] Failed to enable root SSH access on {ip}: {e}")

# Usage
target_ip = input("Enter IP Address:")
normal_user = "fiuser"
normal_password = "F!user@123"
new_root_password = "WW!3iNfR@1"

enable_root_ssh(target_ip, normal_user, normal_password, new_root_password)

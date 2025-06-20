import paramiko
import socket

def check_ssh_login(host, username, password, port=22, timeout=5):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"[🔗] Connecting to {host}...")
        client.connect(host, port=port, username=username, password=password, timeout=timeout)
        print(f"[✅] Login successful: {host}")
        return True
    except paramiko.AuthenticationException:
        print(f"[❌] Authentication failed: {host}")
    except paramiko.SSHException as ssh_exc:
        print(f"[⚠️] SSH error on {host}: {ssh_exc}")
    except socket.timeout:
        print(f"[⏱] Connection timed out: {host}")
    except Exception as e:
        print(f"[❗] Error connecting to {host}: {e}")
    finally:
        client.close()
    return False

# Sample list of hosts to check
hosts = input(
    "Enter IP Address: ",)
    # Add more IPs as needed


username = ("root")
password = ("WW!3iNfR@1")

for host in hosts:
    check_ssh_login(host, username, password)

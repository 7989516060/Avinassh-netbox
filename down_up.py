import paramiko
import time
import subprocess  

hostname = '192.168.19.35'  
username = 'admin'          
password = 'tcs123'

check_status_cmd = "show ip interface ethernet1/5"

def connect_to_switch():
    """Connect to the switch via SSH"""
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {hostname}...")
    ssh_client.connect(hostname, username=username, password=password)
    return ssh_client

def send_config_commands(ssh_client):
    """Send configuration commands to bring the interface up"""
    shell = ssh_client.invoke_shell()
    commands = [
        'conf t',
        'interface ethernet1/5',
        'no shutdown',
        'end'
    ]

    for command in commands:
        print(f"Sending command: {command}")
        shell.send(command + '\n')
        time.sleep(1)
    return shell

def execute_command(ssh_client, command):
    """Execute a command to check the interface status"""
    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode()
    return output

def show_popup_notification(status):
    """
    Shows a popup notification using notify-send.
    """
    icon = "✅" if status == "up" else "❌"
    message = f"ethernet1/5 is {status.upper()}"

    subprocess.run(["notify-send", icon, message], check=False)
    print(f"Popup notification: {message}")

def main():
    try:
        ssh_client = connect_to_switch()

        print("Checking the status of ethernet1/5...")
        status_output = execute_command(ssh_client, check_status_cmd)
        print(f"Output of show ip interface ethernet1/5: \n{status_output}")

        if "protocol-down" in status_output or "admin-down" in status_output:
            show_popup_notification("down")

            print("Bringing interface ethernet1/5 up...")
            send_config_commands(ssh_client)

            print("Re-checking the status of ethernet1/5...")
            status_output = execute_command(ssh_client, check_status_cmd)
            print(f"Output of show ip interface ethernet1/5: \n{status_output}")

            if "protocol-up" in status_output or "link-up" in status_output:
                show_popup_notification("up")

        else:
            show_popup_notification("up")

        ssh_client.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

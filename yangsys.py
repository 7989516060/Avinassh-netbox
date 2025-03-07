 #yangsys.py 
import time
import logging
import sysrepo
from plyer import notification  # For cross-platform popups

# Configure logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Define constants
NOTIF_FILE_PATH = "/home/tcs/Sysrepo/Codes/notifyy.xml"
YANG_NAMESPACE = "urn:ietf:params:xml:ns:yang:ietf-netconf-notifications"

# Function to create the notification XML
def create_notification_xml(modules_status):
    """
    Create a single notification XML file containing multiple module changes.
    """
    event_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    notif_content = f"""<notification xmlns="{YANG_NAMESPACE}">
        <eventTime>{event_time}</eventTime>
        <netconf-config-change>
            <datastore>running</datastore>
    """

    for module, status in modules_status.items():
        notif_content += f"""            <edit>
                <target>/{module}</target>
                <operation>{status}</operation>
            </edit>
    """

    notif_content += """        </netconf-config-change>
    </notification>"""

    try:
        with open(NOTIF_FILE_PATH, "w") as file:
            file.write(notif_content)
        logging.info(f"✅ Created notification XML at {NOTIF_FILE_PATH}")
    except Exception as e:
        logging.error(f"❌ Failed to write notification XML: {e}")

# Function to show popup notifications
def show_popup(title, message):
    """
    Display a system popup notification.
    """
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=5  # Notification disappears after 5 seconds
        )
        logging.info(f"📢 Popup: {title} - {message}")
    except Exception as e:
        logging.error(f"⚠️ Failed to show popup: {e}")

# Function to monitor module states by polling sysrepo
def monitor_modules_by_polling(connection, modules):
    """
    Poll sysrepo for module state changes and generate notifications.
    """
    try:
        logging.info(f"🔍 Monitoring modules: {', '.join(modules)}")

        # Start a session with sysrepo
        with connection.start_session() as session:
            while True:
                for module in modules:
                    # Read the current state of each module
                    xpath = "/ietf-interfaces:interfaces"

                    #xpath = f"/ietf-interfaces:interfaces/interface[name='{module}']"
                    try:
                        data = session.get_data(xpath)  # Fetch the data for the module
                        if data:
                            logging.info(f"🔄 Status of module '{module}': {data}")
                            # Generate and show a notification based on the module data
                            status = "modified"  # Example status, you may want to add logic to check changes
                            create_notification_xml({module: status})
                            show_popup(f"Module {module} status", f"Status: {status}")
                    except sysrepo.SysrepoError as e:
                        logging.error(f"❌ Error while reading module {module}: {e}")

                # Sleep for a defined interval before polling again (e.g., every 10 seconds)
                time.sleep(10)

    except Exception as e:
        logging.error(f"❌ Error while monitoring modules: {e}")

# Main function to start monitoring
def start_monitoring(modules):
    """
    Start monitoring YANG modules using polling.
    """
    try:
        # Create a sysrepo connection
        logging.info(f"🔍 Starting to monitor modules: {', '.join(modules)}")
        connection = sysrepo.SysrepoConnection()
        
        # Monitor modules by polling their status
        monitor_modules_by_polling(connection, modules)

    except sysrepo.SysrepoError as e:
        logging.error(f"❌ Sysrepo connection or session error: {e}")
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    # List of modules you want to monitor (change accordingly)
    yang_modules = ["ietf-interfaces", "ietf-netconf"]
    start_monitoring(yang_modules)
_______________________________________________________
tcs@tcs-01HW531513:~/Sysrepo/Codes$ python3 yangsys.py 
2025-02-28 15:39:01,282 - INFO - 🔍 Starting to monitor modules: ietf-interfaces, ietf-netconf
2025-02-28 15:39:01,292 - INFO - 🔍 Monitoring modules: ietf-interfaces, ietf-netconf
Segmentation fault


---- - _ _ _ __--- --- -
The segmentation fault you're encountering likely stems from an issue with how the Sysrepo C bindings are being used. Specifically, it can occur due to improper resource management, memory allocation, or a bug within the sysrepo library itself when interacting with certain operations, like starting a session or fetching data.
Let's break down the key steps and address the issue:
Possible Causes of Segmentation Fault:

    Session Handling: Sysrepo interacts with C libraries, and improper session handling can lead to segmentation faults, especially when you're polling data in a loop.
    Polling Mechanism: Continuous polling of Sysrepo might cause memory issues if resources aren't cleaned up correctly, or if the polling interval is too short, resulting in overload.
    Sysrepo Version: There might be compatibility issues with the current version of Sysrepo you're using and its interaction with your environment.

Proposed Solution Steps:

    Ensure Proper Resource Management:
        You need to make sure that sessions and connections are managed properly, especially if you're running them in a loop.
        Cleanly disconnect sessions after each polling cycle or when the program ends.

    Add More Debugging Information:
        Check if the segmentation fault happens during a specific operation (e.g., connection, session, or polling).
        Add more logging around critical sections to isolate where the fault occurs.

    Try a Simplified Polling Mechanism: Let's isolate the issue by simplifying your polling function to only fetch data once per loop iteration and handle the session lifecycle more carefully.

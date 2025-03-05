import sysrepo
import threading
import time
import ctypes

# Define the callback function signature using ctypes for the basic types only
CallbackType = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p)

# Define the notification callback function
def notification_callback(module_name, xpath, values, private_data):
    try:
        print(f"Notification received from module: {module_name.decode()}")
        print(f"XPath: {xpath.decode()}")
        
        # Iterate over the values and print them
        for value in values:
            # We assume values are sysrepo.String, you may need to adjust based on the real type
            print(f"  - {value.decode() if isinstance(value, bytes) else value}")  # Decode if it's bytes
    except Exception as e:
        print(f"Error processing notification: {e}")

# Function to simulate notifications for testing
def simulate_notifications():
    # Sleep to ensure subscription happens before simulation starts
    time.sleep(2)

    # Simulate some notifications
    print("Simulating notifications...")

    # Create some sample sysrepo values
    values = [
        sysrepo.String("example-key1"),
        sysrepo.String("example-key2")
    ]

    # Call the notification callback with simulated data
    notification_callback("ietf-netconf-notifications".encode(), "/ietf-netconf-notifications:netconf-notification".encode(), values, None)

# Initialize the Sysrepo connection and session
conn = sysrepo.SysrepoConnection()
sess = conn.start_session()

# Use the XPath for the ietf-netconf-notifications module's notification
module_name = "ietf-netconf-notifications"  # Use the appropriate module name
xpath = "/ietf-netconf-notifications:netconf-notification"  # Correct XPath for the notification

# Subscription
print("Subscribing to notifications...")

# Print the callback type for debugging
print(f"Callback function type: {type(notification_callback)}")

# Ensure notification_callback is a function
if callable(notification_callback):
    try:
        # Use the correct callback type for Sysrepo
        c_callback = CallbackType(notification_callback)
        sub = sess.subscribe_notification(c_callback, module_name, xpath)
        print("Successfully subscribed!")
    except Exception as e:
        print(f"Error during subscription: {e}")
else:
    print("Callback function is not callable.")

# Wait for notifications and simulate them in the background
print("Waiting for notifications...")

# Start a background thread to simulate notifications
notification_thread = threading.Thread(target=simulate_notifications)
notification_thread.start()

# Keep the main thread alive while we simulate and listen for notifications
try:
    while notification_thread.is_alive():
        time.sleep(1)
except KeyboardInterrupt:
    print("Terminating program.")

print("Program completed.")




output:
-----------
Subscribing to notifications...
Callback function type: <class 'function'>
Error during subscription: callback must be a function
Waiting for notifications...
Simulating notifications...
Notification received from module: ietf-netconf-notifications
XPath: /ietf-netconf-notifications:netconf-notification
  - example-key1
  - example-key2
Program completed.



oven.yang
-----------
module oven {
    namespace "http://example.com/ns/oven";
    prefix ov;

    container oven-state {
        leaf temperature {
            type int32;
            description "Current temperature of the oven";
        }
        leaf mode {
            type enumeration {
                enum "off";
                enum "bake";
                enum "broil";
                enum "toast";
            }
            description "Current mode of the oven";
        }
    }

    notification mode-change {
        description "Notification for oven mode change";
        leaf new-mode {
            type enumeration {
                enum "off";
                enum "bake";
                enum "broil";
                enum "toast";
            }
            description "The new mode of the oven";
        }
    }
}






oven_notification.py
--------------------

import sysrepo as sr
import time

# Callback function that is triggered when there is a change in the oven's state
def oven_change_cb(session, module_name, event, private_data):
    if event == sr.SR_EV_CHANGE:
        # Get all the changes made to the module "oven"
        it = session.get_changes_iter("/oven:oven-state//*")
        while True:
            change = session.get_change_next(it)
            if change is None:
                break
            print(f"Changed: {change.xpath} {change.oper} {change.prev_val} {change.new_val}")

            # If the mode has changed, trigger the notification
            if change.xpath == "/oven:oven-state/mode" and change.oper == sr.SR_OP_MODIFIED:
                new_mode = change.new_val.as_string()
                print(f"Mode changed to: {new_mode}")
                # Send notification
                notify_mode_change(new_mode)

    return sr.SR_ERR_OK

# Function to send notification when the mode changes
def notify_mode_change(new_mode):
    # Establish connection to Sysrepo
    conn = sr.Connection("oven_application")
    session = sr.Session(conn, sr.SR_DS_RUNNING)
    
    # Create a notification message
    notification = sr.Val("mode-change", sr.SR_CONTAINER_T)
    notification.set_leaf("/oven:mode-change/new-mode", new_mode)
    
    # Send the notification to Sysrepo
    session.notification_send(notification)
    print(f"Notification sent for mode change to: {new_mode}")

    # Clean up
    session.session_stop()
    conn.disconnect()

# Function to set up the oven module and subscribe to changes
def setup_oven_module():
    # Establish connection to Sysrepo
    conn = sr.Connection("oven_application")
    session = sr.Session(conn, sr.SR_DS_RUNNING)
    
    # Subscribe to changes in the "oven" module
    subscribe = sr.Subscribe(session)
    subscribe.module_change_subscribe("oven", oven_change_cb)
    print("Subscribed to oven module changes.")
    
    # Set initial values for the oven state (for POC testing)
    oven_state = {
        "temperature": 180,
        "mode": "bake"
    }
    session.set_item("/oven:oven-state/temperature", oven_state["temperature"])
    session.set_item("/oven:oven-state/mode", oven_state["mode"])
    session.commit()

    print("Initial oven state set.")

    try:
        while True:
            # The application continues to run, waiting for mode changes
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nApplication terminated.")

    # Clean up
    subscribe.unsubscribe()
    session.session_stop()
    conn.disconnect()

if __name__ == "__main__":
    setup_oven_module()

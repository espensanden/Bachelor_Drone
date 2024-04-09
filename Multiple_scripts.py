import threading
import web_server
import presicion_landing

# Create threads for each script
aruco_thread = threading.Thread(target=web_server.run_server)
landing_thread = threading.Thread(target=presicion_landing.landing_drone)

# Start both threads
aruco_thread.start()
landing_thread.start()

# Wait for both threads to finish
aruco_thread.join()
landing_thread.join()

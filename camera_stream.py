import asyncio
import websockets
import cv2
import base64
import numpy as np
import pyrealsense2 as rs

async def video_stream(websocket, path):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipeline.start(config)

    try:
        while True:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            if not depth_frame or not color_frame:
                continue

            # Process the frames
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Object detection logic
            threshold_distance = 0.6  # meters
            object_mask = depth_image < threshold_distance * 1000  # Convert meters to millimeters for mask
            contours, _ = cv2.findContours(np.uint8(object_mask), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            object_details = ""

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 5000:  # Minimum area threshold
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        distance = depth_frame.get_distance(cx, cy)
                        if distance > 0:
                            intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
                            xyz = rs.rs2_deproject_pixel_to_point(intrinsics, [cx, cy], distance)
                            xyz = [round(num, 2) for num in xyz]
                            cv2.putText(color_image, f"XYZ: {xyz} m", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                            object_details += f"Object at ({xyz[0]}, {xyz[1]}, {xyz[2]}) m; "

            # Encode the frame in JPEG format
            _, buffer = cv2.imencode('.jpg', color_image)
            jpg_as_text = base64.b64encode(buffer).decode()
            # Combine image data with object details
            await websocket.send(f"{jpg_as_text};{object_details}")
            await asyncio.sleep(0.1)
    finally:
        pipeline.stop()

#ip to raspberry pi
start_server = websockets.serve(video_stream, '192.168.0.165', 8765) # raspberry pi 4 = 192.168.0.165 "localhost"
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
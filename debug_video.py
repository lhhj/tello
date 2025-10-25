#!/usr/bin/env python3
"""
Debug Tello Video Stream Configuration
Let's check how djitellopy configures the video stream
"""

from djitellopy import Tello
import cv2

def debug_video_config():
    """Debug the video stream configuration"""
    print("=== Tello Video Stream Debug ===")
    
    try:
        tello = Tello()
        print(f"Tello host: {tello.address}")
        print(f"Command port: {tello.clientsocket.getsockname()}")
        
        # Check if there are any video-related attributes
        for attr in dir(tello):
            if 'video' in attr.lower() or 'stream' in attr.lower():
                print(f"Video attribute: {attr}")
                
        # Check the frame reader
        tello.connect()
        tello.streamon()
        
        frame_read = tello.get_frame_read()
        print(f"Frame reader type: {type(frame_read)}")
        print(f"Frame reader attributes: {[attr for attr in dir(frame_read) if not attr.startswith('_')]}")
        
        # Check if we can see the video source
        if hasattr(frame_read, 'cap'):
            cap = frame_read.cap
            print(f"Video capture backend: {cap.getBackendName()}")
            print(f"Video capture properties:")
            print(f"  - Width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
            print(f"  - Height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
            print(f"  - FPS: {cap.get(cv2.CAP_PROP_FPS)}")
            print(f"  - Buffer size: {cap.get(cv2.CAP_PROP_BUFFERSIZE)}")
            
        tello.streamoff()
        
    except Exception as e:
        print(f"Debug error: {e}")

if __name__ == "__main__":
    debug_video_config()
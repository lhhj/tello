#!/usr/bin/env python3
"""
Test different video stream URLs for Tello drone
This script helps find the correct video stream configuration
"""

import cv2
import time
from djitellopy import Tello

def test_video_urls():
    """Test different video stream URLs"""
    print("=== Tello Video Stream URL Test ===\n")
    
    # Connect to drone first
    print("1. Connecting to Tello...")
    try:
        tello = Tello()
        tello.connect()
        print("✓ Connected to Tello")
        
        # Start video stream
        tello.streamon()
        print("✓ Video stream enabled")
        time.sleep(2)  # Wait for stream to initialize
        
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return
    
    # Test different URLs
    video_urls = [
        "udp://192.168.10.1:11111",     # Correct Tello IP
        "udp://@192.168.10.1:11111",    # Alternative format
        "udp://0.0.0.0:11111",          # Library default (incorrect)
        "udp://@0.0.0.0:11111",         # Library format (incorrect)
    ]
    
    print("\n2. Testing video stream URLs...")
    
    for i, url in enumerate(video_urls):
        print(f"\nTest {i+1}: {url}")
        
        try:
            cap = cv2.VideoCapture(url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Try to read a frame
            success = False
            for attempt in range(10):  # Try 10 times
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    print(f"  ✓ Success! Frame size: {frame.shape}")
                    print(f"  ✓ Frame type: {frame.dtype}")
                    
                    # Save a test image
                    filename = f"test_frame_{i+1}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"  ✓ Test frame saved as: {filename}")
                    
                    success = True
                    break
                else:
                    time.sleep(0.1)
            
            if not success:
                print(f"  ✗ Failed to get valid frame")
                
            cap.release()
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Test djitellopy default method
    print(f"\n3. Testing djitellopy default method...")
    try:
        frame_read = tello.get_frame_read()
        time.sleep(1)  # Wait for frame reader to initialize
        
        frame = frame_read.frame
        if frame is not None and frame.size > 0:
            print(f"  ✓ Success! Frame size: {frame.shape}")
            cv2.imwrite("test_frame_djitellopy.jpg", frame)
            print(f"  ✓ Test frame saved as: test_frame_djitellopy.jpg")
        else:
            print(f"  ✗ No frame received from djitellopy method")
            
    except Exception as e:
        print(f"  ✗ djitellopy method error: {e}")
    
    # Cleanup
    try:
        tello.streamoff()
        print("\n✓ Video stream stopped")
    except:
        pass
    
    print("\n=== Test Complete ===")
    print("Check the saved test images to see which method worked!")

def test_network_connectivity():
    """Test basic network connectivity to Tello"""
    print("=== Network Connectivity Test ===\n")
    
    import subprocess
    import platform
    
    # Test ping to Tello
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(['ping', '-n', '1', '192.168.10.1'], 
                                  capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(['ping', '-c', '1', '192.168.10.1'], 
                                  capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ Can ping Tello (192.168.10.1)")
        else:
            print("✗ Cannot ping Tello")
            print("Make sure you're connected to Tello WiFi network")
            return False
            
    except Exception as e:
        print(f"Ping test failed: {e}")
        return False
    
    # Test UDP port accessibility
    import socket
    print("Testing UDP ports...")
    
    ports = [8889, 8890, 11111]
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            sock.sendto(b'test', ('192.168.10.1', port))
            sock.close()
            print(f"✓ Port {port} accessible")
        except Exception as e:
            print(f"✗ Port {port} error: {e}")
    
    return True

if __name__ == "__main__":
    print("Tello Video Stream URL Tester")
    print("=" * 40)
    
    # First test network
    if test_network_connectivity():
        print("\nNetwork tests passed, proceeding with video tests...\n")
        test_video_urls()
    else:
        print("\nNetwork tests failed. Please check your connection to Tello.")
        print("Make sure you're connected to the Tello WiFi network (TELLO-XXXXXX)")
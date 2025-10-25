#!/usr/bin/env python3
"""
Simple Tello Drone Connection Test
This script tests basic connectivity to a Tello drone without GUI
"""

import time
import sys
from djitellopy import Tello

def test_connection():
    """Test basic connection to Tello drone"""
    print("=== Tello Drone Connection Test ===\n")
    
    # Check if we can create a Tello instance
    print("1. Creating Tello instance...")
    try:
        tello = Tello()
        print("✓ Tello instance created successfully")
    except Exception as e:
        print(f"✗ Failed to create Tello instance: {e}")
        return False
    
    # Test connection
    print("\n2. Attempting to connect to drone...")
    print("   Make sure you're connected to the Tello WiFi network (TELLO-XXXXXX)")
    try:
        tello.connect()
        print("✓ Successfully connected to Tello drone")
        
        # Give the drone a moment to initialize
        print("   Waiting for drone to initialize...")
        time.sleep(2)
        
    except Exception as e:
        error_msg = str(e)
        if "state packet" in error_msg.lower():
            print("⚠ Connection established but state monitoring failed")
            print("  This is often normal and won't affect basic control")
            print("  Continuing with connection test...")
        else:
            print(f"✗ Connection failed: {e}")
            print("\nTroubleshooting:")
            print("  - Ensure Tello drone is powered on")
            print("  - Connect to Tello WiFi network (TELLO-XXXXXX)")
            print("  - Make sure no other apps are using the drone")
            return False
    
    # Test basic commands
    print("\n3. Testing basic drone information...")
    
    try:
        # Get battery level
        battery = tello.get_battery()
        print(f"✓ Battery level: {battery}%")
        
        # Get serial number
        serial = tello.get_serial_number()
        print(f"✓ Serial number: {serial}")
        
        # Get SDK version
        sdk_version = tello.get_sdk_version()
        print(f"✓ SDK version: {sdk_version}")
        
        # Get current speed
        speed = tello.get_speed()
        print(f"✓ Current speed: {speed} cm/s")
        
        # Get height (may be 0 if not flying)
        height = tello.get_height()
        print(f"✓ Current height: {height} cm")
        
        # Get temperature
        temp = tello.get_temperature()
        print(f"✓ Temperature: {temp}°C")
        
        # Get flight time
        flight_time = tello.get_flight_time()
        print(f"✓ Flight time: {flight_time} seconds")
        
    except Exception as e:
        print(f"✗ Error getting drone information: {e}")
        return False
    
    # Test video stream capability
    print("\n4. Testing video stream capability...")
    try:
        tello.streamon()
        print("✓ Video stream started successfully")
        time.sleep(1)  # Give it a moment
        
        # Try to get a frame
        frame_read = tello.get_frame_read()
        if frame_read.frame is not None:
            print("✓ Video frame received successfully")
        else:
            print("⚠ Video stream started but no frame received")
            
        tello.streamoff()
        print("✓ Video stream stopped successfully")
        
    except Exception as e:
        print(f"⚠ Video stream test failed: {e}")
        print("  This may not affect basic drone control")
    
    print("\n=== Connection Test Complete ===")
    print("✓ Tello drone is ready for control!")
    print("\nYou can now run:")
    print("  - tello_controller.py (full GUI application)")
    print("  - tello_controller_demo.py (demo mode)")
    
    return True

def quick_battery_check():
    """Quick battery level check"""
    print("=== Quick Battery Check ===")
    try:
        tello = Tello()
        tello.connect()
        battery = tello.get_battery()
        
        print(f"Battery: {battery}%")
        
        if battery < 20:
            print("⚠ WARNING: Low battery! Consider charging before flight.")
        elif battery < 50:
            print("⚠ Battery is getting low. Monitor during flight.")
        else:
            print("✓ Battery level is good for flying.")
            
    except Exception as e:
        print(f"✗ Could not check battery: {e}")

def test_commands():
    """Test sending basic commands"""
    print("\n=== Testing Basic Commands ===")
    
    try:
        tello = Tello()
        tello.connect()
        
        print("Testing command responses...")
        
        # Test query commands (safe)
        commands = [
            ("battery?", lambda: tello.get_battery()),
            ("speed?", lambda: tello.get_speed()),
            ("time?", lambda: tello.get_flight_time()),
            ("height?", lambda: tello.get_height()),
            ("temp?", lambda: tello.get_temperature())
        ]
        
        for cmd_name, cmd_func in commands:
            try:
                result = cmd_func()
                print(f"✓ {cmd_name} -> {result}")
            except Exception as e:
                print(f"✗ {cmd_name} -> Error: {e}")
                
        print("\n✓ Basic command test complete")
        
    except Exception as e:
        print(f"✗ Command test failed: {e}")

def main():
    """Main function with menu"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "battery":
            quick_battery_check()
            return
        elif sys.argv[1] == "commands":
            test_commands()
            return
    
    print("Tello Connection Test Utility")
    print("Usage:")
    print("  python test_connection.py          - Full connection test")
    print("  python test_connection.py battery  - Quick battery check")
    print("  python test_connection.py commands - Test basic commands")
    print()
    
    choice = input("Press Enter to run full test, or type 'battery'/'commands' for specific tests: ").strip().lower()
    
    if choice == "battery":
        quick_battery_check()
    elif choice == "commands":
        test_commands()
    else:
        # Run full test
        success = test_connection()
        
        if success:
            print("\n" + "="*50)
            print("🎉 SUCCESS: Your Tello drone is ready to use!")
            print("="*50)
        else:
            print("\n" + "="*50)
            print("❌ FAILED: Please check the troubleshooting steps above")
            print("="*50)

if __name__ == "__main__":
    main()
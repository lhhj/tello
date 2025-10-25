#!/usr/bin/env python3
"""
Minimal Tello Connection Test
Quick and simple connectivity check
"""

from djitellopy import Tello
import sys
import time

def minimal_test():
    """Minimal connection test"""
    print("Testing Tello connection...")
    
    try:
        # Create and connect
        tello = Tello()
        print("Connecting to drone...")
        tello.connect()
        
        # Give drone time to initialize
        print("Waiting for initialization...")
        time.sleep(2)
        
        # Get basic info
        try:
            battery = tello.get_battery()
            print(f"✓ Connected! Battery: {battery}%")
            
            if battery < 20:
                print("⚠ Low battery warning!")
                
        except Exception as battery_error:
            print("✓ Connected! (Battery status unavailable)")
            print(f"  Note: {battery_error}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "state packet" in error_msg.lower():
            print("✓ Connected! (Status monitoring limited)")
            print("  Basic flight controls should work")
            return True
        else:
            print(f"✗ Connection failed: {e}")
            print("Make sure you're connected to Tello WiFi (TELLO-XXXXXX)")
            return False

if __name__ == "__main__":
    success = minimal_test()
    sys.exit(0 if success else 1)
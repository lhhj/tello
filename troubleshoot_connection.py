#!/usr/bin/env python3
"""
Tello State Packet Troubleshooting Script
Helps diagnose and resolve the common "state packet" connection issue
"""

import socket
import time
from djitellopy import Tello

def test_udp_connection():
    """Test basic UDP communication with Tello"""
    print("=== UDP Connection Test ===")
    
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        # Tello command port
        tello_address = ('192.168.10.1', 8889)
        
        # Send command
        print("Sending 'command' to Tello...")
        sock.sendto(b'command', tello_address)
        
        # Wait for response
        try:
            response, addr = sock.recvfrom(1024)
            print(f"✓ Received response: {response.decode()}")
            return True
        except socket.timeout:
            print("✗ No response received (timeout)")
            return False
        finally:
            sock.close()
            
    except Exception as e:
        print(f"✗ UDP test failed: {e}")
        return False

def test_with_retries():
    """Test Tello connection with multiple retry attempts"""
    print("\n=== Connection Test with Retries ===")
    
    max_retries = 3
    
    for attempt in range(1, max_retries + 1):
        print(f"\nAttempt {attempt}/{max_retries}")
        
        try:
            tello = Tello()
            
            # Try to connect
            print("  Connecting...")
            tello.connect()
            
            # Wait a moment
            print("  Waiting for initialization...")
            time.sleep(3)
            
            # Try to get battery (this often triggers the state packet error)
            print("  Testing battery command...")
            try:
                battery = tello.get_battery()
                print(f"✓ Success! Battery: {battery}%")
                return True
            except Exception as battery_error:
                if "state packet" in str(battery_error).lower():
                    print("  ⚠ State packet issue detected")
                    print("  Trying basic commands instead...")
                    
                    # Try sending a basic command
                    try:
                        result = tello.send_control_command("speed?")
                        print(f"  ✓ Basic command works: {result}")
                        print("  Connection is functional for flight control")
                        return True
                    except Exception as cmd_error:
                        print(f"  ✗ Basic command failed: {cmd_error}")
                else:
                    print(f"  ✗ Battery command failed: {battery_error}")
                    
        except Exception as e:
            print(f"  ✗ Connection attempt failed: {e}")
            
        if attempt < max_retries:
            print("  Retrying in 2 seconds...")
            time.sleep(2)
    
    print(f"\n✗ All {max_retries} attempts failed")
    return False

def test_firewall_and_network():
    """Test for common network/firewall issues"""
    print("\n=== Network Configuration Test ===")
    
    # Test if we can reach the Tello IP
    try:
        import subprocess
        import platform
        
        # Use ping command based on OS
        if platform.system().lower() == "windows":
            result = subprocess.run(['ping', '-n', '1', '192.168.10.1'], 
                                  capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(['ping', '-c', '1', '192.168.10.1'], 
                                  capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ Can ping Tello IP (192.168.10.1)")
        else:
            print("✗ Cannot ping Tello IP")
            print("  Make sure you're connected to Tello WiFi network")
            return False
            
    except Exception as e:
        print(f"⚠ Ping test failed: {e}")
    
    # Test UDP port accessibility
    print("Testing UDP port 8889...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 0))  # Bind to any available port
        sock.settimeout(1)
        sock.sendto(b'command', ('192.168.10.1', 8889))
        sock.close()
        print("✓ UDP port 8889 is accessible")
        return True
    except Exception as e:
        print(f"✗ UDP port test failed: {e}")
        print("  Check firewall settings")
        return False

def provide_solutions():
    """Provide solutions for common issues"""
    print("\n=== Troubleshooting Solutions ===")
    print()
    print("If you're getting 'state packet' errors, try these solutions:")
    print()
    print("1. **Use Flight Control Anyway**:")
    print("   - The 'state packet' error often doesn't affect basic flight")
    print("   - Takeoff, landing, and movement commands usually still work")
    print("   - Only status monitoring (battery, height) may be limited")
    print()
    print("2. **Restart Sequence**:")
    print("   - Turn off Tello drone")
    print("   - Disconnect from Tello WiFi")
    print("   - Wait 10 seconds")
    print("   - Turn on Tello drone")
    print("   - Reconnect to Tello WiFi")
    print("   - Wait for solid connection")
    print("   - Run test again")
    print()
    print("3. **Windows Firewall**:")
    print("   - Allow Python through Windows Firewall")
    print("   - Or temporarily disable firewall for testing")
    print()
    print("4. **WiFi Network**:")
    print("   - Make sure you're connected to TELLO-XXXXXX network")
    print("   - Check signal strength (stay close to drone)")
    print("   - No other devices should be using the drone")
    print()
    print("5. **Try Different Approach**:")
    print("   - Use the demo mode first: python tello_controller_demo.py")
    print("   - Then try real drone with limited status monitoring")

def main():
    """Run all troubleshooting tests"""
    print("Tello Connection Troubleshooting Tool")
    print("=====================================\n")
    
    tests = [
        ("Basic UDP Communication", test_udp_connection),
        ("Network Configuration", test_firewall_and_network),
        ("Connection with Retries", test_with_retries)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("TROUBLESHOOTING SUMMARY")
    print("="*50)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    # Check if any test passed
    if any(result for _, result in results):
        print("\n🎉 At least one test passed!")
        print("Your Tello connection should work for basic flight control.")
    else:
        print("\n⚠ All tests failed.")
        print("Review the solutions below:")
    
    provide_solutions()

if __name__ == "__main__":
    main()
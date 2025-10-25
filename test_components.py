#!/usr/bin/env python3
"""
Test script to verify all Tello controller components work
"""

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
    except ImportError as e:
        print(f"✗ tkinter import failed: {e}")
        return False
        
    try:
        import pygame
        print("✓ pygame imported successfully")
    except ImportError as e:
        print(f"✗ pygame import failed: {e}")
        return False
        
    try:
        import cv2
        print("✓ opencv-python imported successfully")
    except ImportError as e:
        print(f"✗ opencv-python import failed: {e}")
        return False
        
    try:
        from PIL import Image, ImageTk
        print("✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Pillow import failed: {e}")
        return False
        
    try:
        import numpy as np
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        return False
        
    try:
        from djitellopy import Tello
        print("✓ djitellopy imported successfully")
    except ImportError as e:
        print(f"✗ djitellopy import failed: {e}")
        return False
        
    return True

def test_pygame():
    """Test pygame initialization"""
    print("\nTesting pygame...")
    try:
        import pygame
        pygame.init()
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        print(f"✓ Pygame initialized successfully")
        print(f"  Detected {joystick_count} joystick(s)")
        
        if joystick_count > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"  Joystick 0: {joystick.get_name()}")
            
        pygame.quit()
        return True
    except Exception as e:
        print(f"✗ Pygame test failed: {e}")
        return False

def test_gui():
    """Test basic GUI creation"""
    print("\nTesting GUI creation...")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title("Test Window")
        root.geometry("300x200")
        
        # Test basic widgets
        frame = tk.Frame(root)
        frame.pack()
        
        label = tk.Label(frame, text="Test Label")
        label.pack()
        
        button = tk.Button(frame, text="Test Button")
        button.pack()
        
        canvas = tk.Canvas(frame, width=100, height=100, bg='black')
        canvas.pack()
        canvas.create_oval(10, 10, 90, 90, fill='red')
        
        print("✓ GUI components created successfully")
        print("  Close the test window to continue...")
        
        # Show window briefly
        root.after(2000, root.destroy)  # Auto-close after 2 seconds
        root.mainloop()
        
        return True
    except Exception as e:
        print(f"✗ GUI test failed: {e}")
        return False

def test_video_processing():
    """Test video processing capabilities"""
    print("\nTesting video processing...")
    try:
        import cv2
        import numpy as np
        from PIL import Image, ImageTk
        
        # Create a test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:, :] = [100, 150, 200]  # Fill with color
        
        # Test OpenCV operations
        resized = cv2.resize(test_image, (320, 240))
        converted = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Test PIL operations
        pil_image = Image.fromarray(converted)
        
        print("✓ Video processing test successful")
        print(f"  Original size: {test_image.shape}")
        print(f"  Resized to: {resized.shape}")
        
        return True
    except Exception as e:
        print(f"✗ Video processing test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Tello Controller Component Tests ===\n")
    
    tests = [
        ("Package Imports", test_imports),
        ("Pygame Functionality", test_pygame),
        ("GUI Creation", test_gui),
        ("Video Processing", test_video_processing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your Tello controller should work properly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        
    print("\nTo run the applications:")
    print("  Demo mode: python tello_controller_demo.py")
    print("  Real drone: python tello_controller.py")

if __name__ == "__main__":
    main()
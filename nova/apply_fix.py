#!/usr/bin/env python3
"""Nova Emergency Fix Button - applies offline crash fix"""
import tkinter as tk
import sys
import os

# Add nova to path
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/nova"))

def apply_fix():
    """Apply the one-line offline fix"""
    try:
        # Read the file
        nova_file = os.path.expanduser("~/.openclaw/workspace/nova/core/nova_core_full.py")
        with open(nova_file, 'r') as f:
            content = f.read()
        
        # Apply the fix - replace except OSError with except Exception
        if "except OSError:" in content:
            content = content.replace("except OSError:", "except Exception:")
            
            with open(nova_file, 'w') as f:
                f.write(content)
            
            result_label.config(text="✅ Fix applied! Restart Nova.", fg="green")
            print("Fix applied - except Exception instead of except OSError")
        else:
            result_label.config(text="⚠️ Fix already applied", fg="orange")
            
    except Exception as e:
        result_label.config(text=f"❌ Error: {e}", fg="red")

# Build GUI
root = tk.Tk()
root.title("Nova Emergency Fix")
root.geometry("300x120")

label = tk.Label(root, text="Apply offline crash fix:\n(except Exception instead of OSError)")
label.pack(pady=10)

button = tk.Button(root, text="Apply Fix", command=apply_fix, bg="#4CAF50", fg="white", padx=20, pady=10)
button.pack(pady=5)

result_label = tk.Label(root, text="", fg="gray")
result_label.pack(pady=5)

root.mainloop()

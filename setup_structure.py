import os

def create_structure():
    # 1. Define the directories we need (that Django doesn't create by default)
    dirs = [
        os.path.join('core', 'templates'),
    ]

    # 2. Define the new files we need to create (initially empty)
    files = [
        # The HTML template
        os.path.join('core', 'templates', 'home.html'),
        
        # Deployment files
        'Procfile',      # For Railway
        'runtime.txt',   # For Railway Python version
        '.gitignore',    # For Git
        'requirements.txt'
    ]

    # Create Directories
    print("--- Creating Folders ---")
    for d in dirs:
        try:
            os.makedirs(d, exist_ok=True)
            print(f"✅ Created folder: {d}")
        except OSError as e:
            print(f"❌ Error creating {d}: {e}")

    # Create Empty Files
    print("\n--- Creating Empty Files ---")
    for f in files:
        try:
            # open with 'a' (append) prevents overwriting if you already pasted code
            # open with 'w' would wipe it. 
            # We use 'x' (exclusive creation) to be safe, or check existence.
            if not os.path.exists(f):
                with open(f, 'w') as new_file:
                    pass # Just create it empty
                print(f"✅ Created file: {f}")
            else:
                print(f"⚠️  File already exists (skipped): {f}")
        except OSError as e:
            print(f"❌ Error creating {f}: {e}")

    print("\n--- Setup Complete ---")
    print("You can now open these files and paste the code provided.")

if __name__ == "__main__":
    # Check if we are in the right place
    if not os.path.exists('manage.py'):
        print("❌ ERROR: manage.py not found.")
        print("Please run this script inside your Django project folder (where manage.py is).")
    else:
        create_structure()
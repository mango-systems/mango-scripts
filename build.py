import os
import re
import yaml
import hashlib
import time
import secrets  # Python built-in CSPRNG module
import shutil
from colorama import init, Fore, Style

# Initialize Colorama for terminal color formatting
init(autoreset=True)

# Get the absolute path of the directory where this script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Load settings from settings.yaml
settings_file_path = os.path.join(script_directory, 'settings.yaml')
with open(settings_file_path, 'r') as settings_file:
    settings = yaml.safe_load(settings_file)

# Define the SHA-256 signature folder at the root level
SIGNATURE_FOLDER = os.path.join(script_directory, 'sha_signatures')

# Define the regex pattern to match the fields
field_patterns = {
    "Author": r'# Author:\s*(.+)',
    "Title": r'# Title:\s*(.+)',
    "Version": r'# Version:\s*(.+)',
    "Verified": r'# Verified:\s*(.+)',
    "Description": r'# Description:\s*(.+)',
}

# Get the current time in the specified format
def get_current_time():
    return time.strftime("%b %d %Y, %I:%M:%S%p")

# Generate a random passphrase for SHA-256 signatures
def generate_random_passphrase():
    return secrets.token_hex(16)

# Create the SHA-256 signature for a given script
def generate_sha256_signature(script_path):
    sha256 = hashlib.sha256()
    with open(script_path, 'rb') as script_file:
        while True:
            data = script_file.read(8192)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

# Create the signature folder at the root level if it doesn't exist
if not os.path.exists(SIGNATURE_FOLDER):
    os.makedirs(SIGNATURE_FOLDER)

# Get the absolute path of the "validated_scripts" folder
validated_script_folder = os.path.join(script_directory, 'validated_scripts')

# Ensure that the "validated_scripts" folder exists
if not os.path.exists(validated_script_folder):
    os.makedirs(validated_script_folder)

# List all script files in the "validated_scripts" folder
validated_script_files = os.listdir(validated_script_folder)

# Loop through script files in the "validated_scripts" folder
for script_file in validated_script_files:
    script_path = os.path.join(validated_script_folder, script_file)
    signature_path = os.path.join(SIGNATURE_FOLDER, f"{script_file}.sha256")

    # Generate a unique passphrase for each script
    passphrase = generate_random_passphrase()

    # Generate SHA-256 signature
    signature = generate_sha256_signature(script_path)

    # Save the SHA-256 signature to a file at the root level
    with open(signature_path, 'w') as signature_file:
        signature_file.write(signature)

# List all script files in the "scripts" folder
script_files = os.listdir(os.path.join(script_directory, "scripts"))

# Initialize a dictionary to store the extracted information
all_scripts_data = []

# Loop through script files in the "scripts" folder
for script_file in script_files:
    script_path = os.path.join(script_directory, "scripts", script_file)
    validated_script_path = os.path.join(validated_script_folder, script_file)
    signature_path = os.path.join(SIGNATURE_FOLDER, f"{script_file}.sha256")

    # If the script does not exist in the validated_scripts folder, copy it
    if not os.path.exists(validated_script_path):
        shutil.copy2(script_path, validated_script_path)

    # Generate a unique passphrase for each script
    passphrase = generate_random_passphrase()

    # Generate SHA-256 signature
    signature = generate_sha256_signature(validated_script_path)

    # Save the SHA-256 signature to a file at the root level
    with open(signature_path, 'w') as signature_file:
        signature_file.write(signature)

    # Initialize a dictionary to store the extracted information for this script
    extracted_data = {}

    # Read the script file
    with open(validated_script_path, 'r') as file:
        for line in file:
            for field_name, pattern in field_patterns.items():
                match = re.match(pattern, line)
                if match:
                    extracted_data[field_name] = match.group(1)

    # Add the script and signature locations to the extracted data
    extracted_data["script_location"] = f"{settings['script_location_prefix']}{script_file}"
    extracted_data["signature_location"] = f"{settings['signature_location_prefix']}{script_file}.sha256"

    # Add the "last_modified" field to the extracted data
    last_modified = os.path.getmtime(validated_script_path)
    extracted_data["last_modified"] = time.strftime("%b %d %Y, %I:%M:%S%p", time.localtime(last_modified))

    # Append the extracted data to the list
    all_scripts_data.append(extracted_data)

# Create a YAML dictionary with script information numbered as
# 1, 2, 3, ...
yaml_data = {str(i + 1): {k: v for k, v in script_data.items() if k != "passphrase"} for i, script_data in enumerate(all_scripts_data)}

# Output the YAML data to resources.yml
resources_file_path = os.path.join(script_directory, 'resources.yml')
with open(resources_file_path, 'w') as yaml_file:
    yaml.dump(yaml_data, yaml_file, default_flow_style=False)

print(f"[{Fore.GREEN}{get_current_time()}{Style.RESET_ALL}] Data has been saved to resources.yml.")

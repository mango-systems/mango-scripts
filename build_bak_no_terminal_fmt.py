import os
import re
import yaml
import subprocess

# Load settings from settings.yaml
with open('settings.yaml', 'r') as settings_file:
    settings = yaml.safe_load(settings_file)

# Define the GPG key name and link prefixes from the settings
KEY_NAME = settings.get("key_name", "my_gpg_key")
SCRIPT_LOCATION_PREFIX = settings.get("script_location_prefix", "https://example.com/scripts/")
SIGNATURE_LOCATION_PREFIX = settings.get("signature_location_prefix", "https://example.com/signatures/")
FORCE_OVERWRITE = settings.get("force_overwrite", False)  # Set to True to force key overwrite

# Define the regex pattern to match the fields
field_patterns = {
    "Author": r'# Author:\s*(.+)',
    "Title": r'# Title:\s*(.+)',
    "Version": r'# Version:\s*(.+)',
    "Verified": r'# Verified:\s*(.+)',
    "Description": r'# Description:\s*(.+)',
}

# Initialize a dictionary to store the extracted information
all_scripts_data = []

# Create output folders if they don't exist
if not os.path.exists("gpg_signatures"):
    os.mkdir("gpg_signatures")

if not os.path.exists("scripts"):
    os.mkdir("scripts")

# List all script files in the "scripts" folder
script_files = os.listdir("scripts")

# Generate a GPG key pair (if not already done or if force overwrite is True)
key_exists = os.path.exists(f"gpg_signatures/{KEY_NAME}.asc")
if not key_exists or (key_exists and FORCE_OVERWRITE):
    try:
        subprocess.check_output(["gpg", "--gen-key", "--batch", "--yes", f"--passphrase {os.urandom(16)}", f"--quick-gen-key {KEY_NAME}"], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print("Error generating GPG key pair:", e)

# Loop through script files
for script_file in script_files:
    script_path = os.path.join("scripts", script_file)
    signature_path = os.path.join("gpg_signatures", f"{script_file}.asc")

    # Sign the script with the generated GPG key
    try:
        subprocess.check_output(["gpg", "--sign", "--local-user", KEY_NAME, "--yes", "-o", signature_path, script_path], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error signing {script_file} with GPG:", e)
        continue

    # Initialize a dictionary to store the extracted information for this script
    extracted_data = {}

    # Read the script file
    with open(script_path, 'r') as file:
        for line in file:
            for field_name, pattern in field_patterns.items():
                match = re.match(pattern, line)
                if match:
                    extracted_data[field_name] = match.group(1)

    # Add the script and signature locations to the extracted data
    extracted_data["script_location"] = f"{SCRIPT_LOCATION_PREFIX}{script_file}"
    extracted_data["signature_location"] = f"{SIGNATURE_LOCATION_PREFIX}{script_file}.asc"

    # Append the extracted data to the list
    all_scripts_data.append(extracted_data)

# Create a YAML dictionary with script information numbered as 1, 2, 3, ...
yaml_data = {str(i + 1): script_data for i, script_data in enumerate(all_scripts_data)}

# Output the YAML data to resources.yml
with open('resources.yml', 'w') as yaml_file:
    yaml.dump(yaml_data, yaml_file, default_flow_style=False)

print("Data has been saved to resources.yml.")

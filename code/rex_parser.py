import yaml
import os


def find_yaml_files(directory):
    yaml_files = []

    # Walk through the directory recursively
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file ends with .yaml or .yml
            if file.endswith(('.yaml', '.yml')):
                # Get the full file path
                file_path = os.path.join(root, file)
                yaml_files.append(file_path)

    return yaml_files


def parse_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            # Load the YAML file
            data = yaml.safe_load(file)

            # Extract the top-level "Name"
            name = data.get("name")

            # Navigate through the nested properties for "foo.bar.baz"
            email_recipients = data.get("plugin_config", {}).get("etsy", {}).get("datacop", {}).get("email_recipients")
            return name, email_recipients

    except Exception as e:
        print(f"Error parsing YAML file: {e}")
        return None, None


def check_email_contains(emails, match_phrases):
    for email in emails:
        for match_phrase in match_phrases:
            if match_phrase in email:
                return True
    return False

# Example usage
for file in find_yaml_files("/Users/mmoy/code/airflow-rollups/dags/yaml_dags/"):
    name, email_recipients = parse_yaml(file)

    # check if email contains cdata, estein, etoomer, kzhou
    if check_email_contains(email_recipients, ['cdata', 'visits-support', 'wins', 'data-eng', 'wins-alert', 'cdata-alerts']):
        print(f"Name: {name}")
        print(f"Email Recipients: {email_recipients}")

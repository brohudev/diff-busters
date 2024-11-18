import requests
import time
import subprocess

REMOTE_PORT = 8000  # Should match the port used in remote_server.py
REMOTE_HOSTS_FILE = 'remote_hosts.txt'  # File containing the list of remote hosts

def get_local_config():
    try:
        # Use ip6tables-save to get the local configuration
        result = subprocess.run(['ip6tables-save'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        return result.stdout.encode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f'Failed to retrieve local ip6tables configuration: {e.stderr}')
        return None

def get_remote_config(remote_host):
    url = f'http://{remote_host}:{REMOTE_PORT}/config'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.content
        else:
            print(f'Failed to retrieve remote config from {remote_host}: {response.status_code} {response.reason}')
            return None
    except requests.RequestException as e:
        print(f'Connection error with {remote_host}: {e}')
        return None

def update_remote_config(remote_host, config_data):
    url = f'http://{remote_host}:{REMOTE_PORT}/config'
    try:
        response = requests.post(url, data=config_data, timeout=5)
        if response.status_code == 200:
            print(f'Remote configuration on {remote_host} updated successfully.')
        else:
            print(f'Failed to update remote config on {remote_host}: {response.status_code} {response.reason}')
    except requests.RequestException as e:
        print(f'Connection error with {remote_host}: {e}')

def main():
    while True:
        # Get the local ip6tables configuration
        local_config = get_local_config()
        if local_config is None:
            print('Skipping this iteration due to local configuration retrieval failure.')
            time.sleep(300)  # Wait before the next attempt
            continue

        # Read the list of remote hosts
        with open(REMOTE_HOSTS_FILE, 'r') as f:
            remote_hosts = [line.strip() for line in f if line.strip()]

        for remote_host in remote_hosts:
            print(f'Processing remote host: {remote_host}')
            # Retrieve the remote configuration
            remote_config = get_remote_config(remote_host)
            if remote_config is None:
                print(f'Skipping {remote_host} due to retrieval failure.')
                continue  # Proceed to the next host

            # Compare configurations
            if local_config != remote_config:
                print(f'Configurations differ on {remote_host}. Updating remote configuration.')
                update_remote_config(remote_host, local_config)
            else:
                print(f'Configurations are identical on {remote_host}. No action required.')

        # Wait for 5 minutes before the next run
        print('Waiting for 5 minutes before next check...')
        time.sleep(300)  # Sleep for 300 seconds (5 minutes)

if __name__ == '__main__':
    main()

import socket
import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# ANSI escape codes for purple text
PURPLE = "\033[95m"
RESET = "\033[0m"

def clear_console():
    # Clear the console based on the OS
    os.system('cls' if os.name == 'nt' else 'clear')

def get_geolocation(ip_address):
    try:
        response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        data = response.json()
        location_info = {
            "IP": data.get("ip"),
            "City": data.get("city"),
            "Region": data.get("region"),
            "Country": data.get("country"),
            "ISP": data.get("org"),
            "Location": data.get("loc"),
        }
        return location_info
    except requests.RequestException as e:
        print(f"{PURPLE}Error retrieving geolocation data: {e}{RESET}")
        return None

def check_port(ip_address, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Set timeout to 1 second
    result = sock.connect_ex((ip_address, port))
    sock.close()
    return port if result == 0 else None

def check_open_ports(ip_address, port_range):
    open_ports = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_port = {executor.submit(check_port, ip_address, port): port for port in port_range}
        for future in as_completed(future_to_port):
            port = future_to_port[future]
            try:
                result = future.result()
                if result is not None:
                    open_ports.append(result)
            except Exception as e:
                print(f"{PURPLE}Error checking port {port}: {e}{RESET}")
    return open_ports

def save_results(ip_address, geolocation, open_ports):
    # Determine the path for the "Scanned IPs" folder on the Desktop
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    folder_name = "Scanned IPs"
    folder_path = os.path.join(desktop_path, folder_name)

    # Create the folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Create the full JSON file path
    json_file_path = os.path.join(folder_path, f"{ip_address}.json")

    # Delete the existing file if it exists
    if os.path.exists(json_file_path):
        os.remove(json_file_path)
        print(f"{PURPLE}Existing file '{os.path.basename(json_file_path)}' deleted.{RESET}")

    # Prepare the results to save
    results = {
        "Geolocation": geolocation,
        "Open Ports": open_ports
    }
    
    # Save the results to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)
    
    print(f"{PURPLE}Results saved to: {json_file_path}{RESET}")

def main():
    clear_console()  # Clear the console
    
    # Display ASCII art in purple
    print(f"{PURPLE}██╗██████╗     ███████╗ ██████╗ █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗ ")
    print(f"██║██╔══██╗    ██╔════╝██╔════╝██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗")
    print(f"██║██████╔╝    ███████╗██║     ███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝")
    print(f"██║██╔═══╝     ╚════██║██║     ██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗")
    print(f"██║██║         ███████║╚██████╗██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║")
    print(f"╚═╝╚═╝         ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝{RESET}")
    
    ip_address = input(f"{PURPLE}Enter the IP address to scan: {RESET}")
    
    # Get geolocation information
    geolocation = get_geolocation(ip_address)
    if geolocation:
        print(f"\n{PURPLE}Geolocation Information:{RESET}")
        for key, value in geolocation.items():
            print(f"{PURPLE}{key}: {value}{RESET}")
    
    # Check for open ports
    print(f"\n{PURPLE}Checking open ports (1-1000)...{RESET}")
    open_ports = check_open_ports(ip_address, range(1, 1001))
    if open_ports:
        print(f"{PURPLE}Open ports on {ip_address}: {open_ports}{RESET}")
    else:
        print(f"{PURPLE}No open ports found on {ip_address} in the range 1-1000.{RESET}")
    
    # Save the results to a JSON file in the "Scanned IPs" folder on the Desktop
    save_results(ip_address, geolocation, open_ports)

if __name__ == "__main__":
    main()

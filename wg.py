import subprocess
import os

def gen_keys():
    try:
        # Install WireGuard
        subprocess.run(["sudo", "apt", "install", "-y", "wireguard"], check=True)
        subprocess.run(["ssh", "bravo","sudo", "apt", "install", "-y", "wireguard"], check=True)
        subprocess.run(["ssh", "charlie","sudo", "apt", "install", "-y", "wireguard"], check=True)
        # Create the "keys" directory
        keys_dir = "/home/student/wg/keys"
        os.makedirs(keys_dir, exist_ok=True)
        # Change the umask for key file permissions
        os.umask(0o077)
        
        # Key generation
        keys = ["bravo", "charlie", "bchd"]
        for key in keys:
            private_key = subprocess.run([f"sudo -u student wg genkey | tee {keys_dir}/{key}.key | wg pubkey > {keys_dir}/{key}.pub"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, check=False, input="\n", executable="/bin/bash", cwd="/home/student/wg/keys")
            #print(private_key.stdout, "HELLLLLOOOOO")
        set_perms = f"sudo -u student chmod 700 {keys_dir}/*"
        chown_command = f"sudo chown student:student {keys_dir}/*"
        subprocess.run(chown_command, shell=True, check=True)
        subprocess.run(set_perms, shell=True, check=True)

    except Exception as e:
        print(f"An error occurred: {e}")

def execute_commands(WG_BRAVO_PUB, WG_BRAVO_KEY, WG_CHARLIE_PUB, WG_CHARLIE_KEY, WG_BCHD_PUB, WG_BCHD_KEY, BRAVO_IP, BCHD_IP, CHARLIE_IP): 
    try:
        # Install j2cli
        subprocess.run(["python3", "-m", "pip", "install", "--user", "j2cli"])
        subprocess.run(["ssh", "bravo", "python3", "-m", "pip", "install", "--user", "j2cli"], check=True)
        subprocess.run(["ssh", "charlie", "python3", "-m", "pip", "install", "--user", "j2cli"], check=True)
        # Add the bravo host key to known_hosts
        keyscan1 = "sudo -u student ssh-keyscan -t rsa bravo >> ~/.ssh/known_hosts"
        subprocess.run([keyscan1], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, check=True, input="\n", executable="/bin/bash", cwd="/")

        # Generate and remove SSH keys
        subprocess.run(["sudo -u student ssh-keygen -H"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, check=True, input="\n", executable="/bin/bash", cwd="/")
        subprocess.run(["sudo -u student rm ~/.ssh/known_hosts.old"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, check=False, input="\n", executable="/bin/bash", cwd="/")

        # Install WireGuard on bravo
        subprocess.run(["sudo -u student ssh bravo sudo apt install -y wireguard"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, check=True, input="\n", executable="/bin/bash", cwd="/")

        # Create directories and variables
        subprocess.run(["sudo -u student mkdir -p /home/student/wg"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, check=False, input="\n", executable="/bin/bash", cwd="/")
        bravo_pub_path = "/home/student/wg/keys/bravo.pub"
        bravo_key_path = "/home/student/wg/keys/bravo.key"
        charlie_pub_path = "/home/student/wg/keys/charlie.pub"
        charlie_key_path = "/home/student/wg/keys/charlie.key"
        bchd_pub_path = "/home/student/wg/keys/bchd.pub"
        bchd_key_path = "/home/student/wg/keys/bchd.key"

        # Use subprocess to execute 'cat' and capture the output
        WG_BRAVO_PUB = subprocess.check_output(["cat", bravo_pub_path], universal_newlines=True)
        WG_BRAVO_KEY = subprocess.check_output(["cat", bravo_key_path], universal_newlines=True)
        WG_CHARLIE_PUB = subprocess.check_output(["cat", charlie_pub_path], universal_newlines=True)
        WG_CHARLIE_KEY = subprocess.check_output(["cat", charlie_key_path], universal_newlines=True)
        WG_BCHD_PUB = subprocess.check_output(["cat", bchd_pub_path], universal_newlines=True)
        WG_BCHD_KEY = subprocess.check_output(["cat", bchd_key_path], universal_newlines=True)

        # Remove leading/trailing whitespace and newline characters
        WG_BRAVO_PUB = WG_BRAVO_PUB.strip()
        WG_BRAVO_KEY = WG_BRAVO_KEY.strip()
        WG_CHARLIE_PUB = WG_CHARLIE_PUB.strip()
        WG_CHARLIE_KEY = WG_CHARLIE_KEY.strip()
        WG_BCHD_PUB = WG_BCHD_PUB.strip()
        WG_BCHD_KEY = WG_BCHD_KEY.strip()
        BRAVO_IP = subprocess.run(["dig +short +search bravo"], stdout=subprocess.PIPE, shell=True, check=True)
        BRAVO_IP = BRAVO_IP.stdout.decode().strip()
        BCHD_IP = subprocess.run(["dig +short +search bchd"], stdout=subprocess.PIPE, shell=True, check=True)
        BCHD_IP = BCHD_IP.stdout.decode().strip()
        CHARLIE_IP = subprocess.run(["dig +short +search charlie"], stdout=subprocess.PIPE, shell=True, check=True)
        CHARLIE_IP = CHARLIE_IP.stdout.decode().strip()
        print(CHARLIE_IP)
        print(BCHD_IP)
        print(BRAVO_IP)
        print("SHOULD BE HERE")
        print(WG_BCHD_PUB)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.cmd}")
        print(f"Return code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        raise
    return WG_BRAVO_PUB, WG_BRAVO_KEY, WG_CHARLIE_PUB, WG_CHARLIE_KEY, WG_BCHD_PUB, WG_BCHD_KEY, BRAVO_IP, BCHD_IP, CHARLIE_IP

def create_bravo_conf_j2(WG_BRAVO_KEY, WG_CHARLIE_PUB, WG_BCHD_PUB, BCHD_IP, CHARLIE_IP):
    directory_path = "/home/student/wg/j2"
    file_path = os.path.join(directory_path, "bravo.conf.j2")

    # Create the directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)

    # Define the content for bravo.conf.j2
    config_content = f"""
[Interface]
# Name = >>> BRAVO <<<
# Address = 10.65.0.1/32
# SaveConfig = true
# MTU = 1500
PrivateKey = { WG_BRAVO_KEY }
ListenPort = 51820

[Peer]
# name = charlie - KVM server with a local slash 16: 10.66.0.0/26
PublicKey = { WG_CHARLIE_PUB }
AllowedIPs = 10.66.0.0/16
Endpoint = { CHARLIE_IP }:51820
PersistentKeepalive = 25

[Peer]
# Name = bchd
PublicKey = { WG_BCHD_PUB }
AllowedIPs = 10.67.0.1/32
Endpoint = { BCHD_IP }:51820
PersistentKeepalive = 25
"""

    # Write the content to the bravo.conf.j2 file
    with open(file_path, "w") as file:
        file.write(config_content)

def create_bchd_conf_j2(WG_BCHD_KEY, WG_CHARLIE_PUB, WG_BRAVO_PUB, BRAVO_IP, CHARLIE_IP):
    directory_path = "/home/student/wg/j2"
    file_path = os.path.join(directory_path, "bchd.conf.j2")

    # Create the directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)

    # Define the content for bravo.conf.j2
    config_content = f"""
[Interface]
# Name = >>> BCHD <<<
# Address = 10.67.0.1/32
# SaveConfig = true
# MTU = 1500
PrivateKey = { WG_BCHD_KEY }
ListenPort = 51820

[Peer]
# name = charlie - KVM server with a local slash 16: 10.66.0.0/26
PublicKey = { WG_CHARLIE_PUB }
AllowedIPs = 10.66.0.0/16
Endpoint = { CHARLIE_IP }:51820
PersistentKeepalive = 25

[Peer]
# Name = bravo
PublicKey = { WG_BRAVO_PUB }
AllowedIPs = 10.65.0.0/16
Endpoint = { BRAVO_IP }:51820
PersistentKeepalive = 25
"""

    # Write the content to the bravo.conf.j2 file
    with open(file_path, "w") as file:
        file.write(config_content)

def create_charlie_conf_j2(WG_CHARLIE_KEY, WG_BRAVO_PUB, WG_BCHD_PUB, BRAVO_IP, BCHD_IP):
    directory_path = "/home/student/wg/j2"
    file_path = os.path.join(directory_path, "charlie.conf.j2")

    # Create the directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)

    # Define the content for bravo.conf.j2
    config_content = f"""
[Interface]
# Name = >>> CHARLIE <<<
# Address = 10.66.0.1/32
# SaveConfig = true
# MTU = 1500
PrivateKey = { WG_CHARLIE_KEY }
ListenPort = 51820

[Peer]
# name = BCHD - KVM server with a local slash 16: 10.66.0.0/26
PublicKey = { WG_BCHD_PUB }
AllowedIPs = 10.67.0.1/32
Endpoint = { BCHD_IP }:51820
PersistentKeepalive = 25

[Peer]
# Name = bravo
PublicKey = { WG_BRAVO_PUB }
AllowedIPs = 10.65.0.0/16
Endpoint = { BRAVO_IP }:51820
PersistentKeepalive = 25
"""

    # Write the content to the bravo.conf.j2 file
    with open(file_path, "w") as file:
        file.write(config_content)

def configure_wireguard_on_bravo():
    # Create the directory for configuration files
    conf_dir = "/home/student/wg/conf"
    os.makedirs(conf_dir, exist_ok=True)
    
    subprocess.run(["j2 /home/student/wg/j2/bravo.conf.j2   >   /home/student/wg/conf/bravo.conf"], shell=True, check=False)

    # Copy the configuration to the remote host (bravo)
    subprocess.run(["cat /home/student/wg/conf/bravo.conf | ssh bravo sudo tee /etc/wireguard/wg0.conf"], shell=True, check=True)

    # Configure WireGuard on the remote hostguard (bravo)
    #create_wg0="ssh bravo   sudo ip link add dev wg0 type wireguard"
    subprocess.run(["ssh bravo sudo ip netns add core"], shell=True, check=False)
    subprocess.run(["ssh bravo sudo ip link add dev wg0 type wireguard"], shell=True, check=False)
    subprocess.run(["ssh bravo sudo ip link set wg0 netns core"], shell=True, check=False)
    subprocess.run(["ssh bravo sudo ip netns exec core wg setconf wg0 /etc/wireguard/wg0.conf"], shell=True, check=False)
    subprocess.run(["ssh bravo sudo ip -n core -4 address add 10.65.0.1/32 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bravo sudo ip -n core link set mtu 1420 up dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bravo sudo ip -n core -4 route add 10.66.0.0/16 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bravo sudo ip -n core -4 route add 10.67.0.1/32 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bravo sudo ip -n core -4 route add 10.1.0.0/20 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bravo sudo ip netns exec core ip route add default dev wg0 via 10.65.0.1 onlink"], shell=True, check=False)


def configure_wireguard_on_bchd():
    # Create the directory for configuration files
    conf_dir = "/home/student/wg/conf"
    os.makedirs(conf_dir, exist_ok=True)
    
    subprocess.run(["sudo -u student j2 /home/student/wg/j2/bchd.conf.j2   >   /home/student/wg/conf/bchd.conf"], shell=True, check=True)

    # Copy the configuration to the remote host (bchd)
    subprocess.run(["cat /home/student/wg/conf/bchd.conf | ssh bchd sudo tee /etc/wireguard/wg0.conf"], shell=True, check=True)

    # Configure WireGuard on the remote hostguard (bchd)
    #create_wg0="ssh bchd   sudo ip link add dev wg0 type wireguard"
    #subprocess.run(["ssh bchd sudo ip netns add core"], shell=True, check=False)
    subprocess.run(["ssh bchd sudo ip link add wg0 type wireguard"], shell=True, check=False)
    subprocess.run(["ssh bchd sudo ip link set wg0 netns core"], shell=True, check=False)
    subprocess.run(["ssh bchd sudo ip netns exec core wg setconf wg0 /etc/wireguard/wg0.conf"], shell=True, check=False)
    subprocess.run(["ssh bchd sudo ip -n core -4 address add 10.67.0.1/32 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bchd sudo ip -n core link set mtu 1500 up dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bchd sudo ip -n core -4 route add 10.65.0.0/16 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bchd sudo ip -n core -4 route add 10.66.0.0/16 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bchd sudo ip -n core -4 route add 10.1.0.0/20 dev wg0"], shell=True, check=False)


def configure_wireguard_on_charlie():
    # Create the directory for configuration files
    conf_dir = "/home/student/wg/conf"
    os.makedirs(conf_dir, exist_ok=True)
    
    subprocess.run(["sudo -u student j2 /home/student/wg/j2/charlie.conf.j2   >   /home/student/wg/conf/charlie.conf"], shell=True, check=True)

    # Copy the configuration to the remote host (charlie)
    subprocess.run(["cat /home/student/wg/conf/charlie.conf | ssh charlie sudo tee /etc/wireguard/wg0.conf"], shell=True, check=True)

    # Configure WireGuard on the remote hostguard (charlie))
    #create_wg0="ssh bravo   sudo ip link add dev wg0 type wireguard"
    subprocess.run(["ssh charlie sudo ip netns add core"], shell=True, check=False)
    subprocess.run(["ssh charlie sudo ip link add dev wg0 type wireguard"], shell=True, check=False)
    subprocess.run(["ssh charlie sudo ip link set wg0 netns core"], shell=True, check=False)
    subprocess.run(["ssh charlie sudo ip netns exec core wg setconf wg0 /etc/wireguard/wg0.conf"], shell=True, check=False)
    subprocess.run(["ssh charlie sudo ip -n core -4 address add 10.66.0.1/32 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh charlie sudo ip -n core link set mtu 1420 up dev wg0"], shell=True, check=False)
    subprocess.run(["ssh charlie sudo ip -n core -4 route add 10.65.0.0/16 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh charlie sudo ip -n core -4 route add 10.67.0.1/32 dev wg0"], shell=True, check=False) #10.1.0.0/20
    subprocess.run(["ssh charlie sudo ip -n core -4 route add 10.1.0.0/20 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh charlie sudo ip netns exec core ip route add default dev wg0 via 10.66.0.1 onlink"], shell=True, check=False)

def execute_ping_commands():
    # Define the commands and their corresponding comments
    commands = [
        ("sudo ip netns exec core ping 10.65.0.1 -c 1 -W 1", "PING from BCHD (wg0) to BRAVO (wg0)"),
        ("sudo ip netns exec core ping 10.66.0.1 -c 1 -W 1", "PING from BCHD (wg0) to CHARLIE (wg0)"),
        ("ssh bravo sudo ip netns exec core ping 10.66.0.1 -c 1 -W 1", "PING from BRAVO (wg0) to CHARLIE (wg0)"),
        ("ssh bravo sudo ip netns exec core ping 10.67.0.1 -c 1 -W 1", "PING from BRAVO (wg0) to BCHD (wg0)"),
        ("ssh charlie sudo ip netns exec core ping 10.65.0.1 -c 1 -W 1", "PING from CHARLIE (wg0) to BRAVO (wg0)"),
        ("ssh charlie sudo ip netns exec core ping 10.67.0.1 -c 1 -W 1", "PING from CHARLIE (wg0) to BCHD (wg0)"),
        ("sudo ip netns exec whiskey ping 10.65.0.1 -c 1 -W 1", "PING from WHISKEY to BRAVO (wg0)"), 
        ("sudo ip netns exec whiskey ping bravo -c 1 -W 1", "PING from WHISKEY to BRAVO"), 
        ("sudo ip netns exec xray ping 10.65.0.1 -c 1 -W 1", "PING from XRAY to BRAVO (wg0)"),
        ("sudo ip netns exec xray ping bravo -c 1 -W 1", "PING from XRAY to BRAVO"),  
        ("sudo ip netns exec yankee ping 10.65.0.1 -c 1 -W 1", "PING from YANKEE to BRAVO (wg0)"),
        ("sudo ip netns exec yankee ping bravo -c 1 -W 1", "PING from YANKEE to BRAVO"), 
        ("sudo ip netns exec zulu ping 10.65.0.1 -c 1 -W 1", "PING from ZULU to BRAVO (wg0)"), 
        ("sudo ip netns exec zulu ping bravo -c 1 -W 1", "PING from ZULU to BRAVO"), 
        ("sudo ip netns exec whiskey ping 10.66.0.1 -c 1 -W 1", "PING from WHISKEY to CHARLIE (wg0)"), 
        ("sudo ip netns exec whiskey ping charlie -c 1 -W 1", "PING from WHISKEY to CHARLIE"), 
        ("sudo ip netns exec xray ping 10.66.0.1 -c 1 -W 1", "PING from XRAY to CHARLIE (wg0)"),
        ("sudo ip netns exec xray ping charlie -c 1 -W 1", "PING from XRAY to CHARLIE"),  
        ("sudo ip netns exec yankee ping 10.66.0.1 -c 1 -W 1", "PING from YANKEE to CHARLIE (wg0)"),
        ("sudo ip netns exec yankee ping charlie -c 1 -W 1", "PING from YANKEE to CHARLIE"), 
        ("sudo ip netns exec zulu ping 10.66.0.1 -c 1 -W 1", "PING from ZULU to CHARLIE (wg0)"), 
        ("sudo ip netns exec zulu ping charlie -c 1 -W 1", "PING from ZULU to CHARLIE"),
    ]

    # Iterate through the commands and execute them
    for command, comment in commands:
        print(f"\033[92m{comment}\033[0m")  # Print comment in green
        subprocess.run(command, shell=True, check=False)


if __name__ == "__main__":
    WG_BRAVO_KEY=""
    WG_BRAVO_PUB=""
    WG_CHARLIE_KEY=""
    WG_CHARLIE_PUB=""
    WG_BCHD_KEY=""
    WG_BCHD_PUB=""
    BRAVO_IP=""
    BCHD_IP=""
    CHARLIE_IP=""
    gen_keys()
    WG_BRAVO_PUB, WG_BRAVO_KEY, WG_CHARLIE_PUB, WG_CHARLIE_KEY, WG_BCHD_PUB, WG_BCHD_KEY, BRAVO_IP, BCHD_IP, CHARLIE_IP=execute_commands(WG_BRAVO_PUB, WG_BRAVO_KEY, WG_CHARLIE_PUB, WG_CHARLIE_KEY, WG_BCHD_PUB, WG_BCHD_KEY, BRAVO_IP, BCHD_IP, CHARLIE_IP)
    create_bravo_conf_j2(WG_BRAVO_KEY, WG_CHARLIE_PUB, WG_BCHD_PUB, BCHD_IP, CHARLIE_IP)
    create_bchd_conf_j2(WG_BCHD_KEY, WG_CHARLIE_PUB, WG_BRAVO_PUB, BRAVO_IP, CHARLIE_IP)
    create_charlie_conf_j2(WG_CHARLIE_KEY, WG_BRAVO_PUB, WG_BCHD_PUB, BRAVO_IP, BCHD_IP)
    # Call the function to configure WireGuard on bravo
    configure_wireguard_on_bravo()
    configure_wireguard_on_bchd()
    configure_wireguard_on_charlie()
    execute_ping_commands()

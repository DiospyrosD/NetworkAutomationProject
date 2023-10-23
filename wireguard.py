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
            print(private_key.stdout, "HELLLLLOOOOO")

            # Save the keys to files
            # with open(os.path.join(f"/home/student/wg/keys/{key}.key"), "w") as private_file:
            #     private_file.write(private_key.stdout)
            #     subprocess.run([f"cat /home/student/wg/keys/{key}.key | base64 -d | wg pubkey > /home/student/wg/keys/{key}.pub"], shell=True, check=True)
            #with open(os.path.join(f"/home/student/wg/keys/{key}.pub"), "w") as public_file:
                
                #public_file.write(public_key.stdout)

        set_perms = f"sudo -u student chmod 700 {keys_dir}/*"
        chown_command = f"sudo chown student:student {keys_dir}/*"
        subprocess.run(chown_command, shell=True, check=True)
        subprocess.run(set_perms, shell=True, check=True)



    except Exception as e:
        print(f"An error occurred: {e}")

def execute_commands(WG_BRAVO_PUB, WG_BRAVO_KEY, WG_CHARLIE_PUB, WG_CHARLIE_KEY, WG_BCHD_PUB, WG_BCHD_KEY): 
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
        #os.chdir("/home/student/wg")
        #script_path = "/home/student/wg/env_var.sh"
        #os.system('source /home/student/wg/env_var.sh')
        #subprocess.run([f"source {script_path}"], shell=True, executable='/bin/bash')
        # output = subprocess.check_output('cat /home/student/wg/keys/bravo.pub', shell=True, executable='/bin/bash')
        # print("HEOOOOOOOOOOOOOOOO", output)
        # Define the file paths
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
        print("SHOULD BE HERE")
        print(WG_BCHD_PUB)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.cmd}")
        print(f"Return code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        raise
    return WG_BRAVO_PUB, WG_BRAVO_KEY, WG_CHARLIE_PUB, WG_CHARLIE_KEY, WG_BCHD_PUB, WG_BCHD_KEY 

def create_bravo_conf_j2(WG_BRAVO_KEY, WG_CHARLIE_PUB, WG_BCHD_PUB):
    directory_path = "/home/student/wg/j2"
    file_path = os.path.join(directory_path, "bravo.conf.j2")

    # Create the directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)

    # Define the content for bravo.conf.j2
    config_content = f"""
[Interface]
# Name = >>> BRAVO <<<
# Address = 10.65.0.1/32ls
# SaveConfig = true
# MTU = 1500
PrivateKey = { WG_BRAVO_KEY }
ListenPort = 51820

[Peer]
# name = charlie - KVM server with a local slash 16: 10.66.0.0/26
PublicKey = { WG_CHARLIE_PUB }
AllowedIPs = 10.66.0.0/16
Endpoint = charlie:51820
PersistentKeepalive = 25

[Peer]
# Name = bchd
PublicKey = { WG_BCHD_PUB }
AllowedIPs = 10.67.0.1/32
Endpoint = bchd:51820
PersistentKeepalive = 25
"""

    # Write the content to the bravo.conf.j2 file
    with open(file_path, "w") as file:
        file.write(config_content)

def create_bchd_conf_j2(WG_BCHD_KEY, WG_CHARLIE_PUB, WG_BRAVO_PUB):
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
Endpoint = charlie:51820
PersistentKeepalive = 25

[Peer]
# Name = bravo
PublicKey = { WG_BRAVO_PUB }
AllowedIPs = 10.65.0.0/16
Endpoint = bravo:51820
PersistentKeepalive = 25
"""

    # Write the content to the bravo.conf.j2 file
    with open(file_path, "w") as file:
        file.write(config_content)

def create_charlie_conf_j2(WG_CHARLIE_KEY, WG_BRAVO_PUB, WG_BCHD_PUB):
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
Endpoint = bchd:51820
PersistentKeepalive = 25

[Peer]
# Name = bravo
PublicKey = { WG_BRAVO_PUB }
AllowedIPs = 10.65.0.0/16
Endpoint = bravo:51820
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
    subprocess.run(["ssh bravo sudo ip link add dev wg0 type wireguard"], shell=True, check=False)
    subprocess.run(["ssh bravo sudo wg setconf wg0 /etc/wireguard/wg0.conf"], shell=True, check=True)
    subprocess.run(["ssh bravo sudo ip -4 address add 10.65.0.1/32 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bravo sudo ip link set mtu 1500 up dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bravo sudo ip -4 route add 10.67.0.1/32 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bravo sudo ip -4 route add 10.66.0.0/16 dev wg0"], shell=True, check=False)

def configure_wireguard_on_bchd():
    # Create the directory for configuration files
    conf_dir = "/home/student/wg/conf"
    os.makedirs(conf_dir, exist_ok=True)
    
    subprocess.run(["sudo -u student j2 /home/student/wg/j2/bchd.conf.j2   >   /home/student/wg/conf/bchd.conf"], shell=True, check=True)

    # Copy the configuration to the remote host (bchd)
    subprocess.run(["cat /home/student/wg/conf/bchd.conf | ssh bchd sudo tee /etc/wireguard/wg0.conf"], shell=True, check=True)

    # Configure WireGuard on the remote hostguard (bchd)
    #create_wg0="ssh bchd   sudo ip link add dev wg0 type wireguard"
    subprocess.run(["ssh bchd sudo ip link add dev wg0 type wireguard"], shell=True, check=False)
    subprocess.run(["ssh bchd sudo wg setconf wg0 /etc/wireguard/wg0.conf"], shell=True, check=True)
    subprocess.run(["ssh bchd sudo ip -4 address add 10.67.0.1/32 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bchd sudo ip link set mtu 1500 up dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bchd sudo ip -4 route add 10.66.0.0/16 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh bchd sudo ip -4 route add 10.65.0.0/16 dev wg0"], shell=True, check=False)

def configure_wireguard_on_charlie():
    # Create the directory for configuration files
    conf_dir = "/home/student/wg/conf"
    os.makedirs(conf_dir, exist_ok=True)
    
    subprocess.run(["sudo -u student j2 /home/student/wg/j2/charlie.conf.j2   >   /home/student/wg/conf/charlie.conf"], shell=True, check=True)

    # Copy the configuration to the remote host (charlie)
    subprocess.run(["cat /home/student/wg/conf/charlie.conf | ssh charlie sudo tee /etc/wireguard/wg0.conf"], shell=True, check=True)

    # Configure WireGuard on the remote hostguard (charlie))
    #create_wg0="ssh bravo   sudo ip link add dev wg0 type wireguard"
    subprocess.run(["ssh charlie sudo ip link add dev wg0 type wireguard"], shell=True, check=False)
    subprocess.run(["ssh charlie sudo wg setconf wg0 /etc/wireguard/wg0.conf"], shell=True, check=True)
    subprocess.run(["ssh charlie sudo ip -4 address add 10.66.0.1/32 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh charlie sudo ip link set mtu 1500 up dev wg0"], shell=True, check=False)
    subprocess.run(["ssh charlie sudo ip -4 route add 10.65.0.0/16 dev wg0"], shell=True, check=False)
    subprocess.run(["ssh charlie sudo ip -4 route add 10.67.0.1/32 dev wg0"], shell=True, check=False)

if __name__ == "__main__":
    WG_BRAVO_KEY=""
    WG_BRAVO_PUB=""
    WG_CHARLIE_KEY=""
    WG_CHARLIE_PUB=""
    WG_BCHD_KEY=""
    WG_BCHD_PUB=""
    gen_keys()
    WG_BRAVO_PUB, WG_BRAVO_KEY, WG_CHARLIE_PUB, WG_CHARLIE_KEY, WG_BCHD_PUB, WG_BCHD_KEY=execute_commands(WG_BRAVO_PUB, WG_BRAVO_KEY, WG_CHARLIE_PUB, WG_CHARLIE_KEY, WG_BCHD_PUB, WG_BCHD_KEY)
    create_bravo_conf_j2(WG_BRAVO_KEY, WG_CHARLIE_PUB, WG_BCHD_PUB)
    create_bchd_conf_j2(WG_BCHD_KEY, WG_CHARLIE_PUB, WG_BRAVO_PUB)
    create_charlie_conf_j2(WG_CHARLIE_KEY, WG_BRAVO_PUB, WG_BCHD_PUB)
    # Call the function to configure WireGuard on bravo
    configure_wireguard_on_bravo()
    configure_wireguard_on_bchd()
    configure_wireguard_on_charlie()

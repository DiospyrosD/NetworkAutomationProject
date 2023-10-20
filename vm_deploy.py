import subprocess
import os


def main():
    mac1 = create_config()
    install_packages()
    create_config()
    launch_vm(mac1)



def install_packages():
    # Install required packages
    subprocess.run(["sudo", "apt", "install", "-y", "bridge-utils"])
    subprocess.run(["sudo", "apt", "install", "-y", "qemu-kvm"])
    subprocess.run(["sudo", "apt", "install", "-y", "cloud-utils"])
    subprocess.run(["kvm-ok"])

def create_config():
    # Load the br_netfilter module
    subprocess.run(["sudo", "sh", "-c", "echo 'br_netfilter' > /etc/modules-load.d/br_nf.conf"])
    subprocess.run(["sudo", "modprobe", "br_netfilter"])
    subprocess.run(["lsmod", "|", "grep", "netfilter"])

    # Configure sysctl settings for bridge firewall
    bridge_sysctl_settings = [
        "net.bridge.bridge-nf-call-ip6tables = 0",
        "net.bridge.bridge-nf-call-iptables = 0",
        "net.bridge.bridge-nf-call-arptables = 0"
    ]

    with open("/etc/sysctl.d/10-disable-firewall-on-bridge.conf", "w") as sysctl_file:
        sysctl_file.write("\n".join(bridge_sysctl_settings))

    # Configure IP forwarding settings
    ip_forwarding_settings = [
        "net.ipv4.ip_forward = 1",
        "net.ipv6.conf.default.forwarding = 1",
        "net.ipv6.conf.all.forwarding = 1"
    ]   

    with open("/etc/sysctl.d/10-ip-forwarding.conf", "w") as sysctl_file:
        sysctl_file.write("\n".join(ip_forwarding_settings))

    # Apply sysctl settings
    subprocess.run(["sudo", "sysctl", "-p", "/etc/sysctl.d/10-disable-firewall-on-bridge.conf"])
    subprocess.run(["sudo", "sysctl", "-p", "/etc/sysctl.d/10-ip-forwarding.conf"])
    # Verify bridge settings "sudo sysctl -a | grep 'net.bridge.bridge'"

    # Create the /etc/qemu/ directory if it doesn't exist
    subprocess.run(["sudo", "mkdir", "-p", "/etc/qemu"])

    # Create the bridge configuration file
    with open("/etc/qemu/bridge.conf", "w") as bridge_conf_file:
        bridge_conf_file.write("allow br0")

    # Create a bridge interface (br0)
    subprocess.run(["sudo", "ip", "link", "add", "name", "br0", "type", "bridge"])
    subprocess.run(["sudo", "ip", "address", "add", "172.16.0.1/24", "dev", "br0"])
    subprocess.run(["sudo", "ip", "link", "set", "br0", "up"])

    # Create the /var/kvm/images directory and change its ownership
    subprocess.run(["sudo", "mkdir", "-p", "/var/kvm/images"])
    subprocess.run(["sudo", "chown", "student:student", "/var/kvm/images"])
    os.chdir("/var/kvm/images")

    # Download and prepare the VM image
    subprocess.run(["wget", "https://static.alta3.com/projects/kvm/bionic-server-cloudimg-amd64.img"])
    subprocess.run(["qemu-img", "resize", "bionic-server-cloudimg-amd64.img", "8g"])
    subprocess.run(["qemu-img", "convert", "-O", "qcow2", "/var/kvm/images/bionic-server-cloudimg-amd64.img", "/var/kvm/images/beachhead.img"])

    # Create the /var/log/qemu/ directory
    subprocess.run(["sudo", "mkdir", "-p", "/var/log/qemu"])

    # Generate a MAC address
    mac1 = subprocess.check_output(["printf", "aa:a3:a3:%02x:%02x:%02x\n" % (os.urandom(1)[0], os.urandom(1)[0], os.urandom(1)[0])]).decode().strip()

    # Create the meta-data.yaml file
    with open("/var/kvm/images/meta-data.yaml", "w") as meta_data_file:
        meta_data_file.write("instance-id: sdn-1-test\nlocal-hostname: sdn-1-test")

    # Create the user-data.yaml file
    with open("/var/kvm/images/user-data.yaml", "w") as user_data_file:
        user_data_file.write("#cloud-config\nusers:\n  - name: root\n    lock_passwd: false\n    plain_text_passwd: 'alta3'\n    shell: /bin/bash\n  - name: ubuntu\n    lock_passwd: false\n    plain_text_passwd: 'alta3'\n    shell: /bin/bash\n    sudo: ['ALL=(ALL) NOPASSWD:ALL']\n    groups: sudo\n    ssh-authorized-keys:\n    - ssh-rsa $KEY1")

    # Create the net-config.yaml file
    with open("/var/kvm/images/net-config.yaml", "w") as net_config_file:
        net_config_file.write("version: 2\nethernets:\n    ens3:\n      dhcp4: false\n      addresses:\n      - 172.16.0.5/24\n      optional: true\n      gateway4: 172.16.0.1\n      nameservers:\n        addresses: [10.0.0.1]")

    # Create the cloud-init.iso
    subprocess.run(["cloud-localds", "/var/kvm/images/cloud-init.iso", "/var/kvm/images/user-data.yaml", "/var/kvm/images/meta-data.yaml", "--network-config=/var/kvm/images/net-config.yaml"])

    # Configure iptables for network forwarding
    subprocess.run(["sudo", "/sbin/iptables", "-t", "nat", "-A", "POSTROUTING", "-o", "ens3", "-j", "MASQUERADE"])
    subprocess.run(["sudo", "/sbin/iptables", "-A", "FORWARD", "-i", "ens3", "-o", "br0", "-m", "state", "--state", "RELATED,ESTABLISHED", "-j", "ACCEPT"])
    subprocess.run(["sudo", "/sbin/iptables", "-A", "FORWARD", "-i", "br0", "-o", "ens3", "-j", "ACCEPT"])
    
    return mac1

def launch_vm(mac1):
    # Start the VM
    subprocess.run([
        "sudo", "/usr/bin/qemu-system-x86_64",
        "-enable-kvm",
        "-drive", "file=/var/kvm/images/beachhead.img,if=virtio",
        "-cdrom", "/var/kvm/images/cloud-init.iso",
        "-display", "curses",
        "-nographic",
        "-smp", "cpus=1",
        "-m", "1G",
        "-net", "nic,netdev=tap1,macaddr=" + mac1,
        "-netdev", "bridge,id=tap1,br=br0",
        "-d", "int",
        "-D", "/var/log/qemu/qemu.log"
    ])


if __name__=="__main__":
    main()
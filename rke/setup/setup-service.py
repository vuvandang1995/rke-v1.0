import paramiko

with open("state.txt","r") as f:
    hosts = f.readlines()
type_host = "haproxy_hosts:"
username = 'root'

for host in hosts:
    if host.rstrip() == "k8s_hosts:":
        type_host = "k8s_hosts:"
    if type_host == "haproxy_hosts:" and host.rstrip() != type_host:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect( hostname = host.rstrip() , username = username, key_filename="private_key")
        stdin, stdout, stderr = ssh.exec_command("apt-get update && apt-get install -y haproxy")
        for line in stdout:
            print('... ' + line.strip('\n'))
        ssh.close()
    elif type_host == "k8s_hosts:" and host.rstrip() != type_host:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect( hostname = host.rstrip() , username = username, key_filename="private_key")
        stdin, stdout, stderr = ssh.exec_command('''curl -sSL https://get.docker.com/ | sudo sh ; echo '{"log-driver": "json-file","log-opts": {"max-size": "100m","max-file": "3"}}' > /etc/docker/daemon.json ; systemctl restart docker ; sudo useradd kubernetes -m -g docker ; sudo su - kubernetes -c "mkdir -p /home/kubernetes/.ssh"''')
        for line in stdout:
            print('... ' + line.strip('\n'))
        ssh.open_sftp().put('public_key', '/home/kubernetes/.ssh/authorized_keys')
        ssh.open_sftp().close()
        ssh.close()
        
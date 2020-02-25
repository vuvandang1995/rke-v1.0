import paramiko

target_host = [
    '172.101.0.82',
    '172.101.0.83',
    '172.101.0.84',
]
username = 'root'
for host in target_host:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect( hostname = host , username = username, key_filename="haproxy")
    ssh.exec_command("apt-get install -y haproxy")
    ssh.open_sftp().put('./haproxy.cfg', '/etc/haproxy/haproxy.cfg')
    ssh.open_sftp().close()
    ssh.exec_command("systemctl reload haproxy")
    ssh.close()

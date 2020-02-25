from fabric import SerialGroup, Connection
import os

# List of master's HAProxy
_haproxies_hosts = [
    '10.148.0.37',
]

_ssh_user = 'root'
_ssh_private_key = 'haproxy'

conns = [Connection(host, user=_ssh_user, connect_kwargs={
    "key_filename": _ssh_private_key,
}) for host in _haproxies_hosts]

group = SerialGroup.from_connections(conns)


for conn in conns:
    conn.put('./haproxy.cfg', '/etc/haproxy/haproxy.cfg')

result = group.run('systemctl reload haproxy')

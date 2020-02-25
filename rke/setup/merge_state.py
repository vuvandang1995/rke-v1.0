from os import path

if path.exists("state_old.txt"):
    with open("state.txt","r") as f:
        hosts = f.readlines()
    with open("state_old.txt","r") as f1:
        hosts_old = f1.readlines()

    with open("state.txt", "w") as file_new:
        for host in hosts:
            if host not in hosts_old or host.rstrip() == "haproxy_hosts:" or host.rstrip() == "k8s_hosts:":
                file_new.write(host)
else:
    print("state_old.txt file not exist")
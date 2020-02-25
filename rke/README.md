### Rancher kubernetes engine
* RKE
* ...

### Prerequisites
- Tối thiểu 4 server Ubuntu 18.04
  - gitlab-runner
  - haproxy
  - k8s-master
  - k8s-worker

- Tạo repository trên gitlab-server của bạn

#### B1. Cài đặt Gitlab-runner
- Cài docker: `curl -sSL https://get.docker.com/ | sudo sh`
- Cài docker-compose:
  - `sudo curl -L "https://github.com/docker/compose/releases/download/1.25.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose`
  - `sudo chmod +x /usr/local/bin/docker-compose`
- Cấp quyền cho user sử dụng docker: `sudo usermod -aG docker $USER`
- Tạo file `docker-compose.yml` với nội dung như sau:

```
version: "3.7"

services:
    gitlab-runner:
        image: dangvv1995/gitlab-runner-autor-register:0.1
        logging:
          driver: "json-file"
          options:
            max-size: "200k"
            max-file: "10"
        restart: always
        volumes:
          - '/srv/gitlab-runner-auto-register/config:/etc/gitlab-runner'
          - './register_runner/list_runners:/register_runner/list_runners'
          - '/var/run/docker.sock:/var/run/docker.sock'
    cleanup:
        image: quay.io/gitlab/gitlab-runner-docker-cleanup
        logging:
          driver: "json-file"
          options:
            max-size: "200k"
            max-file: "10"
        restart: always
        volumes:
          - /var/run/docker.sock:/var/run/docker.sock
        environment:
          LOW_FREE_SPACE: 10G
          EXPECTED_FREE_SPACE: 20G
          LOW_FREE_FILES_COUNT: 1048576
          EXPECTED_FREE_FILES_COUNT: 2097152
          DEFAULT_TTL: 10m
          USE_DF: 1
```

- Tạo thư mục chứa thông tin runner:
  - `mkdir register_runner`
  - `mkdir register_runner/list_runners`
  - `vim register_runner/list_runners/runners.yml`

  ```
  runner:
    - name: Infras
      url: https://git.devopsnd95.cf/
      token: snwuUT-y7EEqW_ff7pZz
      tag: ci-infras
      executor: docker
      dockerimage: alpine:latest
        
  ```

  - Trong đó, url, token lấy ở `setting/CI-CD/runners` của repository bạn tạo bên trên

- Cuối cùng, tạo gitlab-runner: `docker-compose up -d`

- Tạo cặp ssh key dùng để gitlab-runner có thể ssh vào các server khác và cài đặt:
  - `ssh-keygen`


#### B2: Tạo bucket trên gcs
- Tạo bucket
- Tạo service-account có quyền truy cập vào bucket trên
- Tạo key có quyền truy cập vào bucket trên

#### B3: Tạo variables 
- Vào repository trong bước chuẩn bị, chọn setting -> CI/CD -> variables
- Tạo 3 variable:
  - `GOOGLE_APPLICATION_CREDENTIALS`: là key đã tạo ở bước 2, mã hóa base64
  - `SSH_PRIVATE_KEY`: là private key đã tạo ở bước 1, mã hóa base64
  - `SSH_PUBLIC_KEY`: là public key đã tạo ở bước 1

#### B4: setup môi trường cho các server
- Copy `public key` tạo ở bước 1 sang các master, worker server ở thư mục `/root/.ssh/authorized_keys` và đảm bảo từ gitlab-runner server có thể `ssh` sang các master, worker server bằng tài khoản `root` 
- Clone repo: `git clone git@github.com:vuvandang1995/RKE-v1.0.0.git`
- sửa file `setup/setup-service.py` cho đúng các ip server của bạn
- Push code lên repo bạn đã tạo ở bước chuẩn bị

#### B5: cài đặt cluster sau khi bước 4 hoàn thành
- Truy cập: `https://console.developers.google.com`. Nếu chưa có project thì create
  - Chọn `OAuth consent screen -> create`
  - Chọn `credentials -> create credentials -> OAuth client ID -> Application type: Other`
  - **Cần lưu lại client-id và secret để làm bước tiếp theo**
- Sửa file `rke-lbs-kong/cluster.yml` cho đúng các `ip server`, `oidc-client-id` của bạn, 
- Sửa file `.gitlab-ci.yml` cho đúng tên bucket của bạn
- Push code lên và chờ kết quả

### Clean up a node

```
docker rm -f $(docker ps -qa)
docker rmi -f $(docker images -q)
docker volume rm $(docker volume ls -q)

for mount in $(mount | grep tmpfs | grep '/var/lib/kubelet' | awk '{ print $3 }') /var/lib/kubelet /var/lib/rancher; do umount $mount; done

rm -rf /etc/ceph \
       /etc/cni \
       /etc/kubernetes \
       /opt/cni \
       /opt/rke \
       /run/secrets/kubernetes.io \
       /run/calico \
       /run/flannel \
       /var/lib/calico \
       /var/lib/etcd \
       /var/lib/cni \
       /var/lib/kubelet \
       /var/lib/rancher/rke/log \
       /var/log/containers \
       /var/log/pods \
       /var/run/calico
```


### Auth

* Install this: https://github.com/micahhausler/k8s-oidc-helper

* create `rke-clusters.yaml`, replace `xxx@gmail.com` with your email

```
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUN3akNDQWFxZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFTTVJBd0RnWURWUVFERXdkcmRXSmwKTFdOaE1CNFhEVEU1TVRJeE5qQTRNREUwTjFvWERUSTVNVEl4TXpBNE1ERTBOMW93RWpFUU1BNEdBMVVFQXhNSAphM1ZpWlMxallUQ0NBU0l3RFFZSktvWklodmNOQVFFQkJRQURnZ0VQQURDQ0FRb0NnZ0VCQU0yRUFJN0gyVElECkZIclpOd3RIVGpFaGxIUkpvUDRhV2RVTUJFT2xKclAvUWpra244bUI1cEw2VVo4K1BUemtjUzdGZjdONGtIMzQKTXVEazh5cnB3MTVFUEowb3N4TDA3RTBzVnpaUDJkYnRxbUtjSDZVZWtsQzRzOTBSdk1PTmovL1RSSmVDRU02KwpRazlFb1ZUVW4xMUE0N2FUNFB3SG1ybjVlUW8zNEo0VFpVWlpUR0JHZHpNRXlHVHAyVDRlY09QenN6eVFZN3NiCnhNMEwza3czNGdHZ1ZpWWJZTWp2VFl5ZlVFTjlVelY5T0Nnc2lGLzRPUUNPWTBpZCswZFdiMUJJK2pSRXdSaTYKMjMydzlTem5SbDhmLy9RcE41L1p3Tklzei9sRk1BaisvdnVUTFdyY1kyaHM4SS9LczltRnNNV1RPaWxQa2NjWQpZVWhjK3F4WXpOOENBd0VBQWFNak1DRXdEZ1lEVlIwUEFRSC9CQVFEQWdLa01BOEdBMVVkRXdFQi93UUZNQU1CCkFmOHdEUVlKS29aSWh2Y05BUUVMQlFBRGdnRUJBQTNkSXR5aUpXbHRaQWt6aitRV20vUm9pSXEwUjJnK0tXZDcKblBWajhiUTFNcGJxOG5tNmo4M1BYY3lVZmkxbEVlaTZwR2dSRXoyZ0xEL3c5Rnl4aml0TWpYNE12bVNUbjhTeQpmaWxicGowM1NWZmROTHA3T3hiQkZPOTFDUitsQzdvaUp2TlB1ZjZzbWp4R083Y0t1ZXQ0bXRyWkVGeDRWY0pHClJsSG5kRDNKd3gyQW9BcXQzeTI2VTNXQUVkSXc0ekVrM3JGYzJSK3hvRDBLOGRuYmc1TkdOVDBDQ2QxRU4yNEkKY0drQS9kODllUFk1WEVnVUhNK1VnSHpxUENTUGFqVGJZZjE4Mkp0Y1FLU25YejRTaHFRRHVZMFphZ0NkbWNTSwo3K3h6VHI3VDRVM2JkUEM2aEdZYnNOaCtvNmlGR1BWRDhveml3bXRrWkxwL1ZtVVdyZHM9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
    server: https://k8s.devopsapis.cf:4430
  name: rke-app
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUN3akNDQWFxZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFTTVJBd0RnWURWUVFERXdkcmRXSmwKTFdOaE1CNFhEVEU1TVRJeE5qRTFNVFF4TWxvWERUSTVNVEl4TXpFMU1UUXhNbG93RWpFUU1BNEdBMVVFQXhNSAphM1ZpWlMxallUQ0NBU0l3RFFZSktvWklodmNOQVFFQkJRQURnZ0VQQURDQ0FRb0NnZ0VCQU9KNmdUZy9VbnJICkkrbEhwNHB1RVhlQVkwR0s5WDBHZitPOXZFNTE5QXBxS21mRUV3TmZkTldRK3M1blZFaDJ3N0xiUmR4V29XeVQKSHhOazFLamRMaHFmeElkZ2F3bGtUS1ArRzE3WWVIY0k0eFlvQ1ZZS0R5aHZqNzdZT0Y1ZEErNEZVYTRtbVo3cQpVNXgxc0dUT2FINU9KR2ZlMHJ5aktMU1VoNXpvNDQ0SWtvTDFQdGJVUlBlYnlPNUVoK1lwWXJIY2gya0Z2c1BiCkFLR1l3aXAzMFB3ZlljNW9XWEltNnJWVGpKSzRHb2VKOFNCdktUSlg3OW9oVmdabVN4SXJFNXMza0MvQVZPQ1AKdzNkYkNzSnA1ZGpIdmhvbTgyZVpzOXptdC9MeHc5a2FscVAxK0svUXV1enZjZStiZ2JveXplbGtBNVZBSXpqMApEQ21DUXNWMm1xa0NBd0VBQWFNak1DRXdEZ1lEVlIwUEFRSC9CQVFEQWdLa01BOEdBMVVkRXdFQi93UUZNQU1CCkFmOHdEUVlKS29aSWh2Y05BUUVMQlFBRGdnRUJBTjNZcXhLWjVwTldVQlFrbXNkcWVCWXU2QmpwdUhCWDRSdGYKYTFJT3N4K1NncjZHZ2xvMUZlTVJKZms1T0VhcWdqUVY3dEYzeWg4WnJEdm9oV2h2OGUvY3g3bFhCVW5DQm5hdwpFN2pnVFE2OEVXYlY2OHl5b01YSUFOMDRlV0d3by9LZVhiYnMxZFRibWhiWUlNZU9qcXBZSWlFR2RaY0lNQ01ECjVtOTVBNWVUN0Jyc2ZiYWtLRCtvWHkwOXZ2WFNQS0V0S0hnT1lKWkVvWWpqell4ODBYMk53Y1VGTEVoUExta1cKR2M5ZUdjam12Sy80OEZ1T3MyalYrTUpnV2lvZWlCKzhOM3ZJc1JDbUwvQ3dvbk5qTkhZNXloVEU5ZytNeFY3RApONVRkcEdCV2p2c09Kb0k4V0pJSEhYdHlWaU9FTXoyMGlveVdGenUrc2JoK1NzVWtmVnc9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
    server: https://k8s.devopsapis.cf:4431
  name: rke-db
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUN3akNDQWFxZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFTTVJBd0RnWURWUVFERXdkcmRXSmwKTFdOaE1CNFhEVEU1TVRJeE9ERTFNRFEwTWxvWERUSTVNVEl4TlRFMU1EUTBNbG93RWpFUU1BNEdBMVVFQXhNSAphM1ZpWlMxallUQ0NBU0l3RFFZSktvWklodmNOQVFFQkJRQURnZ0VQQURDQ0FRb0NnZ0VCQU1Ha1A5NHIyN2hKCi9pNGFQcVFHZGFCdEg5bHhOVDBEd1VFVmFnNm5GdnR5d2FkVjFaMXhhaFdyRThMcE05RUNsUHlOS3B5MUdJUlAKanVTdXZWVC84OGNQc3BpQUhsL2VKVEFDM1VhSG9kc3J2cGxzYmFtRTNrVlIxRHloeEwrZkRrZTRxR1lQRFhsUAp4Y05IQ3o4VDdtTGFuOFp6Ly9uUU1DVFRSZ2gwUFN4OG5TeENCR3piREp5YWxZSXB5cTJhY05sdDdNdDFmQ3pvCndsWTkzaTJRbnkyWDdtQnFWMnIyTFJCc0lhMURlOElQV1h3Q3FmUENXK2xMQUFPRDErYkN0Rkc2a0dvaXhRTFoKVGtRc0RwSS83YStpN1RLcDVIeDM3YnRGMzM4cXpUVjVUOUdkeGtOUkYvYzN5UHVvelJUNmsranlhOWgwUS9KcApSWDlKZi90a3VhOENBd0VBQWFNak1DRXdEZ1lEVlIwUEFRSC9CQVFEQWdLa01BOEdBMVVkRXdFQi93UUZNQU1CCkFmOHdEUVlKS29aSWh2Y05BUUVMQlFBRGdnRUJBRE1xQ3JjTDlqanlseW40SERXZTd6cWRTMmxXaFNLODRSTnQKVWFEUWc5cHE4T0xiL2d3aUptbzlHQXc5UzZyT1VQTW1NMkNLbDYvSkNpRU5sa3V3Y3d2QzZJWXp1QlBMUnp4QwpnSHdGS0hVQ3NSbWQzREhEcTBkUlorREpvbTRhbFlXSWNBMDhoZUtacG1lWVdvcXM0L21mUldLaG5QL1ZWQ3NzClNwZlRHb1Z5QXpoZld4VE5wcXM0eGJsOE8rQmFkeFFReURsR04wMGhMejlJZ1pxOXRQMFVvcHNTRkNSQnlmVUcKWGlKcUVFTEY2TFMvbHRSRkNVZ0xGL0Q0eWw5ODQrU3VuVFNuQ1ludlNvcFpidk5yQUZJcU53M3RadzI4NytQdQp4VEl3azdVVXcrcWorV05FaXhObzRTK2k4ZGJoVkZXaWxka1crSk5YVFhvaVRmdEY3Y289Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
    server: https://k8s.devopsapis.cf:4432
  name: rke-lbs-kong
contexts:
- context:
    cluster: rke-app
    user: xxx@gmail.com
  name: rke-app
- context:
    cluster: rke-db
    user: xxx@gmail.com
  name: rke-db
- context:
    cluster: rke-lbs-kong
    user: xxx@gmail.com
  name: rke-lbs-kong
current-context: rke-app
kind: Config
preferences: {}
users: []
```

* Auth to cluster
```
k8s-oidc-helper --client-id '559391004128-m1omv2tivi7jp8j4e8kkolo9e2jrqh4i.apps.googleusercontent.com' --client-secret 'VflCyaDR9apaQkOha6sIYzYb' --file rke-clusters.yaml --write
```
* then export `KUBECONFIG` to `rke-clusters.yaml`

```
export KUBECONFIG=$(pwd)/rke-clusters.yaml
kubectl config set-context --current --user=<your-email-at-gmail.com>
```

* Enjoy


<!-- TABLE OF CONTENTS -->

# 📗 Table of Contents

- [📖 About the Project](#about-project)
  - [🛠 Built With](#built-with)
    - [Tech Stack](#tech-stack)
    - [Key Features](#key-features)
  - [🚀 Live Demo](#live-demo)
- [💻 Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Install](#install)
  - [Usage](#usage)
  - [Deployment](#triangular_flag_on_post-deployment)

<!-- PROJECT DESCRIPTION -->

# 📖 K-Security Server <a name="about-project"></a>

> Describe project in 1 or 2 sentences.

</br>

## 🛠 Built With <a name="built-with"></a>

### Tech Stack <a name="tech-stack"></a>

> Describe the tech stack and include only the relevant sections that apply to your project.

<!-- Features -->

### Key Features <a name="key-features"></a>

> Describe between 1-3 key features of the application.

<!-- LIVE DEMO -->

## 🚀 Live Demo <a name="live-demo"></a>

> Add a link to deployed project.

</br>

<!-- GETTING STARTED -->

## 💻 Getting Started <a name="getting-started"></a>

> Describe how a new developer could make use of project.

To get a local copy up and running, follow these steps.

### 1. Prerequisites

In order to run this project you need:

- Python 3.9

- JRE - Java Runtime Environtment

### 2. Setup

- Clone this repository to your desired folder.

- Install Virtual Environment

  > A virtual environment is a Python tool for dependency management and project isolation. This means that each project can have any package installed locally in an isolated directory instead of being installed globally.

  Install Python virtual environment package.

  ```sh
  $ sudo apt update

  $ sudo apt install python3-venv
  ```

- Install JRE

  ```sh
  $ sudo apt update

  $ sudo apt install default-jre
  ```

### 3. Install

- To install, execute the following command. This command will entering the virtual environment and install dependencies.

  ```sh
  $ sh scripts/install.sh
  ```

### 4. Usage

To run the project, execute the following command:

```sh
$ sh scripts/run.sh
```

### 5. Deployment

You can deploy this project by following these steps:

- Install the docker package.

  - First, update your existing list of packages:

    ```sh
    $ sudo apt update
    ```

  - Next, install a few prerequisite packages which let _`apt`_ use packages over HTTPS:

    ```sh
    $ sudo apt install apt-transport-https ca-certificates curl software-properties-common
    ```

  - Then add the GPG key for the official Docker repository to your system:

    ```sh
    $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    ```

  - Add the Docker repository to APT sources:

    ```sh
     $ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
    ```

  - Next, update the package database with the Docker packages from the newly added repo:

    ```sh
    $ sudo apt update
    ```

    Make sure you are about to install from the Docker repo instead of the default Ubuntu repo:

    ```sh
    $ apt-cache policy docker-ce
    ```

    You’ll see output like this, although the version number for Docker may be different:

    ```
    docker-ce:
    Installed: (none)
    Candidate: 18.03.1~ce~3-0~ubuntu
    Version table:
      18.03.1~ce~3-0~ubuntu 500
          500 https://download.docker.com/linux/ubuntu bionic/stable amd64 Packages
    ```

    Notice that docker-ce is not installed, but the candidate for installation is from the Docker repository for Ubuntu 18.04 (bionic).

  - Finally, install Docker:

    ```sh
    $ sudo apt install docker-ce
    ```

    Docker should now be installed, the daemon started, and the process enabled to start on boot. Check that it’s running:

    ```sh
    $ sudo systemctl status docker
    ```

    The output should be similar to the following, showing that the service is active and running:

    ```
    Output
    ● docker.service - Docker Application Container Engine
      Loaded: loaded (/lib/systemd/system/docker.service; enabled; vendor preset: enabled)
      Active: active (running) since Mon 2021-08-09 19:42:32 UTC; 33s ago
        Docs: https://docs.docker.com
    Main PID: 5231 (dockerd)
        Tasks: 7
      CGroup: /system.slice/docker.service
              └─5231 /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock
    ```

  Installing Docker now gives you not just the Docker service (daemon) but also the docker command line utility, or the Docker client.

- Build and start the Docker container

  - Build docker image

    ```sh
      $ docker build -t ksecurity/server:lastest .

      $ docker compose run -d
    ```

  - Start docker container

    ```sh
      $ docker compose run -d

      $ docker compose ps
    ```

    Expected output:

    ```
    CONTAINER ID   IMAGE                  COMMAND              CREATED       STATUS                    PORTS                                   NAMES
    1479f40b3517   kma/ksecurity-server   "gunicorn src.ma…"   11 days ago   Up 50 minutes (healthy)   0.0.0.0:8000->80/tcp, :::8000->80/tcp   ksecurity-server

    ```

    Also, you can check the response using the following command.

    ```sh
    $ curl http://localhost:8000
    ```

- Setup Nginx as Reverse Proxy

  - Install Nginx

    ```sh
    $ sudo apt install nginx
    ```

  - Add vhost configuration

    Add vhost file to _`sites-available`_ directory.

    ```sh
    $ sudo nano /etc/nginx/sites-available/api.k-security.com.conf
    ```

    Paste the following content (replace _server_domain_ with your actual domain) and save the file

    ```
    server {
      listen 80;
      server_name server_domain;

      location / {
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_pass http://localhost:8000;
        proxy_redirect off;
        client_max_body_size 100M;
      }

      proxy_read_timeout 30;
      proxy_connect_timeout 30;
      proxy_send_timeout 30;
    }
    ```

  - Activate vhost configuration

    Add a soft link of the vhost file in the _`sites-enabled`_ directory.

    ```sh
    $ sudo ln -s /etc/nginx/sites-available/api.k-security.com.conf /etc/nginx/sites-enabled/
    ```

  - Test and reload the configuration

    Test the configuration.

    ```sh
    $ sudo nginx -t
    ```

    Expected output:

    ```
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok

    nginx: configuration file /etc/nginx/nginx.conf test is successful
    ```

    Reload Nginx.

    ```sh
    $ sudo systemctl reload nginx
    ```

- Secure Nginx with an SSL Certificate

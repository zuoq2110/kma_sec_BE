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

- Install the gunicorn Python package.

  ```sh
  $ pip install --no-cache-dir --upgrade gunicorn==20.1.0
  ```

- Create Systemd Service

  - Create and edit systemd unit file.

    ```sh
    $ sudo nano /etc/systemd/system/api.k-security.service
    ```

  - Paste the following code and save the file.

    ```
    [Unit]
    Description=Gunicorn Daemon for K-Security Application
    After=network.target

    [Service]
    User={user}
    Group=www-data
    WorkingDirectory={directory_to_project}
    EnvironmentFile={directory_to_project}/.env
    ExecStart=python3 -m gunicorn src.main:app

    [Install]
    WantedBy=multi-user.target
    ```

  - Start & enable the service.

    ```sh
    $ sudo systemctl start api.k-security.service

    $ sudo systemctl enable api.k-security.service
    ```

    To verify if everything works run the following command.

    ```sh
    $ sudo systemctl status api.k-security.service
    ```

    Expected output:

    ```
    ● api.k-security.service - Gunicorn Daemon for K-Security Application
     Loaded: loaded (/etc/systemd/system/api.k-security.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2023-03-25 03:53:47 UTC; 7min ago
    Main PID: 13314 (python3)
      Tasks: 41 (limit: 4573)
     Memory: 251.7M
     CGroup: /system.slice/api.k-security.service
             ├─13314 /usr/bin/python3 -m gunicorn src.main:app
             ├─13326 /usr/bin/python3 -m gunicorn src.main:app
             ├─13327 /usr/bin/python3 -m gunicorn src.main:app
             ├─13328 /usr/bin/python3 -m gunicorn src.main:app
             ├─13329 /usr/bin/python3 -m gunicorn src.main:app
             └─13330 /usr/bin/python3 -m gunicorn src.main:app

    Mar 25 03:53:47 k-security systemd[1]: Started Gunicorn Daemon for K-Security Application.
    ```

    Also, you can check the response using the following command.

    ```sh
    $ curl http://0.0.0.0:8000
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

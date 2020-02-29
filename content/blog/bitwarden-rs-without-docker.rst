Using Bitwarden-rs without docker
==================================

:date: 2020-02-04
:category: Blog
:slug: bitwarden-rs-without-docker
:tags: linux
:summary:
    Docker is a bit overkill for such a small program, just run it like we did before
    everything was a container.

I use a self-hosted `bitwarden-rs`_ to manage my passwords, and it works great
except using docker to run it was using most of the RAM on my cheap VPS from
Vultr_. Since bitwarden-rs is just a rust program that uses around 16MB of RAM,
it seemed overkill to have docker running around it using over 100MB.

I cloned the repository, checked out the latest tag and then ran

.. code-block:: bash

    cargo build --release --features sqlite

You can use postgresql or mysql if you want but sqlite suites my needs as a single user just fine.

You then need the web UI. Since this is nodejs it takes a lot of RAM to build
so I would recommend just getting the latest release from their `web vault
releases`_. The version I got was 2.12.0. Extract it to a folder `web-fault`.

.. code-block:: bash

    wget https://github.com/dani-garcia/bw_web_builds/releases/download/v2.12.0/bw_web_v2.12.0.tar.gz
    mkdir web-vault
    tar -xf bw_web_v2.12.0.tar.gz -C web-vault

I then setup what will be the app directory; I used `/opt/bitwarden` but you can use whatever you like.

.. code-block:: bash

    mkdir /opt/bitwarden
    cp bitwarden_rs/target/release/bitwarden_rs /opt/bitwarden/bitwarden_rs
    cp -a web-vault/ /opt/bitwarden/web-vault/

You will need to run the bitwarden_rs application, but systemd makes this very
easy. I setup `/etc/systemd/system/bitwarden.service`

.. code-block:: systemd

    [Unit]
    Description=Bitwarden
    After=nginx.service

    [Service]
    Type=simple
    Restart=always
    WorkingDirectory=/opt/bitwarden
    ExecStart=/opt/bitwarden/bitwarden_rs

    [Install]
    WantedBy=local.target

and then enabled and ran it with `systemctl enable --now bitwarden.service`

Then you just need to have a web server to run it, preferably with some SSL
support. This is how my nginx configuration looks for it.

.. code-block:: nginx

    server {
            listen 80;
            listen [::]:80;

            server_name bitwarden.dns.name;

            include letsencrypt/letsencrypt.conf;

            location / {
                    return 301 https://$host$request_uri;
            }

    }

    server {
            listen 443 ssl;
            listen [::]:443 ssl;

            ssl_certificate /etc/letsencrypt/live/bitwarden.dns.name/fullchain.pem;
            ssl_certificate_key /etc/letsencrypt/live/bitwarden.dns.name/privkey.pem;
            include ssl/ssl.conf;

            server_name bitwarden.dns.name;

            location / {
                    proxy_read_timeout 90;
                    proxy_set_header X-Forwarded-For $remote_addr;
                    proxy_set_header Host $http_host;
                    proxy_pass http://localhost:8000/;
            }
    }

.. class:: comment

    I made some extra conf files that all my domains source for nginx to easily
    manage Let's Encrypt and SSL settings, see `my blog post`_ about it.

And now it should be done. Without a lot of effort you have saved yourself the
hassle of running a docker container and are saving some precious memory.

.. _`bitwarden-rs`: https://github.com/dani-garcia/bitwarden_rs
.. _Vultr: https://www.vultr.com/?ref=7515314
.. _`web vault releases`: https://github.com/dani-garcia/bw_web_builds/releases
.. _`my blog post`: /blog/nginx-conf-file-management/
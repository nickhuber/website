Nginx conf file management
===========================

:date: 2020-02-09
:category: Blog
:slug: nginx-conf-file-management
:tags: nginx
:summary: How I manage multiple virtual host configurations on nginx

I like to host many different domains on a single server, all behind nginx. I
didn't want to have too much duplicated configuration logic between the various
configurations so this is what I ended up settling on. This allows any host to
easily support SSL through Lets Encrypt with the webroot method, while keeping
the configuration simple for what each virtual host actually cares about.

This is an example entry that could be what serves a website, under `/etc/nginx/conf.d/foo.conf`

.. code-block:: nginx

    server {
            listen 80;
            listen [::]:80;

            server_name foo.nickhuber.ca;

            include letsencrypt/letsencrypt.conf;

            location / {
                    return 301 https://$host$request_uri;
            }

    }

    server {
            listen 443 ssl;
            listen [::]:443 ssl;

            ssl_certificate /etc/letsencrypt/live/foo.nickhuber.ca/fullchain.pem;
            ssl_certificate_key /etc/letsencrypt/live/foo.nickhuber.ca/privkey.pem;
            include ssl/ssl.conf;

            server_name foo.nickhuber.ca;

            location / {
                    root /var/www/foo/;
            }
    }

This is my `/etc/nginx/letsencrypt/letsencrypt.conf`

.. code-block:: nginx

    location ^~ /.well-known {
        allow all;
        auth_basic off;
        root /var/letsencrypt/;
    }

This is my `/etc/nginx/ssl/ssl.conf`

.. code-block:: nginx

    ssl_session_timeout 5m;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers "ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS";
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_dhparam /etc/nginx/ssl/dhparam.pem;

I also slightly modified the log format of nginx to include the server name so
it is easier to see where each match request is coming from. This is as easy as
just adding the `$host` string into the `log_format`. From
`/etc/nginx/nginx.conf` I changed the `log_format` line to be like this under
the `http` section as follows.

.. code-block:: nginx

    [snip]
    http {
        log_format main '$host $remote_addr - $remote_user [$time_local] "$request" '
                        '$status $body_bytes_sent "$http_referer" '
                        '"$http_user_agent" "$http_x_forwarded_for"';
    [snip]

Using docker compose under systemd
===================================

:date: 2023-12-11
:category: Blog
:slug: traefik-docker-systemd-v2
:tags: linux
:summary:
    After using docker under systemd for a while, I think I'm happy enough with
    this setup to talk about it

This is a revision of `my 2021 post </blog/traefik-docker-systemd>`_ about the
same thing. The main change is how I define and use the docker containers with a
templated systemd service and docker-compose.yml files instead of calling docker
directly with many arguments.

Running docker-compose through systemd
---------------------------------------

I wrote a simple systemd template service that calls into docker compose. Placed
in `/etc/systemd/system/docker-service@.service`, the file looks like this

.. code:: systemd

    [Unit]
    Description=%i Docker service
    After=docker.service docker-traefik-network.service
    Requires=docker.service docker-traefik-network.service
    AssertPathExists=/usr/local/etc/containers/%i/docker-compose.yml

    [Service]
    TimeoutStartSec=0
    Restart=always
    WorkingDirectory=/usr/local/etc/containers/%i
    ExecStart=/usr/bin/docker-compose --file /usr/local/etc/containers/%i/docker-compose.yml --project-name traefik up --force-recreate
    ExecStop=/usr/bin/docker-compose --file /usr/local/etc/containers/%i/docker-compose.yml --project-name traefik down

    [Install]
    WantedBy=multi-user.target

`docker-traefik-network` is another service, which ensures that the externally managed traefik network exists for any of the services that want to use it. The service file looks like this

.. code:: systemd

    [Unit]
    Description=Create treafik network
    After=docker.service
    Requires=docker.service

    [Service]
    Type=oneshot
    ExecStart=/bin/bash -c "/usr/bin/docker network create traefik ||:"
    ExecStop=/usr/bin/docker network rm traefik
    RemainAfterExit=yes

    [Install]
    WantedBy=multi-user.target

This ends up being pretty easy to use, just make a
`/usr/local/etc/containers/{service}` folder for each service you wish to run,
with a `docker-compose.yml` file and any other files you might need to mount in
as configuration adjacent to it.

Here is an example of how I configured pihole in this way, in `/usr/local/etc/containers/pihole/docker-compose.yml`:

.. code-block:: yaml

    ---
    version: "3.8"

    networks:
        traefik:
            external: true
            name: traefik

    services:
        pihole:
            image: pihole/pihole
            networks:
            - traefik
            security_opt:
            - seccomp=unconfined
            - apparmor=unconfined
            environment:
            - "TZ=America/Vancouver"
            - "PIHOLE_DNS_=208.67.222.222;208.67.220.220"
            - "WEBPASSWORD=admin"
            labels:
            traefik.enable: true
            traefik.http.routers.pihole-http.rule: Host(`pihole.home.arpa`)
            traefik.http.routers.pihole-http.entrypoints: web
            traefik.http.routers.pihole-http.service: pihole-http-service
            traefik.http.services.pihole-http-service.loadbalancer.server.port: 80
            traefik.http.middlewares.pihole.addprefix.prefix: /admin
            ports:
            - 53:53/udp
            - 53:53/tcp
            volumes:
            - /ssd-storage/pihole/etc/pihole:/etc/pihole
            - /ssd-storage/pihole/etc/dnsmasq.d:/etc/dnsmasq.d
            restart: unless-stopped

as well as traefik, which is the glue holds my entire setup together, found in `/usr/local/etc/containers/traefik.yml`

.. code-block:: yaml

    ---
    version: "3.8"

    networks:
        traefik:
            external: true
            name: traefik

    services:
        traefik:
            image: traefik:v2.9
            container_name: traefik
            networks:
            - traefik
            environment:
            - PUID=1000
            - PGID=1000
            - TZ=America/Vancouver
            command:
            - "--providers.docker=true"
            - "--providers.docker.exposedbydefault=false"
            - "--entrypoints.web.address=:80"
            - "--api.dashboard=true"
            - "--api.insecure=true"
            labels:
            traefik.enable: true
            traefik.http.routers.api.rule: Host(`traefik.home.arpa`)
            traefik.http.routers.api.entrypoints: web
            traefik.http.routers.api.service: api@internal
            ports:
            - 80:80
            volumes:
            - /storage/traefik/letsencrypt:/letsencrypt
            - /var/run/docker.sock:/var/run/docker.sock:ro
            restart: unless-stopped

I have yet to worry about setting up SSL internally for this but it is next on
my list of things to figure out.

Although not shown above; a nice benefit of this is that using a separate
`docker-compose.yml` for each service allows you to run additional services
needed for certain applications and keep them bound inside an internal network
of each docker-compose environment. I will end this section with an example of
my nextcloud configuration which has a few associated services and was a major
reason for deciding to restructure how I managed the various services I run.

.. code-block:: yaml

    ---
    version: "3.8"

    networks:
        external:
        internal:
            internal: true
        traefik:
            external: true
            name: traefik

    services:
        app:
            depends_on:
            - postgres
            - redis
            environment:
            - POSTGRES_DB=nextcloud
            - POSTGRES_USER=nextcloud
            - POSTGRES_PASSWORD=not-my-password
            - POSTGRES_HOST=postgres
            - REDIS_HOST=redis
            expose:
            - 9000
            hostname: nextcloud.home.arpa
            image: nextcloud:stable-fpm-alpine
            networks:
            - internal
            - external
            restart: unless-stopped
            volumes:
            - /storage/nextcloud/webapp-data:/var/www/html

        cron:
            depends_on:
            - postgres
            entrypoint: /cron.sh
            image: nextcloud:stable-fpm-alpine
            restart: unless-stopped
            volumes:
            - /storage/nextcloud/webapp-data:/var/www/html

        postgres:
            environment:
            - POSTGRES_USER=nextcloud
            - POSTGRES_PASSWORD=not-my-password
            - POSTGRES_DB=nextcloud
            - PGDATA=/var/lib/postgresql/data
            expose:
            - 5432
            image: postgres:15-alpine
            networks:
            - internal
            restart: unless-stopped
            volumes:
            - /storage/nextcloud/pg-data:/var/lib/postgresql/data

        redis:
            expose:
            - 6379
            image: redis:alpine
            networks:
            - internal
            restart: unless-stopped

        web:
            depends_on:
            - app
            image: nginx:alpine
            labels:
            traefik.enable: true
            traefik.docker.network: traefik
            traefik.http.routers.nextcloud-http.entrypoints: web
            traefik.http.routers.nextcloud-http.rule: Host(`nextcloud.home.arpa`)
            traefik.http.routers.nextcloud-http.service: nextcloud-http-service
            traefik.http.services.nextcloud-http-service.loadbalancer.server.port: 80
            networks:
            - traefik
            - internal
            restart: unless-stopped
            volumes:
            - /usr/local/etc/containers/nextcloud/nginx.conf:/etc/nginx/nginx.conf:ro
            - /storage/nextcloud/webapp-data:/var/www/html:ro

Closing remarks
----------------

I am starting to strongly consider if it would have been easier to just run this
through Docker Swarm or Hashicorp Nomad or some other orchestrator but that
seems overkill for a single-server solution to running some containers. This
setup still seems simple enough and I've been quite happy with how reliable it
has been.

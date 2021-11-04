Proxying Docker containers through Traefik, using systemd
==========================================================

:date: 2021-11-03
:category: Blog
:slug: traefik-docker-systemd
:tags: linux
:summary:
    I have no idea if this is a good idea, I don't even know if I like it yet
    but I did get it working and it seems sort of OK.

I've been using Docker more for things lately, along with Traefik for acting as
the reverse proxy. There are lots of guides to getting things going with
docker-compose, but I was curious what it would take to keep each Docker
container managed by systemd while still utilizing the Docker integrations that
Traefik offers.

Non-related networking setup
-----------------------------

I have all of this running on newly built home server which is also acting as my
NAS. I have my router configured to resolve multiple hostnames to the IP of this
server so it can resolve things like `nas.home.arpa` and `plex.home.arpa` and
maybe more as I decide to add more services.

.. class:: comment

    .home.arpa is
    `apparently what you are supposed to use <https://www.rfc-editor.org/rfc/rfc8375>`_
    for "non-unique use in residential home networks". I wonder how many people
    actually use this instead of hijacking some other TLD.

Running Docker containers with systemd
---------------------------------------

I decided the simplest way to do this would be with a systemd service definition
for each docker container, the 2 that I will use to demonstrate here are Traefik
itself, and a Plex media server.

My configuration for Traefik, which I think is pretty standard. I'm not worrying
about anything TLS right now though. I have port 8000 for the Traefik dashboard
to see the state of things and port 80 is used for the actually proxy. ::

    [Unit]
    Description=Traefik for Docker containers
    After=docker.service
    Requires=docker.service

    [Service]
    TimeoutStartSec=0
    Restart=always
    ExecStart=/usr/bin/docker run \
            --rm \
            --name traefik \
            --publish 80:80 \
            --publish 8000:8080 \
            --volume traefik-letsencrypt:/letsencrypt \
            --volume /var/run/docker.sock:/var/run/docker.sock:ro \
            traefik:v2.5 \
            traefik \
            "--providers.docker=true" \
            "--providers.docker.exposedbydefault=false" \
            "--entrypoints.web.address=:80" \
            "--api.dashboard=true" \
            "--api.insecure=true"

    [Install]
    WantedBy=multi-user.target

My configuration for a Plex media server. Most of this is pretty Plex-specific,
but the labels at the end is what lets Traefik discover the service, with a port
32400 designated to be the proxy target with the
`.loadbalancer.server.port=32400` section. ::

    [Unit]
    Description=Plex Media Server
    After=docker.service
    Requires=docker.service

    [Service]
    TimeoutStartSec=0
    Restart=always
    ExecStart=/usr/bin/docker run \
            --rm \
            --name plex \
            -e TZ="America/Vancouver" \
            -e PLEX_CLAIM="claim-XXXXXXXXXX" \
            -e ADVERTISE_IP="plex.home.arpa" \
            --publish 32400:32400/tcp \
            --publish 1900:1900/udp \
            --publish 3005:3005/tcp \
            --publish 5353:5353/udp \
            --publish 8324:8324/tcp \
            --publish 32410:32410/udp \
            --publish 32412:32412/udp \
            --publish 32413:32413/udp \
            --publish 32414:32414/udp \
            --publish 32469:32469/tcp \
            --hostname plex.home.arpa \
            ---volume /storage/plex/config:/config \
            ---volume /storage/plex/transcode:/transcode \
            ---volume /storage/plex/data:/data \
            --label "traefik.enable=true" \
            --label "traefik.http.routers.plex-http.rule=Host(`plex.home.arpa`)" \
            --label "traefik.http.routers.plex-http.entrypoints=web" \
            --label "traefik.http.routers.plex-http.service=plex-http-service" \
            --label "traefik.http.services.plex-http-service.loadbalancer.server.port=32400" \
            plexinc/pms-docker

    [Install]
    WantedBy=multi-user.target

Closing remarks
----------------

Only time will tell if I want to stick with this setup, but it seems to be
working well enough for my simple home use case. The systemd configuration kind
of sucks with so many arguments being passed on the command line to docker so
maybe that will annoy me enough to seek out a different solution.

Maybe it would have been easier to just run this through Docker Swarm or some
other orchestrator but that seems overkill for a single-server solution to
running some containers.

#!/bin/bash
set -e

# Détecte le GID réel de /var/run/docker.sock au runtime
# et ajuste le groupe docker pour que jenkins puisse y accéder
if [ -S /var/run/docker.sock ]; then
    SOCKET_GID=$(stat -c '%g' /var/run/docker.sock)
    DOCKER_GID=$(getent group docker | cut -d: -f3 || echo "")

    if [ "$SOCKET_GID" != "$DOCKER_GID" ]; then
        groupmod -g "$SOCKET_GID" docker 2>/dev/null || \
            groupadd -g "$SOCKET_GID" dockerhost
        usermod -aG docker jenkins 2>/dev/null || true
    fi
fi

exec su -s /bin/bash jenkins -c "exec /usr/local/bin/jenkins.sh"

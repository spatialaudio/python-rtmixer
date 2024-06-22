#!/bin/bash

set -xeo pipefail

if [[ "$(cat /etc/redhat-release)" == 'AlmaLinux'* ]]; then
    dnf config-manager --set-enabled powertools
    dnf install -y epel-release
fi
yum install -y portaudio

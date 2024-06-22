#!/bin/bash

set -xeo pipefail

dnf config-manager --set-enabled powertools || 1
dnf install epel-release || 1
yum install -y portaudio

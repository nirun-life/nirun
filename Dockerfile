FROM nirun/odoo:latest

LABEL org.opencontainers.image.title="nirun" \
      org.opencontainers.image.description="A health management system for healthcare providers" \
      org.opencontainers.image.source="https://github.com/nirun-life/nirun" \
      org.opencontainers.image.vendor="Nirun Project, NSTDA"

USER root

# Move nirun module into extra-addonse and install requirment
COPY . /mnt/extra-addons
RUN pip install -r /mnt/extra-addons/requirements.txt

HEALTHCHECK --start-period=120s --start-interval=15s\
  CMD curl --fail http://localhost:8069/web/health || exit 1

USER odoo

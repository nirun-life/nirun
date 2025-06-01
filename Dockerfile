FROM nirun/odoo:latest

USER root

# Move nirun module into extra-addonse and install requirment
COPY . /mnt/extra-addons
RUN pip install -r /mnt/extra-addons/requirements.txt

HEALTHCHECK --start-period=120s --start-interval=15s\
  CMD curl --fail http://localhost:8069/web/health || exit 1

USER odoo

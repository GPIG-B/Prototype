FROM python:3

# IMPORTANT: This Dockerfile expects to be run from the root of the repository
# and _not_ from within ./sensor_services/!

ADD ./manager/ /manager/
RUN pip install --upgrade pip && \
    pip install -r /manager/requirements.txt
WORKDIR /workdir/
ADD ./sensor_service/requirements.txt ./
RUN pip install -r requirements.txt
ADD ./sensor_service/ ./
RUN chmod +x ./cli.py ./entrypoint.sh
ADD ./configs/ /configs/
ENTRYPOINT ./entrypoint.sh

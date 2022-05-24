FROM python:3

# IMPORTANT: This Dockerfile expects to be run from the root of the repository
# and _not_ from within ./drone_scheduling/!

ADD ./manager/ /manager/
RUN pip install --upgrade pip && \
    pip install -r /manager/requirements.txt
WORKDIR /workdir/
ADD ./drone_scheduling/requirements.txt ./
RUN pip install -r requirements.txt
ADD ./drone_scheduling/ ./
RUN chmod +x ./cli2.py ./cli.py ./entrypoint.sh
ADD ./configs/ /configs/
ENTRYPOINT ./entrypoint.sh

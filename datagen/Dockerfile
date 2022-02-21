FROM python:3

# IMPORTANT: This Dockerfile expects to be run from the root of the repository
# and _not_ from within ./api/!

ADD ./manager/ /manager/
RUN pip install --upgrade pip && \
    pip install -r /manager/requirements.txt
WORKDIR /workdir/
ADD ./datagen/requirements.txt ./
RUN pip install -r requirements.txt
ADD ./datagen/ ./
RUN chmod +x ./cli.py ./entrypoint.sh
ENTRYPOINT ./entrypoint.sh

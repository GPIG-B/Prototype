FROM python:3

# IMPORTANT: This Dockerfile expects to be run from the root of the repository
# and _not_ from within ./api/!

ADD ./manager/ /manager/
RUN pip install --upgrade pip && \
    pip install -r /manager/requirements.txt
ADD ./datagen/ /datagen/
RUN pip install -r /datagen/requirements.txt
WORKDIR /workdir/
ADD ./api/requirements.txt ./
RUN pip install -r requirements.txt
ADD ./api/ ./
RUN chmod +x ./cli.py ./entrypoint.sh
ENTRYPOINT ./entrypoint.sh

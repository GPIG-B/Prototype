FROM python:3

# IMPORTANT: This Dockerfile expects to be run from the root of the repository
# and _not_ from within ./api/!

WORKDIR /workdir/
ADD ./manager/requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
ADD ./manager/ ./
RUN chmod +x ./cli.py ./entrypoint.sh
ENTRYPOINT ./entrypoint.sh

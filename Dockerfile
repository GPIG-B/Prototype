FROM python:3

WORKDIR /workdir/
ADD . .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
RUN chmod +x $(find -name cli.py)

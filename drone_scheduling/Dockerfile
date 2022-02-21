FROM python:3

WORKDIR /workdir/
# TODO: do this with a wildcard?
ADD ./datagen/requirements.txt ./datagen/
ADD ./api/requirements.txt ./api/
ADD ./sensor_service/requirements.txt ./sensor_service/
ADD ./manager/requirements.txt ./manager/
ADD ./drone_scheduling/requirements.txt ./drone_scheduling/
ADD ./requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
ADD ./ ./
RUN pip install -r requirements.local.txt
RUN chmod +x $(find -name cli.py)

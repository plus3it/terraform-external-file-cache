FROM plus3it/tardigrade-ci:0.19.0

COPY requirements.txt /app/requirements.txt

RUN python -m pip install -r /app/requirements.txt

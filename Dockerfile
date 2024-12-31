FROM plus3it/tardigrade-ci:0.26.0

COPY requirements.txt /app/requirements.txt

RUN python -m pip install -r /app/requirements.txt

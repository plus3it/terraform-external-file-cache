FROM plus3it/tardigrade-ci:0.13.1
COPY requirements.txt /app/requirements.txt
RUN python -m pip install -r /app/requirements.txt
WORKDIR /ci-harness
ENTRYPOINT ["make"]


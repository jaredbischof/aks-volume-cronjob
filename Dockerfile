FROM python:3.11.1-alpine3.17

RUN pip3 install kubernetes
ARG COMMIT
LABEL commit=${COMMIT}
ENV COMMIT_SHA=${COMMIT}
USER guest
COPY file_copy.py .

ENTRYPOINT ["/usr/local/bin/python3", "/file_copy.py"]

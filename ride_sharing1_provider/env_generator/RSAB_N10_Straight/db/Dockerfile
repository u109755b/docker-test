FROM postgres:11.2-alpine

LABEL maintainer "miyake <miyake.kouta@ist.osaka-u.ac.jp>"

RUN apk add --update --no-cache \
    build-base \
    bash \
    curl \
    git \
		iproute2 \
    make \
  && rm -rf /var/cache/apk/*

RUN git clone https://github.com/petere/plsh \
  && cd plsh && git checkout 9b108516a005a0592d9c9e145189825f92f820e1 \
  && make && make install

CMD ["postgres", "-c", "config_file=/etc/postgresql.conf"]

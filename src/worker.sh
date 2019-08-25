#!/bin/sh
celery worker -A daemon -l info -c"${CONCURRENCY}"
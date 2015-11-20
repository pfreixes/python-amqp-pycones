#!/usr/bin/env bash

rabbitmqctl stop_app
rabbitmqctl force_reset
rabbitmqctl start_app

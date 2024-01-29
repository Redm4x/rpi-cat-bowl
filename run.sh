#!/bin/bash

echo "Starting pigpod"
sudo pigpiod
echo "Launching flask app"
flask --app app.py run -h 0.0.0.0
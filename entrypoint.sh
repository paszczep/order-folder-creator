#!/bin/sh

if [ $APP_MODE = "test" ]; then
    python -m unittest discover -v
else
    python -m app
fi

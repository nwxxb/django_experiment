#!/usr/bin/env python3
import os
from dotenv import load_dotenv
load_dotenv()
import os
from app import create_app
from flask.cli import FlaskGroup
from app.config import DevelopmentConfig

def create_app_cli():
    return create_app(DevelopmentConfig)

cli = FlaskGroup(create_app=create_app_cli)

if __name__ == '__main__':
    cli()

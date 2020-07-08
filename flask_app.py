#!/bin/python3.6
import os
from app import create_app
app = create_app()

app_env = os.getenv('FLASK_ENV')

if app_env and app_env == 'dev': 
	if __name__ == '__main__':
	    app.run(host='0.0.0.0', port=3000)

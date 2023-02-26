import os
import pathlib
SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')
DATA_DIR = pathlib.Path(__file__).parents[1] / "data"

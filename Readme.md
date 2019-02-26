movies
======

Running:

```bash
# Asumming Ubuntu
sudo apt install virtualenv

virtualenv -p python3 env
source env/bin/activate

git clone git@github.com:wieczorek1990/movies.git
cd movies

pip3 install -r requirements.txt

python3 manage.py migrate
# Generate api key using http://www.omdbapi.com/apikey.aspx
OMDB_API_KEY=$YOUR_OMDB_API_KEY python3 manage.py runserver
```

```sh
export PYTHONPATH=$(pwd)

export PARSHA=10  # or whatever

python parsers/shabat_shalom_parser.py $PARSHA
python parsers/reformjudaism_parser.py $PARSHA

# to find parsha url name go to https://lechaim.ru/torah/, click on your parsha
# and look for https://lechaim.ru/academy/<parsha-url-name>1/
export PARSHA_URL_NAME=parsha-url-name
python parsers/lechaim_parser.py $PARSHA $PARSHA_URL_NAME

python parsers/ramban_commentary_parser.py $PARSHA
python parsers/or_hachaim_commentary_parser.py $PARSHA
python parsers/hebrew_parser.py $PARSHA

# review 'json/10.json' and if it's ok,
export ADMIN_TOKEN='whatever'
export BASE_URL='https://yoursite.com'
python parsers/upload.py $PARSHA
```
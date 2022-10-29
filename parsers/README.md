```sh
export PYTHONPATH=$(pwd)

export PARSHA=10  # or whatever

python parsers/shabat_shalom_parser.py $PARSHA
python parsers/reformjudaism_parser.py $PARSHA
python parsers/parsers/lechaim_parser.py $PARSHA 'parsha-url-name'

# review 'json/10.json' and if it's ok,
export ADMIN_TOKEN='whatever'
python parsers/upload.py $PARSHA
```
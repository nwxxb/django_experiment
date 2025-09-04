```bash
# use flask cli
python run.py
# create and migrate development db
python run.py db upgrade
# snapshot current defined models column into migration file
python run.py db migrate -m "migration file message"
# run dev server
python run.py dev

# run test
pytest
```

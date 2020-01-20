## Flask Migrations

Install `flask-migrate` package.  
Import `Migrate` from the said package.

```python
migrate = Migrate(app, db)
```

You must have docker installed.  
SSH into the docker docker.

```bash
docker exec -it advanced_rest_flask sh
```

To create the migratuons folder, run the command.

```bash
flask db init
```

### To run migrations:

```bash
flask db migrate -m \'message\'.
```

### Create tables

```bash
flask db upgrade
 ```
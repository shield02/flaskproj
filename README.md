## A simple project on Flash library

This project will simply demonstarte a few concepts in flask library.
This concepts will include
- web forms
- database
- error handling
- pagination
- email sending
- date and time
- notification
- background jobs

### Migrations
This application uses the flask-migration extension to manage it migrations.
To initialize migrations, this will create the migration repository, run
```
flask db init
```

To run migrations, run
```
flask db migrate
```

To apply changes to the database, run
```
flask db upgrade
```

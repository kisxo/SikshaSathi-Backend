### postgresql commands for

### login postgres 

Login after fresh install - default user and database

`psql -U postgres -d postgres`

#### Linux (ubuntu)
`sudo -u postgres createuser --interactive`

To create postgres users interactively (recommended)

`sudo -u postgres createdb -O my_user my_database`

To create postgres database named 'my_database' owned by the user 'my_user'

`sudo -u postgres psql -l`

To list all database
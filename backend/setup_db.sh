sudo -u postgres bash -c "pg_ctlcluster 12 main restart"
sudo -u postgres bash -c "psql < setup.sql"
sudo -u postgres bash -c "psql trivia < trivia.psql"
sudo -u postgres bash -c "psql trivia_test < trivia.psql"

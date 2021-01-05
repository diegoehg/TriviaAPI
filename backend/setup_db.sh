sudo systemctl start postgresql@12-main
sudo -u postgres bash -c "psql < setup.sql"
sudo -u postgres bash -c "psql trivia < trivia.psql"
sudo -u postgres bash -c "psql trivia_test < trivia.psql"

-- Create the test database alongside the main one.
-- Mounted into postgres via docker-compose initdb.d.
SELECT 'CREATE DATABASE pivot_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'pivot_test')\gexec

GRANT ALL PRIVILEGES ON DATABASE pivot_test TO pivot;

DROP TABLE IF EXISTS zx_users;
DROP TABLE IF EXISTS domains;
DROP TABLE IF EXISTS mailgunCred;
CREATE TABLE zx_users (id integer PRIMARY KEY AUTOINCREMENT,email string,password string,role string);
CREATE TABLE domains (userid integer,domain string,notify_email string);
CREATE TABLE mailgunCred (domain string, apikey string);

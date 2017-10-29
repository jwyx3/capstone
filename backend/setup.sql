 create database if not exists backend;
 grant all on backend.* to 'user1'@'172.22.0.1' identified by 'passw0rd';
 grant all on backend.* to 'user1'@'localhost' identified by 'passw0rd';
 flush privileges;
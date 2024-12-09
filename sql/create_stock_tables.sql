-- run logged in as the owning user
CREATE DATABASE sdt;

-- connect to the newly created database
\c sdt

-- run connected to the desired database
CREATE TABLE stock_metrics (
stock varchar(10) PRIMARY KEY,
nav_discount_avg_1y numeric(16, 4),
nav_discount_avg_alltime numeric(16, 4)
);

-- insert values for testing
insert into stock_metrics values('AWF', -5.09, -7.89);
insert into stock_metrics values('BST', -3.00, -0.48);

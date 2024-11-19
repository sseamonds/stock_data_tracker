-- run logged in as the owning user
CREATE DATABASE sdt;

-- run connected to the desired database
CREATE TABLE stock_metrics (
stock varchar(10) PRIMARY KEY,
nav_discount_avg_1y numeric(16, 4),
nav_discount_avg_alltime numeric(16, 4)
);
-- insert values to testing
-- insert into stock_metrics values('DUM', 5, 55);

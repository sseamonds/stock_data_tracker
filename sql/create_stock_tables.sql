-- misc useful commands
\l -- list databases
\dt -- list tables

-- create a new database
CREATE DATABASE sdt;
-- connect to the newly created database
\c sdt

-- historical price table
CREATE TABLE stock_history (
symbol varchar(5),
record_date date,
closing_price numeric(8, 4),
closing_nav numeric(8, 4),
PRIMARY KEY(symbol, record_date)
);

-- historical metrics table
CREATE TABLE stock_metrics_history (
symbol varchar(5),
record_date date,
price_avg_60d numeric(8, 4),
price_avg_1yr numeric(8, 4),
nav_discount_premium numeric(6, 4),
nav_discount_premium_avg_60d numeric(6, 4),
nav_discount_premium_avg_1yr numeric(6, 4),
PRIMARY KEY (symbol, record_date)
);

-- current metrics table
CREATE TABLE current_stock_metrics (
symbol varchar(5) PRIMARY KEY,
nav_discount_premium_avg_1yr numeric(6, 4),
nav_discount_premium_avg_max numeric(6, 4),
last_updated TIMESTAMP
);

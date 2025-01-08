-- misc useful commands
\l -- list databases
\dt -- list tables

-- run logged in as the owning user
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
-- INSERT INTO stock_history
-- VALUES ('AWF', to_date('2024-10-10', 'YYYY-MM-DD'), 10, 10.5);
-- select * from stock_history where record_date > '2024-9-9';

-- historical metrics table
CREATE TABLE stock_metrics_history (
symbol varchar(5),
record_date date,
nav_discount numeric(6, 4),
nav_discount_avg_3m numeric(6, 4),
nav_discount_avg_1y numeric(6, 4),
price_avg_3m numeric(6, 4),
price_avg_1y numeric(6, 4),
PRIMARY KEY (symbol, record_date)
);
-- INSERT INTO stock_metrics_history 
-- VALUES ('AWF', to_date('2024-10-10', 'YYYY-MM-DD'), -5.09, -5.09, -5.09, 10, 10);
-- these both work
-- select * from stock_metrics_history where record_date > '9-9-2024';
-- select * from stock_metrics_history where record_date > '2024-9-9';

-- current metrics table
CREATE TABLE current_stock_metrics (
symbol varchar(5) PRIMARY KEY,
nav_discount_avg_1y numeric(16, 4),
nav_discount_avg_alltime numeric(16, 4),
last_updated TIMESTAMP
);
-- INSERT INTO current_stock_metrics 
-- VALUES('AWF', -5.09, -7.89, to_timestamp('2024-10-10 10:10:10', 'YYYY-MM-DD HH24:MI:SS'));
-- select * from current_stock_metrics where last_updated > '2024-10-10 11:9:9';

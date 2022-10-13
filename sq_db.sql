CREATE TABLE IF NOT EXISTS mainmenu (
menu_Id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
url text NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse (
wh_Id integer PRIMARY KEY AUTOINCREMENT,
conf_name text NOT NULL,
product_year integer NOT NULL,
volume float NOT NULL,
amount integer NOT NULL
);

CREATE TABLE IF NOT EXISTS recipe (
recipe_Id integer PRIMARY KEY,
recipe text NOT NULL
);
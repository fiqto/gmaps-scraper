DROP TABLE IF EXISTS item;

CREATE TABLE item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  name TEXT NOT NULL,
  rate TEXT NOT NULL,
  category TEXT NOT NULL,
  address TEXT NOT NULL
);
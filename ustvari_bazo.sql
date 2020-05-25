DROP TABLE IF EXISTS napovedi;
DROP TABLE IF EXISTS tekme;
DROP TABLE IF EXISTS klubi;
DROP TABLE IF EXISTS lige;
DROP TABLE IF EXISTS uporabniki;

CREATE TABLE uporabniki (
  id serial PRIMARY KEY,
  up_ime TEXT NOT NULL,
  geslo TEXT NOT NULL
);

CREATE TABLE lige (
  id serial PRIMARY KEY,
  drzava TEXT NOT NULL,
  ime TEXT
);

CREATE TABLE klubi (
  id integer PRIMARY KEY,
  ime_ekipe TEXT NOT NULL,
  liga integer REFERENCES lige(id)
);

CREATE TABLE tekme (
  stevilka serial PRIMARY KEY,
  domaca_ekipa integer NOT NULL REFERENCES klubi(id),
  gostujoca_ekipa integer NOT NULL REFERENCES klubi(id),
  rezultat TEXT,
  krog integer,
  datum DATE,
  ura TEXT,
  liga integer REFERENCES lige(id)
);

CREATE TABLE napovedi (
  stevilka serial PRIMARY KEY,
  uporabnik integer REFERENCES uporabniki(id),
  tekma integer REFERENCES tekme(stevilka),
  rez_dom integer NOT NULL,
  rez_gos integer NOT NULL,
  tocke integer,
  gol_razlika integer,
  UNIQUE (uporabnik, tekma)
);
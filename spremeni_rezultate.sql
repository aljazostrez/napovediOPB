UPDATE tekme SET rezultat = '1-0' WHERE tekme.stevilka = 3029363;
UPDATE tekme SET rezultat = '3-0' WHERE tekme.stevilka = 3029364;
UPDATE tekme SET rezultat = '0-1' WHERE tekme.stevilka = 3029365;
UPDATE tekme SET rezultat = '1-0' WHERE tekme.stevilka = 3029368;

UPDATE tekme SET rezultat = 'Neodigrana' WHERE tekme.stevilka = 3029363;
UPDATE tekme SET rezultat = 'Neodigrana' WHERE tekme.stevilka = 3029364;
UPDATE tekme SET rezultat = 'Neodigrana' WHERE tekme.stevilka = 3029365;
UPDATE tekme SET rezultat = 'Neodigrana' WHERE tekme.stevilka = 3029368;

DELETE FROM napovedi WHERE tekma=3029363 and uporabnik=14;
DELETE FROM napovedi WHERE tekma=3029364 and uporabnik=14;
DELETE FROM napovedi WHERE tekma=3029365 and uporabnik=14;
DELETE FROM napovedi WHERE tekma=3029368 and uporabnik=14;
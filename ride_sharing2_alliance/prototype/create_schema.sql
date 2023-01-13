DROP TABLE IF EXISTS mt;
CREATE TABLE mt(
    V int,
    L int,
    D int,
    R int,
    P CHAR
);
INSERT INTO mt(V, L, D, R, P) VALUES(1, 120, 1765, 1, 'A');
INSERT INTO mt(V, L, D, R, P) VALUES(2, 3866, 5228, 2, 'A');
INSERT INTO mt(V, L, D, R, P) VALUES(3, 6545, 6545, 0, 'A');


DROP TABLE IF EXISTS bt;
CREATE TABLE bt(
    V int,
    L int,
    D int,
    R int
);
INSERT INTO bt(V, L, D, R) VALUES(1, 120, 1765, 1);
INSERT INTO bt(V, L, D, R) VALUES(2, 3866, 5228, 2);
INSERT INTO bt(V, L, D, R) VALUES(3, 6545, 6545, 0);
CREATE TABLE User
(
    username varchar(20) NOT NULL,
    firstname varchar(20) NOT NULL,
    lastname varchar(20) NOT NULL,
    password varchar(256) NOT NULL,
    email varchar(40) NOT NULL,
    PRIMARY KEY (username)
);

CREATE TABLE Album
(
    albumid int NOT NULL AUTO_INCREMENT,
    title varchar(50) NOT NULL,
    created timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lastupdated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    username varchar(20) NOT NULL,
    access ENUM('public', 'private') NOT NULL DEFAULT 'private',
    PRIMARY KEY (albumid),
    FOREIGN KEY (username) REFERENCES User(username)
);

CREATE TABLE Photo
(
    picid varchar(40) NOT NULL,
    format char(3) NOT NULL,
    date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (picid)
);

CREATE TABLE Contain
(
    sequencenum int NOT NULL,
    albumid int NOT NULL,
    picid varchar(40) NOT NULL,
    caption varchar(255) NOT NULL DEFAULT '',
    PRIMARY KEY (sequencenum),
    FOREIGN KEY (albumid) REFERENCES Album(albumid),
    FOREIGN KEY (picid) REFERENCES Photo(picid)
);

CREATE TABLE AlbumAccess
(
    albumid int NOT NULL,
    username varchar(20) NOT NULL,
    FOREIGN KEY (albumid) REFERENCES Album(albumid),
    FOREIGN KEY (username) REFERENCES User(username)
);

delimiter //

CREATE TRIGGER before_insert_contain BEFORE INSERT on Contain
    FOR EACH ROW BEGIN
        DECLARE mid int;
        UPDATE Album SET Album.lastupdated = CURRENT_TIMESTAMP
        WHERE Album.albumid = new.albumid;
        SELECT MAX(sequencenum) INTO mid FROM Contain;
        IF mid IS NULL THEN
           SET new.sequencenum = 0;
        ELSE
           SET new.sequencenum = mid + 1;
        END IF;
    END;

CREATE TRIGGER update_date_del BEFORE DELETE on Contain
    FOR EACH ROW BEGIN
        UPDATE Album SET Album.lastupdated = CURRENT_TIMESTAMP
        WHERE Album.albumid = old.albumid;
    END;
//
delimiter ;

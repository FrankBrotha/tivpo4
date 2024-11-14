CREATE TABLE USERS (
    ID integer PRIMARY KEY,
    "name" varchar(255) NOT NULL,
    email varchar(255) NOT NULL,
    "password" varchar(255) NOT NULL,
    phoneNumber varchar(255) NOT NULL
);

CREATE TABLE ROOMS (
    ID integer PRIMARY KEY,
    roomType varchar(255),
    roomNumber varchar(20) UNIQUE NOT NULL,
    floor integer,
    hasTV boolean,
    hasWiFi boolean,
    hasMiniBar boolean,
    pricePerNight integer NOT NULL,
    capacity integer NOT NULL
);

CREATE TABLE BOOKINGS (
    ID integer PRIMARY KEY,
    userID integer,
    roomID integer,
    startDate date,
    endDate date,
    nights integer GENERATED ALWAYS AS (endDate - startDate) STORED,
    totalPrice integer,
    CONSTRAINT fk_room FOREIGN KEY (roomID) REFERENCES ROOMS (ID),
    CONSTRAINT fk_user FOREIGN KEY (userID) REFERENCES USERS (ID)
);

CREATE TABLE REVIEWS (
    ID integer PRIMARY KEY,
    bookingID integer,
    rating integer,
    reviewText text,
    CONSTRAINT fk_reservation FOREIGN KEY (bookingID) REFERENCES BOOKINGS (ID)
);

CREATE TABLE ADMINS (
    ID integer PRIMARY KEY,
    username varchar(255) NOT NULL,
    password varchar(255) NOT NULL
);

CREATE FUNCTION public.check_start_date() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.startDate < CURRENT_DATE THEN
        RAISE EXCEPTION 'Ошибка: дата начала бронирования не может быть в прошлом.';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER validate_start_date BEFORE INSERT ON public.bookings FOR EACH ROW EXECUTE FUNCTION public.check_start_date();


INSERT INTO USERS VALUES (1,'Alexander Prokopik', '1', '1', '88005553535');
INSERT INTO ADMINS VALUES (1,'admin','admin');
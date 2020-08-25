CREATE TABLE Film (
    Domestic_BO_Rank Int,
    Name varchar(255),
    Gross_Dollar Int,
    Release_Date_Raw varchar(30),
    BO_Year Int,
    BOMojoTableURL varchar(255),
    BOMojoFilmURL varchar(255),
    RawDuration varchar(10),
    DurationMinutes Int,
    ReleaseDate timestamp,
    PRIMARY KEY (Name, BO_Year)
);

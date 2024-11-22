DROP DATABASE IF EXISTS 'Xaitsnoo';
CREATE DATABASE 'Xaitsnoo';
USE 'Xaitsnoo';

-- All UUIDs I think should have the same format
-- Most other things have the keys as ints
-- But in the mock up, it has it with a reference to the table, so maybe a CHAR(size) would be better?
-- although that slightly depends on the number of entries we have, because that would be locked in size but having it locked in to be like, D01 seems betterish

-- The main table listing lexeme entries
CREATE TABLE Dictionary (
    UUID INT NOT NULL,
    Headword VARCHAR(255)
    Translation VARCHAR(255)
    GrammarID INT
    Notes VARCHAR(65535)
    PRIMARY KEY (UUID)
    FOREIGN KEY (GrammarID) REFERENCES Grammar(UUID)
);

-- Lists variants that may exist for a dictionary entry
-- Variants were causing issues in other components, should this be removed for now?
CREATE TABLE Variants (
    UUID INT NOT NULL,
    Variant VARCHAR(255)
    Context VARCHAR(255)
    DictionaryID INT
    SpeakerID INT
    PRIMARY KEY (UUID)
    FOREIGN KEY (DictionaryID) REFERENCES Dictionary(UUID)
    FOREIGN KEY (SpeakerID) REFERENCES Speakers(UUID)
);

-- Lists speakers
CREATE TABLE Speakers (
    UUID INT NOT NULL,
    FirstName VARCHAR(255)
    LastName VARCHAR(255)
    PRIMARY KEY (UUID)
);

-- Connects a dictionary entry with its speaker(s)
CREATE TABLE Dictionary_SpeakerAssociation (
    DictionaryID INT
    SpeakerID INT
    FOREIGN KEY (DictionaryID) REFERENCES Dictionary(UUID)
    FOREIGN KEY (SpeakerID) REFERENCES Speakers(UUID)
);

-- lists semantic classification
CREATE TABLE Classifications (
    UUID INT NOT NULL,
    ClassName VARCHAR(255)
    PRIMARY KEY (UUID)
);

-- Shows relationships between classifications
-- Because the same field is used as two foreign keys, each should get their own join
CREATE TABLE Classification_Taxonomy (
    ClassificationID INT
    ClassAssociationID INT
    FOREIGN KEY (ClassificationID) REFERENCES Classifications(UUID)
    FOREIGN KEY (ClassAssociationID) REFERENCES Classifications(UUID)
);

-- Links a dictionary entry with its classification(s)
CREATE TABLE Dictionary_ClassificationAssociation (
    DictionaryID INT
    ClassificationID INT
    FOREIGN KEY (DictionaryID) REFERENCES Dictionary(UUID)
    FOREIGN KEY (ClassificationID) REFERENCES Classifications(UUID)
);

-- Audio files from wherever it's floating around
CREATE TABLE Audio (
    UUID INT NOT NULL,
    AudioFile VARCHAR(255)
    PRIMARY KEY (UUID)
);

-- Connects a dictionary entry with its audio file(s)
CREATE TABLE Dictionary_AudioAssociation (
    DictionaryID INT
    AudioID INT
    FOREIGN KEY (DictionaryID) REFERENCES Dictionary(UUID)
    FOREIGN KEY (AudioID) REFERENCES Audio(UUID)
);

-- Photo files from wherever
CREATE TABLE Photo (
    UUID INT NOT NULL,
    PhotoFile VARCHAR(255)
    PRIMARY KEY (UUID)
);

-- Connects a dictionary entry with its photo file(s)
CREATE TABLE Dictionary_PhotoAssociation (
    DictionaryID INT
    PhotoID INT
    FOREIGN KEY (DictionaryID) REFERENCES Dictionary(UUID)
    FOREIGN KEY (PhotoID) REFERENCES Photo(UUID)
);

-- table of grammatical types
CREATE Grammar (
    UUID INT NOT NULL,
    GrammarType VARCHAR(255)
    PRIMARY KEY (UUID)
)
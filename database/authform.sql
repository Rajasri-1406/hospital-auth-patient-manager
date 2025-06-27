select * from tab;

--patient table(buffer)
CREATE TABLE patients (
    patient_id Varchar2(15) PRIMARY KEY,
    name VARCHAR2(100) NOT NULL,
    dob DATE NOT NULL,
    gender VARCHAR2(10) CHECK (gender IN ('Male', 'Female')) NOT NULL,
    age NUMBER NOT NULL,
    address VARCHAR2(255),
    phone VARCHAR2(10) CONSTRAINT phone_length CHECK (LENGTH(phone) < 15),
    patient_type VARCHAR2(10) CHECK (patient_type IN ('Normal', 'VIP')) NOT NULL
);


drop table patients;

select * from main_table;
select * from patients;

--main table(backend)
CREATE TABLE main_table (
    patient_id VARCHAR2(50) ,
    name VARCHAR2(100),
    dob DATE,
    gender VARCHAR2(10),
    age NUMBER(3),
    address VARCHAR2(255),
    phone VARCHAR2(15),
    patient_type VARCHAR2(10)
);

drop table main_table;

--authentication user
CREATE TABLE users (
    username VARCHAR2(50) PRIMARY KEY,
    password VARCHAR2(100),
    alternate_password VARCHAR2(255) NOT NULL
);
SELECT * FROM users;
--sequence creation for autoincr
CREATE SEQUENCE patient_id_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE;
    
drop sequence patient_id_seq;


-- Create a trigger to auto-generate patient_id
CREATE OR REPLACE TRIGGER trg_generate_patient_id
BEFORE INSERT ON patients
FOR EACH ROW
BEGIN
    :NEW.patient_id := 'P' || LPAD(patient_id_seq.NEXTVAL, 3, '00');
END;
/



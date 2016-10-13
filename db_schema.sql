
\c mimi_vtest

-- Table: categories
DROP TABLE IF EXISTS categories CASCADE;
CREATE TABLE categories
(
  name text,
  idcategory serial NOT NULL,
  CONSTRAINT categories_pkey PRIMARY KEY (idcategory),
  CONSTRAINT cat_name_unique UNIQUE (name)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE categories
  OWNER TO mimi;

-- Table: whenexpectfunctions
DROP TABLE IF EXISTS whenexpectfunctions CASCADE;
CREATE TABLE whenexpectfunctions
(
  name text NOT NULL,
  idwhenexpectfunction serial NOT NULL,
  CONSTRAINT function_pkey PRIMARY KEY (idwhenexpectfunction),
  CONSTRAINT funcname_unique UNIQUE (name)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE whenexpectfunctions
  OWNER TO postgres;

-- Table: function_category
DROP TABLE IF EXISTS function_category CASCADE;
CREATE TABLE function_category
(
  idcategory integer NOT NULL,
  idwhenexpectfunction integer NOT NULL,
  CONSTRAINT func_category_pkey PRIMARY KEY (idcategory, idwhenexpectfunction),
  CONSTRAINT categories_fkey FOREIGN KEY (idcategory)
      REFERENCES categories (idcategory) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT functions_fkey FOREIGN KEY (idwhenexpectfunction)
      REFERENCES whenexpectfunctions (idwhenexpectfunction) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE function_category
  OWNER TO mimi;

-- Table: testruns
DROP TABLE IF EXISTS testruns CASCADE;
CREATE TABLE testruns
(
  idtestrun serial NOT NULL,
  gitbranch text,
  githash text,
  stamp timestamp with time zone,
  driver text,
  os text,
  CONSTRAINT testruns_pkey PRIMARY KEY (idtestrun)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE testruns
  OWNER TO mimi;

-- Table: testcases
DROP TABLE IF EXISTS testcases CASCADE;
CREATE TABLE testcases
(
  idtestcase serial NOT NULL,
  fail boolean,
  idtestrun integer,
  idwhenexpectfunction integer,
  CONSTRAINT testcases_pkey PRIMARY KEY (idtestcase),
  CONSTRAINT function_fkey FOREIGN KEY (idwhenexpectfunction)
      REFERENCES whenexpectfunctions (idwhenexpectfunction) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT testruns_fkey FOREIGN KEY (idtestrun)
      REFERENCES testruns (idtestrun) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE testcases
  OWNER TO mimi;

-- Table: teststeps
DROP TABLE IF EXISTS teststeps CASCADE;
CREATE TABLE teststeps
(
  idteststep serial NOT NULL,
  idtestcase integer,
  logmessage text,
  logtype text,
  CONSTRAINT teststeps_pkey PRIMARY KEY (idteststep),
  CONSTRAINT testcases_fkey FOREIGN KEY (idtestcase)
      REFERENCES testcases (idtestcase) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE teststeps
  OWNER TO mimi;
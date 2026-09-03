ALTER TABLE ppe_compliance_logs 
  ALTER COLUMN start_timestamp TYPE DOUBLE PRECISION USING start_timestamp::double precision,
  ALTER COLUMN end_timestamp TYPE DOUBLE PRECISION USING end_timestamp::double precision;
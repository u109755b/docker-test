CREATE OR REPLACE VIEW public.d_warehouse AS 
SELECT __dummy__.COL0 AS W_ID, __dummy__.COL1 AS W_YTD, __dummy__.COL2 AS W_TAX, __dummy__.COL3 AS W_NAME, __dummy__.COL4 AS W_STREET_1, __dummy__.COL5 AS W_STREET_2, __dummy__.COL6 AS W_CITY, __dummy__.COL7 AS W_STATE, __dummy__.COL8 AS W_ZIP, __dummy__.COL9 AS LINEAGE FROM (SELECT d_warehouse_a10_0.COL0 AS COL0, d_warehouse_a10_0.COL1 AS COL1, d_warehouse_a10_0.COL2 AS COL2, d_warehouse_a10_0.COL3 AS COL3, d_warehouse_a10_0.COL4 AS COL4, d_warehouse_a10_0.COL5 AS COL5, d_warehouse_a10_0.COL6 AS COL6, d_warehouse_a10_0.COL7 AS COL7, d_warehouse_a10_0.COL8 AS COL8, d_warehouse_a10_0.COL9 AS COL9 FROM (SELECT warehouse_a10_0.W_ID AS COL0, warehouse_a10_0.W_YTD AS COL1, warehouse_a10_0.W_TAX AS COL2, warehouse_a10_0.W_NAME AS COL3, warehouse_a10_0.W_STREET_1 AS COL4, warehouse_a10_0.W_STREET_2 AS COL5, warehouse_a10_0.W_CITY AS COL6, warehouse_a10_0.W_STATE AS COL7, warehouse_a10_0.W_ZIP AS COL8, warehouse_a10_0.LINEAGE AS COL9 FROM public.warehouse AS warehouse_a10_0   ) AS d_warehouse_a10_0   ) AS __dummy__   ;

CREATE EXTENSION IF NOT EXISTS plsh;

CREATE TABLE IF NOT EXISTS public.__dummy__d_warehouse_detected_deletions (txid int, LIKE public.d_warehouse );
CREATE INDEX IF NOT EXISTS idx__dummy__d_warehouse_detected_deletions ON public.__dummy__d_warehouse_detected_deletions (txid);
CREATE TABLE IF NOT EXISTS public.__dummy__d_warehouse_detected_insertions (txid int, LIKE public.d_warehouse );
CREATE INDEX IF NOT EXISTS idx__dummy__d_warehouse_detected_insertions ON public.__dummy__d_warehouse_detected_insertions (txid);

CREATE OR REPLACE FUNCTION public.d_warehouse_get_detected_update_data(txid int)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  deletion_data text;
  insertion_data text;
  json_data text;
  BEGIN
    insertion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__d_warehouse_detected_insertions as t where t.txid = $1);
    IF insertion_data IS NOT DISTINCT FROM NULL THEN
        insertion_data := '[]';
    END IF;
    deletion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__d_warehouse_detected_deletions as t where t.txid = $1);
    IF deletion_data IS NOT DISTINCT FROM NULL THEN
        deletion_data := '[]';
    END IF;
    IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN
        -- calcuate the update data
        json_data := concat('{"view": ' , '"public.d_warehouse"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
        -- clear the update data
        DELETE FROM public.__dummy__d_warehouse_detected_deletions t where t.txid = $1;
        DELETE FROM public.__dummy__d_warehouse_detected_insertions t where t.txid = $1;
    END IF;
    RETURN json_data;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d_warehouse_run_shell(text) RETURNS text AS $$
#!/bin/sh

result=$(curl -s -X POST -H "Content-Type: application/json" $DEJIMA_EXECUTION_ENDPOINT -d "$1")
if  [ "$result" = "true" ];  then
    echo "true"
else 
    echo $result
fi
$$ LANGUAGE plsh;

CREATE OR REPLACE FUNCTION public.warehouse_materialization_for_d_warehouse()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_warehouse_for_d_warehouse' OR table_name = '__tmp_delta_del_warehouse_for_d_warehouse')
    THEN
        -- RAISE LOG 'execute procedure warehouse_materialization_for_d_warehouse';
        CREATE TEMPORARY TABLE __tmp_delta_ins_warehouse_for_d_warehouse ( LIKE public.warehouse ) WITH OIDS ON COMMIT DROP;
        CREATE TEMPORARY TABLE __tmp_delta_del_warehouse_for_d_warehouse ( LIKE public.warehouse ) WITH OIDS ON COMMIT DROP;

    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.warehouse';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.warehouse ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS warehouse_trigger_materialization_for_d_warehouse ON public.warehouse;
CREATE TRIGGER warehouse_trigger_materialization_for_d_warehouse
    BEFORE INSERT OR UPDATE OR DELETE ON
    public.warehouse FOR EACH STATEMENT EXECUTE PROCEDURE public.warehouse_materialization_for_d_warehouse();

CREATE OR REPLACE FUNCTION public.warehouse_update_for_d_warehouse()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    -- RAISE LOG 'execute procedure warehouse_update_for_d_warehouse';
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd_warehouse_delta_action_flag') THEN
        IF TG_OP = 'INSERT' THEN
        -- RAISE LOG 'NEW: %', NEW;
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_del_warehouse_for_d_warehouse WHERE ROW(W_ID,W_YTD,W_TAX,W_NAME,W_STREET_1,W_STREET_2,W_CITY,W_STATE,W_ZIP,LINEAGE)= NEW;
        INSERT INTO __tmp_delta_ins_warehouse_for_d_warehouse SELECT (NEW).*;
        ELSIF TG_OP = 'UPDATE' THEN
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_ins_warehouse_for_d_warehouse WHERE ROW(W_ID,W_YTD,W_TAX,W_NAME,W_STREET_1,W_STREET_2,W_CITY,W_STATE,W_ZIP,LINEAGE) = OLD;
        INSERT INTO __tmp_delta_del_warehouse_for_d_warehouse SELECT (OLD).*;
        DELETE FROM __tmp_delta_del_warehouse_for_d_warehouse WHERE ROW(W_ID,W_YTD,W_TAX,W_NAME,W_STREET_1,W_STREET_2,W_CITY,W_STATE,W_ZIP,LINEAGE) = NEW;
        INSERT INTO __tmp_delta_ins_warehouse_for_d_warehouse SELECT (NEW).*;
        ELSIF TG_OP = 'DELETE' THEN
        -- RAISE LOG 'OLD: %', OLD;
        DELETE FROM __tmp_delta_ins_warehouse_for_d_warehouse WHERE ROW(W_ID,W_YTD,W_TAX,W_NAME,W_STREET_1,W_STREET_2,W_CITY,W_STATE,W_ZIP,LINEAGE) = OLD;
        INSERT INTO __tmp_delta_del_warehouse_for_d_warehouse SELECT (OLD).*;
        END IF;
    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.warehouse';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.warehouse ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS warehouse_trigger_update_for_d_warehouse ON public.warehouse;
CREATE TRIGGER warehouse_trigger_update_for_d_warehouse
    AFTER INSERT OR UPDATE OR DELETE ON
    public.warehouse FOR EACH ROW EXECUTE PROCEDURE public.warehouse_update_for_d_warehouse();

CREATE OR REPLACE FUNCTION public.warehouse_detect_update_on_d_warehouse()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
func text;
tv text;
deletion_data text;
insertion_data text;
json_data text;
result text;
user_name text;
xid int;
array_delta_del public.warehouse[];
array_delta_ins public.warehouse[];
detected_deletions public.d_warehouse[];
detected_insertions public.d_warehouse[];
delta_ins_size int;
delta_del_size int;
BEGIN
IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'warehouse_detect_update_on_d_warehouse_flag') THEN
    CREATE TEMPORARY TABLE warehouse_detect_update_on_d_warehouse_flag ON COMMIT DROP AS (SELECT true as finish);
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd_warehouse_delta_action_flag') THEN
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_warehouse_for_d_warehouse AS tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_warehouse_for_d_warehouse;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_warehouse_for_d_warehouse tbl;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_warehouse_for_d_warehouse;

        WITH __tmp_delta_ins_warehouse_for_d_warehouse_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size),
        __tmp_delta_del_warehouse_for_d_warehouse_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_insertions FROM (SELECT __dummy__.COL0 AS W_ID, __dummy__.COL1 AS W_YTD, __dummy__.COL2 AS W_TAX, __dummy__.COL3 AS W_NAME, __dummy__.COL4 AS W_STREET_1, __dummy__.COL5 AS W_STREET_2, __dummy__.COL6 AS W_CITY, __dummy__.COL7 AS W_STATE, __dummy__.COL8 AS W_ZIP, __dummy__.COL9 AS LINEAGE FROM (SELECT part_ins_d_warehouse_a10_0.COL0 AS COL0, part_ins_d_warehouse_a10_0.COL1 AS COL1, part_ins_d_warehouse_a10_0.COL2 AS COL2, part_ins_d_warehouse_a10_0.COL3 AS COL3, part_ins_d_warehouse_a10_0.COL4 AS COL4, part_ins_d_warehouse_a10_0.COL5 AS COL5, part_ins_d_warehouse_a10_0.COL6 AS COL6, part_ins_d_warehouse_a10_0.COL7 AS COL7, part_ins_d_warehouse_a10_0.COL8 AS COL8, part_ins_d_warehouse_a10_0.COL9 AS COL9 FROM (SELECT p_0_a10_0.COL0 AS COL0, p_0_a10_0.COL1 AS COL1, p_0_a10_0.COL2 AS COL2, p_0_a10_0.COL3 AS COL3, p_0_a10_0.COL4 AS COL4, p_0_a10_0.COL5 AS COL5, p_0_a10_0.COL6 AS COL6, p_0_a10_0.COL7 AS COL7, p_0_a10_0.COL8 AS COL8, p_0_a10_0.COL9 AS COL9 FROM (SELECT __tmp_delta_ins_warehouse_for_d_warehouse_ar_a10_0.W_ID AS COL0, __tmp_delta_ins_warehouse_for_d_warehouse_ar_a10_0.W_YTD AS COL1, __tmp_delta_ins_warehouse_for_d_warehouse_ar_a10_0.W_TAX AS COL2, __tmp_delta_ins_warehouse_for_d_warehouse_ar_a10_0.W_NAME AS COL3, __tmp_delta_ins_warehouse_for_d_warehouse_ar_a10_0.W_STREET_1 AS COL4, __tmp_delta_ins_warehouse_for_d_warehouse_ar_a10_0.W_STREET_2 AS COL5, __tmp_delta_ins_warehouse_for_d_warehouse_ar_a10_0.W_CITY AS COL6, __tmp_delta_ins_warehouse_for_d_warehouse_ar_a10_0.W_STATE AS COL7, __tmp_delta_ins_warehouse_for_d_warehouse_ar_a10_0.W_ZIP AS COL8, __tmp_delta_ins_warehouse_for_d_warehouse_ar_a10_0.LINEAGE AS COL9 FROM __tmp_delta_ins_warehouse_for_d_warehouse_ar AS __tmp_delta_ins_warehouse_for_d_warehouse_ar_a10_0   ) AS p_0_a10_0   ) AS part_ins_d_warehouse_a10_0   ) AS __dummy__   ) AS tbl;

        insertion_data := (SELECT (array_to_json(detected_insertions))::text);
        IF insertion_data IS NOT DISTINCT FROM NULL THEN
            insertion_data := '[]';
        END IF;

        WITH __tmp_delta_ins_warehouse_for_d_warehouse_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size),
        __tmp_delta_del_warehouse_for_d_warehouse_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_deletions FROM (SELECT __dummy__.COL0 AS W_ID, __dummy__.COL1 AS W_YTD, __dummy__.COL2 AS W_TAX, __dummy__.COL3 AS W_NAME, __dummy__.COL4 AS W_STREET_1, __dummy__.COL5 AS W_STREET_2, __dummy__.COL6 AS W_CITY, __dummy__.COL7 AS W_STATE, __dummy__.COL8 AS W_ZIP, __dummy__.COL9 AS LINEAGE FROM (SELECT part_del_d_warehouse_a10_0.COL0 AS COL0, part_del_d_warehouse_a10_0.COL1 AS COL1, part_del_d_warehouse_a10_0.COL2 AS COL2, part_del_d_warehouse_a10_0.COL3 AS COL3, part_del_d_warehouse_a10_0.COL4 AS COL4, part_del_d_warehouse_a10_0.COL5 AS COL5, part_del_d_warehouse_a10_0.COL6 AS COL6, part_del_d_warehouse_a10_0.COL7 AS COL7, part_del_d_warehouse_a10_0.COL8 AS COL8, part_del_d_warehouse_a10_0.COL9 AS COL9 FROM (SELECT p_0_a10_0.COL0 AS COL0, p_0_a10_0.COL1 AS COL1, p_0_a10_0.COL2 AS COL2, p_0_a10_0.COL3 AS COL3, p_0_a10_0.COL4 AS COL4, p_0_a10_0.COL5 AS COL5, p_0_a10_0.COL6 AS COL6, p_0_a10_0.COL7 AS COL7, p_0_a10_0.COL8 AS COL8, p_0_a10_0.COL9 AS COL9 FROM (SELECT __tmp_delta_del_warehouse_for_d_warehouse_ar_a10_0.W_ID AS COL0, __tmp_delta_del_warehouse_for_d_warehouse_ar_a10_0.W_YTD AS COL1, __tmp_delta_del_warehouse_for_d_warehouse_ar_a10_0.W_TAX AS COL2, __tmp_delta_del_warehouse_for_d_warehouse_ar_a10_0.W_NAME AS COL3, __tmp_delta_del_warehouse_for_d_warehouse_ar_a10_0.W_STREET_1 AS COL4, __tmp_delta_del_warehouse_for_d_warehouse_ar_a10_0.W_STREET_2 AS COL5, __tmp_delta_del_warehouse_for_d_warehouse_ar_a10_0.W_CITY AS COL6, __tmp_delta_del_warehouse_for_d_warehouse_ar_a10_0.W_STATE AS COL7, __tmp_delta_del_warehouse_for_d_warehouse_ar_a10_0.W_ZIP AS COL8, __tmp_delta_del_warehouse_for_d_warehouse_ar_a10_0.LINEAGE AS COL9 FROM __tmp_delta_del_warehouse_for_d_warehouse_ar AS __tmp_delta_del_warehouse_for_d_warehouse_ar_a10_0   ) AS p_0_a10_0   ) AS part_del_d_warehouse_a10_0   ) AS __dummy__   ) AS tbl;

        deletion_data := (
        SELECT (array_to_json(detected_deletions))::text);
        IF deletion_data IS NOT DISTINCT FROM NULL THEN
            deletion_data := '[]';
        END IF;
        IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN
            user_name := (SELECT session_user);
            IF NOT (user_name = 'dejima') THEN
                xid := (SELECT txid_current());
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.d_warehouse"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.d_warehouse_run_shell(json_data);
                IF result = 'true' THEN
                    DROP TABLE __tmp_delta_ins_warehouse_for_d_warehouse;
                    DROP TABLE __tmp_delta_del_warehouse_for_d_warehouse;
                ELSE
                    CREATE TEMPORARY TABLE IF NOT EXISTS dejima_abort_flag ON COMMIT DROP AS (SELECT true as finish);
                    RAISE LOG 'update on view is rejected by the external tool, result from running the sh script: %', result;
                    -- RAISE check_violation USING MESSAGE = 'update on view is rejected by the external tool, result from running the sh script: '
                    -- || result;
                END IF;
            ELSE
                RAISE LOG 'function of detecting dejima update is called by % , no request sent to dejima proxy', user_name;
                xid := (SELECT txid_current());

                -- update the table that stores the insertions and deletions we calculated
                -- DELETE FROM public.__dummy__d_warehouse_detected_deletions;
                INSERT INTO public.__dummy__d_warehouse_detected_deletions
                    ( SELECT xid, * FROM unnest(detected_deletions) as detected_deletions_alias );

                -- DELETE FROM public.__dummy__d_warehouse_detected_insertions;
                INSERT INTO public.__dummy__d_warehouse_detected_insertions
                    ( SELECT xid, * FROM unnest(detected_insertions) as detected_insertions_alias );
            END IF;
        END IF;
    END IF;
END IF;
RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.warehouse';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the function public.warehouse_detect_update_on_d_warehouse() ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS warehouse_detect_update_on_d_warehouse ON public.warehouse;
CREATE CONSTRAINT TRIGGER warehouse_detect_update_on_d_warehouse
    AFTER INSERT OR UPDATE OR DELETE ON
    public.warehouse DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.warehouse_detect_update_on_d_warehouse();

CREATE OR REPLACE FUNCTION public.warehouse_propagate_updates_to_d_warehouse ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS public.warehouse_detect_update_on_d_warehouse IMMEDIATE;
    SET CONSTRAINTS public.warehouse_detect_update_on_d_warehouse DEFERRED;
    DROP TABLE IF EXISTS warehouse_detect_update_on_d_warehouse_flag;
    DROP TABLE IF EXISTS __tmp_delta_del_warehouse_for_d_warehouse;
    DROP TABLE IF EXISTS __tmp_delta_ins_warehouse_for_d_warehouse;
    RETURN true;
  END;
$$;



CREATE OR REPLACE FUNCTION public.d_warehouse_delta_action()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  deletion_data text;
  insertion_data text;
  json_data text;
  result text;
  user_name text;
  xid int;
  delta_ins_size int;
  delta_del_size int;
  array_delta_del public.d_warehouse[];
  array_delta_ins public.d_warehouse[];
  temprec_delta_del_warehouse public.warehouse%ROWTYPE;
            array_delta_del_warehouse public.warehouse[];
temprec_delta_ins_warehouse public.warehouse%ROWTYPE;
            array_delta_ins_warehouse public.warehouse[];
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd_warehouse_delta_action_flag') THEN
        -- RAISE LOG 'execute procedure d_warehouse_delta_action';
        CREATE TEMPORARY TABLE d_warehouse_delta_action_flag ON COMMIT DROP AS (SELECT true as finish);
        IF EXISTS (SELECT WHERE false )
        THEN
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the view are violated';
        END IF;
        IF EXISTS (SELECT WHERE false )
        THEN
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the source relations are violated';
        END IF;
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_d_warehouse AS tbl;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_d_warehouse as tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_d_warehouse;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_d_warehouse;
        
            WITH __tmp_delta_del_d_warehouse_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_d_warehouse_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_del_warehouse FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9) :: public.warehouse).*
            FROM (SELECT delta_del_warehouse_a10_0.COL0 AS COL0, delta_del_warehouse_a10_0.COL1 AS COL1, delta_del_warehouse_a10_0.COL2 AS COL2, delta_del_warehouse_a10_0.COL3 AS COL3, delta_del_warehouse_a10_0.COL4 AS COL4, delta_del_warehouse_a10_0.COL5 AS COL5, delta_del_warehouse_a10_0.COL6 AS COL6, delta_del_warehouse_a10_0.COL7 AS COL7, delta_del_warehouse_a10_0.COL8 AS COL8, delta_del_warehouse_a10_0.COL9 AS COL9 FROM (SELECT p_0_a10_0.COL0 AS COL0, p_0_a10_0.COL1 AS COL1, p_0_a10_0.COL2 AS COL2, p_0_a10_0.COL3 AS COL3, p_0_a10_0.COL4 AS COL4, p_0_a10_0.COL5 AS COL5, p_0_a10_0.COL6 AS COL6, p_0_a10_0.COL7 AS COL7, p_0_a10_0.COL8 AS COL8, p_0_a10_0.COL9 AS COL9 FROM (SELECT warehouse_a10_1.W_ID AS COL0, warehouse_a10_1.W_YTD AS COL1, warehouse_a10_1.W_TAX AS COL2, warehouse_a10_1.W_NAME AS COL3, warehouse_a10_1.W_STREET_1 AS COL4, warehouse_a10_1.W_STREET_2 AS COL5, warehouse_a10_1.W_CITY AS COL6, warehouse_a10_1.W_STATE AS COL7, warehouse_a10_1.W_ZIP AS COL8, warehouse_a10_1.LINEAGE AS COL9 FROM __tmp_delta_del_d_warehouse_ar AS __tmp_delta_del_d_warehouse_ar_a10_0, public.warehouse AS warehouse_a10_1 WHERE warehouse_a10_1.W_STATE = __tmp_delta_del_d_warehouse_ar_a10_0.W_STATE AND warehouse_a10_1.W_STREET_2 = __tmp_delta_del_d_warehouse_ar_a10_0.W_STREET_2 AND warehouse_a10_1.W_TAX = __tmp_delta_del_d_warehouse_ar_a10_0.W_TAX AND warehouse_a10_1.W_CITY = __tmp_delta_del_d_warehouse_ar_a10_0.W_CITY AND warehouse_a10_1.W_YTD = __tmp_delta_del_d_warehouse_ar_a10_0.W_YTD AND warehouse_a10_1.W_NAME = __tmp_delta_del_d_warehouse_ar_a10_0.W_NAME AND warehouse_a10_1.W_ZIP = __tmp_delta_del_d_warehouse_ar_a10_0.W_ZIP AND warehouse_a10_1.LINEAGE = __tmp_delta_del_d_warehouse_ar_a10_0.LINEAGE AND warehouse_a10_1.W_ID = __tmp_delta_del_d_warehouse_ar_a10_0.W_ID AND warehouse_a10_1.W_STREET_1 = __tmp_delta_del_d_warehouse_ar_a10_0.W_STREET_1  ) AS p_0_a10_0   ) AS delta_del_warehouse_a10_0   ) AS delta_del_warehouse_extra_alias) AS tbl;


            WITH __tmp_delta_del_d_warehouse_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_d_warehouse_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_ins_warehouse FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9) :: public.warehouse).*
            FROM (SELECT delta_ins_warehouse_a10_0.COL0 AS COL0, delta_ins_warehouse_a10_0.COL1 AS COL1, delta_ins_warehouse_a10_0.COL2 AS COL2, delta_ins_warehouse_a10_0.COL3 AS COL3, delta_ins_warehouse_a10_0.COL4 AS COL4, delta_ins_warehouse_a10_0.COL5 AS COL5, delta_ins_warehouse_a10_0.COL6 AS COL6, delta_ins_warehouse_a10_0.COL7 AS COL7, delta_ins_warehouse_a10_0.COL8 AS COL8, delta_ins_warehouse_a10_0.COL9 AS COL9 FROM (SELECT p_0_a10_0.COL0 AS COL0, p_0_a10_0.COL1 AS COL1, p_0_a10_0.COL2 AS COL2, p_0_a10_0.COL3 AS COL3, p_0_a10_0.COL4 AS COL4, p_0_a10_0.COL5 AS COL5, p_0_a10_0.COL6 AS COL6, p_0_a10_0.COL7 AS COL7, p_0_a10_0.COL8 AS COL8, p_0_a10_0.COL9 AS COL9 FROM (SELECT __tmp_delta_ins_d_warehouse_ar_a10_0.W_ID AS COL0, __tmp_delta_ins_d_warehouse_ar_a10_0.W_YTD AS COL1, __tmp_delta_ins_d_warehouse_ar_a10_0.W_TAX AS COL2, __tmp_delta_ins_d_warehouse_ar_a10_0.W_NAME AS COL3, __tmp_delta_ins_d_warehouse_ar_a10_0.W_STREET_1 AS COL4, __tmp_delta_ins_d_warehouse_ar_a10_0.W_STREET_2 AS COL5, __tmp_delta_ins_d_warehouse_ar_a10_0.W_CITY AS COL6, __tmp_delta_ins_d_warehouse_ar_a10_0.W_STATE AS COL7, __tmp_delta_ins_d_warehouse_ar_a10_0.W_ZIP AS COL8, __tmp_delta_ins_d_warehouse_ar_a10_0.LINEAGE AS COL9 FROM __tmp_delta_ins_d_warehouse_ar AS __tmp_delta_ins_d_warehouse_ar_a10_0 WHERE NOT EXISTS ( SELECT * FROM public.warehouse AS warehouse_a10 WHERE warehouse_a10.LINEAGE = __tmp_delta_ins_d_warehouse_ar_a10_0.LINEAGE AND warehouse_a10.W_ZIP = __tmp_delta_ins_d_warehouse_ar_a10_0.W_ZIP AND warehouse_a10.W_STATE = __tmp_delta_ins_d_warehouse_ar_a10_0.W_STATE AND warehouse_a10.W_CITY = __tmp_delta_ins_d_warehouse_ar_a10_0.W_CITY AND warehouse_a10.W_STREET_2 = __tmp_delta_ins_d_warehouse_ar_a10_0.W_STREET_2 AND warehouse_a10.W_STREET_1 = __tmp_delta_ins_d_warehouse_ar_a10_0.W_STREET_1 AND warehouse_a10.W_NAME = __tmp_delta_ins_d_warehouse_ar_a10_0.W_NAME AND warehouse_a10.W_TAX = __tmp_delta_ins_d_warehouse_ar_a10_0.W_TAX AND warehouse_a10.W_YTD = __tmp_delta_ins_d_warehouse_ar_a10_0.W_YTD AND warehouse_a10.W_ID = __tmp_delta_ins_d_warehouse_ar_a10_0.W_ID )  ) AS p_0_a10_0   ) AS delta_ins_warehouse_a10_0   ) AS delta_ins_warehouse_extra_alias) AS tbl; 


            IF array_delta_del_warehouse IS DISTINCT FROM NULL THEN
                FOREACH temprec_delta_del_warehouse IN array array_delta_del_warehouse  LOOP
                   DELETE FROM public.warehouse WHERE W_ID = temprec_delta_del_warehouse.W_ID AND W_YTD = temprec_delta_del_warehouse.W_YTD AND W_TAX = temprec_delta_del_warehouse.W_TAX AND W_NAME = temprec_delta_del_warehouse.W_NAME AND W_STREET_1 = temprec_delta_del_warehouse.W_STREET_1 AND W_STREET_2 = temprec_delta_del_warehouse.W_STREET_2 AND W_CITY = temprec_delta_del_warehouse.W_CITY AND W_STATE = temprec_delta_del_warehouse.W_STATE AND W_ZIP = temprec_delta_del_warehouse.W_ZIP AND LINEAGE = temprec_delta_del_warehouse.LINEAGE;
                END LOOP;
            END IF;


            IF array_delta_ins_warehouse IS DISTINCT FROM NULL THEN
                INSERT INTO public.warehouse (SELECT * FROM unnest(array_delta_ins_warehouse) as array_delta_ins_warehouse_alias) ;
            END IF;

        insertion_data := (SELECT (array_to_json(array_delta_ins))::text);
        IF insertion_data IS NOT DISTINCT FROM NULL THEN
            insertion_data := '[]';
        END IF;
        deletion_data := (SELECT (array_to_json(array_delta_del))::text);
        IF deletion_data IS NOT DISTINCT FROM NULL THEN
            deletion_data := '[]';
        END IF;
        IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN
            user_name := (SELECT session_user);
            IF NOT (user_name = 'dejima') THEN
                xid := (SELECT txid_current());
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.d_warehouse"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.d_warehouse_run_shell(json_data);
                IF NOT (result = 'true') THEN
                    CREATE TEMPORARY TABLE IF NOT EXISTS dejima_abort_flag ON COMMIT DROP AS (SELECT true as finish);
                    RAISE LOG 'update on view is rejected by the external tool, result from running the sh script: %', result;
                    -- RAISE check_violation USING MESSAGE = 'update on view is rejected by the external tool, result from running the sh script: '
                    -- || result;
                END IF;
            ELSE
                RAISE LOG 'function of detecting dejima update is called by % , no request sent to dejima proxy', user_name;
                xid := (SELECT txid_current());

                -- update the table that stores the insertions and deletions we calculated
                --DELETE FROM public.__dummy__d_warehouse_detected_deletions;
                INSERT INTO public.__dummy__d_warehouse_detected_deletions
                    SELECT xid, * FROM __tmp_delta_del_d_warehouse;

                --DELETE FROM public.__dummy__d_warehouse_detected_insertions;
                INSERT INTO public.__dummy__d_warehouse_detected_insertions
                    SELECT xid, * FROM __tmp_delta_ins_d_warehouse;
            END IF;
        END IF;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d_warehouse';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d_warehouse ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d_warehouse_materialization()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_d_warehouse' OR table_name = '__tmp_delta_del_d_warehouse')
    THEN
        -- RAISE LOG 'execute procedure d_warehouse_materialization';
        CREATE TEMPORARY TABLE __tmp_delta_ins_d_warehouse ( LIKE public.d_warehouse ) WITH OIDS ON COMMIT DROP;
        CREATE CONSTRAINT TRIGGER __tmp_d_warehouse_trigger_delta_action_ins
        AFTER INSERT OR UPDATE OR DELETE ON
            __tmp_delta_ins_d_warehouse DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW EXECUTE PROCEDURE public.d_warehouse_delta_action();

        CREATE TEMPORARY TABLE __tmp_delta_del_d_warehouse ( LIKE public.d_warehouse ) WITH OIDS ON COMMIT DROP;
        CREATE CONSTRAINT TRIGGER __tmp_d_warehouse_trigger_delta_action_del
        AFTER INSERT OR UPDATE OR DELETE ON
            __tmp_delta_del_d_warehouse DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW EXECUTE PROCEDURE public.d_warehouse_delta_action();
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d_warehouse';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d_warehouse ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS d_warehouse_trigger_materialization ON public.d_warehouse;
CREATE TRIGGER d_warehouse_trigger_materialization
    BEFORE INSERT OR UPDATE OR DELETE ON
      public.d_warehouse FOR EACH STATEMENT EXECUTE PROCEDURE public.d_warehouse_materialization();

CREATE OR REPLACE FUNCTION public.d_warehouse_update()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    -- RAISE LOG 'execute procedure d_warehouse_update';
    IF TG_OP = 'INSERT' THEN
      -- RAISE LOG 'NEW: %', NEW;
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_del_d_warehouse WHERE ROW(W_ID,W_YTD,W_TAX,W_NAME,W_STREET_1,W_STREET_2,W_CITY,W_STATE,W_ZIP,LINEAGE) = NEW;
      INSERT INTO __tmp_delta_ins_d_warehouse SELECT (NEW).*;
    ELSIF TG_OP = 'UPDATE' THEN
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_ins_d_warehouse WHERE ROW(W_ID,W_YTD,W_TAX,W_NAME,W_STREET_1,W_STREET_2,W_CITY,W_STATE,W_ZIP,LINEAGE) = OLD;
      INSERT INTO __tmp_delta_del_d_warehouse SELECT (OLD).*;
      DELETE FROM __tmp_delta_del_d_warehouse WHERE ROW(W_ID,W_YTD,W_TAX,W_NAME,W_STREET_1,W_STREET_2,W_CITY,W_STATE,W_ZIP,LINEAGE) = NEW;
      INSERT INTO __tmp_delta_ins_d_warehouse SELECT (NEW).*;
    ELSIF TG_OP = 'DELETE' THEN
      -- RAISE LOG 'OLD: %', OLD;
      DELETE FROM __tmp_delta_ins_d_warehouse WHERE ROW(W_ID,W_YTD,W_TAX,W_NAME,W_STREET_1,W_STREET_2,W_CITY,W_STATE,W_ZIP,LINEAGE) = OLD;
      INSERT INTO __tmp_delta_del_d_warehouse SELECT (OLD).*;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d_warehouse';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d_warehouse ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS d_warehouse_trigger_update ON public.d_warehouse;
CREATE TRIGGER d_warehouse_trigger_update
    INSTEAD OF INSERT OR UPDATE OR DELETE ON
      public.d_warehouse FOR EACH ROW EXECUTE PROCEDURE public.d_warehouse_update();

CREATE OR REPLACE FUNCTION public.d_warehouse_propagate_updates ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS __tmp_d_warehouse_trigger_delta_action_ins, __tmp_d_warehouse_trigger_delta_action_del IMMEDIATE;
    SET CONSTRAINTS __tmp_d_warehouse_trigger_delta_action_ins, __tmp_d_warehouse_trigger_delta_action_del DEFERRED;
    DROP TABLE IF EXISTS d_warehouse_delta_action_flag;
    DROP TABLE IF EXISTS __tmp_delta_del_d_warehouse;
    DROP TABLE IF EXISTS __tmp_delta_ins_d_warehouse;
    RETURN true;
  END;
$$;

CREATE OR REPLACE FUNCTION public.warehouse_propagates_to_d_warehouse(txid int)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    DELETE FROM public.__dummy__d_warehouse_detected_deletions t where t.txid = $1;
    DELETE FROM public.__dummy__d_warehouse_detected_insertions t where t.txid = $1;
    PERFORM public.warehouse_propagate_updates_to_d_warehouse();
    RETURN true;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d_warehouse_propagate(txid int)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    DELETE FROM public.__dummy__d_warehouse_detected_deletions t where t.txid = $1;
    DELETE FROM public.__dummy__d_warehouse_detected_insertions t where t.txid = $1;
    PERFORM public.d_warehouse_propagate_updates();
    RETURN true;
  END;
$$;

CREATE OR REPLACE FUNCTION public.remove_dummy_d_warehouse(txid int)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    DELETE FROM public.__dummy__d_warehouse_detected_deletions t where t.txid = $1;
    DELETE FROM public.__dummy__d_warehouse_detected_insertions t where t.txid = $1;
    RETURN true;
  END;
$$;
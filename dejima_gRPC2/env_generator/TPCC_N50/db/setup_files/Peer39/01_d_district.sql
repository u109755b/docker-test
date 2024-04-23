CREATE OR REPLACE VIEW public.d_district AS 
SELECT __dummy__.COL0 AS D_W_ID, __dummy__.COL1 AS D_ID, __dummy__.COL2 AS D_YTD, __dummy__.COL3 AS D_TAX, __dummy__.COL4 AS D_NEXT_O_ID, __dummy__.COL5 AS D_NAME, __dummy__.COL6 AS D_STREET_1, __dummy__.COL7 AS D_STREET_2, __dummy__.COL8 AS D_CITY, __dummy__.COL9 AS D_STATE, __dummy__.COL10 AS D_ZIP, __dummy__.COL11 AS LINEAGE FROM (SELECT d_district_a12_0.COL0 AS COL0, d_district_a12_0.COL1 AS COL1, d_district_a12_0.COL2 AS COL2, d_district_a12_0.COL3 AS COL3, d_district_a12_0.COL4 AS COL4, d_district_a12_0.COL5 AS COL5, d_district_a12_0.COL6 AS COL6, d_district_a12_0.COL7 AS COL7, d_district_a12_0.COL8 AS COL8, d_district_a12_0.COL9 AS COL9, d_district_a12_0.COL10 AS COL10, d_district_a12_0.COL11 AS COL11 FROM (SELECT district_a12_0.D_W_ID AS COL0, district_a12_0.D_ID AS COL1, district_a12_0.D_YTD AS COL2, district_a12_0.D_TAX AS COL3, district_a12_0.D_NEXT_O_ID AS COL4, district_a12_0.D_NAME AS COL5, district_a12_0.D_STREET_1 AS COL6, district_a12_0.D_STREET_2 AS COL7, district_a12_0.D_CITY AS COL8, district_a12_0.D_STATE AS COL9, district_a12_0.D_ZIP AS COL10, district_a12_0.LINEAGE AS COL11 FROM public.district AS district_a12_0   ) AS d_district_a12_0   ) AS __dummy__   ;

CREATE EXTENSION IF NOT EXISTS plsh;

CREATE TABLE IF NOT EXISTS public.__dummy__d_district_detected_deletions (txid int, LIKE public.d_district );
CREATE INDEX IF NOT EXISTS idx__dummy__d_district_detected_deletions ON public.__dummy__d_district_detected_deletions (txid);
CREATE TABLE IF NOT EXISTS public.__dummy__d_district_detected_insertions (txid int, LIKE public.d_district );
CREATE INDEX IF NOT EXISTS idx__dummy__d_district_detected_insertions ON public.__dummy__d_district_detected_insertions (txid);

CREATE OR REPLACE FUNCTION public.d_district_get_detected_update_data(txid int)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  deletion_data text;
  insertion_data text;
  json_data text;
  BEGIN
    insertion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__d_district_detected_insertions as t where t.txid = $1);
    IF insertion_data IS NOT DISTINCT FROM NULL THEN
        insertion_data := '[]';
    END IF;
    deletion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__d_district_detected_deletions as t where t.txid = $1);
    IF deletion_data IS NOT DISTINCT FROM NULL THEN
        deletion_data := '[]';
    END IF;
    IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN
        -- calcuate the update data
        json_data := concat('{"view": ' , '"public.d_district"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
        -- clear the update data
        DELETE FROM public.__dummy__d_district_detected_deletions t where t.txid = $1;
        DELETE FROM public.__dummy__d_district_detected_insertions t where t.txid = $1;
    END IF;
    RETURN json_data;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d_district_run_shell(text) RETURNS text AS $$
#!/bin/sh

result=$(curl -s -X POST -H "Content-Type: application/json" $DEJIMA_EXECUTION_ENDPOINT -d "$1")
if  [ "$result" = "true" ];  then
    echo "true"
else 
    echo $result
fi
$$ LANGUAGE plsh;

CREATE OR REPLACE FUNCTION public.district_materialization_for_d_district()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_district_for_d_district' OR table_name = '__tmp_delta_del_district_for_d_district')
    THEN
        -- RAISE LOG 'execute procedure district_materialization_for_d_district';
        CREATE TEMPORARY TABLE __tmp_delta_ins_district_for_d_district ( LIKE public.district ) WITH OIDS ON COMMIT DROP;
        CREATE TEMPORARY TABLE __tmp_delta_del_district_for_d_district ( LIKE public.district ) WITH OIDS ON COMMIT DROP;

    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.district';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.district ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS district_trigger_materialization_for_d_district ON public.district;
CREATE TRIGGER district_trigger_materialization_for_d_district
    BEFORE INSERT OR UPDATE OR DELETE ON
    public.district FOR EACH STATEMENT EXECUTE PROCEDURE public.district_materialization_for_d_district();

CREATE OR REPLACE FUNCTION public.district_update_for_d_district()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    -- RAISE LOG 'execute procedure district_update_for_d_district';
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd_district_delta_action_flag') THEN
        IF TG_OP = 'INSERT' THEN
        -- RAISE LOG 'NEW: %', NEW;
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_del_district_for_d_district WHERE ROW(D_W_ID,D_ID,D_YTD,D_TAX,D_NEXT_O_ID,D_NAME,D_STREET_1,D_STREET_2,D_CITY,D_STATE,D_ZIP,LINEAGE)= NEW;
        INSERT INTO __tmp_delta_ins_district_for_d_district SELECT (NEW).*;
        ELSIF TG_OP = 'UPDATE' THEN
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_ins_district_for_d_district WHERE ROW(D_W_ID,D_ID,D_YTD,D_TAX,D_NEXT_O_ID,D_NAME,D_STREET_1,D_STREET_2,D_CITY,D_STATE,D_ZIP,LINEAGE) = OLD;
        INSERT INTO __tmp_delta_del_district_for_d_district SELECT (OLD).*;
        DELETE FROM __tmp_delta_del_district_for_d_district WHERE ROW(D_W_ID,D_ID,D_YTD,D_TAX,D_NEXT_O_ID,D_NAME,D_STREET_1,D_STREET_2,D_CITY,D_STATE,D_ZIP,LINEAGE) = NEW;
        INSERT INTO __tmp_delta_ins_district_for_d_district SELECT (NEW).*;
        ELSIF TG_OP = 'DELETE' THEN
        -- RAISE LOG 'OLD: %', OLD;
        DELETE FROM __tmp_delta_ins_district_for_d_district WHERE ROW(D_W_ID,D_ID,D_YTD,D_TAX,D_NEXT_O_ID,D_NAME,D_STREET_1,D_STREET_2,D_CITY,D_STATE,D_ZIP,LINEAGE) = OLD;
        INSERT INTO __tmp_delta_del_district_for_d_district SELECT (OLD).*;
        END IF;
    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.district';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.district ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS district_trigger_update_for_d_district ON public.district;
CREATE TRIGGER district_trigger_update_for_d_district
    AFTER INSERT OR UPDATE OR DELETE ON
    public.district FOR EACH ROW EXECUTE PROCEDURE public.district_update_for_d_district();

CREATE OR REPLACE FUNCTION public.district_detect_update_on_d_district()
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
array_delta_del public.district[];
array_delta_ins public.district[];
detected_deletions public.d_district[];
detected_insertions public.d_district[];
delta_ins_size int;
delta_del_size int;
BEGIN
IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'district_detect_update_on_d_district_flag') THEN
    CREATE TEMPORARY TABLE district_detect_update_on_d_district_flag ON COMMIT DROP AS (SELECT true as finish);
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd_district_delta_action_flag') THEN
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_district_for_d_district AS tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_district_for_d_district;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_district_for_d_district tbl;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_district_for_d_district;

        WITH __tmp_delta_ins_district_for_d_district_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size),
        __tmp_delta_del_district_for_d_district_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_insertions FROM (SELECT __dummy__.COL0 AS D_W_ID, __dummy__.COL1 AS D_ID, __dummy__.COL2 AS D_YTD, __dummy__.COL3 AS D_TAX, __dummy__.COL4 AS D_NEXT_O_ID, __dummy__.COL5 AS D_NAME, __dummy__.COL6 AS D_STREET_1, __dummy__.COL7 AS D_STREET_2, __dummy__.COL8 AS D_CITY, __dummy__.COL9 AS D_STATE, __dummy__.COL10 AS D_ZIP, __dummy__.COL11 AS LINEAGE FROM (SELECT part_ins_d_district_a12_0.COL0 AS COL0, part_ins_d_district_a12_0.COL1 AS COL1, part_ins_d_district_a12_0.COL2 AS COL2, part_ins_d_district_a12_0.COL3 AS COL3, part_ins_d_district_a12_0.COL4 AS COL4, part_ins_d_district_a12_0.COL5 AS COL5, part_ins_d_district_a12_0.COL6 AS COL6, part_ins_d_district_a12_0.COL7 AS COL7, part_ins_d_district_a12_0.COL8 AS COL8, part_ins_d_district_a12_0.COL9 AS COL9, part_ins_d_district_a12_0.COL10 AS COL10, part_ins_d_district_a12_0.COL11 AS COL11 FROM (SELECT p_0_a12_0.COL0 AS COL0, p_0_a12_0.COL1 AS COL1, p_0_a12_0.COL2 AS COL2, p_0_a12_0.COL3 AS COL3, p_0_a12_0.COL4 AS COL4, p_0_a12_0.COL5 AS COL5, p_0_a12_0.COL6 AS COL6, p_0_a12_0.COL7 AS COL7, p_0_a12_0.COL8 AS COL8, p_0_a12_0.COL9 AS COL9, p_0_a12_0.COL10 AS COL10, p_0_a12_0.COL11 AS COL11 FROM (SELECT __tmp_delta_ins_district_for_d_district_ar_a12_0.D_W_ID AS COL0, __tmp_delta_ins_district_for_d_district_ar_a12_0.D_ID AS COL1, __tmp_delta_ins_district_for_d_district_ar_a12_0.D_YTD AS COL2, __tmp_delta_ins_district_for_d_district_ar_a12_0.D_TAX AS COL3, __tmp_delta_ins_district_for_d_district_ar_a12_0.D_NEXT_O_ID AS COL4, __tmp_delta_ins_district_for_d_district_ar_a12_0.D_NAME AS COL5, __tmp_delta_ins_district_for_d_district_ar_a12_0.D_STREET_1 AS COL6, __tmp_delta_ins_district_for_d_district_ar_a12_0.D_STREET_2 AS COL7, __tmp_delta_ins_district_for_d_district_ar_a12_0.D_CITY AS COL8, __tmp_delta_ins_district_for_d_district_ar_a12_0.D_STATE AS COL9, __tmp_delta_ins_district_for_d_district_ar_a12_0.D_ZIP AS COL10, __tmp_delta_ins_district_for_d_district_ar_a12_0.LINEAGE AS COL11 FROM __tmp_delta_ins_district_for_d_district_ar AS __tmp_delta_ins_district_for_d_district_ar_a12_0   ) AS p_0_a12_0   ) AS part_ins_d_district_a12_0   ) AS __dummy__   ) AS tbl;

        insertion_data := (SELECT (array_to_json(detected_insertions))::text);
        IF insertion_data IS NOT DISTINCT FROM NULL THEN
            insertion_data := '[]';
        END IF;

        WITH __tmp_delta_ins_district_for_d_district_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size),
        __tmp_delta_del_district_for_d_district_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_deletions FROM (SELECT __dummy__.COL0 AS D_W_ID, __dummy__.COL1 AS D_ID, __dummy__.COL2 AS D_YTD, __dummy__.COL3 AS D_TAX, __dummy__.COL4 AS D_NEXT_O_ID, __dummy__.COL5 AS D_NAME, __dummy__.COL6 AS D_STREET_1, __dummy__.COL7 AS D_STREET_2, __dummy__.COL8 AS D_CITY, __dummy__.COL9 AS D_STATE, __dummy__.COL10 AS D_ZIP, __dummy__.COL11 AS LINEAGE FROM (SELECT part_del_d_district_a12_0.COL0 AS COL0, part_del_d_district_a12_0.COL1 AS COL1, part_del_d_district_a12_0.COL2 AS COL2, part_del_d_district_a12_0.COL3 AS COL3, part_del_d_district_a12_0.COL4 AS COL4, part_del_d_district_a12_0.COL5 AS COL5, part_del_d_district_a12_0.COL6 AS COL6, part_del_d_district_a12_0.COL7 AS COL7, part_del_d_district_a12_0.COL8 AS COL8, part_del_d_district_a12_0.COL9 AS COL9, part_del_d_district_a12_0.COL10 AS COL10, part_del_d_district_a12_0.COL11 AS COL11 FROM (SELECT p_0_a12_0.COL0 AS COL0, p_0_a12_0.COL1 AS COL1, p_0_a12_0.COL2 AS COL2, p_0_a12_0.COL3 AS COL3, p_0_a12_0.COL4 AS COL4, p_0_a12_0.COL5 AS COL5, p_0_a12_0.COL6 AS COL6, p_0_a12_0.COL7 AS COL7, p_0_a12_0.COL8 AS COL8, p_0_a12_0.COL9 AS COL9, p_0_a12_0.COL10 AS COL10, p_0_a12_0.COL11 AS COL11 FROM (SELECT __tmp_delta_del_district_for_d_district_ar_a12_0.D_W_ID AS COL0, __tmp_delta_del_district_for_d_district_ar_a12_0.D_ID AS COL1, __tmp_delta_del_district_for_d_district_ar_a12_0.D_YTD AS COL2, __tmp_delta_del_district_for_d_district_ar_a12_0.D_TAX AS COL3, __tmp_delta_del_district_for_d_district_ar_a12_0.D_NEXT_O_ID AS COL4, __tmp_delta_del_district_for_d_district_ar_a12_0.D_NAME AS COL5, __tmp_delta_del_district_for_d_district_ar_a12_0.D_STREET_1 AS COL6, __tmp_delta_del_district_for_d_district_ar_a12_0.D_STREET_2 AS COL7, __tmp_delta_del_district_for_d_district_ar_a12_0.D_CITY AS COL8, __tmp_delta_del_district_for_d_district_ar_a12_0.D_STATE AS COL9, __tmp_delta_del_district_for_d_district_ar_a12_0.D_ZIP AS COL10, __tmp_delta_del_district_for_d_district_ar_a12_0.LINEAGE AS COL11 FROM __tmp_delta_del_district_for_d_district_ar AS __tmp_delta_del_district_for_d_district_ar_a12_0   ) AS p_0_a12_0   ) AS part_del_d_district_a12_0   ) AS __dummy__   ) AS tbl;

        deletion_data := (
        SELECT (array_to_json(detected_deletions))::text);
        IF deletion_data IS NOT DISTINCT FROM NULL THEN
            deletion_data := '[]';
        END IF;
        IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN
            user_name := (SELECT session_user);
            IF NOT (user_name = 'dejima') THEN
                xid := (SELECT txid_current());
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.d_district"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.d_district_run_shell(json_data);
                IF result = 'true' THEN
                    DROP TABLE __tmp_delta_ins_district_for_d_district;
                    DROP TABLE __tmp_delta_del_district_for_d_district;
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
                -- DELETE FROM public.__dummy__d_district_detected_deletions;
                INSERT INTO public.__dummy__d_district_detected_deletions
                    ( SELECT xid, * FROM unnest(detected_deletions) as detected_deletions_alias );

                -- DELETE FROM public.__dummy__d_district_detected_insertions;
                INSERT INTO public.__dummy__d_district_detected_insertions
                    ( SELECT xid, * FROM unnest(detected_insertions) as detected_insertions_alias );
            END IF;
        END IF;
    END IF;
END IF;
RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.district';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the function public.district_detect_update_on_d_district() ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS district_detect_update_on_d_district ON public.district;
CREATE CONSTRAINT TRIGGER district_detect_update_on_d_district
    AFTER INSERT OR UPDATE OR DELETE ON
    public.district DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.district_detect_update_on_d_district();

CREATE OR REPLACE FUNCTION public.district_propagate_updates_to_d_district ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS public.district_detect_update_on_d_district IMMEDIATE;
    SET CONSTRAINTS public.district_detect_update_on_d_district DEFERRED;
    DROP TABLE IF EXISTS district_detect_update_on_d_district_flag;
    DROP TABLE IF EXISTS __tmp_delta_del_district_for_d_district;
    DROP TABLE IF EXISTS __tmp_delta_ins_district_for_d_district;
    RETURN true;
  END;
$$;



CREATE OR REPLACE FUNCTION public.d_district_delta_action()
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
  array_delta_del public.d_district[];
  array_delta_ins public.d_district[];
  temprec_delta_del_district public.district%ROWTYPE;
            array_delta_del_district public.district[];
temprec_delta_ins_district public.district%ROWTYPE;
            array_delta_ins_district public.district[];
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd_district_delta_action_flag') THEN
        -- RAISE LOG 'execute procedure d_district_delta_action';
        CREATE TEMPORARY TABLE d_district_delta_action_flag ON COMMIT DROP AS (SELECT true as finish);
        IF EXISTS (SELECT WHERE false )
        THEN
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the view are violated';
        END IF;
        IF EXISTS (SELECT WHERE false )
        THEN
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the source relations are violated';
        END IF;
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_d_district AS tbl;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_d_district as tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_d_district;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_d_district;
        
            WITH __tmp_delta_del_d_district_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_d_district_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_del_district FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11) :: public.district).*
            FROM (SELECT delta_del_district_a12_0.COL0 AS COL0, delta_del_district_a12_0.COL1 AS COL1, delta_del_district_a12_0.COL2 AS COL2, delta_del_district_a12_0.COL3 AS COL3, delta_del_district_a12_0.COL4 AS COL4, delta_del_district_a12_0.COL5 AS COL5, delta_del_district_a12_0.COL6 AS COL6, delta_del_district_a12_0.COL7 AS COL7, delta_del_district_a12_0.COL8 AS COL8, delta_del_district_a12_0.COL9 AS COL9, delta_del_district_a12_0.COL10 AS COL10, delta_del_district_a12_0.COL11 AS COL11 FROM (SELECT p_0_a12_0.COL0 AS COL0, p_0_a12_0.COL1 AS COL1, p_0_a12_0.COL2 AS COL2, p_0_a12_0.COL3 AS COL3, p_0_a12_0.COL4 AS COL4, p_0_a12_0.COL5 AS COL5, p_0_a12_0.COL6 AS COL6, p_0_a12_0.COL7 AS COL7, p_0_a12_0.COL8 AS COL8, p_0_a12_0.COL9 AS COL9, p_0_a12_0.COL10 AS COL10, p_0_a12_0.COL11 AS COL11 FROM (SELECT district_a12_1.D_W_ID AS COL0, district_a12_1.D_ID AS COL1, district_a12_1.D_YTD AS COL2, district_a12_1.D_TAX AS COL3, district_a12_1.D_NEXT_O_ID AS COL4, district_a12_1.D_NAME AS COL5, district_a12_1.D_STREET_1 AS COL6, district_a12_1.D_STREET_2 AS COL7, district_a12_1.D_CITY AS COL8, district_a12_1.D_STATE AS COL9, district_a12_1.D_ZIP AS COL10, district_a12_1.LINEAGE AS COL11 FROM __tmp_delta_del_d_district_ar AS __tmp_delta_del_d_district_ar_a12_0, public.district AS district_a12_1 WHERE district_a12_1.D_STREET_2 = __tmp_delta_del_d_district_ar_a12_0.D_STREET_2 AND district_a12_1.D_NAME = __tmp_delta_del_d_district_ar_a12_0.D_NAME AND district_a12_1.D_YTD = __tmp_delta_del_d_district_ar_a12_0.D_YTD AND district_a12_1.D_STREET_1 = __tmp_delta_del_d_district_ar_a12_0.D_STREET_1 AND district_a12_1.D_ZIP = __tmp_delta_del_d_district_ar_a12_0.D_ZIP AND district_a12_1.D_ID = __tmp_delta_del_d_district_ar_a12_0.D_ID AND district_a12_1.D_TAX = __tmp_delta_del_d_district_ar_a12_0.D_TAX AND district_a12_1.D_CITY = __tmp_delta_del_d_district_ar_a12_0.D_CITY AND district_a12_1.LINEAGE = __tmp_delta_del_d_district_ar_a12_0.LINEAGE AND district_a12_1.D_STATE = __tmp_delta_del_d_district_ar_a12_0.D_STATE AND district_a12_1.D_W_ID = __tmp_delta_del_d_district_ar_a12_0.D_W_ID AND district_a12_1.D_NEXT_O_ID = __tmp_delta_del_d_district_ar_a12_0.D_NEXT_O_ID  ) AS p_0_a12_0   ) AS delta_del_district_a12_0   ) AS delta_del_district_extra_alias) AS tbl;


            WITH __tmp_delta_del_d_district_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_d_district_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_ins_district FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11) :: public.district).*
            FROM (SELECT delta_ins_district_a12_0.COL0 AS COL0, delta_ins_district_a12_0.COL1 AS COL1, delta_ins_district_a12_0.COL2 AS COL2, delta_ins_district_a12_0.COL3 AS COL3, delta_ins_district_a12_0.COL4 AS COL4, delta_ins_district_a12_0.COL5 AS COL5, delta_ins_district_a12_0.COL6 AS COL6, delta_ins_district_a12_0.COL7 AS COL7, delta_ins_district_a12_0.COL8 AS COL8, delta_ins_district_a12_0.COL9 AS COL9, delta_ins_district_a12_0.COL10 AS COL10, delta_ins_district_a12_0.COL11 AS COL11 FROM (SELECT p_0_a12_0.COL0 AS COL0, p_0_a12_0.COL1 AS COL1, p_0_a12_0.COL2 AS COL2, p_0_a12_0.COL3 AS COL3, p_0_a12_0.COL4 AS COL4, p_0_a12_0.COL5 AS COL5, p_0_a12_0.COL6 AS COL6, p_0_a12_0.COL7 AS COL7, p_0_a12_0.COL8 AS COL8, p_0_a12_0.COL9 AS COL9, p_0_a12_0.COL10 AS COL10, p_0_a12_0.COL11 AS COL11 FROM (SELECT __tmp_delta_ins_d_district_ar_a12_0.D_W_ID AS COL0, __tmp_delta_ins_d_district_ar_a12_0.D_ID AS COL1, __tmp_delta_ins_d_district_ar_a12_0.D_YTD AS COL2, __tmp_delta_ins_d_district_ar_a12_0.D_TAX AS COL3, __tmp_delta_ins_d_district_ar_a12_0.D_NEXT_O_ID AS COL4, __tmp_delta_ins_d_district_ar_a12_0.D_NAME AS COL5, __tmp_delta_ins_d_district_ar_a12_0.D_STREET_1 AS COL6, __tmp_delta_ins_d_district_ar_a12_0.D_STREET_2 AS COL7, __tmp_delta_ins_d_district_ar_a12_0.D_CITY AS COL8, __tmp_delta_ins_d_district_ar_a12_0.D_STATE AS COL9, __tmp_delta_ins_d_district_ar_a12_0.D_ZIP AS COL10, __tmp_delta_ins_d_district_ar_a12_0.LINEAGE AS COL11 FROM __tmp_delta_ins_d_district_ar AS __tmp_delta_ins_d_district_ar_a12_0 WHERE NOT EXISTS ( SELECT * FROM public.district AS district_a12 WHERE district_a12.LINEAGE = __tmp_delta_ins_d_district_ar_a12_0.LINEAGE AND district_a12.D_ZIP = __tmp_delta_ins_d_district_ar_a12_0.D_ZIP AND district_a12.D_STATE = __tmp_delta_ins_d_district_ar_a12_0.D_STATE AND district_a12.D_CITY = __tmp_delta_ins_d_district_ar_a12_0.D_CITY AND district_a12.D_STREET_2 = __tmp_delta_ins_d_district_ar_a12_0.D_STREET_2 AND district_a12.D_STREET_1 = __tmp_delta_ins_d_district_ar_a12_0.D_STREET_1 AND district_a12.D_NAME = __tmp_delta_ins_d_district_ar_a12_0.D_NAME AND district_a12.D_NEXT_O_ID = __tmp_delta_ins_d_district_ar_a12_0.D_NEXT_O_ID AND district_a12.D_TAX = __tmp_delta_ins_d_district_ar_a12_0.D_TAX AND district_a12.D_YTD = __tmp_delta_ins_d_district_ar_a12_0.D_YTD AND district_a12.D_ID = __tmp_delta_ins_d_district_ar_a12_0.D_ID AND district_a12.D_W_ID = __tmp_delta_ins_d_district_ar_a12_0.D_W_ID )  ) AS p_0_a12_0   ) AS delta_ins_district_a12_0   ) AS delta_ins_district_extra_alias) AS tbl; 


            IF array_delta_del_district IS DISTINCT FROM NULL THEN
                FOREACH temprec_delta_del_district IN array array_delta_del_district  LOOP
                   DELETE FROM public.district WHERE D_W_ID = temprec_delta_del_district.D_W_ID AND D_ID = temprec_delta_del_district.D_ID AND D_YTD = temprec_delta_del_district.D_YTD AND D_TAX = temprec_delta_del_district.D_TAX AND D_NEXT_O_ID = temprec_delta_del_district.D_NEXT_O_ID AND D_NAME = temprec_delta_del_district.D_NAME AND D_STREET_1 = temprec_delta_del_district.D_STREET_1 AND D_STREET_2 = temprec_delta_del_district.D_STREET_2 AND D_CITY = temprec_delta_del_district.D_CITY AND D_STATE = temprec_delta_del_district.D_STATE AND D_ZIP = temprec_delta_del_district.D_ZIP AND LINEAGE = temprec_delta_del_district.LINEAGE;
                END LOOP;
            END IF;


            IF array_delta_ins_district IS DISTINCT FROM NULL THEN
                INSERT INTO public.district (SELECT * FROM unnest(array_delta_ins_district) as array_delta_ins_district_alias) ;
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
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.d_district"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.d_district_run_shell(json_data);
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
                --DELETE FROM public.__dummy__d_district_detected_deletions;
                INSERT INTO public.__dummy__d_district_detected_deletions
                    SELECT xid, * FROM __tmp_delta_del_d_district;

                --DELETE FROM public.__dummy__d_district_detected_insertions;
                INSERT INTO public.__dummy__d_district_detected_insertions
                    SELECT xid, * FROM __tmp_delta_ins_d_district;
            END IF;
        END IF;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d_district';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d_district ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d_district_materialization()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_d_district' OR table_name = '__tmp_delta_del_d_district')
    THEN
        -- RAISE LOG 'execute procedure d_district_materialization';
        CREATE TEMPORARY TABLE __tmp_delta_ins_d_district ( LIKE public.d_district ) WITH OIDS ON COMMIT DROP;
        CREATE CONSTRAINT TRIGGER __tmp_d_district_trigger_delta_action_ins
        AFTER INSERT OR UPDATE OR DELETE ON
            __tmp_delta_ins_d_district DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW EXECUTE PROCEDURE public.d_district_delta_action();

        CREATE TEMPORARY TABLE __tmp_delta_del_d_district ( LIKE public.d_district ) WITH OIDS ON COMMIT DROP;
        CREATE CONSTRAINT TRIGGER __tmp_d_district_trigger_delta_action_del
        AFTER INSERT OR UPDATE OR DELETE ON
            __tmp_delta_del_d_district DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW EXECUTE PROCEDURE public.d_district_delta_action();
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d_district';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d_district ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS d_district_trigger_materialization ON public.d_district;
CREATE TRIGGER d_district_trigger_materialization
    BEFORE INSERT OR UPDATE OR DELETE ON
      public.d_district FOR EACH STATEMENT EXECUTE PROCEDURE public.d_district_materialization();

CREATE OR REPLACE FUNCTION public.d_district_update()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    -- RAISE LOG 'execute procedure d_district_update';
    IF TG_OP = 'INSERT' THEN
      -- RAISE LOG 'NEW: %', NEW;
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_del_d_district WHERE ROW(D_W_ID,D_ID,D_YTD,D_TAX,D_NEXT_O_ID,D_NAME,D_STREET_1,D_STREET_2,D_CITY,D_STATE,D_ZIP,LINEAGE) = NEW;
      INSERT INTO __tmp_delta_ins_d_district SELECT (NEW).*;
    ELSIF TG_OP = 'UPDATE' THEN
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_ins_d_district WHERE ROW(D_W_ID,D_ID,D_YTD,D_TAX,D_NEXT_O_ID,D_NAME,D_STREET_1,D_STREET_2,D_CITY,D_STATE,D_ZIP,LINEAGE) = OLD;
      INSERT INTO __tmp_delta_del_d_district SELECT (OLD).*;
      DELETE FROM __tmp_delta_del_d_district WHERE ROW(D_W_ID,D_ID,D_YTD,D_TAX,D_NEXT_O_ID,D_NAME,D_STREET_1,D_STREET_2,D_CITY,D_STATE,D_ZIP,LINEAGE) = NEW;
      INSERT INTO __tmp_delta_ins_d_district SELECT (NEW).*;
    ELSIF TG_OP = 'DELETE' THEN
      -- RAISE LOG 'OLD: %', OLD;
      DELETE FROM __tmp_delta_ins_d_district WHERE ROW(D_W_ID,D_ID,D_YTD,D_TAX,D_NEXT_O_ID,D_NAME,D_STREET_1,D_STREET_2,D_CITY,D_STATE,D_ZIP,LINEAGE) = OLD;
      INSERT INTO __tmp_delta_del_d_district SELECT (OLD).*;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d_district';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d_district ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS d_district_trigger_update ON public.d_district;
CREATE TRIGGER d_district_trigger_update
    INSTEAD OF INSERT OR UPDATE OR DELETE ON
      public.d_district FOR EACH ROW EXECUTE PROCEDURE public.d_district_update();

CREATE OR REPLACE FUNCTION public.d_district_propagate_updates ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS __tmp_d_district_trigger_delta_action_ins, __tmp_d_district_trigger_delta_action_del IMMEDIATE;
    SET CONSTRAINTS __tmp_d_district_trigger_delta_action_ins, __tmp_d_district_trigger_delta_action_del DEFERRED;
    DROP TABLE IF EXISTS d_district_delta_action_flag;
    DROP TABLE IF EXISTS __tmp_delta_del_d_district;
    DROP TABLE IF EXISTS __tmp_delta_ins_d_district;
    RETURN true;
  END;
$$;

CREATE OR REPLACE FUNCTION public.district_propagates_to_d_district(txid int)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    DELETE FROM public.__dummy__d_district_detected_deletions t where t.txid = $1;
    DELETE FROM public.__dummy__d_district_detected_insertions t where t.txid = $1;
    PERFORM public.district_propagate_updates_to_d_district();
    RETURN true;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d_district_propagate(txid int)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    DELETE FROM public.__dummy__d_district_detected_deletions t where t.txid = $1;
    DELETE FROM public.__dummy__d_district_detected_insertions t where t.txid = $1;
    PERFORM public.d_district_propagate_updates();
    RETURN true;
  END;
$$;

CREATE OR REPLACE FUNCTION public.remove_dummy_d_district(txid int)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    DELETE FROM public.__dummy__d_district_detected_deletions t where t.txid = $1;
    DELETE FROM public.__dummy__d_district_detected_insertions t where t.txid = $1;
    RETURN true;
  END;
$$;
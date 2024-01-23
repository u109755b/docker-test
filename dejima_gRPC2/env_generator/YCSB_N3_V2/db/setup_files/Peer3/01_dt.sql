CREATE OR REPLACE VIEW public.dt AS 
SELECT __dummy__.COL0 AS ID, __dummy__.COL1 AS COL1, __dummy__.COL2 AS COL2, __dummy__.COL3 AS COL3, __dummy__.COL4 AS COL4, __dummy__.COL5 AS COL5, __dummy__.COL6 AS COL6, __dummy__.COL7 AS COL7, __dummy__.COL8 AS COL8, __dummy__.COL9 AS COL9, __dummy__.COL10 AS COL10, __dummy__.COL11 AS LINEAGE FROM (SELECT dt_a12_0.COL0 AS COL0, dt_a12_0.COL1 AS COL1, dt_a12_0.COL2 AS COL2, dt_a12_0.COL3 AS COL3, dt_a12_0.COL4 AS COL4, dt_a12_0.COL5 AS COL5, dt_a12_0.COL6 AS COL6, dt_a12_0.COL7 AS COL7, dt_a12_0.COL8 AS COL8, dt_a12_0.COL9 AS COL9, dt_a12_0.COL10 AS COL10, dt_a12_0.COL11 AS COL11 FROM (SELECT bt_a12_0.ID AS COL0, bt_a12_0.COL1 AS COL1, bt_a12_0.COL2 AS COL2, bt_a12_0.COL3 AS COL3, bt_a12_0.COL4 AS COL4, bt_a12_0.COL5 AS COL5, bt_a12_0.COL6 AS COL6, bt_a12_0.COL7 AS COL7, bt_a12_0.COL8 AS COL8, bt_a12_0.COL9 AS COL9, bt_a12_0.COL10 AS COL10, bt_a12_0.LINEAGE AS COL11 FROM public.bt AS bt_a12_0   ) AS dt_a12_0   ) AS __dummy__   ;

CREATE EXTENSION IF NOT EXISTS plsh;

CREATE TABLE IF NOT EXISTS public.__dummy__dt_detected_deletions (txid int, LIKE public.dt );
CREATE INDEX IF NOT EXISTS idx__dummy__dt_detected_deletions ON public.__dummy__dt_detected_deletions (txid);
CREATE TABLE IF NOT EXISTS public.__dummy__dt_detected_insertions (txid int, LIKE public.dt );
CREATE INDEX IF NOT EXISTS idx__dummy__dt_detected_insertions ON public.__dummy__dt_detected_insertions (txid);

CREATE OR REPLACE FUNCTION public.dt_get_detected_update_data(txid int)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  deletion_data text;
  insertion_data text;
  json_data text;
  BEGIN
    insertion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__dt_detected_insertions as t where t.txid = $1);
    IF insertion_data IS NOT DISTINCT FROM NULL THEN
        insertion_data := '[]';
    END IF;
    deletion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__dt_detected_deletions as t where t.txid = $1);
    IF deletion_data IS NOT DISTINCT FROM NULL THEN
        deletion_data := '[]';
    END IF;
    IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN
        -- calcuate the update data
        json_data := concat('{"view": ' , '"public.dt"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
        -- clear the update data
        DELETE FROM public.__dummy__dt_detected_deletions t where t.txid = $1;
        DELETE FROM public.__dummy__dt_detected_insertions t where t.txid = $1;
    END IF;
    RETURN json_data;
  END;
$$;

CREATE OR REPLACE FUNCTION public.dt_run_shell(text) RETURNS text AS $$
#!/bin/sh

result=$(curl -s -X POST -H "Content-Type: application/json" $DEJIMA_EXECUTION_ENDPOINT -d "$1")
if  [ "$result" = "true" ];  then
    echo "true"
else 
    echo $result
fi
$$ LANGUAGE plsh;

CREATE OR REPLACE FUNCTION public.bt_materialization_for_dt()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_bt_for_dt' OR table_name = '__tmp_delta_del_bt_for_dt')
    THEN
        -- RAISE LOG 'execute procedure bt_materialization_for_dt';
        CREATE TEMPORARY TABLE __tmp_delta_ins_bt_for_dt ( LIKE public.bt ) WITH OIDS ON COMMIT DROP;
        CREATE TEMPORARY TABLE __tmp_delta_del_bt_for_dt ( LIKE public.bt ) WITH OIDS ON COMMIT DROP;

    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.bt';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.bt ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS bt_trigger_materialization_for_dt ON public.bt;
CREATE TRIGGER bt_trigger_materialization_for_dt
    BEFORE INSERT OR UPDATE OR DELETE ON
    public.bt FOR EACH STATEMENT EXECUTE PROCEDURE public.bt_materialization_for_dt();

CREATE OR REPLACE FUNCTION public.bt_update_for_dt()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    -- RAISE LOG 'execute procedure bt_update_for_dt';
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'dt_delta_action_flag') THEN
        IF TG_OP = 'INSERT' THEN
        -- RAISE LOG 'NEW: %', NEW;
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_del_bt_for_dt WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE)= NEW;
        INSERT INTO __tmp_delta_ins_bt_for_dt SELECT (NEW).*;
        ELSIF TG_OP = 'UPDATE' THEN
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_ins_bt_for_dt WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE) = OLD;
        INSERT INTO __tmp_delta_del_bt_for_dt SELECT (OLD).*;
        DELETE FROM __tmp_delta_del_bt_for_dt WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE) = NEW;
        INSERT INTO __tmp_delta_ins_bt_for_dt SELECT (NEW).*;
        ELSIF TG_OP = 'DELETE' THEN
        -- RAISE LOG 'OLD: %', OLD;
        DELETE FROM __tmp_delta_ins_bt_for_dt WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE) = OLD;
        INSERT INTO __tmp_delta_del_bt_for_dt SELECT (OLD).*;
        END IF;
    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.bt';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.bt ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS bt_trigger_update_for_dt ON public.bt;
CREATE TRIGGER bt_trigger_update_for_dt
    AFTER INSERT OR UPDATE OR DELETE ON
    public.bt FOR EACH ROW EXECUTE PROCEDURE public.bt_update_for_dt();

CREATE OR REPLACE FUNCTION public.bt_detect_update_on_dt()
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
array_delta_del public.bt[];
array_delta_ins public.bt[];
detected_deletions public.dt[];
detected_insertions public.dt[];
delta_ins_size int;
delta_del_size int;
BEGIN
IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'bt_detect_update_on_dt_flag') THEN
    CREATE TEMPORARY TABLE bt_detect_update_on_dt_flag ON COMMIT DROP AS (SELECT true as finish);
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'dt_delta_action_flag') THEN
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_bt_for_dt AS tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_bt_for_dt;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_bt_for_dt tbl;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_bt_for_dt;

        WITH __tmp_delta_ins_bt_for_dt_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size),
        __tmp_delta_del_bt_for_dt_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_insertions FROM (SELECT __dummy__.COL0 AS ID, __dummy__.COL1 AS COL1, __dummy__.COL2 AS COL2, __dummy__.COL3 AS COL3, __dummy__.COL4 AS COL4, __dummy__.COL5 AS COL5, __dummy__.COL6 AS COL6, __dummy__.COL7 AS COL7, __dummy__.COL8 AS COL8, __dummy__.COL9 AS COL9, __dummy__.COL10 AS COL10, __dummy__.COL11 AS LINEAGE FROM (SELECT part_ins_dt_a12_0.COL0 AS COL0, part_ins_dt_a12_0.COL1 AS COL1, part_ins_dt_a12_0.COL2 AS COL2, part_ins_dt_a12_0.COL3 AS COL3, part_ins_dt_a12_0.COL4 AS COL4, part_ins_dt_a12_0.COL5 AS COL5, part_ins_dt_a12_0.COL6 AS COL6, part_ins_dt_a12_0.COL7 AS COL7, part_ins_dt_a12_0.COL8 AS COL8, part_ins_dt_a12_0.COL9 AS COL9, part_ins_dt_a12_0.COL10 AS COL10, part_ins_dt_a12_0.COL11 AS COL11 FROM (SELECT p_0_a12_0.COL0 AS COL0, p_0_a12_0.COL1 AS COL1, p_0_a12_0.COL2 AS COL2, p_0_a12_0.COL3 AS COL3, p_0_a12_0.COL4 AS COL4, p_0_a12_0.COL5 AS COL5, p_0_a12_0.COL6 AS COL6, p_0_a12_0.COL7 AS COL7, p_0_a12_0.COL8 AS COL8, p_0_a12_0.COL9 AS COL9, p_0_a12_0.COL10 AS COL10, p_0_a12_0.COL11 AS COL11 FROM (SELECT __tmp_delta_ins_bt_for_dt_ar_a12_0.ID AS COL0, __tmp_delta_ins_bt_for_dt_ar_a12_0.COL1 AS COL1, __tmp_delta_ins_bt_for_dt_ar_a12_0.COL2 AS COL2, __tmp_delta_ins_bt_for_dt_ar_a12_0.COL3 AS COL3, __tmp_delta_ins_bt_for_dt_ar_a12_0.COL4 AS COL4, __tmp_delta_ins_bt_for_dt_ar_a12_0.COL5 AS COL5, __tmp_delta_ins_bt_for_dt_ar_a12_0.COL6 AS COL6, __tmp_delta_ins_bt_for_dt_ar_a12_0.COL7 AS COL7, __tmp_delta_ins_bt_for_dt_ar_a12_0.COL8 AS COL8, __tmp_delta_ins_bt_for_dt_ar_a12_0.COL9 AS COL9, __tmp_delta_ins_bt_for_dt_ar_a12_0.COL10 AS COL10, __tmp_delta_ins_bt_for_dt_ar_a12_0.LINEAGE AS COL11 FROM __tmp_delta_ins_bt_for_dt_ar AS __tmp_delta_ins_bt_for_dt_ar_a12_0   ) AS p_0_a12_0   ) AS part_ins_dt_a12_0   ) AS __dummy__   ) AS tbl;

        insertion_data := (SELECT (array_to_json(detected_insertions))::text);
        IF insertion_data IS NOT DISTINCT FROM NULL THEN
            insertion_data := '[]';
        END IF;

        WITH __tmp_delta_ins_bt_for_dt_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size),
        __tmp_delta_del_bt_for_dt_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_deletions FROM (SELECT __dummy__.COL0 AS ID, __dummy__.COL1 AS COL1, __dummy__.COL2 AS COL2, __dummy__.COL3 AS COL3, __dummy__.COL4 AS COL4, __dummy__.COL5 AS COL5, __dummy__.COL6 AS COL6, __dummy__.COL7 AS COL7, __dummy__.COL8 AS COL8, __dummy__.COL9 AS COL9, __dummy__.COL10 AS COL10, __dummy__.COL11 AS LINEAGE FROM (SELECT part_del_dt_a12_0.COL0 AS COL0, part_del_dt_a12_0.COL1 AS COL1, part_del_dt_a12_0.COL2 AS COL2, part_del_dt_a12_0.COL3 AS COL3, part_del_dt_a12_0.COL4 AS COL4, part_del_dt_a12_0.COL5 AS COL5, part_del_dt_a12_0.COL6 AS COL6, part_del_dt_a12_0.COL7 AS COL7, part_del_dt_a12_0.COL8 AS COL8, part_del_dt_a12_0.COL9 AS COL9, part_del_dt_a12_0.COL10 AS COL10, part_del_dt_a12_0.COL11 AS COL11 FROM (SELECT p_0_a12_0.COL0 AS COL0, p_0_a12_0.COL1 AS COL1, p_0_a12_0.COL2 AS COL2, p_0_a12_0.COL3 AS COL3, p_0_a12_0.COL4 AS COL4, p_0_a12_0.COL5 AS COL5, p_0_a12_0.COL6 AS COL6, p_0_a12_0.COL7 AS COL7, p_0_a12_0.COL8 AS COL8, p_0_a12_0.COL9 AS COL9, p_0_a12_0.COL10 AS COL10, p_0_a12_0.COL11 AS COL11 FROM (SELECT __tmp_delta_del_bt_for_dt_ar_a12_0.ID AS COL0, __tmp_delta_del_bt_for_dt_ar_a12_0.COL1 AS COL1, __tmp_delta_del_bt_for_dt_ar_a12_0.COL2 AS COL2, __tmp_delta_del_bt_for_dt_ar_a12_0.COL3 AS COL3, __tmp_delta_del_bt_for_dt_ar_a12_0.COL4 AS COL4, __tmp_delta_del_bt_for_dt_ar_a12_0.COL5 AS COL5, __tmp_delta_del_bt_for_dt_ar_a12_0.COL6 AS COL6, __tmp_delta_del_bt_for_dt_ar_a12_0.COL7 AS COL7, __tmp_delta_del_bt_for_dt_ar_a12_0.COL8 AS COL8, __tmp_delta_del_bt_for_dt_ar_a12_0.COL9 AS COL9, __tmp_delta_del_bt_for_dt_ar_a12_0.COL10 AS COL10, __tmp_delta_del_bt_for_dt_ar_a12_0.LINEAGE AS COL11 FROM __tmp_delta_del_bt_for_dt_ar AS __tmp_delta_del_bt_for_dt_ar_a12_0   ) AS p_0_a12_0   ) AS part_del_dt_a12_0   ) AS __dummy__   ) AS tbl;

        deletion_data := (
        SELECT (array_to_json(detected_deletions))::text);
        IF deletion_data IS NOT DISTINCT FROM NULL THEN
            deletion_data := '[]';
        END IF;
        IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN
            user_name := (SELECT session_user);
            IF NOT (user_name = 'dejima') THEN
                xid := (SELECT txid_current());
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.dt"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.dt_run_shell(json_data);
                IF result = 'true' THEN
                    DROP TABLE __tmp_delta_ins_bt_for_dt;
                    DROP TABLE __tmp_delta_del_bt_for_dt;
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
                -- DELETE FROM public.__dummy__dt_detected_deletions;
                INSERT INTO public.__dummy__dt_detected_deletions
                    ( SELECT xid, * FROM unnest(detected_deletions) as detected_deletions_alias );

                -- DELETE FROM public.__dummy__dt_detected_insertions;
                INSERT INTO public.__dummy__dt_detected_insertions
                    ( SELECT xid, * FROM unnest(detected_insertions) as detected_insertions_alias );
            END IF;
        END IF;
    END IF;
END IF;
RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.bt';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the function public.bt_detect_update_on_dt() ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS bt_detect_update_on_dt ON public.bt;
CREATE CONSTRAINT TRIGGER bt_detect_update_on_dt
    AFTER INSERT OR UPDATE OR DELETE ON
    public.bt DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.bt_detect_update_on_dt();

CREATE OR REPLACE FUNCTION public.bt_propagate_updates_to_dt ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS public.bt_detect_update_on_dt IMMEDIATE;
    SET CONSTRAINTS public.bt_detect_update_on_dt DEFERRED;
    DROP TABLE IF EXISTS bt_detect_update_on_dt_flag;
    DROP TABLE IF EXISTS __tmp_delta_del_bt_for_dt;
    DROP TABLE IF EXISTS __tmp_delta_ins_bt_for_dt;
    RETURN true;
  END;
$$;



CREATE OR REPLACE FUNCTION public.dt_delta_action()
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
  array_delta_del public.dt[];
  array_delta_ins public.dt[];
  temprec_delta_del_bt public.bt%ROWTYPE;
            array_delta_del_bt public.bt[];
temprec_delta_ins_bt public.bt%ROWTYPE;
            array_delta_ins_bt public.bt[];
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'dt_delta_action_flag') THEN
        -- RAISE LOG 'execute procedure dt_delta_action';
        CREATE TEMPORARY TABLE dt_delta_action_flag ON COMMIT DROP AS (SELECT true as finish);
        IF EXISTS (SELECT WHERE false )
        THEN
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the view are violated';
        END IF;
        IF EXISTS (SELECT WHERE false )
        THEN
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the source relations are violated';
        END IF;
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_dt AS tbl;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_dt as tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_dt;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_dt;
        
            WITH __tmp_delta_del_dt_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_dt_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_del_bt FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11) :: public.bt).*
            FROM (SELECT delta_del_bt_a12_0.COL0 AS COL0, delta_del_bt_a12_0.COL1 AS COL1, delta_del_bt_a12_0.COL2 AS COL2, delta_del_bt_a12_0.COL3 AS COL3, delta_del_bt_a12_0.COL4 AS COL4, delta_del_bt_a12_0.COL5 AS COL5, delta_del_bt_a12_0.COL6 AS COL6, delta_del_bt_a12_0.COL7 AS COL7, delta_del_bt_a12_0.COL8 AS COL8, delta_del_bt_a12_0.COL9 AS COL9, delta_del_bt_a12_0.COL10 AS COL10, delta_del_bt_a12_0.COL11 AS COL11 FROM (SELECT p_0_a12_0.COL0 AS COL0, p_0_a12_0.COL1 AS COL1, p_0_a12_0.COL2 AS COL2, p_0_a12_0.COL3 AS COL3, p_0_a12_0.COL4 AS COL4, p_0_a12_0.COL5 AS COL5, p_0_a12_0.COL6 AS COL6, p_0_a12_0.COL7 AS COL7, p_0_a12_0.COL8 AS COL8, p_0_a12_0.COL9 AS COL9, p_0_a12_0.COL10 AS COL10, p_0_a12_0.COL11 AS COL11 FROM (SELECT bt_a12_1.ID AS COL0, bt_a12_1.COL1 AS COL1, bt_a12_1.COL2 AS COL2, bt_a12_1.COL3 AS COL3, bt_a12_1.COL4 AS COL4, bt_a12_1.COL5 AS COL5, bt_a12_1.COL6 AS COL6, bt_a12_1.COL7 AS COL7, bt_a12_1.COL8 AS COL8, bt_a12_1.COL9 AS COL9, bt_a12_1.COL10 AS COL10, bt_a12_1.LINEAGE AS COL11 FROM __tmp_delta_del_dt_ar AS __tmp_delta_del_dt_ar_a12_0, public.bt AS bt_a12_1 WHERE bt_a12_1.COL7 = __tmp_delta_del_dt_ar_a12_0.COL7 AND bt_a12_1.COL5 = __tmp_delta_del_dt_ar_a12_0.COL5 AND bt_a12_1.COL2 = __tmp_delta_del_dt_ar_a12_0.COL2 AND bt_a12_1.COL6 = __tmp_delta_del_dt_ar_a12_0.COL6 AND bt_a12_1.COL10 = __tmp_delta_del_dt_ar_a12_0.COL10 AND bt_a12_1.COL1 = __tmp_delta_del_dt_ar_a12_0.COL1 AND bt_a12_1.COL3 = __tmp_delta_del_dt_ar_a12_0.COL3 AND bt_a12_1.COL8 = __tmp_delta_del_dt_ar_a12_0.COL8 AND bt_a12_1.LINEAGE = __tmp_delta_del_dt_ar_a12_0.LINEAGE AND bt_a12_1.COL9 = __tmp_delta_del_dt_ar_a12_0.COL9 AND bt_a12_1.ID = __tmp_delta_del_dt_ar_a12_0.ID AND bt_a12_1.COL4 = __tmp_delta_del_dt_ar_a12_0.COL4  ) AS p_0_a12_0   ) AS delta_del_bt_a12_0   ) AS delta_del_bt_extra_alias) AS tbl;


            WITH __tmp_delta_del_dt_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_dt_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_ins_bt FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11) :: public.bt).*
            FROM (SELECT delta_ins_bt_a12_0.COL0 AS COL0, delta_ins_bt_a12_0.COL1 AS COL1, delta_ins_bt_a12_0.COL2 AS COL2, delta_ins_bt_a12_0.COL3 AS COL3, delta_ins_bt_a12_0.COL4 AS COL4, delta_ins_bt_a12_0.COL5 AS COL5, delta_ins_bt_a12_0.COL6 AS COL6, delta_ins_bt_a12_0.COL7 AS COL7, delta_ins_bt_a12_0.COL8 AS COL8, delta_ins_bt_a12_0.COL9 AS COL9, delta_ins_bt_a12_0.COL10 AS COL10, delta_ins_bt_a12_0.COL11 AS COL11 FROM (SELECT p_0_a12_0.COL0 AS COL0, p_0_a12_0.COL1 AS COL1, p_0_a12_0.COL2 AS COL2, p_0_a12_0.COL3 AS COL3, p_0_a12_0.COL4 AS COL4, p_0_a12_0.COL5 AS COL5, p_0_a12_0.COL6 AS COL6, p_0_a12_0.COL7 AS COL7, p_0_a12_0.COL8 AS COL8, p_0_a12_0.COL9 AS COL9, p_0_a12_0.COL10 AS COL10, p_0_a12_0.COL11 AS COL11 FROM (SELECT __tmp_delta_ins_dt_ar_a12_0.ID AS COL0, __tmp_delta_ins_dt_ar_a12_0.COL1 AS COL1, __tmp_delta_ins_dt_ar_a12_0.COL2 AS COL2, __tmp_delta_ins_dt_ar_a12_0.COL3 AS COL3, __tmp_delta_ins_dt_ar_a12_0.COL4 AS COL4, __tmp_delta_ins_dt_ar_a12_0.COL5 AS COL5, __tmp_delta_ins_dt_ar_a12_0.COL6 AS COL6, __tmp_delta_ins_dt_ar_a12_0.COL7 AS COL7, __tmp_delta_ins_dt_ar_a12_0.COL8 AS COL8, __tmp_delta_ins_dt_ar_a12_0.COL9 AS COL9, __tmp_delta_ins_dt_ar_a12_0.COL10 AS COL10, __tmp_delta_ins_dt_ar_a12_0.LINEAGE AS COL11 FROM __tmp_delta_ins_dt_ar AS __tmp_delta_ins_dt_ar_a12_0 WHERE NOT EXISTS ( SELECT * FROM public.bt AS bt_a12 WHERE bt_a12.LINEAGE = __tmp_delta_ins_dt_ar_a12_0.LINEAGE AND bt_a12.COL10 = __tmp_delta_ins_dt_ar_a12_0.COL10 AND bt_a12.COL9 = __tmp_delta_ins_dt_ar_a12_0.COL9 AND bt_a12.COL8 = __tmp_delta_ins_dt_ar_a12_0.COL8 AND bt_a12.COL7 = __tmp_delta_ins_dt_ar_a12_0.COL7 AND bt_a12.COL6 = __tmp_delta_ins_dt_ar_a12_0.COL6 AND bt_a12.COL5 = __tmp_delta_ins_dt_ar_a12_0.COL5 AND bt_a12.COL4 = __tmp_delta_ins_dt_ar_a12_0.COL4 AND bt_a12.COL3 = __tmp_delta_ins_dt_ar_a12_0.COL3 AND bt_a12.COL2 = __tmp_delta_ins_dt_ar_a12_0.COL2 AND bt_a12.COL1 = __tmp_delta_ins_dt_ar_a12_0.COL1 AND bt_a12.ID = __tmp_delta_ins_dt_ar_a12_0.ID )  ) AS p_0_a12_0   ) AS delta_ins_bt_a12_0   ) AS delta_ins_bt_extra_alias) AS tbl; 


            IF array_delta_del_bt IS DISTINCT FROM NULL THEN
                FOREACH temprec_delta_del_bt IN array array_delta_del_bt  LOOP
                   DELETE FROM public.bt WHERE ID = temprec_delta_del_bt.ID AND COL1 = temprec_delta_del_bt.COL1 AND COL2 = temprec_delta_del_bt.COL2 AND COL3 = temprec_delta_del_bt.COL3 AND COL4 = temprec_delta_del_bt.COL4 AND COL5 = temprec_delta_del_bt.COL5 AND COL6 = temprec_delta_del_bt.COL6 AND COL7 = temprec_delta_del_bt.COL7 AND COL8 = temprec_delta_del_bt.COL8 AND COL9 = temprec_delta_del_bt.COL9 AND COL10 = temprec_delta_del_bt.COL10 AND LINEAGE = temprec_delta_del_bt.LINEAGE;
                END LOOP;
            END IF;


            IF array_delta_ins_bt IS DISTINCT FROM NULL THEN
                INSERT INTO public.bt (SELECT * FROM unnest(array_delta_ins_bt) as array_delta_ins_bt_alias) ;
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
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.dt"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.dt_run_shell(json_data);
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
                --DELETE FROM public.__dummy__dt_detected_deletions;
                INSERT INTO public.__dummy__dt_detected_deletions
                    SELECT xid, * FROM __tmp_delta_del_dt;

                --DELETE FROM public.__dummy__dt_detected_insertions;
                INSERT INTO public.__dummy__dt_detected_insertions
                    SELECT xid, * FROM __tmp_delta_ins_dt;
            END IF;
        END IF;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.dt';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.dt ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

CREATE OR REPLACE FUNCTION public.dt_materialization()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_dt' OR table_name = '__tmp_delta_del_dt')
    THEN
        -- RAISE LOG 'execute procedure dt_materialization';
        CREATE TEMPORARY TABLE __tmp_delta_ins_dt ( LIKE public.dt ) WITH OIDS ON COMMIT DROP;
        CREATE CONSTRAINT TRIGGER __tmp_dt_trigger_delta_action_ins
        AFTER INSERT OR UPDATE OR DELETE ON
            __tmp_delta_ins_dt DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW EXECUTE PROCEDURE public.dt_delta_action();

        CREATE TEMPORARY TABLE __tmp_delta_del_dt ( LIKE public.dt ) WITH OIDS ON COMMIT DROP;
        CREATE CONSTRAINT TRIGGER __tmp_dt_trigger_delta_action_del
        AFTER INSERT OR UPDATE OR DELETE ON
            __tmp_delta_del_dt DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW EXECUTE PROCEDURE public.dt_delta_action();
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.dt';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.dt ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS dt_trigger_materialization ON public.dt;
CREATE TRIGGER dt_trigger_materialization
    BEFORE INSERT OR UPDATE OR DELETE ON
      public.dt FOR EACH STATEMENT EXECUTE PROCEDURE public.dt_materialization();

CREATE OR REPLACE FUNCTION public.dt_update()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    -- RAISE LOG 'execute procedure dt_update';
    IF TG_OP = 'INSERT' THEN
      -- RAISE LOG 'NEW: %', NEW;
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_del_dt WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE) = NEW;
      INSERT INTO __tmp_delta_ins_dt SELECT (NEW).*;
    ELSIF TG_OP = 'UPDATE' THEN
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_ins_dt WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE) = OLD;
      INSERT INTO __tmp_delta_del_dt SELECT (OLD).*;
      DELETE FROM __tmp_delta_del_dt WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE) = NEW;
      INSERT INTO __tmp_delta_ins_dt SELECT (NEW).*;
    ELSIF TG_OP = 'DELETE' THEN
      -- RAISE LOG 'OLD: %', OLD;
      DELETE FROM __tmp_delta_ins_dt WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE) = OLD;
      INSERT INTO __tmp_delta_del_dt SELECT (OLD).*;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.dt';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.dt ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS dt_trigger_update ON public.dt;
CREATE TRIGGER dt_trigger_update
    INSTEAD OF INSERT OR UPDATE OR DELETE ON
      public.dt FOR EACH ROW EXECUTE PROCEDURE public.dt_update();

CREATE OR REPLACE FUNCTION public.dt_propagate_updates ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS __tmp_dt_trigger_delta_action_ins, __tmp_dt_trigger_delta_action_del IMMEDIATE;
    SET CONSTRAINTS __tmp_dt_trigger_delta_action_ins, __tmp_dt_trigger_delta_action_del DEFERRED;
    DROP TABLE IF EXISTS dt_delta_action_flag;
    DROP TABLE IF EXISTS __tmp_delta_del_dt;
    DROP TABLE IF EXISTS __tmp_delta_ins_dt;
    RETURN true;
  END;
$$;


CREATE OR REPLACE VIEW public.d2_10 AS 
SELECT __dummy__.COL0 AS V, __dummy__.COL1 AS L, __dummy__.COL2 AS D, __dummy__.COL3 AS R, __dummy__.COL4 AS P, __dummy__.COL5 AS LINEAGE, __dummy__.COL6 AS COND1, __dummy__.COL7 AS COND2, __dummy__.COL8 AS COND3, __dummy__.COL9 AS COND4, __dummy__.COL10 AS COND5, __dummy__.COL11 AS COND6, __dummy__.COL12 AS COND7, __dummy__.COL13 AS COND8, __dummy__.COL14 AS COND9, __dummy__.COL15 AS COND10 
FROM (SELECT d2_10_a16_0.COL0 AS COL0, d2_10_a16_0.COL1 AS COL1, d2_10_a16_0.COL2 AS COL2, d2_10_a16_0.COL3 AS COL3, d2_10_a16_0.COL4 AS COL4, d2_10_a16_0.COL5 AS COL5, d2_10_a16_0.COL6 AS COL6, d2_10_a16_0.COL7 AS COL7, d2_10_a16_0.COL8 AS COL8, d2_10_a16_0.COL9 AS COL9, d2_10_a16_0.COL10 AS COL10, d2_10_a16_0.COL11 AS COL11, d2_10_a16_0.COL12 AS COL12, d2_10_a16_0.COL13 AS COL13, d2_10_a16_0.COL14 AS COL14, d2_10_a16_0.COL15 AS COL15 
FROM (SELECT mt_a16_0.V AS COL0, mt_a16_0.L AS COL1, mt_a16_0.D AS COL2, mt_a16_0.R AS COL3, mt_a16_0.P AS COL4, mt_a16_0.LINEAGE AS COL5, mt_a16_0.COND1 AS COL6, mt_a16_0.COND2 AS COL7, mt_a16_0.COND3 AS COL8, mt_a16_0.COND4 AS COL9, mt_a16_0.COND5 AS COL10, mt_a16_0.COND6 AS COL11, mt_a16_0.COND7 AS COL12, mt_a16_0.COND8 AS COL13, mt_a16_0.COND9 AS COL14, mt_a16_0.COND10 AS COL15 
FROM public.mt AS mt_a16_0 
WHERE mt_a16_0.COND2  <  80 ) AS d2_10_a16_0  ) AS __dummy__;

CREATE EXTENSION IF NOT EXISTS plsh;

CREATE TABLE IF NOT EXISTS public.__dummy__d2_10_detected_deletions (txid int, LIKE public.d2_10 );
CREATE INDEX IF NOT EXISTS idx__dummy__d2_10_detected_deletions ON public.__dummy__d2_10_detected_deletions (txid);
CREATE TABLE IF NOT EXISTS public.__dummy__d2_10_detected_insertions (txid int, LIKE public.d2_10 );
CREATE INDEX IF NOT EXISTS idx__dummy__d2_10_detected_insertions ON public.__dummy__d2_10_detected_insertions (txid);

CREATE OR REPLACE FUNCTION public.d2_10_get_detected_update_data(txid int)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  deletion_data text;
  insertion_data text;
  json_data text;
  BEGIN
    insertion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__d2_10_detected_insertions as t where t.txid = $1);
    IF insertion_data IS NOT DISTINCT FROM NULL THEN 
        insertion_data := '[]';
    END IF; 
    deletion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__d2_10_detected_deletions as t where t.txid = $1);
    IF deletion_data IS NOT DISTINCT FROM NULL THEN 
        deletion_data := '[]';
    END IF; 
    IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN 
        -- calcuate the update data
        json_data := concat('{"view": ' , '"public.d2_10"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
        -- clear the update data
        --DELETE FROM public.__dummy__d2_10_detected_deletions;
        --DELETE FROM public.__dummy__d2_10_detected_insertions;
    END IF;
    RETURN json_data;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d2_10_run_shell(text) RETURNS text AS $$
#!/bin/sh

result=$(curl -s -X POST -H "Content-Type: application/json" $DEJIMA_API_ENDPOINT -d "$1")
# echo  "`date`: there is an update on the dejima view: $1" >> /tmp/dejima.txt
# result="true"
if  [ "$result" = "true" ];  then
    echo "true"
else 
    echo $result
    exit 1
fi
$$ LANGUAGE plsh;

CREATE OR REPLACE FUNCTION public.mt_materialization_for_d2_10()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_mt_for_d2_10' OR table_name = '__tmp_delta_del_mt_for_d2_10')
    THEN
        -- RAISE LOG 'execute procedure mt_materialization_for_d2_10';
        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_ins_mt_for_d2_10 ( LIKE public.mt ) WITH OIDS ON COMMIT DELETE ROWS;
        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_del_mt_for_d2_10 ( LIKE public.mt ) WITH OIDS ON COMMIT DELETE ROWS;
        
    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.mt';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.mt ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS mt_trigger_materialization_for_d2_10 ON public.mt;
CREATE TRIGGER mt_trigger_materialization_for_d2_10
    BEFORE INSERT OR UPDATE OR DELETE ON
    public.mt FOR EACH STATEMENT EXECUTE PROCEDURE public.mt_materialization_for_d2_10();

CREATE OR REPLACE FUNCTION public.mt_update_for_d2_10()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    -- RAISE LOG 'execute procedure mt_update_for_d2_10';
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd2_10_delta_action_flag') THEN
        IF TG_OP = 'INSERT' THEN
        -- RAISE LOG 'NEW: %', NEW;
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_del_mt_for_d2_10 WHERE ROW(V,L,D,R,P,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = NEW;
        INSERT INTO __tmp_delta_ins_mt_for_d2_10 SELECT (NEW).*; 
        ELSIF TG_OP = 'UPDATE' THEN
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_ins_mt_for_d2_10 WHERE ROW(V,L,D,R,P,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = OLD;
        INSERT INTO __tmp_delta_del_mt_for_d2_10 SELECT (OLD).*;
        DELETE FROM __tmp_delta_del_mt_for_d2_10 WHERE ROW(V,L,D,R,P,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = NEW;
        INSERT INTO __tmp_delta_ins_mt_for_d2_10 SELECT (NEW).*; 
        ELSIF TG_OP = 'DELETE' THEN
        -- RAISE LOG 'OLD: %', OLD;
        DELETE FROM __tmp_delta_ins_mt_for_d2_10 WHERE ROW(V,L,D,R,P,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = OLD;
        INSERT INTO __tmp_delta_del_mt_for_d2_10 SELECT (OLD).*;
        END IF;
    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.mt';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.mt ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS mt_trigger_update_for_d2_10 ON public.mt;
CREATE TRIGGER mt_trigger_update_for_d2_10
    AFTER INSERT OR UPDATE OR DELETE ON
    public.mt FOR EACH ROW EXECUTE PROCEDURE public.mt_update_for_d2_10();

CREATE OR REPLACE FUNCTION public.mt_detect_update_on_d2_10()
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
array_delta_del public.mt[];
array_delta_ins public.mt[];
detected_deletions public.d2_10[];
detected_insertions public.d2_10[];
delta_ins_size int;
delta_del_size int;
BEGIN
IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'mt_detect_update_on_d2_10_flag') THEN
    CREATE TEMPORARY TABLE mt_detect_update_on_d2_10_flag ON COMMIT DROP AS (SELECT true as finish);
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd2_10_delta_action_flag') THEN
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_mt_for_d2_10 AS tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_mt_for_d2_10;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_mt_for_d2_10 tbl;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_mt_for_d2_10;

        WITH __tmp_delta_ins_mt_for_d2_10_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size), 
        __tmp_delta_del_mt_for_d2_10_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_insertions FROM (SELECT __dummy__.COL0 AS V, __dummy__.COL1 AS L, __dummy__.COL2 AS D, __dummy__.COL3 AS R, __dummy__.COL4 AS P, __dummy__.COL5 AS LINEAGE, __dummy__.COL6 AS COND1, __dummy__.COL7 AS COND2, __dummy__.COL8 AS COND3, __dummy__.COL9 AS COND4, __dummy__.COL10 AS COND5, __dummy__.COL11 AS COND6, __dummy__.COL12 AS COND7, __dummy__.COL13 AS COND8, __dummy__.COL14 AS COND9, __dummy__.COL15 AS COND10 
FROM (SELECT part_ins_d2_10_a16_0.COL0 AS COL0, part_ins_d2_10_a16_0.COL1 AS COL1, part_ins_d2_10_a16_0.COL2 AS COL2, part_ins_d2_10_a16_0.COL3 AS COL3, part_ins_d2_10_a16_0.COL4 AS COL4, part_ins_d2_10_a16_0.COL5 AS COL5, part_ins_d2_10_a16_0.COL6 AS COL6, part_ins_d2_10_a16_0.COL7 AS COL7, part_ins_d2_10_a16_0.COL8 AS COL8, part_ins_d2_10_a16_0.COL9 AS COL9, part_ins_d2_10_a16_0.COL10 AS COL10, part_ins_d2_10_a16_0.COL11 AS COL11, part_ins_d2_10_a16_0.COL12 AS COL12, part_ins_d2_10_a16_0.COL13 AS COL13, part_ins_d2_10_a16_0.COL14 AS COL14, part_ins_d2_10_a16_0.COL15 AS COL15 
FROM (SELECT p_0_a16_0.COL0 AS COL0, p_0_a16_0.COL1 AS COL1, p_0_a16_0.COL2 AS COL2, p_0_a16_0.COL3 AS COL3, p_0_a16_0.COL4 AS COL4, p_0_a16_0.COL5 AS COL5, p_0_a16_0.COL6 AS COL6, p_0_a16_0.COL7 AS COL7, p_0_a16_0.COL8 AS COL8, p_0_a16_0.COL9 AS COL9, p_0_a16_0.COL10 AS COL10, p_0_a16_0.COL11 AS COL11, p_0_a16_0.COL12 AS COL12, p_0_a16_0.COL13 AS COL13, p_0_a16_0.COL14 AS COL14, p_0_a16_0.COL15 AS COL15 
FROM (SELECT __tmp_delta_ins_mt_for_d2_10_ar_a16_0.V AS COL0, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.L AS COL1, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.D AS COL2, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.R AS COL3, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.P AS COL4, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.LINEAGE AS COL5, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.COND1 AS COL6, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.COND2 AS COL7, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.COND3 AS COL8, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.COND4 AS COL9, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.COND5 AS COL10, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.COND6 AS COL11, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.COND7 AS COL12, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.COND8 AS COL13, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.COND9 AS COL14, __tmp_delta_ins_mt_for_d2_10_ar_a16_0.COND10 AS COL15 
FROM __tmp_delta_ins_mt_for_d2_10_ar AS __tmp_delta_ins_mt_for_d2_10_ar_a16_0 
WHERE __tmp_delta_ins_mt_for_d2_10_ar_a16_0.COND2  <  80 ) AS p_0_a16_0  ) AS part_ins_d2_10_a16_0  ) AS __dummy__) AS tbl;

        insertion_data := (SELECT (array_to_json(detected_insertions))::text);
        IF insertion_data IS NOT DISTINCT FROM NULL THEN 
            insertion_data := '[]';
        END IF; 

        WITH __tmp_delta_ins_mt_for_d2_10_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size), 
        __tmp_delta_del_mt_for_d2_10_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_deletions FROM (SELECT __dummy__.COL0 AS V, __dummy__.COL1 AS L, __dummy__.COL2 AS D, __dummy__.COL3 AS R, __dummy__.COL4 AS P, __dummy__.COL5 AS LINEAGE, __dummy__.COL6 AS COND1, __dummy__.COL7 AS COND2, __dummy__.COL8 AS COND3, __dummy__.COL9 AS COND4, __dummy__.COL10 AS COND5, __dummy__.COL11 AS COND6, __dummy__.COL12 AS COND7, __dummy__.COL13 AS COND8, __dummy__.COL14 AS COND9, __dummy__.COL15 AS COND10 
FROM (SELECT part_del_d2_10_a16_0.COL0 AS COL0, part_del_d2_10_a16_0.COL1 AS COL1, part_del_d2_10_a16_0.COL2 AS COL2, part_del_d2_10_a16_0.COL3 AS COL3, part_del_d2_10_a16_0.COL4 AS COL4, part_del_d2_10_a16_0.COL5 AS COL5, part_del_d2_10_a16_0.COL6 AS COL6, part_del_d2_10_a16_0.COL7 AS COL7, part_del_d2_10_a16_0.COL8 AS COL8, part_del_d2_10_a16_0.COL9 AS COL9, part_del_d2_10_a16_0.COL10 AS COL10, part_del_d2_10_a16_0.COL11 AS COL11, part_del_d2_10_a16_0.COL12 AS COL12, part_del_d2_10_a16_0.COL13 AS COL13, part_del_d2_10_a16_0.COL14 AS COL14, part_del_d2_10_a16_0.COL15 AS COL15 
FROM (SELECT p_0_a16_0.COL0 AS COL0, p_0_a16_0.COL1 AS COL1, p_0_a16_0.COL2 AS COL2, p_0_a16_0.COL3 AS COL3, p_0_a16_0.COL4 AS COL4, p_0_a16_0.COL5 AS COL5, p_0_a16_0.COL6 AS COL6, p_0_a16_0.COL7 AS COL7, p_0_a16_0.COL8 AS COL8, p_0_a16_0.COL9 AS COL9, p_0_a16_0.COL10 AS COL10, p_0_a16_0.COL11 AS COL11, p_0_a16_0.COL12 AS COL12, p_0_a16_0.COL13 AS COL13, p_0_a16_0.COL14 AS COL14, p_0_a16_0.COL15 AS COL15 
FROM (SELECT __tmp_delta_del_mt_for_d2_10_ar_a16_0.V AS COL0, __tmp_delta_del_mt_for_d2_10_ar_a16_0.L AS COL1, __tmp_delta_del_mt_for_d2_10_ar_a16_0.D AS COL2, __tmp_delta_del_mt_for_d2_10_ar_a16_0.R AS COL3, __tmp_delta_del_mt_for_d2_10_ar_a16_0.P AS COL4, __tmp_delta_del_mt_for_d2_10_ar_a16_0.LINEAGE AS COL5, __tmp_delta_del_mt_for_d2_10_ar_a16_0.COND1 AS COL6, __tmp_delta_del_mt_for_d2_10_ar_a16_0.COND2 AS COL7, __tmp_delta_del_mt_for_d2_10_ar_a16_0.COND3 AS COL8, __tmp_delta_del_mt_for_d2_10_ar_a16_0.COND4 AS COL9, __tmp_delta_del_mt_for_d2_10_ar_a16_0.COND5 AS COL10, __tmp_delta_del_mt_for_d2_10_ar_a16_0.COND6 AS COL11, __tmp_delta_del_mt_for_d2_10_ar_a16_0.COND7 AS COL12, __tmp_delta_del_mt_for_d2_10_ar_a16_0.COND8 AS COL13, __tmp_delta_del_mt_for_d2_10_ar_a16_0.COND9 AS COL14, __tmp_delta_del_mt_for_d2_10_ar_a16_0.COND10 AS COL15 
FROM __tmp_delta_del_mt_for_d2_10_ar AS __tmp_delta_del_mt_for_d2_10_ar_a16_0 
WHERE __tmp_delta_del_mt_for_d2_10_ar_a16_0.COND2  <  80 ) AS p_0_a16_0  ) AS part_del_d2_10_a16_0  ) AS __dummy__) AS tbl;

        deletion_data := (  
        SELECT (array_to_json(detected_deletions))::text);
        IF deletion_data IS NOT DISTINCT FROM NULL THEN 
            deletion_data := '[]';
        END IF; 
        IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN 
            user_name := (SELECT session_user);
            IF NOT (user_name = 'dejima') THEN 
                xid := (SELECT txid_current());
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.d2_10"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.d2_10_run_shell(json_data);
                IF result = 'true' THEN 
                    DROP TABLE __tmp_delta_ins_mt_for_d2_10;
                    DROP TABLE __tmp_delta_del_mt_for_d2_10;
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
                -- DELETE FROM public.__dummy__d2_10_detected_deletions;
                INSERT INTO public.__dummy__d2_10_detected_deletions
                    ( SELECT xid, * FROM unnest(detected_deletions) as detected_deletions_alias );

                -- DELETE FROM public.__dummy__d2_10_detected_insertions;
                INSERT INTO public.__dummy__d2_10_detected_insertions
                    ( SELECT xid, * FROM unnest(detected_insertions) as detected_insertions_alias );
            END IF;
        END IF;
    END IF;
END IF;
RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.mt';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the function public.mt_detect_update_on_d2_10() ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS mt_detect_update_on_d2_10 ON public.mt;
CREATE CONSTRAINT TRIGGER mt_detect_update_on_d2_10
    AFTER INSERT OR UPDATE OR DELETE ON
    public.mt DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.mt_detect_update_on_d2_10();

CREATE OR REPLACE FUNCTION public.mt_propagate_updates_to_d2_10 ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS public.mt_detect_update_on_d2_10 IMMEDIATE;
    SET CONSTRAINTS public.mt_detect_update_on_d2_10 DEFERRED;
    DROP TABLE IF EXISTS mt_detect_update_on_d2_10_flag;
    RETURN true;
  END;
$$;



CREATE OR REPLACE FUNCTION public.d2_10_delta_action()
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
  array_delta_del public.d2_10[];
  array_delta_ins public.d2_10[];
  temprec_delta_del_mt public.mt%ROWTYPE;
            array_delta_del_mt public.mt[];
temprec_delta_ins_mt public.mt%ROWTYPE;
            array_delta_ins_mt public.mt[];
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd2_10_delta_action_flag') THEN
        -- RAISE LOG 'execute procedure d2_10_delta_action';
        CREATE TEMPORARY TABLE d2_10_delta_action_flag ON COMMIT DROP AS (SELECT true as finish);
        IF EXISTS (SELECT WHERE false )
        THEN 
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the view are violated';
        END IF;
        IF EXISTS (SELECT WHERE false )
        THEN 
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the source relations are violated';
        END IF;
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_d2_10 AS tbl;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_d2_10 as tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_d2_10;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_d2_10;
        
            WITH __tmp_delta_del_d2_10_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_d2_10_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_del_mt FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11,COL12,COL13,COL14,COL15) :: public.mt).* 
            FROM (SELECT delta_del_mt_a16_0.COL0 AS COL0, delta_del_mt_a16_0.COL1 AS COL1, delta_del_mt_a16_0.COL2 AS COL2, delta_del_mt_a16_0.COL3 AS COL3, delta_del_mt_a16_0.COL4 AS COL4, delta_del_mt_a16_0.COL5 AS COL5, delta_del_mt_a16_0.COL6 AS COL6, delta_del_mt_a16_0.COL7 AS COL7, delta_del_mt_a16_0.COL8 AS COL8, delta_del_mt_a16_0.COL9 AS COL9, delta_del_mt_a16_0.COL10 AS COL10, delta_del_mt_a16_0.COL11 AS COL11, delta_del_mt_a16_0.COL12 AS COL12, delta_del_mt_a16_0.COL13 AS COL13, delta_del_mt_a16_0.COL14 AS COL14, delta_del_mt_a16_0.COL15 AS COL15 
FROM (SELECT p_0_a16_0.COL0 AS COL0, p_0_a16_0.COL1 AS COL1, p_0_a16_0.COL2 AS COL2, p_0_a16_0.COL3 AS COL3, p_0_a16_0.COL4 AS COL4, p_0_a16_0.COL5 AS COL5, p_0_a16_0.COL6 AS COL6, p_0_a16_0.COL7 AS COL7, p_0_a16_0.COL8 AS COL8, p_0_a16_0.COL9 AS COL9, p_0_a16_0.COL10 AS COL10, p_0_a16_0.COL11 AS COL11, p_0_a16_0.COL12 AS COL12, p_0_a16_0.COL13 AS COL13, p_0_a16_0.COL14 AS COL14, p_0_a16_0.COL15 AS COL15 
FROM (SELECT mt_a16_1.V AS COL0, mt_a16_1.L AS COL1, mt_a16_1.D AS COL2, mt_a16_1.R AS COL3, mt_a16_1.P AS COL4, mt_a16_1.LINEAGE AS COL5, mt_a16_1.COND1 AS COL6, mt_a16_1.COND2 AS COL7, mt_a16_1.COND3 AS COL8, mt_a16_1.COND4 AS COL9, mt_a16_1.COND5 AS COL10, mt_a16_1.COND6 AS COL11, mt_a16_1.COND7 AS COL12, mt_a16_1.COND8 AS COL13, mt_a16_1.COND9 AS COL14, mt_a16_1.COND10 AS COL15 
FROM __tmp_delta_del_d2_10_ar AS __tmp_delta_del_d2_10_ar_a16_0, public.mt AS mt_a16_1 
WHERE mt_a16_1.V = __tmp_delta_del_d2_10_ar_a16_0.V AND mt_a16_1.L = __tmp_delta_del_d2_10_ar_a16_0.L AND mt_a16_1.D = __tmp_delta_del_d2_10_ar_a16_0.D AND mt_a16_1.R = __tmp_delta_del_d2_10_ar_a16_0.R AND mt_a16_1.P = __tmp_delta_del_d2_10_ar_a16_0.P AND mt_a16_1.LINEAGE = __tmp_delta_del_d2_10_ar_a16_0.LINEAGE AND mt_a16_1.COND1 = __tmp_delta_del_d2_10_ar_a16_0.COND1 AND mt_a16_1.COND2 = __tmp_delta_del_d2_10_ar_a16_0.COND2 AND mt_a16_1.COND3 = __tmp_delta_del_d2_10_ar_a16_0.COND3 AND mt_a16_1.COND4 = __tmp_delta_del_d2_10_ar_a16_0.COND4 AND mt_a16_1.COND5 = __tmp_delta_del_d2_10_ar_a16_0.COND5 AND mt_a16_1.COND6 = __tmp_delta_del_d2_10_ar_a16_0.COND6 AND mt_a16_1.COND7 = __tmp_delta_del_d2_10_ar_a16_0.COND7 AND mt_a16_1.COND8 = __tmp_delta_del_d2_10_ar_a16_0.COND8 AND mt_a16_1.COND9 = __tmp_delta_del_d2_10_ar_a16_0.COND9 AND mt_a16_1.COND10 = __tmp_delta_del_d2_10_ar_a16_0.COND10 AND mt_a16_1.COND2  <  80 ) AS p_0_a16_0  ) AS delta_del_mt_a16_0  ) AS delta_del_mt_extra_alias) AS tbl;


            WITH __tmp_delta_del_d2_10_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_d2_10_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_ins_mt FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11,COL12,COL13,COL14,COL15) :: public.mt).* 
            FROM (SELECT delta_ins_mt_a16_0.COL0 AS COL0, delta_ins_mt_a16_0.COL1 AS COL1, delta_ins_mt_a16_0.COL2 AS COL2, delta_ins_mt_a16_0.COL3 AS COL3, delta_ins_mt_a16_0.COL4 AS COL4, delta_ins_mt_a16_0.COL5 AS COL5, delta_ins_mt_a16_0.COL6 AS COL6, delta_ins_mt_a16_0.COL7 AS COL7, delta_ins_mt_a16_0.COL8 AS COL8, delta_ins_mt_a16_0.COL9 AS COL9, delta_ins_mt_a16_0.COL10 AS COL10, delta_ins_mt_a16_0.COL11 AS COL11, delta_ins_mt_a16_0.COL12 AS COL12, delta_ins_mt_a16_0.COL13 AS COL13, delta_ins_mt_a16_0.COL14 AS COL14, delta_ins_mt_a16_0.COL15 AS COL15 
FROM (SELECT p_0_a16_0.COL0 AS COL0, p_0_a16_0.COL1 AS COL1, p_0_a16_0.COL2 AS COL2, p_0_a16_0.COL3 AS COL3, p_0_a16_0.COL4 AS COL4, p_0_a16_0.COL5 AS COL5, p_0_a16_0.COL6 AS COL6, p_0_a16_0.COL7 AS COL7, p_0_a16_0.COL8 AS COL8, p_0_a16_0.COL9 AS COL9, p_0_a16_0.COL10 AS COL10, p_0_a16_0.COL11 AS COL11, p_0_a16_0.COL12 AS COL12, p_0_a16_0.COL13 AS COL13, p_0_a16_0.COL14 AS COL14, p_0_a16_0.COL15 AS COL15 
FROM (SELECT __tmp_delta_ins_d2_10_ar_a16_0.V AS COL0, __tmp_delta_ins_d2_10_ar_a16_0.L AS COL1, __tmp_delta_ins_d2_10_ar_a16_0.D AS COL2, __tmp_delta_ins_d2_10_ar_a16_0.R AS COL3, __tmp_delta_ins_d2_10_ar_a16_0.P AS COL4, __tmp_delta_ins_d2_10_ar_a16_0.LINEAGE AS COL5, __tmp_delta_ins_d2_10_ar_a16_0.COND1 AS COL6, __tmp_delta_ins_d2_10_ar_a16_0.COND2 AS COL7, __tmp_delta_ins_d2_10_ar_a16_0.COND3 AS COL8, __tmp_delta_ins_d2_10_ar_a16_0.COND4 AS COL9, __tmp_delta_ins_d2_10_ar_a16_0.COND5 AS COL10, __tmp_delta_ins_d2_10_ar_a16_0.COND6 AS COL11, __tmp_delta_ins_d2_10_ar_a16_0.COND7 AS COL12, __tmp_delta_ins_d2_10_ar_a16_0.COND8 AS COL13, __tmp_delta_ins_d2_10_ar_a16_0.COND9 AS COL14, __tmp_delta_ins_d2_10_ar_a16_0.COND10 AS COL15 
FROM __tmp_delta_ins_d2_10_ar AS __tmp_delta_ins_d2_10_ar_a16_0 
WHERE __tmp_delta_ins_d2_10_ar_a16_0.COND2  <  80 AND NOT EXISTS ( SELECT * 
FROM public.mt AS mt_a16 
WHERE mt_a16.V = __tmp_delta_ins_d2_10_ar_a16_0.V AND mt_a16.L = __tmp_delta_ins_d2_10_ar_a16_0.L AND mt_a16.D = __tmp_delta_ins_d2_10_ar_a16_0.D AND mt_a16.R = __tmp_delta_ins_d2_10_ar_a16_0.R AND mt_a16.P = __tmp_delta_ins_d2_10_ar_a16_0.P AND mt_a16.LINEAGE = __tmp_delta_ins_d2_10_ar_a16_0.LINEAGE AND mt_a16.COND1 = __tmp_delta_ins_d2_10_ar_a16_0.COND1 AND mt_a16.COND2 = __tmp_delta_ins_d2_10_ar_a16_0.COND2 AND mt_a16.COND3 = __tmp_delta_ins_d2_10_ar_a16_0.COND3 AND mt_a16.COND4 = __tmp_delta_ins_d2_10_ar_a16_0.COND4 AND mt_a16.COND5 = __tmp_delta_ins_d2_10_ar_a16_0.COND5 AND mt_a16.COND6 = __tmp_delta_ins_d2_10_ar_a16_0.COND6 AND mt_a16.COND7 = __tmp_delta_ins_d2_10_ar_a16_0.COND7 AND mt_a16.COND8 = __tmp_delta_ins_d2_10_ar_a16_0.COND8 AND mt_a16.COND9 = __tmp_delta_ins_d2_10_ar_a16_0.COND9 AND mt_a16.COND10 = __tmp_delta_ins_d2_10_ar_a16_0.COND10 ) ) AS p_0_a16_0  ) AS delta_ins_mt_a16_0  ) AS delta_ins_mt_extra_alias) AS tbl; 


            IF array_delta_del_mt IS DISTINCT FROM NULL THEN 
                FOREACH temprec_delta_del_mt IN array array_delta_del_mt  LOOP 
                   DELETE FROM public.mt WHERE V =  temprec_delta_del_mt.V AND L =  temprec_delta_del_mt.L AND D =  temprec_delta_del_mt.D AND R =  temprec_delta_del_mt.R AND P =  temprec_delta_del_mt.P AND LINEAGE =  temprec_delta_del_mt.LINEAGE AND COND1 =  temprec_delta_del_mt.COND1 AND COND2 =  temprec_delta_del_mt.COND2 AND COND3 =  temprec_delta_del_mt.COND3 AND COND4 =  temprec_delta_del_mt.COND4 AND COND5 =  temprec_delta_del_mt.COND5 AND COND6 =  temprec_delta_del_mt.COND6 AND COND7 =  temprec_delta_del_mt.COND7 AND COND8 =  temprec_delta_del_mt.COND8 AND COND9 =  temprec_delta_del_mt.COND9 AND COND10 =  temprec_delta_del_mt.COND10;
                END LOOP;
            END IF;


            IF array_delta_ins_mt IS DISTINCT FROM NULL THEN 
                INSERT INTO public.mt (SELECT * FROM unnest(array_delta_ins_mt) as array_delta_ins_mt_alias) ; 
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
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.d2_10"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.d2_10_run_shell(json_data);
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
                --DELETE FROM public.__dummy__d2_10_detected_deletions;
                INSERT INTO public.__dummy__d2_10_detected_deletions
                    SELECT xid, * FROM __tmp_delta_del_d2_10;

                --DELETE FROM public.__dummy__d2_10_detected_insertions;
                INSERT INTO public.__dummy__d2_10_detected_insertions
                    SELECT xid, * FROM __tmp_delta_ins_d2_10;
            END IF;
        END IF;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d2_10';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d2_10 ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d2_10_materialization()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_d2_10' OR table_name = '__tmp_delta_del_d2_10')
    THEN
        -- RAISE LOG 'execute procedure d2_10_materialization';
        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_ins_d2_10 ( LIKE public.d2_10 ) WITH OIDS ON COMMIT DELETE ROWS;
        CREATE CONSTRAINT TRIGGER __tmp_d2_10_trigger_delta_action_ins
        AFTER INSERT OR UPDATE OR DELETE ON 
            __tmp_delta_ins_d2_10 DEFERRABLE INITIALLY DEFERRED 
            FOR EACH ROW EXECUTE PROCEDURE public.d2_10_delta_action();

        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_del_d2_10 ( LIKE public.d2_10 ) WITH OIDS ON COMMIT DELETE ROWS;
        CREATE CONSTRAINT TRIGGER __tmp_d2_10_trigger_delta_action_del
        AFTER INSERT OR UPDATE OR DELETE ON 
            __tmp_delta_del_d2_10 DEFERRABLE INITIALLY DEFERRED 
            FOR EACH ROW EXECUTE PROCEDURE public.d2_10_delta_action();
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d2_10';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d2_10 ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS d2_10_trigger_materialization ON public.d2_10;
CREATE TRIGGER d2_10_trigger_materialization
    BEFORE INSERT OR UPDATE OR DELETE ON
      public.d2_10 FOR EACH STATEMENT EXECUTE PROCEDURE public.d2_10_materialization();

CREATE OR REPLACE FUNCTION public.d2_10_update()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    -- RAISE LOG 'execute procedure d2_10_update';
    IF TG_OP = 'INSERT' THEN
      -- RAISE LOG 'NEW: %', NEW;
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_del_d2_10 WHERE ROW(V,L,D,R,P,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = NEW;
      INSERT INTO __tmp_delta_ins_d2_10 SELECT (NEW).*; 
    ELSIF TG_OP = 'UPDATE' THEN
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_ins_d2_10 WHERE ROW(V,L,D,R,P,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = OLD;
      INSERT INTO __tmp_delta_del_d2_10 SELECT (OLD).*;
      DELETE FROM __tmp_delta_del_d2_10 WHERE ROW(V,L,D,R,P,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = NEW;
      INSERT INTO __tmp_delta_ins_d2_10 SELECT (NEW).*; 
    ELSIF TG_OP = 'DELETE' THEN
      -- RAISE LOG 'OLD: %', OLD;
      DELETE FROM __tmp_delta_ins_d2_10 WHERE ROW(V,L,D,R,P,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = OLD;
      INSERT INTO __tmp_delta_del_d2_10 SELECT (OLD).*;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d2_10';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d2_10 ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS d2_10_trigger_update ON public.d2_10;
CREATE TRIGGER d2_10_trigger_update
    INSTEAD OF INSERT OR UPDATE OR DELETE ON
      public.d2_10 FOR EACH ROW EXECUTE PROCEDURE public.d2_10_update();

CREATE OR REPLACE FUNCTION public.d2_10_propagate_updates ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS __tmp_d2_10_trigger_delta_action_ins, __tmp_d2_10_trigger_delta_action_del IMMEDIATE;
    SET CONSTRAINTS __tmp_d2_10_trigger_delta_action_ins, __tmp_d2_10_trigger_delta_action_del DEFERRED;
    DROP TABLE IF EXISTS d2_10_delta_action_flag;
    DROP TABLE IF EXISTS __tmp_delta_del_d2_10;
    DROP TABLE IF EXISTS __tmp_delta_ins_d2_10;
    RETURN true;
  END;
$$;

CREATE OR REPLACE FUNCTION public.clean_dummy_d2_10 ()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  xid int;
  BEGIN
    xid := (SELECT txid_current());
    DELETE FROM public.__dummy__d2_10_detected_deletions as t where t.txid = xid;
    DELETE FROM public.__dummy__d2_10_detected_insertions as t where t.txid = xid;
    RAISE LOG 'clean __dummy__d2_10_detected_deletions/insertions';
    RETURN NULL;
  END;
$$;

CREATE CONSTRAINT TRIGGER __zzz_clean_d2_10
    AFTER INSERT OR UPDATE OR DELETE ON
    public.mt DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.clean_dummy_d2_10();

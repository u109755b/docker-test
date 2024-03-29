CREATE OR REPLACE VIEW public.d1_6 AS 
SELECT __dummy__.COL0 AS V, __dummy__.COL1 AS L, __dummy__.COL2 AS D, __dummy__.COL3 AS R, __dummy__.COL4 AS T, __dummy__.COL5 AS AL1, __dummy__.COL6 AS AL2, __dummy__.COL7 AS AL3, __dummy__.COL8 AS AL4, __dummy__.COL9 AS AL5, __dummy__.COL10 AS LINEAGE, __dummy__.COL11 AS COND1, __dummy__.COL12 AS COND2, __dummy__.COL13 AS COND3, __dummy__.COL14 AS COND4, __dummy__.COL15 AS COND5, __dummy__.COL16 AS COND6, __dummy__.COL17 AS COND7, __dummy__.COL18 AS COND8, __dummy__.COL19 AS COND9, __dummy__.COL20 AS COND10 
FROM (SELECT d1_6_a21_0.COL0 AS COL0, d1_6_a21_0.COL1 AS COL1, d1_6_a21_0.COL2 AS COL2, d1_6_a21_0.COL3 AS COL3, d1_6_a21_0.COL4 AS COL4, d1_6_a21_0.COL5 AS COL5, d1_6_a21_0.COL6 AS COL6, d1_6_a21_0.COL7 AS COL7, d1_6_a21_0.COL8 AS COL8, d1_6_a21_0.COL9 AS COL9, d1_6_a21_0.COL10 AS COL10, d1_6_a21_0.COL11 AS COL11, d1_6_a21_0.COL12 AS COL12, d1_6_a21_0.COL13 AS COL13, d1_6_a21_0.COL14 AS COL14, d1_6_a21_0.COL15 AS COL15, d1_6_a21_0.COL16 AS COL16, d1_6_a21_0.COL17 AS COL17, d1_6_a21_0.COL18 AS COL18, d1_6_a21_0.COL19 AS COL19, d1_6_a21_0.COL20 AS COL20 
FROM (SELECT bt_a21_0.V AS COL0, bt_a21_0.L AS COL1, bt_a21_0.D AS COL2, bt_a21_0.R AS COL3, bt_a21_0.T AS COL4, bt_a21_0.AL1 AS COL5, bt_a21_0.AL2 AS COL6, bt_a21_0.AL3 AS COL7, bt_a21_0.AL4 AS COL8, bt_a21_0.AL5 AS COL9, bt_a21_0.LINEAGE AS COL10, bt_a21_0.COND1 AS COL11, bt_a21_0.COND2 AS COL12, bt_a21_0.COND3 AS COL13, bt_a21_0.COND4 AS COL14, bt_a21_0.COND5 AS COL15, bt_a21_0.COND6 AS COL16, bt_a21_0.COND7 AS COL17, bt_a21_0.COND8 AS COL18, bt_a21_0.COND9 AS COL19, bt_a21_0.COND10 AS COL20 
FROM public.bt AS bt_a21_0 
WHERE bt_a21_0.COND10  <  80 ) AS d1_6_a21_0  ) AS __dummy__;

CREATE EXTENSION IF NOT EXISTS plsh;

CREATE TABLE IF NOT EXISTS public.__dummy__d1_6_detected_deletions (txid int, LIKE public.d1_6 );
CREATE INDEX IF NOT EXISTS idx__dummy__d1_6_detected_deletions ON public.__dummy__d1_6_detected_deletions (txid);
CREATE TABLE IF NOT EXISTS public.__dummy__d1_6_detected_insertions (txid int, LIKE public.d1_6 );
CREATE INDEX IF NOT EXISTS idx__dummy__d1_6_detected_insertions ON public.__dummy__d1_6_detected_insertions (txid);

CREATE OR REPLACE FUNCTION public.d1_6_get_detected_update_data(txid int)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  deletion_data text;
  insertion_data text;
  json_data text;
  BEGIN
    insertion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__d1_6_detected_insertions as t where t.txid = $1);
    IF insertion_data IS NOT DISTINCT FROM NULL THEN 
        insertion_data := '[]';
    END IF; 
    deletion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__d1_6_detected_deletions as t where t.txid = $1);
    IF deletion_data IS NOT DISTINCT FROM NULL THEN 
        deletion_data := '[]';
    END IF; 
    IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN 
        -- calcuate the update data
        json_data := concat('{"view": ' , '"public.d1_6"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
        -- clear the update data
        --DELETE FROM public.__dummy__d1_6_detected_deletions;
        --DELETE FROM public.__dummy__d1_6_detected_insertions;
    END IF;
    RETURN json_data;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d1_6_run_shell(text) RETURNS text AS $$
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

CREATE OR REPLACE FUNCTION public.bt_materialization_for_d1_6()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_bt_for_d1_6' OR table_name = '__tmp_delta_del_bt_for_d1_6')
    THEN
        -- RAISE LOG 'execute procedure bt_materialization_for_d1_6';
        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_ins_bt_for_d1_6 ( LIKE public.bt ) WITH OIDS ON COMMIT DELETE ROWS;
        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_del_bt_for_d1_6 ( LIKE public.bt ) WITH OIDS ON COMMIT DELETE ROWS;
        
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

DROP TRIGGER IF EXISTS bt_trigger_materialization_for_d1_6 ON public.bt;
CREATE TRIGGER bt_trigger_materialization_for_d1_6
    BEFORE INSERT OR UPDATE OR DELETE ON
    public.bt FOR EACH STATEMENT EXECUTE PROCEDURE public.bt_materialization_for_d1_6();

CREATE OR REPLACE FUNCTION public.bt_update_for_d1_6()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    -- RAISE LOG 'execute procedure bt_update_for_d1_6';
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd1_6_delta_action_flag') THEN
        IF TG_OP = 'INSERT' THEN
        -- RAISE LOG 'NEW: %', NEW;
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_del_bt_for_d1_6 WHERE ROW(V,L,D,R,T,AL1,AL2,AL3,AL4,AL5,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = NEW;
        INSERT INTO __tmp_delta_ins_bt_for_d1_6 SELECT (NEW).*; 
        ELSIF TG_OP = 'UPDATE' THEN
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_ins_bt_for_d1_6 WHERE ROW(V,L,D,R,T,AL1,AL2,AL3,AL4,AL5,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = OLD;
        INSERT INTO __tmp_delta_del_bt_for_d1_6 SELECT (OLD).*;
        DELETE FROM __tmp_delta_del_bt_for_d1_6 WHERE ROW(V,L,D,R,T,AL1,AL2,AL3,AL4,AL5,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = NEW;
        INSERT INTO __tmp_delta_ins_bt_for_d1_6 SELECT (NEW).*; 
        ELSIF TG_OP = 'DELETE' THEN
        -- RAISE LOG 'OLD: %', OLD;
        DELETE FROM __tmp_delta_ins_bt_for_d1_6 WHERE ROW(V,L,D,R,T,AL1,AL2,AL3,AL4,AL5,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = OLD;
        INSERT INTO __tmp_delta_del_bt_for_d1_6 SELECT (OLD).*;
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

DROP TRIGGER IF EXISTS bt_trigger_update_for_d1_6 ON public.bt;
CREATE TRIGGER bt_trigger_update_for_d1_6
    AFTER INSERT OR UPDATE OR DELETE ON
    public.bt FOR EACH ROW EXECUTE PROCEDURE public.bt_update_for_d1_6();

CREATE OR REPLACE FUNCTION public.bt_detect_update_on_d1_6()
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
detected_deletions public.d1_6[];
detected_insertions public.d1_6[];
delta_ins_size int;
delta_del_size int;
BEGIN
IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'bt_detect_update_on_d1_6_flag') THEN
    CREATE TEMPORARY TABLE bt_detect_update_on_d1_6_flag ON COMMIT DROP AS (SELECT true as finish);
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd1_6_delta_action_flag') THEN
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_bt_for_d1_6 AS tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_bt_for_d1_6;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_bt_for_d1_6 tbl;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_bt_for_d1_6;

        WITH __tmp_delta_ins_bt_for_d1_6_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size), 
        __tmp_delta_del_bt_for_d1_6_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_insertions FROM (SELECT __dummy__.COL0 AS V, __dummy__.COL1 AS L, __dummy__.COL2 AS D, __dummy__.COL3 AS R, __dummy__.COL4 AS T, __dummy__.COL5 AS AL1, __dummy__.COL6 AS AL2, __dummy__.COL7 AS AL3, __dummy__.COL8 AS AL4, __dummy__.COL9 AS AL5, __dummy__.COL10 AS LINEAGE, __dummy__.COL11 AS COND1, __dummy__.COL12 AS COND2, __dummy__.COL13 AS COND3, __dummy__.COL14 AS COND4, __dummy__.COL15 AS COND5, __dummy__.COL16 AS COND6, __dummy__.COL17 AS COND7, __dummy__.COL18 AS COND8, __dummy__.COL19 AS COND9, __dummy__.COL20 AS COND10 
FROM (SELECT part_ins_d1_6_a21_0.COL0 AS COL0, part_ins_d1_6_a21_0.COL1 AS COL1, part_ins_d1_6_a21_0.COL2 AS COL2, part_ins_d1_6_a21_0.COL3 AS COL3, part_ins_d1_6_a21_0.COL4 AS COL4, part_ins_d1_6_a21_0.COL5 AS COL5, part_ins_d1_6_a21_0.COL6 AS COL6, part_ins_d1_6_a21_0.COL7 AS COL7, part_ins_d1_6_a21_0.COL8 AS COL8, part_ins_d1_6_a21_0.COL9 AS COL9, part_ins_d1_6_a21_0.COL10 AS COL10, part_ins_d1_6_a21_0.COL11 AS COL11, part_ins_d1_6_a21_0.COL12 AS COL12, part_ins_d1_6_a21_0.COL13 AS COL13, part_ins_d1_6_a21_0.COL14 AS COL14, part_ins_d1_6_a21_0.COL15 AS COL15, part_ins_d1_6_a21_0.COL16 AS COL16, part_ins_d1_6_a21_0.COL17 AS COL17, part_ins_d1_6_a21_0.COL18 AS COL18, part_ins_d1_6_a21_0.COL19 AS COL19, part_ins_d1_6_a21_0.COL20 AS COL20 
FROM (SELECT p_0_a21_0.COL0 AS COL0, p_0_a21_0.COL1 AS COL1, p_0_a21_0.COL2 AS COL2, p_0_a21_0.COL3 AS COL3, p_0_a21_0.COL4 AS COL4, p_0_a21_0.COL5 AS COL5, p_0_a21_0.COL6 AS COL6, p_0_a21_0.COL7 AS COL7, p_0_a21_0.COL8 AS COL8, p_0_a21_0.COL9 AS COL9, p_0_a21_0.COL10 AS COL10, p_0_a21_0.COL11 AS COL11, p_0_a21_0.COL12 AS COL12, p_0_a21_0.COL13 AS COL13, p_0_a21_0.COL14 AS COL14, p_0_a21_0.COL15 AS COL15, p_0_a21_0.COL16 AS COL16, p_0_a21_0.COL17 AS COL17, p_0_a21_0.COL18 AS COL18, p_0_a21_0.COL19 AS COL19, p_0_a21_0.COL20 AS COL20 
FROM (SELECT __tmp_delta_ins_bt_for_d1_6_ar_a21_0.V AS COL0, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.L AS COL1, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.D AS COL2, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.R AS COL3, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.T AS COL4, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.AL1 AS COL5, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.AL2 AS COL6, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.AL3 AS COL7, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.AL4 AS COL8, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.AL5 AS COL9, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.LINEAGE AS COL10, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.COND1 AS COL11, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.COND2 AS COL12, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.COND3 AS COL13, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.COND4 AS COL14, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.COND5 AS COL15, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.COND6 AS COL16, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.COND7 AS COL17, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.COND8 AS COL18, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.COND9 AS COL19, __tmp_delta_ins_bt_for_d1_6_ar_a21_0.COND10 AS COL20 
FROM __tmp_delta_ins_bt_for_d1_6_ar AS __tmp_delta_ins_bt_for_d1_6_ar_a21_0 
WHERE __tmp_delta_ins_bt_for_d1_6_ar_a21_0.COND10  <  80 ) AS p_0_a21_0  ) AS part_ins_d1_6_a21_0  ) AS __dummy__) AS tbl;

        insertion_data := (SELECT (array_to_json(detected_insertions))::text);
        IF insertion_data IS NOT DISTINCT FROM NULL THEN 
            insertion_data := '[]';
        END IF; 

        WITH __tmp_delta_ins_bt_for_d1_6_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size), 
        __tmp_delta_del_bt_for_d1_6_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_deletions FROM (SELECT __dummy__.COL0 AS V, __dummy__.COL1 AS L, __dummy__.COL2 AS D, __dummy__.COL3 AS R, __dummy__.COL4 AS T, __dummy__.COL5 AS AL1, __dummy__.COL6 AS AL2, __dummy__.COL7 AS AL3, __dummy__.COL8 AS AL4, __dummy__.COL9 AS AL5, __dummy__.COL10 AS LINEAGE, __dummy__.COL11 AS COND1, __dummy__.COL12 AS COND2, __dummy__.COL13 AS COND3, __dummy__.COL14 AS COND4, __dummy__.COL15 AS COND5, __dummy__.COL16 AS COND6, __dummy__.COL17 AS COND7, __dummy__.COL18 AS COND8, __dummy__.COL19 AS COND9, __dummy__.COL20 AS COND10 
FROM (SELECT part_del_d1_6_a21_0.COL0 AS COL0, part_del_d1_6_a21_0.COL1 AS COL1, part_del_d1_6_a21_0.COL2 AS COL2, part_del_d1_6_a21_0.COL3 AS COL3, part_del_d1_6_a21_0.COL4 AS COL4, part_del_d1_6_a21_0.COL5 AS COL5, part_del_d1_6_a21_0.COL6 AS COL6, part_del_d1_6_a21_0.COL7 AS COL7, part_del_d1_6_a21_0.COL8 AS COL8, part_del_d1_6_a21_0.COL9 AS COL9, part_del_d1_6_a21_0.COL10 AS COL10, part_del_d1_6_a21_0.COL11 AS COL11, part_del_d1_6_a21_0.COL12 AS COL12, part_del_d1_6_a21_0.COL13 AS COL13, part_del_d1_6_a21_0.COL14 AS COL14, part_del_d1_6_a21_0.COL15 AS COL15, part_del_d1_6_a21_0.COL16 AS COL16, part_del_d1_6_a21_0.COL17 AS COL17, part_del_d1_6_a21_0.COL18 AS COL18, part_del_d1_6_a21_0.COL19 AS COL19, part_del_d1_6_a21_0.COL20 AS COL20 
FROM (SELECT p_0_a21_0.COL0 AS COL0, p_0_a21_0.COL1 AS COL1, p_0_a21_0.COL2 AS COL2, p_0_a21_0.COL3 AS COL3, p_0_a21_0.COL4 AS COL4, p_0_a21_0.COL5 AS COL5, p_0_a21_0.COL6 AS COL6, p_0_a21_0.COL7 AS COL7, p_0_a21_0.COL8 AS COL8, p_0_a21_0.COL9 AS COL9, p_0_a21_0.COL10 AS COL10, p_0_a21_0.COL11 AS COL11, p_0_a21_0.COL12 AS COL12, p_0_a21_0.COL13 AS COL13, p_0_a21_0.COL14 AS COL14, p_0_a21_0.COL15 AS COL15, p_0_a21_0.COL16 AS COL16, p_0_a21_0.COL17 AS COL17, p_0_a21_0.COL18 AS COL18, p_0_a21_0.COL19 AS COL19, p_0_a21_0.COL20 AS COL20 
FROM (SELECT __tmp_delta_del_bt_for_d1_6_ar_a21_0.V AS COL0, __tmp_delta_del_bt_for_d1_6_ar_a21_0.L AS COL1, __tmp_delta_del_bt_for_d1_6_ar_a21_0.D AS COL2, __tmp_delta_del_bt_for_d1_6_ar_a21_0.R AS COL3, __tmp_delta_del_bt_for_d1_6_ar_a21_0.T AS COL4, __tmp_delta_del_bt_for_d1_6_ar_a21_0.AL1 AS COL5, __tmp_delta_del_bt_for_d1_6_ar_a21_0.AL2 AS COL6, __tmp_delta_del_bt_for_d1_6_ar_a21_0.AL3 AS COL7, __tmp_delta_del_bt_for_d1_6_ar_a21_0.AL4 AS COL8, __tmp_delta_del_bt_for_d1_6_ar_a21_0.AL5 AS COL9, __tmp_delta_del_bt_for_d1_6_ar_a21_0.LINEAGE AS COL10, __tmp_delta_del_bt_for_d1_6_ar_a21_0.COND1 AS COL11, __tmp_delta_del_bt_for_d1_6_ar_a21_0.COND2 AS COL12, __tmp_delta_del_bt_for_d1_6_ar_a21_0.COND3 AS COL13, __tmp_delta_del_bt_for_d1_6_ar_a21_0.COND4 AS COL14, __tmp_delta_del_bt_for_d1_6_ar_a21_0.COND5 AS COL15, __tmp_delta_del_bt_for_d1_6_ar_a21_0.COND6 AS COL16, __tmp_delta_del_bt_for_d1_6_ar_a21_0.COND7 AS COL17, __tmp_delta_del_bt_for_d1_6_ar_a21_0.COND8 AS COL18, __tmp_delta_del_bt_for_d1_6_ar_a21_0.COND9 AS COL19, __tmp_delta_del_bt_for_d1_6_ar_a21_0.COND10 AS COL20 
FROM __tmp_delta_del_bt_for_d1_6_ar AS __tmp_delta_del_bt_for_d1_6_ar_a21_0 
WHERE __tmp_delta_del_bt_for_d1_6_ar_a21_0.COND10  <  80 ) AS p_0_a21_0  ) AS part_del_d1_6_a21_0  ) AS __dummy__) AS tbl;

        deletion_data := (  
        SELECT (array_to_json(detected_deletions))::text);
        IF deletion_data IS NOT DISTINCT FROM NULL THEN 
            deletion_data := '[]';
        END IF; 
        IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN 
            user_name := (SELECT session_user);
            IF NOT (user_name = 'dejima') THEN 
                xid := (SELECT txid_current());
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.d1_6"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.d1_6_run_shell(json_data);
                IF result = 'true' THEN 
                    DROP TABLE __tmp_delta_ins_bt_for_d1_6;
                    DROP TABLE __tmp_delta_del_bt_for_d1_6;
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
                -- DELETE FROM public.__dummy__d1_6_detected_deletions;
                INSERT INTO public.__dummy__d1_6_detected_deletions
                    ( SELECT xid, * FROM unnest(detected_deletions) as detected_deletions_alias );

                -- DELETE FROM public.__dummy__d1_6_detected_insertions;
                INSERT INTO public.__dummy__d1_6_detected_insertions
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
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the function public.bt_detect_update_on_d1_6() ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS bt_detect_update_on_d1_6 ON public.bt;
CREATE CONSTRAINT TRIGGER bt_detect_update_on_d1_6
    AFTER INSERT OR UPDATE OR DELETE ON
    public.bt DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.bt_detect_update_on_d1_6();

CREATE OR REPLACE FUNCTION public.bt_propagate_updates_to_d1_6 ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS public.bt_detect_update_on_d1_6 IMMEDIATE;
    SET CONSTRAINTS public.bt_detect_update_on_d1_6 DEFERRED;
    DROP TABLE IF EXISTS bt_detect_update_on_d1_6_flag;
    RETURN true;
  END;
$$;



CREATE OR REPLACE FUNCTION public.d1_6_delta_action()
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
  array_delta_del public.d1_6[];
  array_delta_ins public.d1_6[];
  temprec_delta_del_bt public.bt%ROWTYPE;
            array_delta_del_bt public.bt[];
temprec_delta_ins_bt public.bt%ROWTYPE;
            array_delta_ins_bt public.bt[];
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd1_6_delta_action_flag') THEN
        -- RAISE LOG 'execute procedure d1_6_delta_action';
        CREATE TEMPORARY TABLE d1_6_delta_action_flag ON COMMIT DROP AS (SELECT true as finish);
        IF EXISTS (SELECT WHERE false )
        THEN 
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the view are violated';
        END IF;
        IF EXISTS (SELECT WHERE false )
        THEN 
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the source relations are violated';
        END IF;
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_d1_6 AS tbl;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_d1_6 as tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_d1_6;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_d1_6;
        
            WITH __tmp_delta_del_d1_6_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_d1_6_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_del_bt FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11,COL12,COL13,COL14,COL15,COL16,COL17,COL18,COL19,COL20) :: public.bt).* 
            FROM (SELECT delta_del_bt_a21_0.COL0 AS COL0, delta_del_bt_a21_0.COL1 AS COL1, delta_del_bt_a21_0.COL2 AS COL2, delta_del_bt_a21_0.COL3 AS COL3, delta_del_bt_a21_0.COL4 AS COL4, delta_del_bt_a21_0.COL5 AS COL5, delta_del_bt_a21_0.COL6 AS COL6, delta_del_bt_a21_0.COL7 AS COL7, delta_del_bt_a21_0.COL8 AS COL8, delta_del_bt_a21_0.COL9 AS COL9, delta_del_bt_a21_0.COL10 AS COL10, delta_del_bt_a21_0.COL11 AS COL11, delta_del_bt_a21_0.COL12 AS COL12, delta_del_bt_a21_0.COL13 AS COL13, delta_del_bt_a21_0.COL14 AS COL14, delta_del_bt_a21_0.COL15 AS COL15, delta_del_bt_a21_0.COL16 AS COL16, delta_del_bt_a21_0.COL17 AS COL17, delta_del_bt_a21_0.COL18 AS COL18, delta_del_bt_a21_0.COL19 AS COL19, delta_del_bt_a21_0.COL20 AS COL20 
FROM (SELECT p_0_a21_0.COL0 AS COL0, p_0_a21_0.COL1 AS COL1, p_0_a21_0.COL2 AS COL2, p_0_a21_0.COL3 AS COL3, p_0_a21_0.COL4 AS COL4, p_0_a21_0.COL5 AS COL5, p_0_a21_0.COL6 AS COL6, p_0_a21_0.COL7 AS COL7, p_0_a21_0.COL8 AS COL8, p_0_a21_0.COL9 AS COL9, p_0_a21_0.COL10 AS COL10, p_0_a21_0.COL11 AS COL11, p_0_a21_0.COL12 AS COL12, p_0_a21_0.COL13 AS COL13, p_0_a21_0.COL14 AS COL14, p_0_a21_0.COL15 AS COL15, p_0_a21_0.COL16 AS COL16, p_0_a21_0.COL17 AS COL17, p_0_a21_0.COL18 AS COL18, p_0_a21_0.COL19 AS COL19, p_0_a21_0.COL20 AS COL20 
FROM (SELECT bt_a21_1.V AS COL0, bt_a21_1.L AS COL1, bt_a21_1.D AS COL2, bt_a21_1.R AS COL3, bt_a21_1.T AS COL4, bt_a21_1.AL1 AS COL5, bt_a21_1.AL2 AS COL6, bt_a21_1.AL3 AS COL7, bt_a21_1.AL4 AS COL8, bt_a21_1.AL5 AS COL9, bt_a21_1.LINEAGE AS COL10, bt_a21_1.COND1 AS COL11, bt_a21_1.COND2 AS COL12, bt_a21_1.COND3 AS COL13, bt_a21_1.COND4 AS COL14, bt_a21_1.COND5 AS COL15, bt_a21_1.COND6 AS COL16, bt_a21_1.COND7 AS COL17, bt_a21_1.COND8 AS COL18, bt_a21_1.COND9 AS COL19, bt_a21_1.COND10 AS COL20 
FROM __tmp_delta_del_d1_6_ar AS __tmp_delta_del_d1_6_ar_a21_0, public.bt AS bt_a21_1 
WHERE bt_a21_1.V = __tmp_delta_del_d1_6_ar_a21_0.V AND bt_a21_1.L = __tmp_delta_del_d1_6_ar_a21_0.L AND bt_a21_1.D = __tmp_delta_del_d1_6_ar_a21_0.D AND bt_a21_1.R = __tmp_delta_del_d1_6_ar_a21_0.R AND bt_a21_1.T = __tmp_delta_del_d1_6_ar_a21_0.T AND bt_a21_1.AL1 = __tmp_delta_del_d1_6_ar_a21_0.AL1 AND bt_a21_1.AL2 = __tmp_delta_del_d1_6_ar_a21_0.AL2 AND bt_a21_1.AL3 = __tmp_delta_del_d1_6_ar_a21_0.AL3 AND bt_a21_1.AL4 = __tmp_delta_del_d1_6_ar_a21_0.AL4 AND bt_a21_1.AL5 = __tmp_delta_del_d1_6_ar_a21_0.AL5 AND bt_a21_1.LINEAGE = __tmp_delta_del_d1_6_ar_a21_0.LINEAGE AND bt_a21_1.COND1 = __tmp_delta_del_d1_6_ar_a21_0.COND1 AND bt_a21_1.COND2 = __tmp_delta_del_d1_6_ar_a21_0.COND2 AND bt_a21_1.COND3 = __tmp_delta_del_d1_6_ar_a21_0.COND3 AND bt_a21_1.COND4 = __tmp_delta_del_d1_6_ar_a21_0.COND4 AND bt_a21_1.COND5 = __tmp_delta_del_d1_6_ar_a21_0.COND5 AND bt_a21_1.COND6 = __tmp_delta_del_d1_6_ar_a21_0.COND6 AND bt_a21_1.COND7 = __tmp_delta_del_d1_6_ar_a21_0.COND7 AND bt_a21_1.COND8 = __tmp_delta_del_d1_6_ar_a21_0.COND8 AND bt_a21_1.COND9 = __tmp_delta_del_d1_6_ar_a21_0.COND9 AND bt_a21_1.COND10 = __tmp_delta_del_d1_6_ar_a21_0.COND10 AND bt_a21_1.COND10  <  80 ) AS p_0_a21_0  ) AS delta_del_bt_a21_0  ) AS delta_del_bt_extra_alias) AS tbl;


            WITH __tmp_delta_del_d1_6_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_d1_6_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_ins_bt FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11,COL12,COL13,COL14,COL15,COL16,COL17,COL18,COL19,COL20) :: public.bt).* 
            FROM (SELECT delta_ins_bt_a21_0.COL0 AS COL0, delta_ins_bt_a21_0.COL1 AS COL1, delta_ins_bt_a21_0.COL2 AS COL2, delta_ins_bt_a21_0.COL3 AS COL3, delta_ins_bt_a21_0.COL4 AS COL4, delta_ins_bt_a21_0.COL5 AS COL5, delta_ins_bt_a21_0.COL6 AS COL6, delta_ins_bt_a21_0.COL7 AS COL7, delta_ins_bt_a21_0.COL8 AS COL8, delta_ins_bt_a21_0.COL9 AS COL9, delta_ins_bt_a21_0.COL10 AS COL10, delta_ins_bt_a21_0.COL11 AS COL11, delta_ins_bt_a21_0.COL12 AS COL12, delta_ins_bt_a21_0.COL13 AS COL13, delta_ins_bt_a21_0.COL14 AS COL14, delta_ins_bt_a21_0.COL15 AS COL15, delta_ins_bt_a21_0.COL16 AS COL16, delta_ins_bt_a21_0.COL17 AS COL17, delta_ins_bt_a21_0.COL18 AS COL18, delta_ins_bt_a21_0.COL19 AS COL19, delta_ins_bt_a21_0.COL20 AS COL20 
FROM (SELECT p_0_a21_0.COL0 AS COL0, p_0_a21_0.COL1 AS COL1, p_0_a21_0.COL2 AS COL2, p_0_a21_0.COL3 AS COL3, p_0_a21_0.COL4 AS COL4, p_0_a21_0.COL5 AS COL5, p_0_a21_0.COL6 AS COL6, p_0_a21_0.COL7 AS COL7, p_0_a21_0.COL8 AS COL8, p_0_a21_0.COL9 AS COL9, p_0_a21_0.COL10 AS COL10, p_0_a21_0.COL11 AS COL11, p_0_a21_0.COL12 AS COL12, p_0_a21_0.COL13 AS COL13, p_0_a21_0.COL14 AS COL14, p_0_a21_0.COL15 AS COL15, p_0_a21_0.COL16 AS COL16, p_0_a21_0.COL17 AS COL17, p_0_a21_0.COL18 AS COL18, p_0_a21_0.COL19 AS COL19, p_0_a21_0.COL20 AS COL20 
FROM (SELECT __tmp_delta_ins_d1_6_ar_a21_0.V AS COL0, __tmp_delta_ins_d1_6_ar_a21_0.L AS COL1, __tmp_delta_ins_d1_6_ar_a21_0.D AS COL2, __tmp_delta_ins_d1_6_ar_a21_0.R AS COL3, __tmp_delta_ins_d1_6_ar_a21_0.T AS COL4, __tmp_delta_ins_d1_6_ar_a21_0.AL1 AS COL5, __tmp_delta_ins_d1_6_ar_a21_0.AL2 AS COL6, __tmp_delta_ins_d1_6_ar_a21_0.AL3 AS COL7, __tmp_delta_ins_d1_6_ar_a21_0.AL4 AS COL8, __tmp_delta_ins_d1_6_ar_a21_0.AL5 AS COL9, __tmp_delta_ins_d1_6_ar_a21_0.LINEAGE AS COL10, __tmp_delta_ins_d1_6_ar_a21_0.COND1 AS COL11, __tmp_delta_ins_d1_6_ar_a21_0.COND2 AS COL12, __tmp_delta_ins_d1_6_ar_a21_0.COND3 AS COL13, __tmp_delta_ins_d1_6_ar_a21_0.COND4 AS COL14, __tmp_delta_ins_d1_6_ar_a21_0.COND5 AS COL15, __tmp_delta_ins_d1_6_ar_a21_0.COND6 AS COL16, __tmp_delta_ins_d1_6_ar_a21_0.COND7 AS COL17, __tmp_delta_ins_d1_6_ar_a21_0.COND8 AS COL18, __tmp_delta_ins_d1_6_ar_a21_0.COND9 AS COL19, __tmp_delta_ins_d1_6_ar_a21_0.COND10 AS COL20 
FROM __tmp_delta_ins_d1_6_ar AS __tmp_delta_ins_d1_6_ar_a21_0 
WHERE __tmp_delta_ins_d1_6_ar_a21_0.COND10  <  80 AND NOT EXISTS ( SELECT * 
FROM public.bt AS bt_a21 
WHERE bt_a21.V = __tmp_delta_ins_d1_6_ar_a21_0.V AND bt_a21.L = __tmp_delta_ins_d1_6_ar_a21_0.L AND bt_a21.D = __tmp_delta_ins_d1_6_ar_a21_0.D AND bt_a21.R = __tmp_delta_ins_d1_6_ar_a21_0.R AND bt_a21.T = __tmp_delta_ins_d1_6_ar_a21_0.T AND bt_a21.AL1 = __tmp_delta_ins_d1_6_ar_a21_0.AL1 AND bt_a21.AL2 = __tmp_delta_ins_d1_6_ar_a21_0.AL2 AND bt_a21.AL3 = __tmp_delta_ins_d1_6_ar_a21_0.AL3 AND bt_a21.AL4 = __tmp_delta_ins_d1_6_ar_a21_0.AL4 AND bt_a21.AL5 = __tmp_delta_ins_d1_6_ar_a21_0.AL5 AND bt_a21.LINEAGE = __tmp_delta_ins_d1_6_ar_a21_0.LINEAGE AND bt_a21.COND1 = __tmp_delta_ins_d1_6_ar_a21_0.COND1 AND bt_a21.COND2 = __tmp_delta_ins_d1_6_ar_a21_0.COND2 AND bt_a21.COND3 = __tmp_delta_ins_d1_6_ar_a21_0.COND3 AND bt_a21.COND4 = __tmp_delta_ins_d1_6_ar_a21_0.COND4 AND bt_a21.COND5 = __tmp_delta_ins_d1_6_ar_a21_0.COND5 AND bt_a21.COND6 = __tmp_delta_ins_d1_6_ar_a21_0.COND6 AND bt_a21.COND7 = __tmp_delta_ins_d1_6_ar_a21_0.COND7 AND bt_a21.COND8 = __tmp_delta_ins_d1_6_ar_a21_0.COND8 AND bt_a21.COND9 = __tmp_delta_ins_d1_6_ar_a21_0.COND9 AND bt_a21.COND10 = __tmp_delta_ins_d1_6_ar_a21_0.COND10 ) ) AS p_0_a21_0  ) AS delta_ins_bt_a21_0  ) AS delta_ins_bt_extra_alias) AS tbl; 


            IF array_delta_del_bt IS DISTINCT FROM NULL THEN 
                FOREACH temprec_delta_del_bt IN array array_delta_del_bt  LOOP 
                   DELETE FROM public.bt WHERE V =  temprec_delta_del_bt.V AND L =  temprec_delta_del_bt.L AND D =  temprec_delta_del_bt.D AND R =  temprec_delta_del_bt.R AND T =  temprec_delta_del_bt.T AND AL1 =  temprec_delta_del_bt.AL1 AND AL2 =  temprec_delta_del_bt.AL2 AND AL3 =  temprec_delta_del_bt.AL3 AND AL4 =  temprec_delta_del_bt.AL4 AND AL5 =  temprec_delta_del_bt.AL5 AND LINEAGE =  temprec_delta_del_bt.LINEAGE AND COND1 =  temprec_delta_del_bt.COND1 AND COND2 =  temprec_delta_del_bt.COND2 AND COND3 =  temprec_delta_del_bt.COND3 AND COND4 =  temprec_delta_del_bt.COND4 AND COND5 =  temprec_delta_del_bt.COND5 AND COND6 =  temprec_delta_del_bt.COND6 AND COND7 =  temprec_delta_del_bt.COND7 AND COND8 =  temprec_delta_del_bt.COND8 AND COND9 =  temprec_delta_del_bt.COND9 AND COND10 =  temprec_delta_del_bt.COND10;
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
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.d1_6"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.d1_6_run_shell(json_data);
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
                --DELETE FROM public.__dummy__d1_6_detected_deletions;
                INSERT INTO public.__dummy__d1_6_detected_deletions
                    SELECT xid, * FROM __tmp_delta_del_d1_6;

                --DELETE FROM public.__dummy__d1_6_detected_insertions;
                INSERT INTO public.__dummy__d1_6_detected_insertions
                    SELECT xid, * FROM __tmp_delta_ins_d1_6;
            END IF;
        END IF;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d1_6';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d1_6 ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d1_6_materialization()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_d1_6' OR table_name = '__tmp_delta_del_d1_6')
    THEN
        -- RAISE LOG 'execute procedure d1_6_materialization';
        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_ins_d1_6 ( LIKE public.d1_6 ) WITH OIDS ON COMMIT DELETE ROWS;
        CREATE CONSTRAINT TRIGGER __tmp_d1_6_trigger_delta_action_ins
        AFTER INSERT OR UPDATE OR DELETE ON 
            __tmp_delta_ins_d1_6 DEFERRABLE INITIALLY DEFERRED 
            FOR EACH ROW EXECUTE PROCEDURE public.d1_6_delta_action();

        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_del_d1_6 ( LIKE public.d1_6 ) WITH OIDS ON COMMIT DELETE ROWS;
        CREATE CONSTRAINT TRIGGER __tmp_d1_6_trigger_delta_action_del
        AFTER INSERT OR UPDATE OR DELETE ON 
            __tmp_delta_del_d1_6 DEFERRABLE INITIALLY DEFERRED 
            FOR EACH ROW EXECUTE PROCEDURE public.d1_6_delta_action();
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d1_6';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d1_6 ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS d1_6_trigger_materialization ON public.d1_6;
CREATE TRIGGER d1_6_trigger_materialization
    BEFORE INSERT OR UPDATE OR DELETE ON
      public.d1_6 FOR EACH STATEMENT EXECUTE PROCEDURE public.d1_6_materialization();

CREATE OR REPLACE FUNCTION public.d1_6_update()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    -- RAISE LOG 'execute procedure d1_6_update';
    IF TG_OP = 'INSERT' THEN
      -- RAISE LOG 'NEW: %', NEW;
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_del_d1_6 WHERE ROW(V,L,D,R,T,AL1,AL2,AL3,AL4,AL5,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = NEW;
      INSERT INTO __tmp_delta_ins_d1_6 SELECT (NEW).*; 
    ELSIF TG_OP = 'UPDATE' THEN
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_ins_d1_6 WHERE ROW(V,L,D,R,T,AL1,AL2,AL3,AL4,AL5,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = OLD;
      INSERT INTO __tmp_delta_del_d1_6 SELECT (OLD).*;
      DELETE FROM __tmp_delta_del_d1_6 WHERE ROW(V,L,D,R,T,AL1,AL2,AL3,AL4,AL5,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = NEW;
      INSERT INTO __tmp_delta_ins_d1_6 SELECT (NEW).*; 
    ELSIF TG_OP = 'DELETE' THEN
      -- RAISE LOG 'OLD: %', OLD;
      DELETE FROM __tmp_delta_ins_d1_6 WHERE ROW(V,L,D,R,T,AL1,AL2,AL3,AL4,AL5,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = OLD;
      INSERT INTO __tmp_delta_del_d1_6 SELECT (OLD).*;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d1_6';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d1_6 ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS d1_6_trigger_update ON public.d1_6;
CREATE TRIGGER d1_6_trigger_update
    INSTEAD OF INSERT OR UPDATE OR DELETE ON
      public.d1_6 FOR EACH ROW EXECUTE PROCEDURE public.d1_6_update();

CREATE OR REPLACE FUNCTION public.d1_6_propagate_updates ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS __tmp_d1_6_trigger_delta_action_ins, __tmp_d1_6_trigger_delta_action_del IMMEDIATE;
    SET CONSTRAINTS __tmp_d1_6_trigger_delta_action_ins, __tmp_d1_6_trigger_delta_action_del DEFERRED;
    DROP TABLE IF EXISTS d1_6_delta_action_flag;
    DROP TABLE IF EXISTS __tmp_delta_del_d1_6;
    DROP TABLE IF EXISTS __tmp_delta_ins_d1_6;
    RETURN true;
  END;
$$;

CREATE OR REPLACE FUNCTION public.clean_dummy_d1_6 ()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  xid int;
  BEGIN
    xid := (SELECT txid_current());
    DELETE FROM public.__dummy__d1_6_detected_deletions as t where t.txid = xid;
    DELETE FROM public.__dummy__d1_6_detected_insertions as t where t.txid = xid;
    RAISE LOG 'clean __dummy__d1_6_detected_deletions/insertions';
    RETURN NULL;
  END;
$$;

CREATE CONSTRAINT TRIGGER __zzz_clean_d1_6
    AFTER INSERT OR UPDATE OR DELETE ON
    public.bt DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.clean_dummy_d1_6();

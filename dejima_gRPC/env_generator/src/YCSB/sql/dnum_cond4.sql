CREATE OR REPLACE VIEW public.dnum AS 
SELECT __dummy__.COL0 AS ID,__dummy__.COL1 AS COL1,__dummy__.COL2 AS COL2,__dummy__.COL3 AS COL3,__dummy__.COL4 AS COL4,__dummy__.COL5 AS COL5,__dummy__.COL6 AS COL6,__dummy__.COL7 AS COL7,__dummy__.COL8 AS COL8,__dummy__.COL9 AS COL9,__dummy__.COL10 AS COL10,__dummy__.COL11 AS LINEAGE,__dummy__.COL12 AS COND1,__dummy__.COL13 AS COND2,__dummy__.COL14 AS COND3,__dummy__.COL15 AS COND4,__dummy__.COL16 AS COND5,__dummy__.COL17 AS COND6,__dummy__.COL18 AS COND7,__dummy__.COL19 AS COND8,__dummy__.COL20 AS COND9,__dummy__.COL21 AS COND10 
FROM (SELECT dnum_a22_0.COL0 AS COL0, dnum_a22_0.COL1 AS COL1, dnum_a22_0.COL2 AS COL2, dnum_a22_0.COL3 AS COL3, dnum_a22_0.COL4 AS COL4, dnum_a22_0.COL5 AS COL5, dnum_a22_0.COL6 AS COL6, dnum_a22_0.COL7 AS COL7, dnum_a22_0.COL8 AS COL8, dnum_a22_0.COL9 AS COL9, dnum_a22_0.COL10 AS COL10, dnum_a22_0.COL11 AS COL11, dnum_a22_0.COL12 AS COL12, dnum_a22_0.COL13 AS COL13, dnum_a22_0.COL14 AS COL14, dnum_a22_0.COL15 AS COL15, dnum_a22_0.COL16 AS COL16, dnum_a22_0.COL17 AS COL17, dnum_a22_0.COL18 AS COL18, dnum_a22_0.COL19 AS COL19, dnum_a22_0.COL20 AS COL20, dnum_a22_0.COL21 AS COL21 
FROM (SELECT bt_a22_0.ID AS COL0, bt_a22_0.COL1 AS COL1, bt_a22_0.COL2 AS COL2, bt_a22_0.COL3 AS COL3, bt_a22_0.COL4 AS COL4, bt_a22_0.COL5 AS COL5, bt_a22_0.COL6 AS COL6, bt_a22_0.COL7 AS COL7, bt_a22_0.COL8 AS COL8, bt_a22_0.COL9 AS COL9, bt_a22_0.COL10 AS COL10, bt_a22_0.LINEAGE AS COL11, bt_a22_0.COND1 AS COL12, bt_a22_0.COND2 AS COL13, bt_a22_0.COND3 AS COL14, bt_a22_0.COND4 AS COL15, bt_a22_0.COND5 AS COL16, bt_a22_0.COND6 AS COL17, bt_a22_0.COND7 AS COL18, bt_a22_0.COND8 AS COL19, bt_a22_0.COND9 AS COL20, bt_a22_0.COND10 AS COL21 
FROM public.bt AS bt_a22_0 
WHERE bt_a22_0.COND4  <  <border> ) AS dnum_a22_0  ) AS __dummy__;

CREATE EXTENSION IF NOT EXISTS plsh;

CREATE TABLE IF NOT EXISTS public.__dummy__dnum_detected_deletions (txid int, LIKE public.dnum );
CREATE INDEX IF NOT EXISTS idx__dummy__dnum_detected_deletions ON public.__dummy__dnum_detected_deletions (txid);
CREATE TABLE IF NOT EXISTS public.__dummy__dnum_detected_insertions (txid int, LIKE public.dnum );
CREATE INDEX IF NOT EXISTS idx__dummy__dnum_detected_insertions ON public.__dummy__dnum_detected_insertions (txid);

CREATE OR REPLACE FUNCTION public.dnum_get_detected_update_data(txid int)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  deletion_data text;
  insertion_data text;
  json_data text;
  BEGIN
    insertion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__dnum_detected_insertions as t where t.txid = $1);
    IF insertion_data IS NOT DISTINCT FROM NULL THEN 
        insertion_data := '[]';
    END IF; 
    deletion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__dnum_detected_deletions as t where t.txid = $1);
    IF deletion_data IS NOT DISTINCT FROM NULL THEN 
        deletion_data := '[]';
    END IF; 
    IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN 
        -- calcuate the update data
        json_data := concat('{"view": ' , '"public.dnum"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
        -- clear the update data
        --DELETE FROM public.__dummy__dnum_detected_deletions;
        --DELETE FROM public.__dummy__dnum_detected_insertions;
    END IF;
    RETURN json_data;
  END;
$$;

CREATE OR REPLACE FUNCTION public.dnum_run_shell(text) RETURNS text AS $$
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

CREATE OR REPLACE FUNCTION public.bt_materialization_for_dnum()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_bt_for_dnum' OR table_name = '__tmp_delta_del_bt_for_dnum')
    THEN
        -- RAISE LOG 'execute procedure bt_materialization_for_dnum';
        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_ins_bt_for_dnum ( LIKE public.bt ) WITH OIDS ON COMMIT DELETE ROWS;
        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_del_bt_for_dnum ( LIKE public.bt ) WITH OIDS ON COMMIT DELETE ROWS;
        
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

DROP TRIGGER IF EXISTS bt_trigger_materialization_for_dnum ON public.bt;
CREATE TRIGGER bt_trigger_materialization_for_dnum
    BEFORE INSERT OR UPDATE OR DELETE ON
    public.bt FOR EACH STATEMENT EXECUTE PROCEDURE public.bt_materialization_for_dnum();

CREATE OR REPLACE FUNCTION public.bt_update_for_dnum()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    -- RAISE LOG 'execute procedure bt_update_for_dnum';
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'dnum_delta_action_flag') THEN
        IF TG_OP = 'INSERT' THEN
        -- RAISE LOG 'NEW: %', NEW;
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_del_bt_for_dnum WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = NEW;
        INSERT INTO __tmp_delta_ins_bt_for_dnum SELECT (NEW).*; 
        ELSIF TG_OP = 'UPDATE' THEN
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_ins_bt_for_dnum WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = OLD;
        INSERT INTO __tmp_delta_del_bt_for_dnum SELECT (OLD).*;
        DELETE FROM __tmp_delta_del_bt_for_dnum WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = NEW;
        INSERT INTO __tmp_delta_ins_bt_for_dnum SELECT (NEW).*; 
        ELSIF TG_OP = 'DELETE' THEN
        -- RAISE LOG 'OLD: %', OLD;
        DELETE FROM __tmp_delta_ins_bt_for_dnum WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = OLD;
        INSERT INTO __tmp_delta_del_bt_for_dnum SELECT (OLD).*;
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

DROP TRIGGER IF EXISTS bt_trigger_update_for_dnum ON public.bt;
CREATE TRIGGER bt_trigger_update_for_dnum
    AFTER INSERT OR UPDATE OR DELETE ON
    public.bt FOR EACH ROW EXECUTE PROCEDURE public.bt_update_for_dnum();

CREATE OR REPLACE FUNCTION public.bt_detect_update_on_dnum()
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
detected_deletions public.dnum[];
detected_insertions public.dnum[];
delta_ins_size int;
delta_del_size int;
BEGIN
IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'bt_detect_update_on_dnum_flag') THEN
    CREATE TEMPORARY TABLE bt_detect_update_on_dnum_flag ON COMMIT DROP AS (SELECT true as finish);
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'dnum_delta_action_flag') THEN
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_bt_for_dnum AS tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_bt_for_dnum;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_bt_for_dnum tbl;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_bt_for_dnum;

        WITH __tmp_delta_ins_bt_for_dnum_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size), 
        __tmp_delta_del_bt_for_dnum_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_insertions FROM (SELECT __dummy__.COL0 AS ID,__dummy__.COL1 AS COL1,__dummy__.COL2 AS COL2,__dummy__.COL3 AS COL3,__dummy__.COL4 AS COL4,__dummy__.COL5 AS COL5,__dummy__.COL6 AS COL6,__dummy__.COL7 AS COL7,__dummy__.COL8 AS COL8,__dummy__.COL9 AS COL9,__dummy__.COL10 AS COL10,__dummy__.COL11 AS LINEAGE,__dummy__.COL12 AS COND1,__dummy__.COL13 AS COND2,__dummy__.COL14 AS COND3,__dummy__.COL15 AS COND4,__dummy__.COL16 AS COND5,__dummy__.COL17 AS COND6,__dummy__.COL18 AS COND7,__dummy__.COL19 AS COND8,__dummy__.COL20 AS COND9,__dummy__.COL21 AS COND10 
FROM (SELECT part_ins_dnum_a22_0.COL0 AS COL0, part_ins_dnum_a22_0.COL1 AS COL1, part_ins_dnum_a22_0.COL2 AS COL2, part_ins_dnum_a22_0.COL3 AS COL3, part_ins_dnum_a22_0.COL4 AS COL4, part_ins_dnum_a22_0.COL5 AS COL5, part_ins_dnum_a22_0.COL6 AS COL6, part_ins_dnum_a22_0.COL7 AS COL7, part_ins_dnum_a22_0.COL8 AS COL8, part_ins_dnum_a22_0.COL9 AS COL9, part_ins_dnum_a22_0.COL10 AS COL10, part_ins_dnum_a22_0.COL11 AS COL11, part_ins_dnum_a22_0.COL12 AS COL12, part_ins_dnum_a22_0.COL13 AS COL13, part_ins_dnum_a22_0.COL14 AS COL14, part_ins_dnum_a22_0.COL15 AS COL15, part_ins_dnum_a22_0.COL16 AS COL16, part_ins_dnum_a22_0.COL17 AS COL17, part_ins_dnum_a22_0.COL18 AS COL18, part_ins_dnum_a22_0.COL19 AS COL19, part_ins_dnum_a22_0.COL20 AS COL20, part_ins_dnum_a22_0.COL21 AS COL21 
FROM (SELECT p_0_a22_0.COL0 AS COL0, p_0_a22_0.COL1 AS COL1, p_0_a22_0.COL2 AS COL2, p_0_a22_0.COL3 AS COL3, p_0_a22_0.COL4 AS COL4, p_0_a22_0.COL5 AS COL5, p_0_a22_0.COL6 AS COL6, p_0_a22_0.COL7 AS COL7, p_0_a22_0.COL8 AS COL8, p_0_a22_0.COL9 AS COL9, p_0_a22_0.COL10 AS COL10, p_0_a22_0.COL11 AS COL11, p_0_a22_0.COL12 AS COL12, p_0_a22_0.COL13 AS COL13, p_0_a22_0.COL14 AS COL14, p_0_a22_0.COL15 AS COL15, p_0_a22_0.COL16 AS COL16, p_0_a22_0.COL17 AS COL17, p_0_a22_0.COL18 AS COL18, p_0_a22_0.COL19 AS COL19, p_0_a22_0.COL20 AS COL20, p_0_a22_0.COL21 AS COL21 
FROM (SELECT __tmp_delta_ins_bt_for_dnum_ar_a22_0.ID AS COL0, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COL1 AS COL1, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COL2 AS COL2, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COL3 AS COL3, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COL4 AS COL4, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COL5 AS COL5, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COL6 AS COL6, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COL7 AS COL7, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COL8 AS COL8, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COL9 AS COL9, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COL10 AS COL10, __tmp_delta_ins_bt_for_dnum_ar_a22_0.LINEAGE AS COL11, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COND1 AS COL12, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COND2 AS COL13, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COND3 AS COL14, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COND4 AS COL15, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COND5 AS COL16, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COND6 AS COL17, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COND7 AS COL18, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COND8 AS COL19, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COND9 AS COL20, __tmp_delta_ins_bt_for_dnum_ar_a22_0.COND10 AS COL21 
FROM __tmp_delta_ins_bt_for_dnum_ar AS __tmp_delta_ins_bt_for_dnum_ar_a22_0 
WHERE __tmp_delta_ins_bt_for_dnum_ar_a22_0.COND4  <  <border> ) AS p_0_a22_0  ) AS part_ins_dnum_a22_0  ) AS __dummy__) AS tbl;

        insertion_data := (SELECT (array_to_json(detected_insertions))::text);
        IF insertion_data IS NOT DISTINCT FROM NULL THEN 
            insertion_data := '[]';
        END IF; 

        WITH __tmp_delta_ins_bt_for_dnum_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size), 
        __tmp_delta_del_bt_for_dnum_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_deletions FROM (SELECT __dummy__.COL0 AS ID,__dummy__.COL1 AS COL1,__dummy__.COL2 AS COL2,__dummy__.COL3 AS COL3,__dummy__.COL4 AS COL4,__dummy__.COL5 AS COL5,__dummy__.COL6 AS COL6,__dummy__.COL7 AS COL7,__dummy__.COL8 AS COL8,__dummy__.COL9 AS COL9,__dummy__.COL10 AS COL10,__dummy__.COL11 AS LINEAGE,__dummy__.COL12 AS COND1,__dummy__.COL13 AS COND2,__dummy__.COL14 AS COND3,__dummy__.COL15 AS COND4,__dummy__.COL16 AS COND5,__dummy__.COL17 AS COND6,__dummy__.COL18 AS COND7,__dummy__.COL19 AS COND8,__dummy__.COL20 AS COND9,__dummy__.COL21 AS COND10 
FROM (SELECT part_del_dnum_a22_0.COL0 AS COL0, part_del_dnum_a22_0.COL1 AS COL1, part_del_dnum_a22_0.COL2 AS COL2, part_del_dnum_a22_0.COL3 AS COL3, part_del_dnum_a22_0.COL4 AS COL4, part_del_dnum_a22_0.COL5 AS COL5, part_del_dnum_a22_0.COL6 AS COL6, part_del_dnum_a22_0.COL7 AS COL7, part_del_dnum_a22_0.COL8 AS COL8, part_del_dnum_a22_0.COL9 AS COL9, part_del_dnum_a22_0.COL10 AS COL10, part_del_dnum_a22_0.COL11 AS COL11, part_del_dnum_a22_0.COL12 AS COL12, part_del_dnum_a22_0.COL13 AS COL13, part_del_dnum_a22_0.COL14 AS COL14, part_del_dnum_a22_0.COL15 AS COL15, part_del_dnum_a22_0.COL16 AS COL16, part_del_dnum_a22_0.COL17 AS COL17, part_del_dnum_a22_0.COL18 AS COL18, part_del_dnum_a22_0.COL19 AS COL19, part_del_dnum_a22_0.COL20 AS COL20, part_del_dnum_a22_0.COL21 AS COL21 
FROM (SELECT p_0_a22_0.COL0 AS COL0, p_0_a22_0.COL1 AS COL1, p_0_a22_0.COL2 AS COL2, p_0_a22_0.COL3 AS COL3, p_0_a22_0.COL4 AS COL4, p_0_a22_0.COL5 AS COL5, p_0_a22_0.COL6 AS COL6, p_0_a22_0.COL7 AS COL7, p_0_a22_0.COL8 AS COL8, p_0_a22_0.COL9 AS COL9, p_0_a22_0.COL10 AS COL10, p_0_a22_0.COL11 AS COL11, p_0_a22_0.COL12 AS COL12, p_0_a22_0.COL13 AS COL13, p_0_a22_0.COL14 AS COL14, p_0_a22_0.COL15 AS COL15, p_0_a22_0.COL16 AS COL16, p_0_a22_0.COL17 AS COL17, p_0_a22_0.COL18 AS COL18, p_0_a22_0.COL19 AS COL19, p_0_a22_0.COL20 AS COL20, p_0_a22_0.COL21 AS COL21 
FROM (SELECT __tmp_delta_del_bt_for_dnum_ar_a22_0.ID AS COL0, __tmp_delta_del_bt_for_dnum_ar_a22_0.COL1 AS COL1, __tmp_delta_del_bt_for_dnum_ar_a22_0.COL2 AS COL2, __tmp_delta_del_bt_for_dnum_ar_a22_0.COL3 AS COL3, __tmp_delta_del_bt_for_dnum_ar_a22_0.COL4 AS COL4, __tmp_delta_del_bt_for_dnum_ar_a22_0.COL5 AS COL5, __tmp_delta_del_bt_for_dnum_ar_a22_0.COL6 AS COL6, __tmp_delta_del_bt_for_dnum_ar_a22_0.COL7 AS COL7, __tmp_delta_del_bt_for_dnum_ar_a22_0.COL8 AS COL8, __tmp_delta_del_bt_for_dnum_ar_a22_0.COL9 AS COL9, __tmp_delta_del_bt_for_dnum_ar_a22_0.COL10 AS COL10, __tmp_delta_del_bt_for_dnum_ar_a22_0.LINEAGE AS COL11, __tmp_delta_del_bt_for_dnum_ar_a22_0.COND1 AS COL12, __tmp_delta_del_bt_for_dnum_ar_a22_0.COND2 AS COL13, __tmp_delta_del_bt_for_dnum_ar_a22_0.COND3 AS COL14, __tmp_delta_del_bt_for_dnum_ar_a22_0.COND4 AS COL15, __tmp_delta_del_bt_for_dnum_ar_a22_0.COND5 AS COL16, __tmp_delta_del_bt_for_dnum_ar_a22_0.COND6 AS COL17, __tmp_delta_del_bt_for_dnum_ar_a22_0.COND7 AS COL18, __tmp_delta_del_bt_for_dnum_ar_a22_0.COND8 AS COL19, __tmp_delta_del_bt_for_dnum_ar_a22_0.COND9 AS COL20, __tmp_delta_del_bt_for_dnum_ar_a22_0.COND10 AS COL21 
FROM __tmp_delta_del_bt_for_dnum_ar AS __tmp_delta_del_bt_for_dnum_ar_a22_0 
WHERE __tmp_delta_del_bt_for_dnum_ar_a22_0.COND4  <  <border> ) AS p_0_a22_0  ) AS part_del_dnum_a22_0  ) AS __dummy__) AS tbl;

        deletion_data := (  
        SELECT (array_to_json(detected_deletions))::text);
        IF deletion_data IS NOT DISTINCT FROM NULL THEN 
            deletion_data := '[]';
        END IF; 
        IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN 
            user_name := (SELECT session_user);
            IF NOT (user_name = 'dejima') THEN 
                xid := (SELECT txid_current());
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.dnum"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.dnum_run_shell(json_data);
                IF result = 'true' THEN 
                    DROP TABLE __tmp_delta_ins_bt_for_dnum;
                    DROP TABLE __tmp_delta_del_bt_for_dnum;
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
                -- DELETE FROM public.__dummy__dnum_detected_deletions;
                INSERT INTO public.__dummy__dnum_detected_deletions
                    ( SELECT xid, * FROM unnest(detected_deletions) as detected_deletions_alias );

                -- DELETE FROM public.__dummy__dnum_detected_insertions;
                INSERT INTO public.__dummy__dnum_detected_insertions
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
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the function public.bt_detect_update_on_dnum() ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS bt_detect_update_on_dnum ON public.bt;
CREATE CONSTRAINT TRIGGER bt_detect_update_on_dnum
    AFTER INSERT OR UPDATE OR DELETE ON
    public.bt DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.bt_detect_update_on_dnum();

CREATE OR REPLACE FUNCTION public.bt_propagate_updates_to_dnum ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS public.bt_detect_update_on_dnum IMMEDIATE;
    SET CONSTRAINTS public.bt_detect_update_on_dnum DEFERRED;
    DROP TABLE IF EXISTS bt_detect_update_on_dnum_flag;
    RETURN true;
  END;
$$;



CREATE OR REPLACE FUNCTION public.dnum_delta_action()
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
  array_delta_del public.dnum[];
  array_delta_ins public.dnum[];
  temprec_delta_del_bt public.bt%ROWTYPE;
            array_delta_del_bt public.bt[];
temprec_delta_ins_bt public.bt%ROWTYPE;
            array_delta_ins_bt public.bt[];
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'dnum_delta_action_flag') THEN
        -- RAISE LOG 'execute procedure dnum_delta_action';
        CREATE TEMPORARY TABLE dnum_delta_action_flag ON COMMIT DROP AS (SELECT true as finish);
        IF EXISTS (SELECT WHERE false )
        THEN 
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the view are violated';
        END IF;
        IF EXISTS (SELECT WHERE false )
        THEN 
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the source relations are violated';
        END IF;
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_dnum AS tbl;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_dnum as tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_dnum;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_dnum;
        
            WITH __tmp_delta_del_dnum_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_dnum_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_del_bt FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11,COL12,COL13,COL14,COL15,COL16,COL17,COL18,COL19,COL20,COL21) :: public.bt).* 
            FROM (SELECT delta_del_bt_a22_0.COL0 AS COL0, delta_del_bt_a22_0.COL1 AS COL1, delta_del_bt_a22_0.COL2 AS COL2, delta_del_bt_a22_0.COL3 AS COL3, delta_del_bt_a22_0.COL4 AS COL4, delta_del_bt_a22_0.COL5 AS COL5, delta_del_bt_a22_0.COL6 AS COL6, delta_del_bt_a22_0.COL7 AS COL7, delta_del_bt_a22_0.COL8 AS COL8, delta_del_bt_a22_0.COL9 AS COL9, delta_del_bt_a22_0.COL10 AS COL10, delta_del_bt_a22_0.COL11 AS COL11, delta_del_bt_a22_0.COL12 AS COL12, delta_del_bt_a22_0.COL13 AS COL13, delta_del_bt_a22_0.COL14 AS COL14, delta_del_bt_a22_0.COL15 AS COL15, delta_del_bt_a22_0.COL16 AS COL16, delta_del_bt_a22_0.COL17 AS COL17, delta_del_bt_a22_0.COL18 AS COL18, delta_del_bt_a22_0.COL19 AS COL19, delta_del_bt_a22_0.COL20 AS COL20, delta_del_bt_a22_0.COL21 AS COL21 
FROM (SELECT p_0_a22_0.COL0 AS COL0, p_0_a22_0.COL1 AS COL1, p_0_a22_0.COL2 AS COL2, p_0_a22_0.COL3 AS COL3, p_0_a22_0.COL4 AS COL4, p_0_a22_0.COL5 AS COL5, p_0_a22_0.COL6 AS COL6, p_0_a22_0.COL7 AS COL7, p_0_a22_0.COL8 AS COL8, p_0_a22_0.COL9 AS COL9, p_0_a22_0.COL10 AS COL10, p_0_a22_0.COL11 AS COL11, p_0_a22_0.COL12 AS COL12, p_0_a22_0.COL13 AS COL13, p_0_a22_0.COL14 AS COL14, p_0_a22_0.COL15 AS COL15, p_0_a22_0.COL16 AS COL16, p_0_a22_0.COL17 AS COL17, p_0_a22_0.COL18 AS COL18, p_0_a22_0.COL19 AS COL19, p_0_a22_0.COL20 AS COL20, p_0_a22_0.COL21 AS COL21 
FROM (SELECT bt_a22_1.ID AS COL0, bt_a22_1.COL1 AS COL1, bt_a22_1.COL2 AS COL2, bt_a22_1.COL3 AS COL3, bt_a22_1.COL4 AS COL4, bt_a22_1.COL5 AS COL5, bt_a22_1.COL6 AS COL6, bt_a22_1.COL7 AS COL7, bt_a22_1.COL8 AS COL8, bt_a22_1.COL9 AS COL9, bt_a22_1.COL10 AS COL10, bt_a22_1.LINEAGE AS COL11, bt_a22_1.COND1 AS COL12, bt_a22_1.COND2 AS COL13, bt_a22_1.COND3 AS COL14, bt_a22_1.COND4 AS COL15, bt_a22_1.COND5 AS COL16, bt_a22_1.COND6 AS COL17, bt_a22_1.COND7 AS COL18, bt_a22_1.COND8 AS COL19, bt_a22_1.COND9 AS COL20, bt_a22_1.COND10 AS COL21 
FROM __tmp_delta_del_dnum_ar AS __tmp_delta_del_dnum_ar_a22_0, public.bt AS bt_a22_1 
WHERE bt_a22_1.COL7 = __tmp_delta_del_dnum_ar_a22_0.COL7 AND bt_a22_1.COL5 = __tmp_delta_del_dnum_ar_a22_0.COL5 AND bt_a22_1.COL2 = __tmp_delta_del_dnum_ar_a22_0.COL2 AND bt_a22_1.COND10 = __tmp_delta_del_dnum_ar_a22_0.COND10 AND bt_a22_1.COND5 = __tmp_delta_del_dnum_ar_a22_0.COND5 AND bt_a22_1.COND7 = __tmp_delta_del_dnum_ar_a22_0.COND7 AND bt_a22_1.COL6 = __tmp_delta_del_dnum_ar_a22_0.COL6 AND bt_a22_1.COND1 = __tmp_delta_del_dnum_ar_a22_0.COND1 AND bt_a22_1.COL1 = __tmp_delta_del_dnum_ar_a22_0.COL1 AND bt_a22_1.COL3 = __tmp_delta_del_dnum_ar_a22_0.COL3 AND bt_a22_1.COL8 = __tmp_delta_del_dnum_ar_a22_0.COL8 AND bt_a22_1.COND4 = __tmp_delta_del_dnum_ar_a22_0.COND4 AND bt_a22_1.COND8 = __tmp_delta_del_dnum_ar_a22_0.COND8 AND bt_a22_1.COL9 = __tmp_delta_del_dnum_ar_a22_0.COL9 AND bt_a22_1.ID = __tmp_delta_del_dnum_ar_a22_0.ID AND bt_a22_1.COND2 = __tmp_delta_del_dnum_ar_a22_0.COND2 AND bt_a22_1.COND3 = __tmp_delta_del_dnum_ar_a22_0.COND3 AND bt_a22_1.COL10 = __tmp_delta_del_dnum_ar_a22_0.COL10 AND bt_a22_1.COND9 = __tmp_delta_del_dnum_ar_a22_0.COND9 AND bt_a22_1.COND6 = __tmp_delta_del_dnum_ar_a22_0.COND6 AND bt_a22_1.LINEAGE = __tmp_delta_del_dnum_ar_a22_0.LINEAGE AND bt_a22_1.COL4 = __tmp_delta_del_dnum_ar_a22_0.COL4 AND bt_a22_1.COND4  <  <border> ) AS p_0_a22_0  ) AS delta_del_bt_a22_0  ) AS delta_del_bt_extra_alias) AS tbl;


            WITH __tmp_delta_del_dnum_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_dnum_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_ins_bt FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11,COL12,COL13,COL14,COL15,COL16,COL17,COL18,COL19,COL20,COL21) :: public.bt).* 
            FROM (SELECT delta_ins_bt_a22_0.COL0 AS COL0, delta_ins_bt_a22_0.COL1 AS COL1, delta_ins_bt_a22_0.COL2 AS COL2, delta_ins_bt_a22_0.COL3 AS COL3, delta_ins_bt_a22_0.COL4 AS COL4, delta_ins_bt_a22_0.COL5 AS COL5, delta_ins_bt_a22_0.COL6 AS COL6, delta_ins_bt_a22_0.COL7 AS COL7, delta_ins_bt_a22_0.COL8 AS COL8, delta_ins_bt_a22_0.COL9 AS COL9, delta_ins_bt_a22_0.COL10 AS COL10, delta_ins_bt_a22_0.COL11 AS COL11, delta_ins_bt_a22_0.COL12 AS COL12, delta_ins_bt_a22_0.COL13 AS COL13, delta_ins_bt_a22_0.COL14 AS COL14, delta_ins_bt_a22_0.COL15 AS COL15, delta_ins_bt_a22_0.COL16 AS COL16, delta_ins_bt_a22_0.COL17 AS COL17, delta_ins_bt_a22_0.COL18 AS COL18, delta_ins_bt_a22_0.COL19 AS COL19, delta_ins_bt_a22_0.COL20 AS COL20, delta_ins_bt_a22_0.COL21 AS COL21 
FROM (SELECT p_0_a22_0.COL0 AS COL0, p_0_a22_0.COL1 AS COL1, p_0_a22_0.COL2 AS COL2, p_0_a22_0.COL3 AS COL3, p_0_a22_0.COL4 AS COL4, p_0_a22_0.COL5 AS COL5, p_0_a22_0.COL6 AS COL6, p_0_a22_0.COL7 AS COL7, p_0_a22_0.COL8 AS COL8, p_0_a22_0.COL9 AS COL9, p_0_a22_0.COL10 AS COL10, p_0_a22_0.COL11 AS COL11, p_0_a22_0.COL12 AS COL12, p_0_a22_0.COL13 AS COL13, p_0_a22_0.COL14 AS COL14, p_0_a22_0.COL15 AS COL15, p_0_a22_0.COL16 AS COL16, p_0_a22_0.COL17 AS COL17, p_0_a22_0.COL18 AS COL18, p_0_a22_0.COL19 AS COL19, p_0_a22_0.COL20 AS COL20, p_0_a22_0.COL21 AS COL21 
FROM (SELECT __tmp_delta_ins_dnum_ar_a22_0.ID AS COL0, __tmp_delta_ins_dnum_ar_a22_0.COL1 AS COL1, __tmp_delta_ins_dnum_ar_a22_0.COL2 AS COL2, __tmp_delta_ins_dnum_ar_a22_0.COL3 AS COL3, __tmp_delta_ins_dnum_ar_a22_0.COL4 AS COL4, __tmp_delta_ins_dnum_ar_a22_0.COL5 AS COL5, __tmp_delta_ins_dnum_ar_a22_0.COL6 AS COL6, __tmp_delta_ins_dnum_ar_a22_0.COL7 AS COL7, __tmp_delta_ins_dnum_ar_a22_0.COL8 AS COL8, __tmp_delta_ins_dnum_ar_a22_0.COL9 AS COL9, __tmp_delta_ins_dnum_ar_a22_0.COL10 AS COL10, __tmp_delta_ins_dnum_ar_a22_0.LINEAGE AS COL11, __tmp_delta_ins_dnum_ar_a22_0.COND1 AS COL12, __tmp_delta_ins_dnum_ar_a22_0.COND2 AS COL13, __tmp_delta_ins_dnum_ar_a22_0.COND3 AS COL14, __tmp_delta_ins_dnum_ar_a22_0.COND4 AS COL15, __tmp_delta_ins_dnum_ar_a22_0.COND5 AS COL16, __tmp_delta_ins_dnum_ar_a22_0.COND6 AS COL17, __tmp_delta_ins_dnum_ar_a22_0.COND7 AS COL18, __tmp_delta_ins_dnum_ar_a22_0.COND8 AS COL19, __tmp_delta_ins_dnum_ar_a22_0.COND9 AS COL20, __tmp_delta_ins_dnum_ar_a22_0.COND10 AS COL21 
FROM __tmp_delta_ins_dnum_ar AS __tmp_delta_ins_dnum_ar_a22_0 
WHERE __tmp_delta_ins_dnum_ar_a22_0.COND4  <  <border> AND NOT EXISTS ( SELECT * 
FROM public.bt AS bt_a22 
WHERE bt_a22.COND10 = __tmp_delta_ins_dnum_ar_a22_0.COND10 AND bt_a22.COND9 = __tmp_delta_ins_dnum_ar_a22_0.COND9 AND bt_a22.COND8 = __tmp_delta_ins_dnum_ar_a22_0.COND8 AND bt_a22.COND7 = __tmp_delta_ins_dnum_ar_a22_0.COND7 AND bt_a22.COND6 = __tmp_delta_ins_dnum_ar_a22_0.COND6 AND bt_a22.COND5 = __tmp_delta_ins_dnum_ar_a22_0.COND5 AND bt_a22.COND4 = __tmp_delta_ins_dnum_ar_a22_0.COND4 AND bt_a22.COND3 = __tmp_delta_ins_dnum_ar_a22_0.COND3 AND bt_a22.COND2 = __tmp_delta_ins_dnum_ar_a22_0.COND2 AND bt_a22.COND1 = __tmp_delta_ins_dnum_ar_a22_0.COND1 AND bt_a22.LINEAGE = __tmp_delta_ins_dnum_ar_a22_0.LINEAGE AND bt_a22.COL10 = __tmp_delta_ins_dnum_ar_a22_0.COL10 AND bt_a22.COL9 = __tmp_delta_ins_dnum_ar_a22_0.COL9 AND bt_a22.COL8 = __tmp_delta_ins_dnum_ar_a22_0.COL8 AND bt_a22.COL7 = __tmp_delta_ins_dnum_ar_a22_0.COL7 AND bt_a22.COL6 = __tmp_delta_ins_dnum_ar_a22_0.COL6 AND bt_a22.COL5 = __tmp_delta_ins_dnum_ar_a22_0.COL5 AND bt_a22.COL4 = __tmp_delta_ins_dnum_ar_a22_0.COL4 AND bt_a22.COL3 = __tmp_delta_ins_dnum_ar_a22_0.COL3 AND bt_a22.COL2 = __tmp_delta_ins_dnum_ar_a22_0.COL2 AND bt_a22.COL1 = __tmp_delta_ins_dnum_ar_a22_0.COL1 AND bt_a22.ID = __tmp_delta_ins_dnum_ar_a22_0.ID ) ) AS p_0_a22_0  ) AS delta_ins_bt_a22_0  ) AS delta_ins_bt_extra_alias) AS tbl; 


            IF array_delta_del_bt IS DISTINCT FROM NULL THEN 
                FOREACH temprec_delta_del_bt IN array array_delta_del_bt  LOOP 
                   DELETE FROM public.bt WHERE ID =  temprec_delta_del_bt.ID AND COL1 =  temprec_delta_del_bt.COL1 AND COL2 =  temprec_delta_del_bt.COL2 AND COL3 =  temprec_delta_del_bt.COL3 AND COL4 =  temprec_delta_del_bt.COL4 AND COL5 =  temprec_delta_del_bt.COL5 AND COL6 =  temprec_delta_del_bt.COL6 AND COL7 =  temprec_delta_del_bt.COL7 AND COL8 =  temprec_delta_del_bt.COL8 AND COL9 =  temprec_delta_del_bt.COL9 AND COL10 =  temprec_delta_del_bt.COL10 AND LINEAGE =  temprec_delta_del_bt.LINEAGE AND COND1 =  temprec_delta_del_bt.COND1 AND COND2 =  temprec_delta_del_bt.COND2 AND COND3 =  temprec_delta_del_bt.COND3 AND COND4 =  temprec_delta_del_bt.COND4 AND COND5 =  temprec_delta_del_bt.COND5 AND COND6 =  temprec_delta_del_bt.COND6 AND COND7 =  temprec_delta_del_bt.COND7 AND COND8 =  temprec_delta_del_bt.COND8 AND COND9 =  temprec_delta_del_bt.COND9 AND COND10 =  temprec_delta_del_bt.COND10;
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
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.dnum"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.dnum_run_shell(json_data);
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
                --DELETE FROM public.__dummy__dnum_detected_deletions;
                INSERT INTO public.__dummy__dnum_detected_deletions
                    SELECT xid, * FROM __tmp_delta_del_dnum;

                --DELETE FROM public.__dummy__dnum_detected_insertions;
                INSERT INTO public.__dummy__dnum_detected_insertions
                    SELECT xid, * FROM __tmp_delta_ins_dnum;
            END IF;
        END IF;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.dnum';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.dnum ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

CREATE OR REPLACE FUNCTION public.dnum_materialization()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_dnum' OR table_name = '__tmp_delta_del_dnum')
    THEN
        -- RAISE LOG 'execute procedure dnum_materialization';
        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_ins_dnum ( LIKE public.dnum ) WITH OIDS ON COMMIT DELETE ROWS;
        CREATE CONSTRAINT TRIGGER __tmp_dnum_trigger_delta_action_ins
        AFTER INSERT OR UPDATE OR DELETE ON 
            __tmp_delta_ins_dnum DEFERRABLE INITIALLY DEFERRED 
            FOR EACH ROW EXECUTE PROCEDURE public.dnum_delta_action();

        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_del_dnum ( LIKE public.dnum ) WITH OIDS ON COMMIT DELETE ROWS;
        CREATE CONSTRAINT TRIGGER __tmp_dnum_trigger_delta_action_del
        AFTER INSERT OR UPDATE OR DELETE ON 
            __tmp_delta_del_dnum DEFERRABLE INITIALLY DEFERRED 
            FOR EACH ROW EXECUTE PROCEDURE public.dnum_delta_action();
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.dnum';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.dnum ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS dnum_trigger_materialization ON public.dnum;
CREATE TRIGGER dnum_trigger_materialization
    BEFORE INSERT OR UPDATE OR DELETE ON
      public.dnum FOR EACH STATEMENT EXECUTE PROCEDURE public.dnum_materialization();

CREATE OR REPLACE FUNCTION public.dnum_update()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    -- RAISE LOG 'execute procedure dnum_update';
    IF TG_OP = 'INSERT' THEN
      -- RAISE LOG 'NEW: %', NEW;
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_del_dnum WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = NEW;
      INSERT INTO __tmp_delta_ins_dnum SELECT (NEW).*; 
    ELSIF TG_OP = 'UPDATE' THEN
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_ins_dnum WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = OLD;
      INSERT INTO __tmp_delta_del_dnum SELECT (OLD).*;
      DELETE FROM __tmp_delta_del_dnum WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = NEW;
      INSERT INTO __tmp_delta_ins_dnum SELECT (NEW).*; 
    ELSIF TG_OP = 'DELETE' THEN
      -- RAISE LOG 'OLD: %', OLD;
      DELETE FROM __tmp_delta_ins_dnum WHERE ROW(ID,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,LINEAGE,COND1,COND2,COND3,COND4,COND5,COND6,COND7,COND8,COND9,COND10) = OLD;
      INSERT INTO __tmp_delta_del_dnum SELECT (OLD).*;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.dnum';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.dnum ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS dnum_trigger_update ON public.dnum;
CREATE TRIGGER dnum_trigger_update
    INSTEAD OF INSERT OR UPDATE OR DELETE ON
      public.dnum FOR EACH ROW EXECUTE PROCEDURE public.dnum_update();

CREATE OR REPLACE FUNCTION public.dnum_propagate_updates ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS __tmp_dnum_trigger_delta_action_ins, __tmp_dnum_trigger_delta_action_del IMMEDIATE;
    SET CONSTRAINTS __tmp_dnum_trigger_delta_action_ins, __tmp_dnum_trigger_delta_action_del DEFERRED;
    DROP TABLE IF EXISTS dnum_delta_action_flag;
    DROP TABLE IF EXISTS __tmp_delta_del_dnum;
    DROP TABLE IF EXISTS __tmp_delta_ins_dnum;
    RETURN true;
  END;
$$;

CREATE OR REPLACE FUNCTION public.clean_dummy_dnum ()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  xid int;
  BEGIN
    xid := (SELECT txid_current());
    DELETE FROM public.__dummy__dnum_detected_deletions as t where t.txid = xid;
    DELETE FROM public.__dummy__dnum_detected_insertions as t where t.txid = xid;
    RAISE LOG 'clean __dummy__dnum_detected_deletions/insertions';
    RETURN NULL;
  END;
$$;

CREATE CONSTRAINT TRIGGER __zzz_clean_dnum
    AFTER INSERT OR UPDATE OR DELETE ON
    public.bt DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.clean_dummy_dnum();

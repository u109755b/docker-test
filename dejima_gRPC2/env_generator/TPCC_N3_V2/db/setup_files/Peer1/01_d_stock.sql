CREATE OR REPLACE VIEW public.d_stock AS 
SELECT __dummy__.COL0 AS S_W_ID, __dummy__.COL1 AS S_I_ID, __dummy__.COL2 AS S_QUANTITY, __dummy__.COL3 AS S_YTD, __dummy__.COL4 AS S_ORDER_CNT, __dummy__.COL5 AS S_REMOTE_CNT, __dummy__.COL6 AS S_DATA, __dummy__.COL7 AS S_DIST_01, __dummy__.COL8 AS S_DIST_02, __dummy__.COL9 AS S_DIST_03, __dummy__.COL10 AS S_DIST_04, __dummy__.COL11 AS S_DIST_05, __dummy__.COL12 AS S_DIST_06, __dummy__.COL13 AS S_DIST_07, __dummy__.COL14 AS S_DIST_08, __dummy__.COL15 AS S_DIST_09, __dummy__.COL16 AS S_DIST_10, __dummy__.COL17 AS LINEAGE FROM (SELECT d_stock_a18_0.COL0 AS COL0, d_stock_a18_0.COL1 AS COL1, d_stock_a18_0.COL2 AS COL2, d_stock_a18_0.COL3 AS COL3, d_stock_a18_0.COL4 AS COL4, d_stock_a18_0.COL5 AS COL5, d_stock_a18_0.COL6 AS COL6, d_stock_a18_0.COL7 AS COL7, d_stock_a18_0.COL8 AS COL8, d_stock_a18_0.COL9 AS COL9, d_stock_a18_0.COL10 AS COL10, d_stock_a18_0.COL11 AS COL11, d_stock_a18_0.COL12 AS COL12, d_stock_a18_0.COL13 AS COL13, d_stock_a18_0.COL14 AS COL14, d_stock_a18_0.COL15 AS COL15, d_stock_a18_0.COL16 AS COL16, d_stock_a18_0.COL17 AS COL17 FROM (SELECT stock_a18_0.S_W_ID AS COL0, stock_a18_0.S_I_ID AS COL1, stock_a18_0.S_QUANTITY AS COL2, stock_a18_0.S_YTD AS COL3, stock_a18_0.S_ORDER_CNT AS COL4, stock_a18_0.S_REMOTE_CNT AS COL5, stock_a18_0.S_DATA AS COL6, stock_a18_0.S_DIST_01 AS COL7, stock_a18_0.S_DIST_02 AS COL8, stock_a18_0.S_DIST_03 AS COL9, stock_a18_0.S_DIST_04 AS COL10, stock_a18_0.S_DIST_05 AS COL11, stock_a18_0.S_DIST_06 AS COL12, stock_a18_0.S_DIST_07 AS COL13, stock_a18_0.S_DIST_08 AS COL14, stock_a18_0.S_DIST_09 AS COL15, stock_a18_0.S_DIST_10 AS COL16, stock_a18_0.LINEAGE AS COL17 FROM public.stock AS stock_a18_0   ) AS d_stock_a18_0   ) AS __dummy__   ;

CREATE EXTENSION IF NOT EXISTS plsh;

CREATE TABLE IF NOT EXISTS public.__dummy__d_stock_detected_deletions (txid int, LIKE public.d_stock );
CREATE INDEX IF NOT EXISTS idx__dummy__d_stock_detected_deletions ON public.__dummy__d_stock_detected_deletions (txid);
CREATE TABLE IF NOT EXISTS public.__dummy__d_stock_detected_insertions (txid int, LIKE public.d_stock );
CREATE INDEX IF NOT EXISTS idx__dummy__d_stock_detected_insertions ON public.__dummy__d_stock_detected_insertions (txid);

CREATE OR REPLACE FUNCTION public.d_stock_get_detected_update_data(txid int)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  deletion_data text;
  insertion_data text;
  json_data text;
  BEGIN
    insertion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__d_stock_detected_insertions as t where t.txid = $1);
    IF insertion_data IS NOT DISTINCT FROM NULL THEN
        insertion_data := '[]';
    END IF;
    deletion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__d_stock_detected_deletions as t where t.txid = $1);
    IF deletion_data IS NOT DISTINCT FROM NULL THEN
        deletion_data := '[]';
    END IF;
    IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN
        -- calcuate the update data
        json_data := concat('{"view": ' , '"public.d_stock"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
        -- clear the update data
        DELETE FROM public.__dummy__d_stock_detected_deletions t where t.txid = $1;
        DELETE FROM public.__dummy__d_stock_detected_insertions t where t.txid = $1;
    END IF;
    RETURN json_data;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d_stock_run_shell(text) RETURNS text AS $$
#!/bin/sh

result=$(curl -s -X POST -H "Content-Type: application/json" $DEJIMA_EXECUTION_ENDPOINT -d "$1")
if  [ "$result" = "true" ];  then
    echo "true"
else 
    echo $result
fi
$$ LANGUAGE plsh;

CREATE OR REPLACE FUNCTION public.stock_materialization_for_d_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_stock_for_d_stock' OR table_name = '__tmp_delta_del_stock_for_d_stock')
    THEN
        -- RAISE LOG 'execute procedure stock_materialization_for_d_stock';
        CREATE TEMPORARY TABLE __tmp_delta_ins_stock_for_d_stock ( LIKE public.stock ) WITH OIDS ON COMMIT DROP;
        CREATE TEMPORARY TABLE __tmp_delta_del_stock_for_d_stock ( LIKE public.stock ) WITH OIDS ON COMMIT DROP;

    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.stock';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.stock ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS stock_trigger_materialization_for_d_stock ON public.stock;
CREATE TRIGGER stock_trigger_materialization_for_d_stock
    BEFORE INSERT OR UPDATE OR DELETE ON
    public.stock FOR EACH STATEMENT EXECUTE PROCEDURE public.stock_materialization_for_d_stock();

CREATE OR REPLACE FUNCTION public.stock_update_for_d_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    -- RAISE LOG 'execute procedure stock_update_for_d_stock';
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd_stock_delta_action_flag') THEN
        IF TG_OP = 'INSERT' THEN
        -- RAISE LOG 'NEW: %', NEW;
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_del_stock_for_d_stock WHERE ROW(S_W_ID,S_I_ID,S_QUANTITY,S_YTD,S_ORDER_CNT,S_REMOTE_CNT,S_DATA,S_DIST_01,S_DIST_02,S_DIST_03,S_DIST_04,S_DIST_05,S_DIST_06,S_DIST_07,S_DIST_08,S_DIST_09,S_DIST_10,LINEAGE)= NEW;
        INSERT INTO __tmp_delta_ins_stock_for_d_stock SELECT (NEW).*;
        ELSIF TG_OP = 'UPDATE' THEN
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_ins_stock_for_d_stock WHERE ROW(S_W_ID,S_I_ID,S_QUANTITY,S_YTD,S_ORDER_CNT,S_REMOTE_CNT,S_DATA,S_DIST_01,S_DIST_02,S_DIST_03,S_DIST_04,S_DIST_05,S_DIST_06,S_DIST_07,S_DIST_08,S_DIST_09,S_DIST_10,LINEAGE) = OLD;
        INSERT INTO __tmp_delta_del_stock_for_d_stock SELECT (OLD).*;
        DELETE FROM __tmp_delta_del_stock_for_d_stock WHERE ROW(S_W_ID,S_I_ID,S_QUANTITY,S_YTD,S_ORDER_CNT,S_REMOTE_CNT,S_DATA,S_DIST_01,S_DIST_02,S_DIST_03,S_DIST_04,S_DIST_05,S_DIST_06,S_DIST_07,S_DIST_08,S_DIST_09,S_DIST_10,LINEAGE) = NEW;
        INSERT INTO __tmp_delta_ins_stock_for_d_stock SELECT (NEW).*;
        ELSIF TG_OP = 'DELETE' THEN
        -- RAISE LOG 'OLD: %', OLD;
        DELETE FROM __tmp_delta_ins_stock_for_d_stock WHERE ROW(S_W_ID,S_I_ID,S_QUANTITY,S_YTD,S_ORDER_CNT,S_REMOTE_CNT,S_DATA,S_DIST_01,S_DIST_02,S_DIST_03,S_DIST_04,S_DIST_05,S_DIST_06,S_DIST_07,S_DIST_08,S_DIST_09,S_DIST_10,LINEAGE) = OLD;
        INSERT INTO __tmp_delta_del_stock_for_d_stock SELECT (OLD).*;
        END IF;
    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.stock';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.stock ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS stock_trigger_update_for_d_stock ON public.stock;
CREATE TRIGGER stock_trigger_update_for_d_stock
    AFTER INSERT OR UPDATE OR DELETE ON
    public.stock FOR EACH ROW EXECUTE PROCEDURE public.stock_update_for_d_stock();

CREATE OR REPLACE FUNCTION public.stock_detect_update_on_d_stock()
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
array_delta_del public.stock[];
array_delta_ins public.stock[];
detected_deletions public.d_stock[];
detected_insertions public.d_stock[];
delta_ins_size int;
delta_del_size int;
BEGIN
IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'stock_detect_update_on_d_stock_flag') THEN
    CREATE TEMPORARY TABLE stock_detect_update_on_d_stock_flag ON COMMIT DROP AS (SELECT true as finish);
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd_stock_delta_action_flag') THEN
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_stock_for_d_stock AS tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_stock_for_d_stock;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_stock_for_d_stock tbl;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_stock_for_d_stock;

        WITH __tmp_delta_ins_stock_for_d_stock_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size),
        __tmp_delta_del_stock_for_d_stock_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_insertions FROM (SELECT __dummy__.COL0 AS S_W_ID, __dummy__.COL1 AS S_I_ID, __dummy__.COL2 AS S_QUANTITY, __dummy__.COL3 AS S_YTD, __dummy__.COL4 AS S_ORDER_CNT, __dummy__.COL5 AS S_REMOTE_CNT, __dummy__.COL6 AS S_DATA, __dummy__.COL7 AS S_DIST_01, __dummy__.COL8 AS S_DIST_02, __dummy__.COL9 AS S_DIST_03, __dummy__.COL10 AS S_DIST_04, __dummy__.COL11 AS S_DIST_05, __dummy__.COL12 AS S_DIST_06, __dummy__.COL13 AS S_DIST_07, __dummy__.COL14 AS S_DIST_08, __dummy__.COL15 AS S_DIST_09, __dummy__.COL16 AS S_DIST_10, __dummy__.COL17 AS LINEAGE FROM (SELECT part_ins_d_stock_a18_0.COL0 AS COL0, part_ins_d_stock_a18_0.COL1 AS COL1, part_ins_d_stock_a18_0.COL2 AS COL2, part_ins_d_stock_a18_0.COL3 AS COL3, part_ins_d_stock_a18_0.COL4 AS COL4, part_ins_d_stock_a18_0.COL5 AS COL5, part_ins_d_stock_a18_0.COL6 AS COL6, part_ins_d_stock_a18_0.COL7 AS COL7, part_ins_d_stock_a18_0.COL8 AS COL8, part_ins_d_stock_a18_0.COL9 AS COL9, part_ins_d_stock_a18_0.COL10 AS COL10, part_ins_d_stock_a18_0.COL11 AS COL11, part_ins_d_stock_a18_0.COL12 AS COL12, part_ins_d_stock_a18_0.COL13 AS COL13, part_ins_d_stock_a18_0.COL14 AS COL14, part_ins_d_stock_a18_0.COL15 AS COL15, part_ins_d_stock_a18_0.COL16 AS COL16, part_ins_d_stock_a18_0.COL17 AS COL17 FROM (SELECT p_0_a18_0.COL0 AS COL0, p_0_a18_0.COL1 AS COL1, p_0_a18_0.COL2 AS COL2, p_0_a18_0.COL3 AS COL3, p_0_a18_0.COL4 AS COL4, p_0_a18_0.COL5 AS COL5, p_0_a18_0.COL6 AS COL6, p_0_a18_0.COL7 AS COL7, p_0_a18_0.COL8 AS COL8, p_0_a18_0.COL9 AS COL9, p_0_a18_0.COL10 AS COL10, p_0_a18_0.COL11 AS COL11, p_0_a18_0.COL12 AS COL12, p_0_a18_0.COL13 AS COL13, p_0_a18_0.COL14 AS COL14, p_0_a18_0.COL15 AS COL15, p_0_a18_0.COL16 AS COL16, p_0_a18_0.COL17 AS COL17 FROM (SELECT __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_W_ID AS COL0, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_I_ID AS COL1, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_QUANTITY AS COL2, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_YTD AS COL3, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_ORDER_CNT AS COL4, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_REMOTE_CNT AS COL5, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_DATA AS COL6, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_DIST_01 AS COL7, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_DIST_02 AS COL8, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_DIST_03 AS COL9, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_DIST_04 AS COL10, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_DIST_05 AS COL11, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_DIST_06 AS COL12, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_DIST_07 AS COL13, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_DIST_08 AS COL14, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_DIST_09 AS COL15, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.S_DIST_10 AS COL16, __tmp_delta_ins_stock_for_d_stock_ar_a18_0.LINEAGE AS COL17 FROM __tmp_delta_ins_stock_for_d_stock_ar AS __tmp_delta_ins_stock_for_d_stock_ar_a18_0   ) AS p_0_a18_0   ) AS part_ins_d_stock_a18_0   ) AS __dummy__   ) AS tbl;

        insertion_data := (SELECT (array_to_json(detected_insertions))::text);
        IF insertion_data IS NOT DISTINCT FROM NULL THEN
            insertion_data := '[]';
        END IF;

        WITH __tmp_delta_ins_stock_for_d_stock_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size),
        __tmp_delta_del_stock_for_d_stock_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_deletions FROM (SELECT __dummy__.COL0 AS S_W_ID, __dummy__.COL1 AS S_I_ID, __dummy__.COL2 AS S_QUANTITY, __dummy__.COL3 AS S_YTD, __dummy__.COL4 AS S_ORDER_CNT, __dummy__.COL5 AS S_REMOTE_CNT, __dummy__.COL6 AS S_DATA, __dummy__.COL7 AS S_DIST_01, __dummy__.COL8 AS S_DIST_02, __dummy__.COL9 AS S_DIST_03, __dummy__.COL10 AS S_DIST_04, __dummy__.COL11 AS S_DIST_05, __dummy__.COL12 AS S_DIST_06, __dummy__.COL13 AS S_DIST_07, __dummy__.COL14 AS S_DIST_08, __dummy__.COL15 AS S_DIST_09, __dummy__.COL16 AS S_DIST_10, __dummy__.COL17 AS LINEAGE FROM (SELECT part_del_d_stock_a18_0.COL0 AS COL0, part_del_d_stock_a18_0.COL1 AS COL1, part_del_d_stock_a18_0.COL2 AS COL2, part_del_d_stock_a18_0.COL3 AS COL3, part_del_d_stock_a18_0.COL4 AS COL4, part_del_d_stock_a18_0.COL5 AS COL5, part_del_d_stock_a18_0.COL6 AS COL6, part_del_d_stock_a18_0.COL7 AS COL7, part_del_d_stock_a18_0.COL8 AS COL8, part_del_d_stock_a18_0.COL9 AS COL9, part_del_d_stock_a18_0.COL10 AS COL10, part_del_d_stock_a18_0.COL11 AS COL11, part_del_d_stock_a18_0.COL12 AS COL12, part_del_d_stock_a18_0.COL13 AS COL13, part_del_d_stock_a18_0.COL14 AS COL14, part_del_d_stock_a18_0.COL15 AS COL15, part_del_d_stock_a18_0.COL16 AS COL16, part_del_d_stock_a18_0.COL17 AS COL17 FROM (SELECT p_0_a18_0.COL0 AS COL0, p_0_a18_0.COL1 AS COL1, p_0_a18_0.COL2 AS COL2, p_0_a18_0.COL3 AS COL3, p_0_a18_0.COL4 AS COL4, p_0_a18_0.COL5 AS COL5, p_0_a18_0.COL6 AS COL6, p_0_a18_0.COL7 AS COL7, p_0_a18_0.COL8 AS COL8, p_0_a18_0.COL9 AS COL9, p_0_a18_0.COL10 AS COL10, p_0_a18_0.COL11 AS COL11, p_0_a18_0.COL12 AS COL12, p_0_a18_0.COL13 AS COL13, p_0_a18_0.COL14 AS COL14, p_0_a18_0.COL15 AS COL15, p_0_a18_0.COL16 AS COL16, p_0_a18_0.COL17 AS COL17 FROM (SELECT __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_W_ID AS COL0, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_I_ID AS COL1, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_QUANTITY AS COL2, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_YTD AS COL3, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_ORDER_CNT AS COL4, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_REMOTE_CNT AS COL5, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_DATA AS COL6, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_DIST_01 AS COL7, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_DIST_02 AS COL8, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_DIST_03 AS COL9, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_DIST_04 AS COL10, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_DIST_05 AS COL11, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_DIST_06 AS COL12, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_DIST_07 AS COL13, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_DIST_08 AS COL14, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_DIST_09 AS COL15, __tmp_delta_del_stock_for_d_stock_ar_a18_0.S_DIST_10 AS COL16, __tmp_delta_del_stock_for_d_stock_ar_a18_0.LINEAGE AS COL17 FROM __tmp_delta_del_stock_for_d_stock_ar AS __tmp_delta_del_stock_for_d_stock_ar_a18_0   ) AS p_0_a18_0   ) AS part_del_d_stock_a18_0   ) AS __dummy__   ) AS tbl;

        deletion_data := (
        SELECT (array_to_json(detected_deletions))::text);
        IF deletion_data IS NOT DISTINCT FROM NULL THEN
            deletion_data := '[]';
        END IF;
        IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN
            user_name := (SELECT session_user);
            IF NOT (user_name = 'dejima') THEN
                xid := (SELECT txid_current());
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.d_stock"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.d_stock_run_shell(json_data);
                IF result = 'true' THEN
                    DROP TABLE __tmp_delta_ins_stock_for_d_stock;
                    DROP TABLE __tmp_delta_del_stock_for_d_stock;
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
                -- DELETE FROM public.__dummy__d_stock_detected_deletions;
                INSERT INTO public.__dummy__d_stock_detected_deletions
                    ( SELECT xid, * FROM unnest(detected_deletions) as detected_deletions_alias );

                -- DELETE FROM public.__dummy__d_stock_detected_insertions;
                INSERT INTO public.__dummy__d_stock_detected_insertions
                    ( SELECT xid, * FROM unnest(detected_insertions) as detected_insertions_alias );
            END IF;
        END IF;
    END IF;
END IF;
RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.stock';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the function public.stock_detect_update_on_d_stock() ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS stock_detect_update_on_d_stock ON public.stock;
CREATE CONSTRAINT TRIGGER stock_detect_update_on_d_stock
    AFTER INSERT OR UPDATE OR DELETE ON
    public.stock DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.stock_detect_update_on_d_stock();

CREATE OR REPLACE FUNCTION public.stock_propagate_updates_to_d_stock ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS public.stock_detect_update_on_d_stock IMMEDIATE;
    SET CONSTRAINTS public.stock_detect_update_on_d_stock DEFERRED;
    DROP TABLE IF EXISTS stock_detect_update_on_d_stock_flag;
    DROP TABLE IF EXISTS __tmp_delta_del_stock_for_d_stock;
    DROP TABLE IF EXISTS __tmp_delta_ins_stock_for_d_stock;
    RETURN true;
  END;
$$;



CREATE OR REPLACE FUNCTION public.d_stock_delta_action()
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
  array_delta_del public.d_stock[];
  array_delta_ins public.d_stock[];
  temprec_delta_del_stock public.stock%ROWTYPE;
            array_delta_del_stock public.stock[];
temprec_delta_ins_stock public.stock%ROWTYPE;
            array_delta_ins_stock public.stock[];
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd_stock_delta_action_flag') THEN
        -- RAISE LOG 'execute procedure d_stock_delta_action';
        CREATE TEMPORARY TABLE d_stock_delta_action_flag ON COMMIT DROP AS (SELECT true as finish);
        IF EXISTS (SELECT WHERE false )
        THEN
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the view are violated';
        END IF;
        IF EXISTS (SELECT WHERE false )
        THEN
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the source relations are violated';
        END IF;
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_d_stock AS tbl;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_d_stock as tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_d_stock;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_d_stock;
        
            WITH __tmp_delta_del_d_stock_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_d_stock_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_del_stock FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11,COL12,COL13,COL14,COL15,COL16,COL17) :: public.stock).*
            FROM (SELECT delta_del_stock_a18_0.COL0 AS COL0, delta_del_stock_a18_0.COL1 AS COL1, delta_del_stock_a18_0.COL2 AS COL2, delta_del_stock_a18_0.COL3 AS COL3, delta_del_stock_a18_0.COL4 AS COL4, delta_del_stock_a18_0.COL5 AS COL5, delta_del_stock_a18_0.COL6 AS COL6, delta_del_stock_a18_0.COL7 AS COL7, delta_del_stock_a18_0.COL8 AS COL8, delta_del_stock_a18_0.COL9 AS COL9, delta_del_stock_a18_0.COL10 AS COL10, delta_del_stock_a18_0.COL11 AS COL11, delta_del_stock_a18_0.COL12 AS COL12, delta_del_stock_a18_0.COL13 AS COL13, delta_del_stock_a18_0.COL14 AS COL14, delta_del_stock_a18_0.COL15 AS COL15, delta_del_stock_a18_0.COL16 AS COL16, delta_del_stock_a18_0.COL17 AS COL17 FROM (SELECT p_0_a18_0.COL0 AS COL0, p_0_a18_0.COL1 AS COL1, p_0_a18_0.COL2 AS COL2, p_0_a18_0.COL3 AS COL3, p_0_a18_0.COL4 AS COL4, p_0_a18_0.COL5 AS COL5, p_0_a18_0.COL6 AS COL6, p_0_a18_0.COL7 AS COL7, p_0_a18_0.COL8 AS COL8, p_0_a18_0.COL9 AS COL9, p_0_a18_0.COL10 AS COL10, p_0_a18_0.COL11 AS COL11, p_0_a18_0.COL12 AS COL12, p_0_a18_0.COL13 AS COL13, p_0_a18_0.COL14 AS COL14, p_0_a18_0.COL15 AS COL15, p_0_a18_0.COL16 AS COL16, p_0_a18_0.COL17 AS COL17 FROM (SELECT stock_a18_1.S_W_ID AS COL0, stock_a18_1.S_I_ID AS COL1, stock_a18_1.S_QUANTITY AS COL2, stock_a18_1.S_YTD AS COL3, stock_a18_1.S_ORDER_CNT AS COL4, stock_a18_1.S_REMOTE_CNT AS COL5, stock_a18_1.S_DATA AS COL6, stock_a18_1.S_DIST_01 AS COL7, stock_a18_1.S_DIST_02 AS COL8, stock_a18_1.S_DIST_03 AS COL9, stock_a18_1.S_DIST_04 AS COL10, stock_a18_1.S_DIST_05 AS COL11, stock_a18_1.S_DIST_06 AS COL12, stock_a18_1.S_DIST_07 AS COL13, stock_a18_1.S_DIST_08 AS COL14, stock_a18_1.S_DIST_09 AS COL15, stock_a18_1.S_DIST_10 AS COL16, stock_a18_1.LINEAGE AS COL17 FROM __tmp_delta_del_d_stock_ar AS __tmp_delta_del_d_stock_ar_a18_0, public.stock AS stock_a18_1 WHERE stock_a18_1.S_DIST_01 = __tmp_delta_del_d_stock_ar_a18_0.S_DIST_01 AND stock_a18_1.S_REMOTE_CNT = __tmp_delta_del_d_stock_ar_a18_0.S_REMOTE_CNT AND stock_a18_1.S_QUANTITY = __tmp_delta_del_d_stock_ar_a18_0.S_QUANTITY AND stock_a18_1.S_DIST_10 = __tmp_delta_del_d_stock_ar_a18_0.S_DIST_10 AND stock_a18_1.S_DATA = __tmp_delta_del_d_stock_ar_a18_0.S_DATA AND stock_a18_1.S_DIST_06 = __tmp_delta_del_d_stock_ar_a18_0.S_DIST_06 AND stock_a18_1.S_I_ID = __tmp_delta_del_d_stock_ar_a18_0.S_I_ID AND stock_a18_1.S_YTD = __tmp_delta_del_d_stock_ar_a18_0.S_YTD AND stock_a18_1.S_DIST_02 = __tmp_delta_del_d_stock_ar_a18_0.S_DIST_02 AND stock_a18_1.S_DIST_09 = __tmp_delta_del_d_stock_ar_a18_0.S_DIST_09 AND stock_a18_1.S_DIST_03 = __tmp_delta_del_d_stock_ar_a18_0.S_DIST_03 AND stock_a18_1.S_W_ID = __tmp_delta_del_d_stock_ar_a18_0.S_W_ID AND stock_a18_1.S_DIST_07 = __tmp_delta_del_d_stock_ar_a18_0.S_DIST_07 AND stock_a18_1.S_DIST_08 = __tmp_delta_del_d_stock_ar_a18_0.S_DIST_08 AND stock_a18_1.S_DIST_04 = __tmp_delta_del_d_stock_ar_a18_0.S_DIST_04 AND stock_a18_1.LINEAGE = __tmp_delta_del_d_stock_ar_a18_0.LINEAGE AND stock_a18_1.S_DIST_05 = __tmp_delta_del_d_stock_ar_a18_0.S_DIST_05 AND stock_a18_1.S_ORDER_CNT = __tmp_delta_del_d_stock_ar_a18_0.S_ORDER_CNT  ) AS p_0_a18_0   ) AS delta_del_stock_a18_0   ) AS delta_del_stock_extra_alias) AS tbl;


            WITH __tmp_delta_del_d_stock_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_d_stock_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_ins_stock FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11,COL12,COL13,COL14,COL15,COL16,COL17) :: public.stock).*
            FROM (SELECT delta_ins_stock_a18_0.COL0 AS COL0, delta_ins_stock_a18_0.COL1 AS COL1, delta_ins_stock_a18_0.COL2 AS COL2, delta_ins_stock_a18_0.COL3 AS COL3, delta_ins_stock_a18_0.COL4 AS COL4, delta_ins_stock_a18_0.COL5 AS COL5, delta_ins_stock_a18_0.COL6 AS COL6, delta_ins_stock_a18_0.COL7 AS COL7, delta_ins_stock_a18_0.COL8 AS COL8, delta_ins_stock_a18_0.COL9 AS COL9, delta_ins_stock_a18_0.COL10 AS COL10, delta_ins_stock_a18_0.COL11 AS COL11, delta_ins_stock_a18_0.COL12 AS COL12, delta_ins_stock_a18_0.COL13 AS COL13, delta_ins_stock_a18_0.COL14 AS COL14, delta_ins_stock_a18_0.COL15 AS COL15, delta_ins_stock_a18_0.COL16 AS COL16, delta_ins_stock_a18_0.COL17 AS COL17 FROM (SELECT p_0_a18_0.COL0 AS COL0, p_0_a18_0.COL1 AS COL1, p_0_a18_0.COL2 AS COL2, p_0_a18_0.COL3 AS COL3, p_0_a18_0.COL4 AS COL4, p_0_a18_0.COL5 AS COL5, p_0_a18_0.COL6 AS COL6, p_0_a18_0.COL7 AS COL7, p_0_a18_0.COL8 AS COL8, p_0_a18_0.COL9 AS COL9, p_0_a18_0.COL10 AS COL10, p_0_a18_0.COL11 AS COL11, p_0_a18_0.COL12 AS COL12, p_0_a18_0.COL13 AS COL13, p_0_a18_0.COL14 AS COL14, p_0_a18_0.COL15 AS COL15, p_0_a18_0.COL16 AS COL16, p_0_a18_0.COL17 AS COL17 FROM (SELECT __tmp_delta_ins_d_stock_ar_a18_0.S_W_ID AS COL0, __tmp_delta_ins_d_stock_ar_a18_0.S_I_ID AS COL1, __tmp_delta_ins_d_stock_ar_a18_0.S_QUANTITY AS COL2, __tmp_delta_ins_d_stock_ar_a18_0.S_YTD AS COL3, __tmp_delta_ins_d_stock_ar_a18_0.S_ORDER_CNT AS COL4, __tmp_delta_ins_d_stock_ar_a18_0.S_REMOTE_CNT AS COL5, __tmp_delta_ins_d_stock_ar_a18_0.S_DATA AS COL6, __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_01 AS COL7, __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_02 AS COL8, __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_03 AS COL9, __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_04 AS COL10, __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_05 AS COL11, __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_06 AS COL12, __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_07 AS COL13, __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_08 AS COL14, __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_09 AS COL15, __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_10 AS COL16, __tmp_delta_ins_d_stock_ar_a18_0.LINEAGE AS COL17 FROM __tmp_delta_ins_d_stock_ar AS __tmp_delta_ins_d_stock_ar_a18_0 WHERE NOT EXISTS ( SELECT * FROM public.stock AS stock_a18 WHERE stock_a18.LINEAGE = __tmp_delta_ins_d_stock_ar_a18_0.LINEAGE AND stock_a18.S_DIST_10 = __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_10 AND stock_a18.S_DIST_09 = __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_09 AND stock_a18.S_DIST_08 = __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_08 AND stock_a18.S_DIST_07 = __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_07 AND stock_a18.S_DIST_06 = __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_06 AND stock_a18.S_DIST_05 = __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_05 AND stock_a18.S_DIST_04 = __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_04 AND stock_a18.S_DIST_03 = __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_03 AND stock_a18.S_DIST_02 = __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_02 AND stock_a18.S_DIST_01 = __tmp_delta_ins_d_stock_ar_a18_0.S_DIST_01 AND stock_a18.S_DATA = __tmp_delta_ins_d_stock_ar_a18_0.S_DATA AND stock_a18.S_REMOTE_CNT = __tmp_delta_ins_d_stock_ar_a18_0.S_REMOTE_CNT AND stock_a18.S_ORDER_CNT = __tmp_delta_ins_d_stock_ar_a18_0.S_ORDER_CNT AND stock_a18.S_YTD = __tmp_delta_ins_d_stock_ar_a18_0.S_YTD AND stock_a18.S_QUANTITY = __tmp_delta_ins_d_stock_ar_a18_0.S_QUANTITY AND stock_a18.S_I_ID = __tmp_delta_ins_d_stock_ar_a18_0.S_I_ID AND stock_a18.S_W_ID = __tmp_delta_ins_d_stock_ar_a18_0.S_W_ID )  ) AS p_0_a18_0   ) AS delta_ins_stock_a18_0   ) AS delta_ins_stock_extra_alias) AS tbl; 


            IF array_delta_del_stock IS DISTINCT FROM NULL THEN
                FOREACH temprec_delta_del_stock IN array array_delta_del_stock  LOOP
                   DELETE FROM public.stock WHERE S_W_ID = temprec_delta_del_stock.S_W_ID AND S_I_ID = temprec_delta_del_stock.S_I_ID AND S_QUANTITY = temprec_delta_del_stock.S_QUANTITY AND S_YTD = temprec_delta_del_stock.S_YTD AND S_ORDER_CNT = temprec_delta_del_stock.S_ORDER_CNT AND S_REMOTE_CNT = temprec_delta_del_stock.S_REMOTE_CNT AND S_DATA = temprec_delta_del_stock.S_DATA AND S_DIST_01 = temprec_delta_del_stock.S_DIST_01 AND S_DIST_02 = temprec_delta_del_stock.S_DIST_02 AND S_DIST_03 = temprec_delta_del_stock.S_DIST_03 AND S_DIST_04 = temprec_delta_del_stock.S_DIST_04 AND S_DIST_05 = temprec_delta_del_stock.S_DIST_05 AND S_DIST_06 = temprec_delta_del_stock.S_DIST_06 AND S_DIST_07 = temprec_delta_del_stock.S_DIST_07 AND S_DIST_08 = temprec_delta_del_stock.S_DIST_08 AND S_DIST_09 = temprec_delta_del_stock.S_DIST_09 AND S_DIST_10 = temprec_delta_del_stock.S_DIST_10 AND LINEAGE = temprec_delta_del_stock.LINEAGE;
                END LOOP;
            END IF;


            IF array_delta_ins_stock IS DISTINCT FROM NULL THEN
                INSERT INTO public.stock (SELECT * FROM unnest(array_delta_ins_stock) as array_delta_ins_stock_alias) ;
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
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.d_stock"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.d_stock_run_shell(json_data);
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
                --DELETE FROM public.__dummy__d_stock_detected_deletions;
                INSERT INTO public.__dummy__d_stock_detected_deletions
                    SELECT xid, * FROM __tmp_delta_del_d_stock;

                --DELETE FROM public.__dummy__d_stock_detected_insertions;
                INSERT INTO public.__dummy__d_stock_detected_insertions
                    SELECT xid, * FROM __tmp_delta_ins_d_stock;
            END IF;
        END IF;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d_stock';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d_stock ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d_stock_materialization()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_d_stock' OR table_name = '__tmp_delta_del_d_stock')
    THEN
        -- RAISE LOG 'execute procedure d_stock_materialization';
        CREATE TEMPORARY TABLE __tmp_delta_ins_d_stock ( LIKE public.d_stock ) WITH OIDS ON COMMIT DROP;
        CREATE CONSTRAINT TRIGGER __tmp_d_stock_trigger_delta_action_ins
        AFTER INSERT OR UPDATE OR DELETE ON
            __tmp_delta_ins_d_stock DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW EXECUTE PROCEDURE public.d_stock_delta_action();

        CREATE TEMPORARY TABLE __tmp_delta_del_d_stock ( LIKE public.d_stock ) WITH OIDS ON COMMIT DROP;
        CREATE CONSTRAINT TRIGGER __tmp_d_stock_trigger_delta_action_del
        AFTER INSERT OR UPDATE OR DELETE ON
            __tmp_delta_del_d_stock DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW EXECUTE PROCEDURE public.d_stock_delta_action();
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d_stock';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d_stock ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS d_stock_trigger_materialization ON public.d_stock;
CREATE TRIGGER d_stock_trigger_materialization
    BEFORE INSERT OR UPDATE OR DELETE ON
      public.d_stock FOR EACH STATEMENT EXECUTE PROCEDURE public.d_stock_materialization();

CREATE OR REPLACE FUNCTION public.d_stock_update()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    -- RAISE LOG 'execute procedure d_stock_update';
    IF TG_OP = 'INSERT' THEN
      -- RAISE LOG 'NEW: %', NEW;
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_del_d_stock WHERE ROW(S_W_ID,S_I_ID,S_QUANTITY,S_YTD,S_ORDER_CNT,S_REMOTE_CNT,S_DATA,S_DIST_01,S_DIST_02,S_DIST_03,S_DIST_04,S_DIST_05,S_DIST_06,S_DIST_07,S_DIST_08,S_DIST_09,S_DIST_10,LINEAGE) = NEW;
      INSERT INTO __tmp_delta_ins_d_stock SELECT (NEW).*;
    ELSIF TG_OP = 'UPDATE' THEN
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_ins_d_stock WHERE ROW(S_W_ID,S_I_ID,S_QUANTITY,S_YTD,S_ORDER_CNT,S_REMOTE_CNT,S_DATA,S_DIST_01,S_DIST_02,S_DIST_03,S_DIST_04,S_DIST_05,S_DIST_06,S_DIST_07,S_DIST_08,S_DIST_09,S_DIST_10,LINEAGE) = OLD;
      INSERT INTO __tmp_delta_del_d_stock SELECT (OLD).*;
      DELETE FROM __tmp_delta_del_d_stock WHERE ROW(S_W_ID,S_I_ID,S_QUANTITY,S_YTD,S_ORDER_CNT,S_REMOTE_CNT,S_DATA,S_DIST_01,S_DIST_02,S_DIST_03,S_DIST_04,S_DIST_05,S_DIST_06,S_DIST_07,S_DIST_08,S_DIST_09,S_DIST_10,LINEAGE) = NEW;
      INSERT INTO __tmp_delta_ins_d_stock SELECT (NEW).*;
    ELSIF TG_OP = 'DELETE' THEN
      -- RAISE LOG 'OLD: %', OLD;
      DELETE FROM __tmp_delta_ins_d_stock WHERE ROW(S_W_ID,S_I_ID,S_QUANTITY,S_YTD,S_ORDER_CNT,S_REMOTE_CNT,S_DATA,S_DIST_01,S_DIST_02,S_DIST_03,S_DIST_04,S_DIST_05,S_DIST_06,S_DIST_07,S_DIST_08,S_DIST_09,S_DIST_10,LINEAGE) = OLD;
      INSERT INTO __tmp_delta_del_d_stock SELECT (OLD).*;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d_stock';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d_stock ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS d_stock_trigger_update ON public.d_stock;
CREATE TRIGGER d_stock_trigger_update
    INSTEAD OF INSERT OR UPDATE OR DELETE ON
      public.d_stock FOR EACH ROW EXECUTE PROCEDURE public.d_stock_update();

CREATE OR REPLACE FUNCTION public.d_stock_propagate_updates ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS __tmp_d_stock_trigger_delta_action_ins, __tmp_d_stock_trigger_delta_action_del IMMEDIATE;
    SET CONSTRAINTS __tmp_d_stock_trigger_delta_action_ins, __tmp_d_stock_trigger_delta_action_del DEFERRED;
    DROP TABLE IF EXISTS d_stock_delta_action_flag;
    DROP TABLE IF EXISTS __tmp_delta_del_d_stock;
    DROP TABLE IF EXISTS __tmp_delta_ins_d_stock;
    RETURN true;
  END;
$$;


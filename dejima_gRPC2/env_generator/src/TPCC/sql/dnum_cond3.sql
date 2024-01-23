CREATE OR REPLACE VIEW public.dnum AS 
SELECT __dummy__.COL0 AS C_W_ID,__dummy__.COL1 AS C_D_ID,__dummy__.COL2 AS C_ID,__dummy__.COL3 AS C_DISCOUNT,__dummy__.COL4 AS C_CREDIT,__dummy__.COL5 AS C_LAST,__dummy__.COL6 AS C_FIRST,__dummy__.COL7 AS C_CREDIT_LIM,__dummy__.COL8 AS C_BALANCE,__dummy__.COL9 AS C_YTD_PAYMENT,__dummy__.COL10 AS C_PAYMENT_CNT,__dummy__.COL11 AS C_DELIVERY_CNT,__dummy__.COL12 AS C_STREET_1,__dummy__.COL13 AS C_STREET_2,__dummy__.COL14 AS C_CITY,__dummy__.COL15 AS C_STATE,__dummy__.COL16 AS C_ZIP,__dummy__.COL17 AS C_PHONE,__dummy__.COL18 AS C_SINCE,__dummy__.COL19 AS C_MIDDLE,__dummy__.COL20 AS C_DATA,__dummy__.COL21 AS C_LINEAGE,__dummy__.COL22 AS C_COND01,__dummy__.COL23 AS C_COND02,__dummy__.COL24 AS C_COND03,__dummy__.COL25 AS C_COND04,__dummy__.COL26 AS C_COND05,__dummy__.COL27 AS C_COND06,__dummy__.COL28 AS C_COND07,__dummy__.COL29 AS C_COND08,__dummy__.COL30 AS C_COND09,__dummy__.COL31 AS C_COND10 
FROM (SELECT dnum_a32_0.COL0 AS COL0, dnum_a32_0.COL1 AS COL1, dnum_a32_0.COL2 AS COL2, dnum_a32_0.COL3 AS COL3, dnum_a32_0.COL4 AS COL4, dnum_a32_0.COL5 AS COL5, dnum_a32_0.COL6 AS COL6, dnum_a32_0.COL7 AS COL7, dnum_a32_0.COL8 AS COL8, dnum_a32_0.COL9 AS COL9, dnum_a32_0.COL10 AS COL10, dnum_a32_0.COL11 AS COL11, dnum_a32_0.COL12 AS COL12, dnum_a32_0.COL13 AS COL13, dnum_a32_0.COL14 AS COL14, dnum_a32_0.COL15 AS COL15, dnum_a32_0.COL16 AS COL16, dnum_a32_0.COL17 AS COL17, dnum_a32_0.COL18 AS COL18, dnum_a32_0.COL19 AS COL19, dnum_a32_0.COL20 AS COL20, dnum_a32_0.COL21 AS COL21, dnum_a32_0.COL22 AS COL22, dnum_a32_0.COL23 AS COL23, dnum_a32_0.COL24 AS COL24, dnum_a32_0.COL25 AS COL25, dnum_a32_0.COL26 AS COL26, dnum_a32_0.COL27 AS COL27, dnum_a32_0.COL28 AS COL28, dnum_a32_0.COL29 AS COL29, dnum_a32_0.COL30 AS COL30, dnum_a32_0.COL31 AS COL31 
FROM (SELECT customer_a32_0.C_W_ID AS COL0, customer_a32_0.C_D_ID AS COL1, customer_a32_0.C_ID AS COL2, customer_a32_0.C_DISCOUNT AS COL3, customer_a32_0.C_CREDIT AS COL4, customer_a32_0.C_LAST AS COL5, customer_a32_0.C_FIRST AS COL6, customer_a32_0.C_CREDIT_LIM AS COL7, customer_a32_0.C_BALANCE AS COL8, customer_a32_0.C_YTD_PAYMENT AS COL9, customer_a32_0.C_PAYMENT_CNT AS COL10, customer_a32_0.C_DELIVERY_CNT AS COL11, customer_a32_0.C_STREET_1 AS COL12, customer_a32_0.C_STREET_2 AS COL13, customer_a32_0.C_CITY AS COL14, customer_a32_0.C_STATE AS COL15, customer_a32_0.C_ZIP AS COL16, customer_a32_0.C_PHONE AS COL17, customer_a32_0.C_SINCE AS COL18, customer_a32_0.C_MIDDLE AS COL19, customer_a32_0.C_DATA AS COL20, customer_a32_0.C_LINEAGE AS COL21, customer_a32_0.C_COND01 AS COL22, customer_a32_0.C_COND02 AS COL23, customer_a32_0.C_COND03 AS COL24, customer_a32_0.C_COND04 AS COL25, customer_a32_0.C_COND05 AS COL26, customer_a32_0.C_COND06 AS COL27, customer_a32_0.C_COND07 AS COL28, customer_a32_0.C_COND08 AS COL29, customer_a32_0.C_COND09 AS COL30, customer_a32_0.C_COND10 AS COL31 
FROM public.customer AS customer_a32_0 
WHERE customer_a32_0.C_COND03  <  <border> ) AS dnum_a32_0  ) AS __dummy__;

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

CREATE OR REPLACE FUNCTION public.customer_materialization_for_dnum()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_customer_for_dnum' OR table_name = '__tmp_delta_del_customer_for_dnum')
    THEN
        -- RAISE LOG 'execute procedure customer_materialization_for_dnum';
        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_ins_customer_for_dnum ( LIKE public.customer ) WITH OIDS ON COMMIT DELETE ROWS;
        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_del_customer_for_dnum ( LIKE public.customer ) WITH OIDS ON COMMIT DELETE ROWS;
        
    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.customer';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.customer ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS customer_trigger_materialization_for_dnum ON public.customer;
CREATE TRIGGER customer_trigger_materialization_for_dnum
    BEFORE INSERT OR UPDATE OR DELETE ON
    public.customer FOR EACH STATEMENT EXECUTE PROCEDURE public.customer_materialization_for_dnum();

CREATE OR REPLACE FUNCTION public.customer_update_for_dnum()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    -- RAISE LOG 'execute procedure customer_update_for_dnum';
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'dnum_delta_action_flag') THEN
        IF TG_OP = 'INSERT' THEN
        -- RAISE LOG 'NEW: %', NEW;
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_del_customer_for_dnum WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE,C_COND01,C_COND02,C_COND03,C_COND04,C_COND05,C_COND06,C_COND07,C_COND08,C_COND09,C_COND10) = NEW;
        INSERT INTO __tmp_delta_ins_customer_for_dnum SELECT (NEW).*; 
        ELSIF TG_OP = 'UPDATE' THEN
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_ins_customer_for_dnum WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE,C_COND01,C_COND02,C_COND03,C_COND04,C_COND05,C_COND06,C_COND07,C_COND08,C_COND09,C_COND10) = OLD;
        INSERT INTO __tmp_delta_del_customer_for_dnum SELECT (OLD).*;
        DELETE FROM __tmp_delta_del_customer_for_dnum WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE,C_COND01,C_COND02,C_COND03,C_COND04,C_COND05,C_COND06,C_COND07,C_COND08,C_COND09,C_COND10) = NEW;
        INSERT INTO __tmp_delta_ins_customer_for_dnum SELECT (NEW).*; 
        ELSIF TG_OP = 'DELETE' THEN
        -- RAISE LOG 'OLD: %', OLD;
        DELETE FROM __tmp_delta_ins_customer_for_dnum WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE,C_COND01,C_COND02,C_COND03,C_COND04,C_COND05,C_COND06,C_COND07,C_COND08,C_COND09,C_COND10) = OLD;
        INSERT INTO __tmp_delta_del_customer_for_dnum SELECT (OLD).*;
        END IF;
    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.customer';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.customer ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS customer_trigger_update_for_dnum ON public.customer;
CREATE TRIGGER customer_trigger_update_for_dnum
    AFTER INSERT OR UPDATE OR DELETE ON
    public.customer FOR EACH ROW EXECUTE PROCEDURE public.customer_update_for_dnum();

CREATE OR REPLACE FUNCTION public.customer_detect_update_on_dnum()
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
array_delta_del public.customer[];
array_delta_ins public.customer[];
detected_deletions public.dnum[];
detected_insertions public.dnum[];
delta_ins_size int;
delta_del_size int;
BEGIN
IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'customer_detect_update_on_dnum_flag') THEN
    CREATE TEMPORARY TABLE customer_detect_update_on_dnum_flag ON COMMIT DROP AS (SELECT true as finish);
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'dnum_delta_action_flag') THEN
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_customer_for_dnum AS tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_customer_for_dnum;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_customer_for_dnum tbl;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_customer_for_dnum;

        WITH __tmp_delta_ins_customer_for_dnum_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size), 
        __tmp_delta_del_customer_for_dnum_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_insertions FROM (SELECT __dummy__.COL0 AS C_W_ID,__dummy__.COL1 AS C_D_ID,__dummy__.COL2 AS C_ID,__dummy__.COL3 AS C_DISCOUNT,__dummy__.COL4 AS C_CREDIT,__dummy__.COL5 AS C_LAST,__dummy__.COL6 AS C_FIRST,__dummy__.COL7 AS C_CREDIT_LIM,__dummy__.COL8 AS C_BALANCE,__dummy__.COL9 AS C_YTD_PAYMENT,__dummy__.COL10 AS C_PAYMENT_CNT,__dummy__.COL11 AS C_DELIVERY_CNT,__dummy__.COL12 AS C_STREET_1,__dummy__.COL13 AS C_STREET_2,__dummy__.COL14 AS C_CITY,__dummy__.COL15 AS C_STATE,__dummy__.COL16 AS C_ZIP,__dummy__.COL17 AS C_PHONE,__dummy__.COL18 AS C_SINCE,__dummy__.COL19 AS C_MIDDLE,__dummy__.COL20 AS C_DATA,__dummy__.COL21 AS C_LINEAGE,__dummy__.COL22 AS C_COND01,__dummy__.COL23 AS C_COND02,__dummy__.COL24 AS C_COND03,__dummy__.COL25 AS C_COND04,__dummy__.COL26 AS C_COND05,__dummy__.COL27 AS C_COND06,__dummy__.COL28 AS C_COND07,__dummy__.COL29 AS C_COND08,__dummy__.COL30 AS C_COND09,__dummy__.COL31 AS C_COND10 
FROM (SELECT part_ins_dnum_a32_0.COL0 AS COL0, part_ins_dnum_a32_0.COL1 AS COL1, part_ins_dnum_a32_0.COL2 AS COL2, part_ins_dnum_a32_0.COL3 AS COL3, part_ins_dnum_a32_0.COL4 AS COL4, part_ins_dnum_a32_0.COL5 AS COL5, part_ins_dnum_a32_0.COL6 AS COL6, part_ins_dnum_a32_0.COL7 AS COL7, part_ins_dnum_a32_0.COL8 AS COL8, part_ins_dnum_a32_0.COL9 AS COL9, part_ins_dnum_a32_0.COL10 AS COL10, part_ins_dnum_a32_0.COL11 AS COL11, part_ins_dnum_a32_0.COL12 AS COL12, part_ins_dnum_a32_0.COL13 AS COL13, part_ins_dnum_a32_0.COL14 AS COL14, part_ins_dnum_a32_0.COL15 AS COL15, part_ins_dnum_a32_0.COL16 AS COL16, part_ins_dnum_a32_0.COL17 AS COL17, part_ins_dnum_a32_0.COL18 AS COL18, part_ins_dnum_a32_0.COL19 AS COL19, part_ins_dnum_a32_0.COL20 AS COL20, part_ins_dnum_a32_0.COL21 AS COL21, part_ins_dnum_a32_0.COL22 AS COL22, part_ins_dnum_a32_0.COL23 AS COL23, part_ins_dnum_a32_0.COL24 AS COL24, part_ins_dnum_a32_0.COL25 AS COL25, part_ins_dnum_a32_0.COL26 AS COL26, part_ins_dnum_a32_0.COL27 AS COL27, part_ins_dnum_a32_0.COL28 AS COL28, part_ins_dnum_a32_0.COL29 AS COL29, part_ins_dnum_a32_0.COL30 AS COL30, part_ins_dnum_a32_0.COL31 AS COL31 
FROM (SELECT p_0_a32_0.COL0 AS COL0, p_0_a32_0.COL1 AS COL1, p_0_a32_0.COL2 AS COL2, p_0_a32_0.COL3 AS COL3, p_0_a32_0.COL4 AS COL4, p_0_a32_0.COL5 AS COL5, p_0_a32_0.COL6 AS COL6, p_0_a32_0.COL7 AS COL7, p_0_a32_0.COL8 AS COL8, p_0_a32_0.COL9 AS COL9, p_0_a32_0.COL10 AS COL10, p_0_a32_0.COL11 AS COL11, p_0_a32_0.COL12 AS COL12, p_0_a32_0.COL13 AS COL13, p_0_a32_0.COL14 AS COL14, p_0_a32_0.COL15 AS COL15, p_0_a32_0.COL16 AS COL16, p_0_a32_0.COL17 AS COL17, p_0_a32_0.COL18 AS COL18, p_0_a32_0.COL19 AS COL19, p_0_a32_0.COL20 AS COL20, p_0_a32_0.COL21 AS COL21, p_0_a32_0.COL22 AS COL22, p_0_a32_0.COL23 AS COL23, p_0_a32_0.COL24 AS COL24, p_0_a32_0.COL25 AS COL25, p_0_a32_0.COL26 AS COL26, p_0_a32_0.COL27 AS COL27, p_0_a32_0.COL28 AS COL28, p_0_a32_0.COL29 AS COL29, p_0_a32_0.COL30 AS COL30, p_0_a32_0.COL31 AS COL31 
FROM (SELECT __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_W_ID AS COL0, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_D_ID AS COL1, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_ID AS COL2, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_DISCOUNT AS COL3, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_CREDIT AS COL4, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_LAST AS COL5, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_FIRST AS COL6, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_CREDIT_LIM AS COL7, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_BALANCE AS COL8, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_YTD_PAYMENT AS COL9, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_PAYMENT_CNT AS COL10, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_DELIVERY_CNT AS COL11, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_STREET_1 AS COL12, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_STREET_2 AS COL13, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_CITY AS COL14, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_STATE AS COL15, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_ZIP AS COL16, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_PHONE AS COL17, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_SINCE AS COL18, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_MIDDLE AS COL19, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_DATA AS COL20, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_LINEAGE AS COL21, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_COND01 AS COL22, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_COND02 AS COL23, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_COND03 AS COL24, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_COND04 AS COL25, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_COND05 AS COL26, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_COND06 AS COL27, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_COND07 AS COL28, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_COND08 AS COL29, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_COND09 AS COL30, __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_COND10 AS COL31 
FROM __tmp_delta_ins_customer_for_dnum_ar AS __tmp_delta_ins_customer_for_dnum_ar_a32_0 
WHERE __tmp_delta_ins_customer_for_dnum_ar_a32_0.C_COND03  <  <border> ) AS p_0_a32_0  ) AS part_ins_dnum_a32_0  ) AS __dummy__) AS tbl;

        insertion_data := (SELECT (array_to_json(detected_insertions))::text);
        IF insertion_data IS NOT DISTINCT FROM NULL THEN 
            insertion_data := '[]';
        END IF; 

        WITH __tmp_delta_ins_customer_for_dnum_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size), 
        __tmp_delta_del_customer_for_dnum_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_deletions FROM (SELECT __dummy__.COL0 AS C_W_ID,__dummy__.COL1 AS C_D_ID,__dummy__.COL2 AS C_ID,__dummy__.COL3 AS C_DISCOUNT,__dummy__.COL4 AS C_CREDIT,__dummy__.COL5 AS C_LAST,__dummy__.COL6 AS C_FIRST,__dummy__.COL7 AS C_CREDIT_LIM,__dummy__.COL8 AS C_BALANCE,__dummy__.COL9 AS C_YTD_PAYMENT,__dummy__.COL10 AS C_PAYMENT_CNT,__dummy__.COL11 AS C_DELIVERY_CNT,__dummy__.COL12 AS C_STREET_1,__dummy__.COL13 AS C_STREET_2,__dummy__.COL14 AS C_CITY,__dummy__.COL15 AS C_STATE,__dummy__.COL16 AS C_ZIP,__dummy__.COL17 AS C_PHONE,__dummy__.COL18 AS C_SINCE,__dummy__.COL19 AS C_MIDDLE,__dummy__.COL20 AS C_DATA,__dummy__.COL21 AS C_LINEAGE,__dummy__.COL22 AS C_COND01,__dummy__.COL23 AS C_COND02,__dummy__.COL24 AS C_COND03,__dummy__.COL25 AS C_COND04,__dummy__.COL26 AS C_COND05,__dummy__.COL27 AS C_COND06,__dummy__.COL28 AS C_COND07,__dummy__.COL29 AS C_COND08,__dummy__.COL30 AS C_COND09,__dummy__.COL31 AS C_COND10 
FROM (SELECT part_del_dnum_a32_0.COL0 AS COL0, part_del_dnum_a32_0.COL1 AS COL1, part_del_dnum_a32_0.COL2 AS COL2, part_del_dnum_a32_0.COL3 AS COL3, part_del_dnum_a32_0.COL4 AS COL4, part_del_dnum_a32_0.COL5 AS COL5, part_del_dnum_a32_0.COL6 AS COL6, part_del_dnum_a32_0.COL7 AS COL7, part_del_dnum_a32_0.COL8 AS COL8, part_del_dnum_a32_0.COL9 AS COL9, part_del_dnum_a32_0.COL10 AS COL10, part_del_dnum_a32_0.COL11 AS COL11, part_del_dnum_a32_0.COL12 AS COL12, part_del_dnum_a32_0.COL13 AS COL13, part_del_dnum_a32_0.COL14 AS COL14, part_del_dnum_a32_0.COL15 AS COL15, part_del_dnum_a32_0.COL16 AS COL16, part_del_dnum_a32_0.COL17 AS COL17, part_del_dnum_a32_0.COL18 AS COL18, part_del_dnum_a32_0.COL19 AS COL19, part_del_dnum_a32_0.COL20 AS COL20, part_del_dnum_a32_0.COL21 AS COL21, part_del_dnum_a32_0.COL22 AS COL22, part_del_dnum_a32_0.COL23 AS COL23, part_del_dnum_a32_0.COL24 AS COL24, part_del_dnum_a32_0.COL25 AS COL25, part_del_dnum_a32_0.COL26 AS COL26, part_del_dnum_a32_0.COL27 AS COL27, part_del_dnum_a32_0.COL28 AS COL28, part_del_dnum_a32_0.COL29 AS COL29, part_del_dnum_a32_0.COL30 AS COL30, part_del_dnum_a32_0.COL31 AS COL31 
FROM (SELECT p_0_a32_0.COL0 AS COL0, p_0_a32_0.COL1 AS COL1, p_0_a32_0.COL2 AS COL2, p_0_a32_0.COL3 AS COL3, p_0_a32_0.COL4 AS COL4, p_0_a32_0.COL5 AS COL5, p_0_a32_0.COL6 AS COL6, p_0_a32_0.COL7 AS COL7, p_0_a32_0.COL8 AS COL8, p_0_a32_0.COL9 AS COL9, p_0_a32_0.COL10 AS COL10, p_0_a32_0.COL11 AS COL11, p_0_a32_0.COL12 AS COL12, p_0_a32_0.COL13 AS COL13, p_0_a32_0.COL14 AS COL14, p_0_a32_0.COL15 AS COL15, p_0_a32_0.COL16 AS COL16, p_0_a32_0.COL17 AS COL17, p_0_a32_0.COL18 AS COL18, p_0_a32_0.COL19 AS COL19, p_0_a32_0.COL20 AS COL20, p_0_a32_0.COL21 AS COL21, p_0_a32_0.COL22 AS COL22, p_0_a32_0.COL23 AS COL23, p_0_a32_0.COL24 AS COL24, p_0_a32_0.COL25 AS COL25, p_0_a32_0.COL26 AS COL26, p_0_a32_0.COL27 AS COL27, p_0_a32_0.COL28 AS COL28, p_0_a32_0.COL29 AS COL29, p_0_a32_0.COL30 AS COL30, p_0_a32_0.COL31 AS COL31 
FROM (SELECT __tmp_delta_del_customer_for_dnum_ar_a32_0.C_W_ID AS COL0, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_D_ID AS COL1, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_ID AS COL2, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_DISCOUNT AS COL3, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_CREDIT AS COL4, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_LAST AS COL5, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_FIRST AS COL6, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_CREDIT_LIM AS COL7, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_BALANCE AS COL8, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_YTD_PAYMENT AS COL9, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_PAYMENT_CNT AS COL10, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_DELIVERY_CNT AS COL11, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_STREET_1 AS COL12, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_STREET_2 AS COL13, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_CITY AS COL14, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_STATE AS COL15, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_ZIP AS COL16, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_PHONE AS COL17, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_SINCE AS COL18, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_MIDDLE AS COL19, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_DATA AS COL20, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_LINEAGE AS COL21, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_COND01 AS COL22, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_COND02 AS COL23, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_COND03 AS COL24, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_COND04 AS COL25, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_COND05 AS COL26, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_COND06 AS COL27, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_COND07 AS COL28, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_COND08 AS COL29, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_COND09 AS COL30, __tmp_delta_del_customer_for_dnum_ar_a32_0.C_COND10 AS COL31 
FROM __tmp_delta_del_customer_for_dnum_ar AS __tmp_delta_del_customer_for_dnum_ar_a32_0 
WHERE __tmp_delta_del_customer_for_dnum_ar_a32_0.C_COND03  <  <border> ) AS p_0_a32_0  ) AS part_del_dnum_a32_0  ) AS __dummy__) AS tbl;

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
                    DROP TABLE __tmp_delta_ins_customer_for_dnum;
                    DROP TABLE __tmp_delta_del_customer_for_dnum;
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
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.customer';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the function public.customer_detect_update_on_dnum() ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS customer_detect_update_on_dnum ON public.customer;
CREATE CONSTRAINT TRIGGER customer_detect_update_on_dnum
    AFTER INSERT OR UPDATE OR DELETE ON
    public.customer DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.customer_detect_update_on_dnum();

CREATE OR REPLACE FUNCTION public.customer_propagate_updates_to_dnum ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS public.customer_detect_update_on_dnum IMMEDIATE;
    SET CONSTRAINTS public.customer_detect_update_on_dnum DEFERRED;
    DROP TABLE IF EXISTS customer_detect_update_on_dnum_flag;
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
  temprec_delta_del_customer public.customer%ROWTYPE;
            array_delta_del_customer public.customer[];
temprec_delta_ins_customer public.customer%ROWTYPE;
            array_delta_ins_customer public.customer[];
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
            SELECT array_agg(tbl) INTO array_delta_del_customer FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11,COL12,COL13,COL14,COL15,COL16,COL17,COL18,COL19,COL20,COL21,COL22,COL23,COL24,COL25,COL26,COL27,COL28,COL29,COL30,COL31) :: public.customer).* 
            FROM (SELECT delta_del_customer_a32_0.COL0 AS COL0, delta_del_customer_a32_0.COL1 AS COL1, delta_del_customer_a32_0.COL2 AS COL2, delta_del_customer_a32_0.COL3 AS COL3, delta_del_customer_a32_0.COL4 AS COL4, delta_del_customer_a32_0.COL5 AS COL5, delta_del_customer_a32_0.COL6 AS COL6, delta_del_customer_a32_0.COL7 AS COL7, delta_del_customer_a32_0.COL8 AS COL8, delta_del_customer_a32_0.COL9 AS COL9, delta_del_customer_a32_0.COL10 AS COL10, delta_del_customer_a32_0.COL11 AS COL11, delta_del_customer_a32_0.COL12 AS COL12, delta_del_customer_a32_0.COL13 AS COL13, delta_del_customer_a32_0.COL14 AS COL14, delta_del_customer_a32_0.COL15 AS COL15, delta_del_customer_a32_0.COL16 AS COL16, delta_del_customer_a32_0.COL17 AS COL17, delta_del_customer_a32_0.COL18 AS COL18, delta_del_customer_a32_0.COL19 AS COL19, delta_del_customer_a32_0.COL20 AS COL20, delta_del_customer_a32_0.COL21 AS COL21, delta_del_customer_a32_0.COL22 AS COL22, delta_del_customer_a32_0.COL23 AS COL23, delta_del_customer_a32_0.COL24 AS COL24, delta_del_customer_a32_0.COL25 AS COL25, delta_del_customer_a32_0.COL26 AS COL26, delta_del_customer_a32_0.COL27 AS COL27, delta_del_customer_a32_0.COL28 AS COL28, delta_del_customer_a32_0.COL29 AS COL29, delta_del_customer_a32_0.COL30 AS COL30, delta_del_customer_a32_0.COL31 AS COL31 
FROM (SELECT p_0_a32_0.COL0 AS COL0, p_0_a32_0.COL1 AS COL1, p_0_a32_0.COL2 AS COL2, p_0_a32_0.COL3 AS COL3, p_0_a32_0.COL4 AS COL4, p_0_a32_0.COL5 AS COL5, p_0_a32_0.COL6 AS COL6, p_0_a32_0.COL7 AS COL7, p_0_a32_0.COL8 AS COL8, p_0_a32_0.COL9 AS COL9, p_0_a32_0.COL10 AS COL10, p_0_a32_0.COL11 AS COL11, p_0_a32_0.COL12 AS COL12, p_0_a32_0.COL13 AS COL13, p_0_a32_0.COL14 AS COL14, p_0_a32_0.COL15 AS COL15, p_0_a32_0.COL16 AS COL16, p_0_a32_0.COL17 AS COL17, p_0_a32_0.COL18 AS COL18, p_0_a32_0.COL19 AS COL19, p_0_a32_0.COL20 AS COL20, p_0_a32_0.COL21 AS COL21, p_0_a32_0.COL22 AS COL22, p_0_a32_0.COL23 AS COL23, p_0_a32_0.COL24 AS COL24, p_0_a32_0.COL25 AS COL25, p_0_a32_0.COL26 AS COL26, p_0_a32_0.COL27 AS COL27, p_0_a32_0.COL28 AS COL28, p_0_a32_0.COL29 AS COL29, p_0_a32_0.COL30 AS COL30, p_0_a32_0.COL31 AS COL31 
FROM (SELECT customer_a32_1.C_W_ID AS COL0, customer_a32_1.C_D_ID AS COL1, customer_a32_1.C_ID AS COL2, customer_a32_1.C_DISCOUNT AS COL3, customer_a32_1.C_CREDIT AS COL4, customer_a32_1.C_LAST AS COL5, customer_a32_1.C_FIRST AS COL6, customer_a32_1.C_CREDIT_LIM AS COL7, customer_a32_1.C_BALANCE AS COL8, customer_a32_1.C_YTD_PAYMENT AS COL9, customer_a32_1.C_PAYMENT_CNT AS COL10, customer_a32_1.C_DELIVERY_CNT AS COL11, customer_a32_1.C_STREET_1 AS COL12, customer_a32_1.C_STREET_2 AS COL13, customer_a32_1.C_CITY AS COL14, customer_a32_1.C_STATE AS COL15, customer_a32_1.C_ZIP AS COL16, customer_a32_1.C_PHONE AS COL17, customer_a32_1.C_SINCE AS COL18, customer_a32_1.C_MIDDLE AS COL19, customer_a32_1.C_DATA AS COL20, customer_a32_1.C_LINEAGE AS COL21, customer_a32_1.C_COND01 AS COL22, customer_a32_1.C_COND02 AS COL23, customer_a32_1.C_COND03 AS COL24, customer_a32_1.C_COND04 AS COL25, customer_a32_1.C_COND05 AS COL26, customer_a32_1.C_COND06 AS COL27, customer_a32_1.C_COND07 AS COL28, customer_a32_1.C_COND08 AS COL29, customer_a32_1.C_COND09 AS COL30, customer_a32_1.C_COND10 AS COL31 
FROM __tmp_delta_del_dnum_ar AS __tmp_delta_del_dnum_ar_a32_0, public.customer AS customer_a32_1 
WHERE customer_a32_1.C_CREDIT_LIM = __tmp_delta_del_dnum_ar_a32_0.C_CREDIT_LIM AND customer_a32_1.C_LAST = __tmp_delta_del_dnum_ar_a32_0.C_LAST AND customer_a32_1.C_ID = __tmp_delta_del_dnum_ar_a32_0.C_ID AND customer_a32_1.C_LINEAGE = __tmp_delta_del_dnum_ar_a32_0.C_LINEAGE AND customer_a32_1.C_ZIP = __tmp_delta_del_dnum_ar_a32_0.C_ZIP AND customer_a32_1.C_SINCE = __tmp_delta_del_dnum_ar_a32_0.C_SINCE AND customer_a32_1.C_COND08 = __tmp_delta_del_dnum_ar_a32_0.C_COND08 AND customer_a32_1.C_FIRST = __tmp_delta_del_dnum_ar_a32_0.C_FIRST AND customer_a32_1.C_STREET_1 = __tmp_delta_del_dnum_ar_a32_0.C_STREET_1 AND customer_a32_1.C_COND06 = __tmp_delta_del_dnum_ar_a32_0.C_COND06 AND customer_a32_1.C_COND09 = __tmp_delta_del_dnum_ar_a32_0.C_COND09 AND customer_a32_1.C_D_ID = __tmp_delta_del_dnum_ar_a32_0.C_D_ID AND customer_a32_1.C_DISCOUNT = __tmp_delta_del_dnum_ar_a32_0.C_DISCOUNT AND customer_a32_1.C_BALANCE = __tmp_delta_del_dnum_ar_a32_0.C_BALANCE AND customer_a32_1.C_COND03 = __tmp_delta_del_dnum_ar_a32_0.C_COND03 AND customer_a32_1.C_STATE = __tmp_delta_del_dnum_ar_a32_0.C_STATE AND customer_a32_1.C_MIDDLE = __tmp_delta_del_dnum_ar_a32_0.C_MIDDLE AND customer_a32_1.C_YTD_PAYMENT = __tmp_delta_del_dnum_ar_a32_0.C_YTD_PAYMENT AND customer_a32_1.C_W_ID = __tmp_delta_del_dnum_ar_a32_0.C_W_ID AND customer_a32_1.C_COND07 = __tmp_delta_del_dnum_ar_a32_0.C_COND07 AND customer_a32_1.C_STREET_2 = __tmp_delta_del_dnum_ar_a32_0.C_STREET_2 AND customer_a32_1.C_CITY = __tmp_delta_del_dnum_ar_a32_0.C_CITY AND customer_a32_1.C_PAYMENT_CNT = __tmp_delta_del_dnum_ar_a32_0.C_PAYMENT_CNT AND customer_a32_1.C_COND02 = __tmp_delta_del_dnum_ar_a32_0.C_COND02 AND customer_a32_1.C_DATA = __tmp_delta_del_dnum_ar_a32_0.C_DATA AND customer_a32_1.C_PHONE = __tmp_delta_del_dnum_ar_a32_0.C_PHONE AND customer_a32_1.C_COND10 = __tmp_delta_del_dnum_ar_a32_0.C_COND10 AND customer_a32_1.C_COND04 = __tmp_delta_del_dnum_ar_a32_0.C_COND04 AND customer_a32_1.C_DELIVERY_CNT = __tmp_delta_del_dnum_ar_a32_0.C_DELIVERY_CNT AND customer_a32_1.C_COND05 = __tmp_delta_del_dnum_ar_a32_0.C_COND05 AND customer_a32_1.C_CREDIT = __tmp_delta_del_dnum_ar_a32_0.C_CREDIT AND customer_a32_1.C_COND01 = __tmp_delta_del_dnum_ar_a32_0.C_COND01 AND customer_a32_1.C_COND03  <  <border> ) AS p_0_a32_0  ) AS delta_del_customer_a32_0  ) AS delta_del_customer_extra_alias) AS tbl;


            WITH __tmp_delta_del_dnum_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_dnum_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_ins_customer FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11,COL12,COL13,COL14,COL15,COL16,COL17,COL18,COL19,COL20,COL21,COL22,COL23,COL24,COL25,COL26,COL27,COL28,COL29,COL30,COL31) :: public.customer).* 
            FROM (SELECT delta_ins_customer_a32_0.COL0 AS COL0, delta_ins_customer_a32_0.COL1 AS COL1, delta_ins_customer_a32_0.COL2 AS COL2, delta_ins_customer_a32_0.COL3 AS COL3, delta_ins_customer_a32_0.COL4 AS COL4, delta_ins_customer_a32_0.COL5 AS COL5, delta_ins_customer_a32_0.COL6 AS COL6, delta_ins_customer_a32_0.COL7 AS COL7, delta_ins_customer_a32_0.COL8 AS COL8, delta_ins_customer_a32_0.COL9 AS COL9, delta_ins_customer_a32_0.COL10 AS COL10, delta_ins_customer_a32_0.COL11 AS COL11, delta_ins_customer_a32_0.COL12 AS COL12, delta_ins_customer_a32_0.COL13 AS COL13, delta_ins_customer_a32_0.COL14 AS COL14, delta_ins_customer_a32_0.COL15 AS COL15, delta_ins_customer_a32_0.COL16 AS COL16, delta_ins_customer_a32_0.COL17 AS COL17, delta_ins_customer_a32_0.COL18 AS COL18, delta_ins_customer_a32_0.COL19 AS COL19, delta_ins_customer_a32_0.COL20 AS COL20, delta_ins_customer_a32_0.COL21 AS COL21, delta_ins_customer_a32_0.COL22 AS COL22, delta_ins_customer_a32_0.COL23 AS COL23, delta_ins_customer_a32_0.COL24 AS COL24, delta_ins_customer_a32_0.COL25 AS COL25, delta_ins_customer_a32_0.COL26 AS COL26, delta_ins_customer_a32_0.COL27 AS COL27, delta_ins_customer_a32_0.COL28 AS COL28, delta_ins_customer_a32_0.COL29 AS COL29, delta_ins_customer_a32_0.COL30 AS COL30, delta_ins_customer_a32_0.COL31 AS COL31 
FROM (SELECT p_0_a32_0.COL0 AS COL0, p_0_a32_0.COL1 AS COL1, p_0_a32_0.COL2 AS COL2, p_0_a32_0.COL3 AS COL3, p_0_a32_0.COL4 AS COL4, p_0_a32_0.COL5 AS COL5, p_0_a32_0.COL6 AS COL6, p_0_a32_0.COL7 AS COL7, p_0_a32_0.COL8 AS COL8, p_0_a32_0.COL9 AS COL9, p_0_a32_0.COL10 AS COL10, p_0_a32_0.COL11 AS COL11, p_0_a32_0.COL12 AS COL12, p_0_a32_0.COL13 AS COL13, p_0_a32_0.COL14 AS COL14, p_0_a32_0.COL15 AS COL15, p_0_a32_0.COL16 AS COL16, p_0_a32_0.COL17 AS COL17, p_0_a32_0.COL18 AS COL18, p_0_a32_0.COL19 AS COL19, p_0_a32_0.COL20 AS COL20, p_0_a32_0.COL21 AS COL21, p_0_a32_0.COL22 AS COL22, p_0_a32_0.COL23 AS COL23, p_0_a32_0.COL24 AS COL24, p_0_a32_0.COL25 AS COL25, p_0_a32_0.COL26 AS COL26, p_0_a32_0.COL27 AS COL27, p_0_a32_0.COL28 AS COL28, p_0_a32_0.COL29 AS COL29, p_0_a32_0.COL30 AS COL30, p_0_a32_0.COL31 AS COL31 
FROM (SELECT __tmp_delta_ins_dnum_ar_a32_0.C_W_ID AS COL0, __tmp_delta_ins_dnum_ar_a32_0.C_D_ID AS COL1, __tmp_delta_ins_dnum_ar_a32_0.C_ID AS COL2, __tmp_delta_ins_dnum_ar_a32_0.C_DISCOUNT AS COL3, __tmp_delta_ins_dnum_ar_a32_0.C_CREDIT AS COL4, __tmp_delta_ins_dnum_ar_a32_0.C_LAST AS COL5, __tmp_delta_ins_dnum_ar_a32_0.C_FIRST AS COL6, __tmp_delta_ins_dnum_ar_a32_0.C_CREDIT_LIM AS COL7, __tmp_delta_ins_dnum_ar_a32_0.C_BALANCE AS COL8, __tmp_delta_ins_dnum_ar_a32_0.C_YTD_PAYMENT AS COL9, __tmp_delta_ins_dnum_ar_a32_0.C_PAYMENT_CNT AS COL10, __tmp_delta_ins_dnum_ar_a32_0.C_DELIVERY_CNT AS COL11, __tmp_delta_ins_dnum_ar_a32_0.C_STREET_1 AS COL12, __tmp_delta_ins_dnum_ar_a32_0.C_STREET_2 AS COL13, __tmp_delta_ins_dnum_ar_a32_0.C_CITY AS COL14, __tmp_delta_ins_dnum_ar_a32_0.C_STATE AS COL15, __tmp_delta_ins_dnum_ar_a32_0.C_ZIP AS COL16, __tmp_delta_ins_dnum_ar_a32_0.C_PHONE AS COL17, __tmp_delta_ins_dnum_ar_a32_0.C_SINCE AS COL18, __tmp_delta_ins_dnum_ar_a32_0.C_MIDDLE AS COL19, __tmp_delta_ins_dnum_ar_a32_0.C_DATA AS COL20, __tmp_delta_ins_dnum_ar_a32_0.C_LINEAGE AS COL21, __tmp_delta_ins_dnum_ar_a32_0.C_COND01 AS COL22, __tmp_delta_ins_dnum_ar_a32_0.C_COND02 AS COL23, __tmp_delta_ins_dnum_ar_a32_0.C_COND03 AS COL24, __tmp_delta_ins_dnum_ar_a32_0.C_COND04 AS COL25, __tmp_delta_ins_dnum_ar_a32_0.C_COND05 AS COL26, __tmp_delta_ins_dnum_ar_a32_0.C_COND06 AS COL27, __tmp_delta_ins_dnum_ar_a32_0.C_COND07 AS COL28, __tmp_delta_ins_dnum_ar_a32_0.C_COND08 AS COL29, __tmp_delta_ins_dnum_ar_a32_0.C_COND09 AS COL30, __tmp_delta_ins_dnum_ar_a32_0.C_COND10 AS COL31 
FROM __tmp_delta_ins_dnum_ar AS __tmp_delta_ins_dnum_ar_a32_0 
WHERE __tmp_delta_ins_dnum_ar_a32_0.C_COND03  <  <border> AND NOT EXISTS ( SELECT * 
FROM public.customer AS customer_a32 
WHERE customer_a32.C_COND10 = __tmp_delta_ins_dnum_ar_a32_0.C_COND10 AND customer_a32.C_COND09 = __tmp_delta_ins_dnum_ar_a32_0.C_COND09 AND customer_a32.C_COND08 = __tmp_delta_ins_dnum_ar_a32_0.C_COND08 AND customer_a32.C_COND07 = __tmp_delta_ins_dnum_ar_a32_0.C_COND07 AND customer_a32.C_COND06 = __tmp_delta_ins_dnum_ar_a32_0.C_COND06 AND customer_a32.C_COND05 = __tmp_delta_ins_dnum_ar_a32_0.C_COND05 AND customer_a32.C_COND04 = __tmp_delta_ins_dnum_ar_a32_0.C_COND04 AND customer_a32.C_COND03 = __tmp_delta_ins_dnum_ar_a32_0.C_COND03 AND customer_a32.C_COND02 = __tmp_delta_ins_dnum_ar_a32_0.C_COND02 AND customer_a32.C_COND01 = __tmp_delta_ins_dnum_ar_a32_0.C_COND01 AND customer_a32.C_LINEAGE = __tmp_delta_ins_dnum_ar_a32_0.C_LINEAGE AND customer_a32.C_DATA = __tmp_delta_ins_dnum_ar_a32_0.C_DATA AND customer_a32.C_MIDDLE = __tmp_delta_ins_dnum_ar_a32_0.C_MIDDLE AND customer_a32.C_SINCE = __tmp_delta_ins_dnum_ar_a32_0.C_SINCE AND customer_a32.C_PHONE = __tmp_delta_ins_dnum_ar_a32_0.C_PHONE AND customer_a32.C_ZIP = __tmp_delta_ins_dnum_ar_a32_0.C_ZIP AND customer_a32.C_STATE = __tmp_delta_ins_dnum_ar_a32_0.C_STATE AND customer_a32.C_CITY = __tmp_delta_ins_dnum_ar_a32_0.C_CITY AND customer_a32.C_STREET_2 = __tmp_delta_ins_dnum_ar_a32_0.C_STREET_2 AND customer_a32.C_STREET_1 = __tmp_delta_ins_dnum_ar_a32_0.C_STREET_1 AND customer_a32.C_DELIVERY_CNT = __tmp_delta_ins_dnum_ar_a32_0.C_DELIVERY_CNT AND customer_a32.C_PAYMENT_CNT = __tmp_delta_ins_dnum_ar_a32_0.C_PAYMENT_CNT AND customer_a32.C_YTD_PAYMENT = __tmp_delta_ins_dnum_ar_a32_0.C_YTD_PAYMENT AND customer_a32.C_BALANCE = __tmp_delta_ins_dnum_ar_a32_0.C_BALANCE AND customer_a32.C_CREDIT_LIM = __tmp_delta_ins_dnum_ar_a32_0.C_CREDIT_LIM AND customer_a32.C_FIRST = __tmp_delta_ins_dnum_ar_a32_0.C_FIRST AND customer_a32.C_LAST = __tmp_delta_ins_dnum_ar_a32_0.C_LAST AND customer_a32.C_CREDIT = __tmp_delta_ins_dnum_ar_a32_0.C_CREDIT AND customer_a32.C_DISCOUNT = __tmp_delta_ins_dnum_ar_a32_0.C_DISCOUNT AND customer_a32.C_ID = __tmp_delta_ins_dnum_ar_a32_0.C_ID AND customer_a32.C_D_ID = __tmp_delta_ins_dnum_ar_a32_0.C_D_ID AND customer_a32.C_W_ID = __tmp_delta_ins_dnum_ar_a32_0.C_W_ID ) ) AS p_0_a32_0  ) AS delta_ins_customer_a32_0  ) AS delta_ins_customer_extra_alias) AS tbl; 


            IF array_delta_del_customer IS DISTINCT FROM NULL THEN 
                FOREACH temprec_delta_del_customer IN array array_delta_del_customer  LOOP 
                   DELETE FROM public.customer WHERE C_W_ID =  temprec_delta_del_customer.C_W_ID AND C_D_ID =  temprec_delta_del_customer.C_D_ID AND C_ID =  temprec_delta_del_customer.C_ID AND C_DISCOUNT =  temprec_delta_del_customer.C_DISCOUNT AND C_CREDIT =  temprec_delta_del_customer.C_CREDIT AND C_LAST =  temprec_delta_del_customer.C_LAST AND C_FIRST =  temprec_delta_del_customer.C_FIRST AND C_CREDIT_LIM =  temprec_delta_del_customer.C_CREDIT_LIM AND C_BALANCE =  temprec_delta_del_customer.C_BALANCE AND C_YTD_PAYMENT =  temprec_delta_del_customer.C_YTD_PAYMENT AND C_PAYMENT_CNT =  temprec_delta_del_customer.C_PAYMENT_CNT AND C_DELIVERY_CNT =  temprec_delta_del_customer.C_DELIVERY_CNT AND C_STREET_1 =  temprec_delta_del_customer.C_STREET_1 AND C_STREET_2 =  temprec_delta_del_customer.C_STREET_2 AND C_CITY =  temprec_delta_del_customer.C_CITY AND C_STATE =  temprec_delta_del_customer.C_STATE AND C_ZIP =  temprec_delta_del_customer.C_ZIP AND C_PHONE =  temprec_delta_del_customer.C_PHONE AND C_SINCE =  temprec_delta_del_customer.C_SINCE AND C_MIDDLE =  temprec_delta_del_customer.C_MIDDLE AND C_DATA =  temprec_delta_del_customer.C_DATA AND C_LINEAGE =  temprec_delta_del_customer.C_LINEAGE AND C_COND01 =  temprec_delta_del_customer.C_COND01 AND C_COND02 =  temprec_delta_del_customer.C_COND02 AND C_COND03 =  temprec_delta_del_customer.C_COND03 AND C_COND04 =  temprec_delta_del_customer.C_COND04 AND C_COND05 =  temprec_delta_del_customer.C_COND05 AND C_COND06 =  temprec_delta_del_customer.C_COND06 AND C_COND07 =  temprec_delta_del_customer.C_COND07 AND C_COND08 =  temprec_delta_del_customer.C_COND08 AND C_COND09 =  temprec_delta_del_customer.C_COND09 AND C_COND10 =  temprec_delta_del_customer.C_COND10;
                END LOOP;
            END IF;


            IF array_delta_ins_customer IS DISTINCT FROM NULL THEN 
                INSERT INTO public.customer (SELECT * FROM unnest(array_delta_ins_customer) as array_delta_ins_customer_alias) ; 
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
      DELETE FROM __tmp_delta_del_dnum WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE,C_COND01,C_COND02,C_COND03,C_COND04,C_COND05,C_COND06,C_COND07,C_COND08,C_COND09,C_COND10) = NEW;
      INSERT INTO __tmp_delta_ins_dnum SELECT (NEW).*; 
    ELSIF TG_OP = 'UPDATE' THEN
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_ins_dnum WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE,C_COND01,C_COND02,C_COND03,C_COND04,C_COND05,C_COND06,C_COND07,C_COND08,C_COND09,C_COND10) = OLD;
      INSERT INTO __tmp_delta_del_dnum SELECT (OLD).*;
      DELETE FROM __tmp_delta_del_dnum WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE,C_COND01,C_COND02,C_COND03,C_COND04,C_COND05,C_COND06,C_COND07,C_COND08,C_COND09,C_COND10) = NEW;
      INSERT INTO __tmp_delta_ins_dnum SELECT (NEW).*; 
    ELSIF TG_OP = 'DELETE' THEN
      -- RAISE LOG 'OLD: %', OLD;
      DELETE FROM __tmp_delta_ins_dnum WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE,C_COND01,C_COND02,C_COND03,C_COND04,C_COND05,C_COND06,C_COND07,C_COND08,C_COND09,C_COND10) = OLD;
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
    public.customer DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.clean_dummy_dnum();


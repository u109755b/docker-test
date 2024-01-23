CREATE OR REPLACE VIEW public.d_customer AS 
SELECT __dummy__.COL0 AS C_W_ID, __dummy__.COL1 AS C_D_ID, __dummy__.COL2 AS C_ID, __dummy__.COL3 AS C_DISCOUNT, __dummy__.COL4 AS C_CREDIT, __dummy__.COL5 AS C_LAST, __dummy__.COL6 AS C_FIRST, __dummy__.COL7 AS C_CREDIT_LIM, __dummy__.COL8 AS C_BALANCE, __dummy__.COL9 AS C_YTD_PAYMENT, __dummy__.COL10 AS C_PAYMENT_CNT, __dummy__.COL11 AS C_DELIVERY_CNT, __dummy__.COL12 AS C_STREET_1, __dummy__.COL13 AS C_STREET_2, __dummy__.COL14 AS C_CITY, __dummy__.COL15 AS C_STATE, __dummy__.COL16 AS C_ZIP, __dummy__.COL17 AS C_PHONE, __dummy__.COL18 AS C_SINCE, __dummy__.COL19 AS C_MIDDLE, __dummy__.COL20 AS C_DATA, __dummy__.COL21 AS C_LINEAGE FROM (SELECT d_customer_a22_0.COL0 AS COL0, d_customer_a22_0.COL1 AS COL1, d_customer_a22_0.COL2 AS COL2, d_customer_a22_0.COL3 AS COL3, d_customer_a22_0.COL4 AS COL4, d_customer_a22_0.COL5 AS COL5, d_customer_a22_0.COL6 AS COL6, d_customer_a22_0.COL7 AS COL7, d_customer_a22_0.COL8 AS COL8, d_customer_a22_0.COL9 AS COL9, d_customer_a22_0.COL10 AS COL10, d_customer_a22_0.COL11 AS COL11, d_customer_a22_0.COL12 AS COL12, d_customer_a22_0.COL13 AS COL13, d_customer_a22_0.COL14 AS COL14, d_customer_a22_0.COL15 AS COL15, d_customer_a22_0.COL16 AS COL16, d_customer_a22_0.COL17 AS COL17, d_customer_a22_0.COL18 AS COL18, d_customer_a22_0.COL19 AS COL19, d_customer_a22_0.COL20 AS COL20, d_customer_a22_0.COL21 AS COL21 FROM (SELECT customer_a22_0.C_W_ID AS COL0, customer_a22_0.C_D_ID AS COL1, customer_a22_0.C_ID AS COL2, customer_a22_0.C_DISCOUNT AS COL3, customer_a22_0.C_CREDIT AS COL4, customer_a22_0.C_LAST AS COL5, customer_a22_0.C_FIRST AS COL6, customer_a22_0.C_CREDIT_LIM AS COL7, customer_a22_0.C_BALANCE AS COL8, customer_a22_0.C_YTD_PAYMENT AS COL9, customer_a22_0.C_PAYMENT_CNT AS COL10, customer_a22_0.C_DELIVERY_CNT AS COL11, customer_a22_0.C_STREET_1 AS COL12, customer_a22_0.C_STREET_2 AS COL13, customer_a22_0.C_CITY AS COL14, customer_a22_0.C_STATE AS COL15, customer_a22_0.C_ZIP AS COL16, customer_a22_0.C_PHONE AS COL17, customer_a22_0.C_SINCE AS COL18, customer_a22_0.C_MIDDLE AS COL19, customer_a22_0.C_DATA AS COL20, customer_a22_0.C_LINEAGE AS COL21 FROM public.customer AS customer_a22_0   ) AS d_customer_a22_0   ) AS __dummy__   ;

CREATE EXTENSION IF NOT EXISTS plsh;

CREATE TABLE IF NOT EXISTS public.__dummy__d_customer_detected_deletions (txid int, LIKE public.d_customer );
CREATE INDEX IF NOT EXISTS idx__dummy__d_customer_detected_deletions ON public.__dummy__d_customer_detected_deletions (txid);
CREATE TABLE IF NOT EXISTS public.__dummy__d_customer_detected_insertions (txid int, LIKE public.d_customer );
CREATE INDEX IF NOT EXISTS idx__dummy__d_customer_detected_insertions ON public.__dummy__d_customer_detected_insertions (txid);

CREATE OR REPLACE FUNCTION public.d_customer_get_detected_update_data(txid int)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  deletion_data text;
  insertion_data text;
  json_data text;
  BEGIN
    insertion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__d_customer_detected_insertions as t where t.txid = $1);
    IF insertion_data IS NOT DISTINCT FROM NULL THEN
        insertion_data := '[]';
    END IF;
    deletion_data := (SELECT (array_to_json(array_agg(t)))::text FROM public.__dummy__d_customer_detected_deletions as t where t.txid = $1);
    IF deletion_data IS NOT DISTINCT FROM NULL THEN
        deletion_data := '[]';
    END IF;
    IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN
        -- calcuate the update data
        json_data := concat('{"view": ' , '"public.d_customer"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
        -- clear the update data
        DELETE FROM public.__dummy__d_customer_detected_deletions t where t.txid = $1;
        DELETE FROM public.__dummy__d_customer_detected_insertions t where t.txid = $1;
    END IF;
    RETURN json_data;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d_customer_run_shell(text) RETURNS text AS $$
#!/bin/sh

result=$(curl -s -X POST -H "Content-Type: application/json" $DEJIMA_EXECUTION_ENDPOINT -d "$1")
if  [ "$result" = "true" ];  then
    echo "true"
else 
    echo $result
fi
$$ LANGUAGE plsh;

CREATE OR REPLACE FUNCTION public.customer_materialization_for_d_customer()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_customer_for_d_customer' OR table_name = '__tmp_delta_del_customer_for_d_customer')
    THEN
        -- RAISE LOG 'execute procedure customer_materialization_for_d_customer';
        CREATE TEMPORARY TABLE __tmp_delta_ins_customer_for_d_customer ( LIKE public.customer ) WITH OIDS ON COMMIT DROP;
        CREATE TEMPORARY TABLE __tmp_delta_del_customer_for_d_customer ( LIKE public.customer ) WITH OIDS ON COMMIT DROP;

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

DROP TRIGGER IF EXISTS customer_trigger_materialization_for_d_customer ON public.customer;
CREATE TRIGGER customer_trigger_materialization_for_d_customer
    BEFORE INSERT OR UPDATE OR DELETE ON
    public.customer FOR EACH STATEMENT EXECUTE PROCEDURE public.customer_materialization_for_d_customer();

CREATE OR REPLACE FUNCTION public.customer_update_for_d_customer()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    -- RAISE LOG 'execute procedure customer_update_for_d_customer';
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd_customer_delta_action_flag') THEN
        IF TG_OP = 'INSERT' THEN
        -- RAISE LOG 'NEW: %', NEW;
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_del_customer_for_d_customer WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE)= NEW;
        INSERT INTO __tmp_delta_ins_customer_for_d_customer SELECT (NEW).*;
        ELSIF TG_OP = 'UPDATE' THEN
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_ins_customer_for_d_customer WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE) = OLD;
        INSERT INTO __tmp_delta_del_customer_for_d_customer SELECT (OLD).*;
        DELETE FROM __tmp_delta_del_customer_for_d_customer WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE) = NEW;
        INSERT INTO __tmp_delta_ins_customer_for_d_customer SELECT (NEW).*;
        ELSIF TG_OP = 'DELETE' THEN
        -- RAISE LOG 'OLD: %', OLD;
        DELETE FROM __tmp_delta_ins_customer_for_d_customer WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE) = OLD;
        INSERT INTO __tmp_delta_del_customer_for_d_customer SELECT (OLD).*;
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

DROP TRIGGER IF EXISTS customer_trigger_update_for_d_customer ON public.customer;
CREATE TRIGGER customer_trigger_update_for_d_customer
    AFTER INSERT OR UPDATE OR DELETE ON
    public.customer FOR EACH ROW EXECUTE PROCEDURE public.customer_update_for_d_customer();

CREATE OR REPLACE FUNCTION public.customer_detect_update_on_d_customer()
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
detected_deletions public.d_customer[];
detected_insertions public.d_customer[];
delta_ins_size int;
delta_del_size int;
BEGIN
IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'customer_detect_update_on_d_customer_flag') THEN
    CREATE TEMPORARY TABLE customer_detect_update_on_d_customer_flag ON COMMIT DROP AS (SELECT true as finish);
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd_customer_delta_action_flag') THEN
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_customer_for_d_customer AS tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_customer_for_d_customer;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_customer_for_d_customer tbl;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_customer_for_d_customer;

        WITH __tmp_delta_ins_customer_for_d_customer_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size),
        __tmp_delta_del_customer_for_d_customer_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_insertions FROM (SELECT __dummy__.COL0 AS C_W_ID, __dummy__.COL1 AS C_D_ID, __dummy__.COL2 AS C_ID, __dummy__.COL3 AS C_DISCOUNT, __dummy__.COL4 AS C_CREDIT, __dummy__.COL5 AS C_LAST, __dummy__.COL6 AS C_FIRST, __dummy__.COL7 AS C_CREDIT_LIM, __dummy__.COL8 AS C_BALANCE, __dummy__.COL9 AS C_YTD_PAYMENT, __dummy__.COL10 AS C_PAYMENT_CNT, __dummy__.COL11 AS C_DELIVERY_CNT, __dummy__.COL12 AS C_STREET_1, __dummy__.COL13 AS C_STREET_2, __dummy__.COL14 AS C_CITY, __dummy__.COL15 AS C_STATE, __dummy__.COL16 AS C_ZIP, __dummy__.COL17 AS C_PHONE, __dummy__.COL18 AS C_SINCE, __dummy__.COL19 AS C_MIDDLE, __dummy__.COL20 AS C_DATA, __dummy__.COL21 AS C_LINEAGE FROM (SELECT part_ins_d_customer_a22_0.COL0 AS COL0, part_ins_d_customer_a22_0.COL1 AS COL1, part_ins_d_customer_a22_0.COL2 AS COL2, part_ins_d_customer_a22_0.COL3 AS COL3, part_ins_d_customer_a22_0.COL4 AS COL4, part_ins_d_customer_a22_0.COL5 AS COL5, part_ins_d_customer_a22_0.COL6 AS COL6, part_ins_d_customer_a22_0.COL7 AS COL7, part_ins_d_customer_a22_0.COL8 AS COL8, part_ins_d_customer_a22_0.COL9 AS COL9, part_ins_d_customer_a22_0.COL10 AS COL10, part_ins_d_customer_a22_0.COL11 AS COL11, part_ins_d_customer_a22_0.COL12 AS COL12, part_ins_d_customer_a22_0.COL13 AS COL13, part_ins_d_customer_a22_0.COL14 AS COL14, part_ins_d_customer_a22_0.COL15 AS COL15, part_ins_d_customer_a22_0.COL16 AS COL16, part_ins_d_customer_a22_0.COL17 AS COL17, part_ins_d_customer_a22_0.COL18 AS COL18, part_ins_d_customer_a22_0.COL19 AS COL19, part_ins_d_customer_a22_0.COL20 AS COL20, part_ins_d_customer_a22_0.COL21 AS COL21 FROM (SELECT p_0_a22_0.COL0 AS COL0, p_0_a22_0.COL1 AS COL1, p_0_a22_0.COL2 AS COL2, p_0_a22_0.COL3 AS COL3, p_0_a22_0.COL4 AS COL4, p_0_a22_0.COL5 AS COL5, p_0_a22_0.COL6 AS COL6, p_0_a22_0.COL7 AS COL7, p_0_a22_0.COL8 AS COL8, p_0_a22_0.COL9 AS COL9, p_0_a22_0.COL10 AS COL10, p_0_a22_0.COL11 AS COL11, p_0_a22_0.COL12 AS COL12, p_0_a22_0.COL13 AS COL13, p_0_a22_0.COL14 AS COL14, p_0_a22_0.COL15 AS COL15, p_0_a22_0.COL16 AS COL16, p_0_a22_0.COL17 AS COL17, p_0_a22_0.COL18 AS COL18, p_0_a22_0.COL19 AS COL19, p_0_a22_0.COL20 AS COL20, p_0_a22_0.COL21 AS COL21 FROM (SELECT __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_W_ID AS COL0, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_D_ID AS COL1, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_ID AS COL2, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_DISCOUNT AS COL3, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_CREDIT AS COL4, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_LAST AS COL5, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_FIRST AS COL6, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_CREDIT_LIM AS COL7, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_BALANCE AS COL8, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_YTD_PAYMENT AS COL9, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_PAYMENT_CNT AS COL10, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_DELIVERY_CNT AS COL11, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_STREET_1 AS COL12, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_STREET_2 AS COL13, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_CITY AS COL14, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_STATE AS COL15, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_ZIP AS COL16, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_PHONE AS COL17, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_SINCE AS COL18, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_MIDDLE AS COL19, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_DATA AS COL20, __tmp_delta_ins_customer_for_d_customer_ar_a22_0.C_LINEAGE AS COL21 FROM __tmp_delta_ins_customer_for_d_customer_ar AS __tmp_delta_ins_customer_for_d_customer_ar_a22_0   ) AS p_0_a22_0   ) AS part_ins_d_customer_a22_0   ) AS __dummy__   ) AS tbl;

        insertion_data := (SELECT (array_to_json(detected_insertions))::text);
        IF insertion_data IS NOT DISTINCT FROM NULL THEN
            insertion_data := '[]';
        END IF;

        WITH __tmp_delta_ins_customer_for_d_customer_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size),
        __tmp_delta_del_customer_for_d_customer_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_deletions FROM (SELECT __dummy__.COL0 AS C_W_ID, __dummy__.COL1 AS C_D_ID, __dummy__.COL2 AS C_ID, __dummy__.COL3 AS C_DISCOUNT, __dummy__.COL4 AS C_CREDIT, __dummy__.COL5 AS C_LAST, __dummy__.COL6 AS C_FIRST, __dummy__.COL7 AS C_CREDIT_LIM, __dummy__.COL8 AS C_BALANCE, __dummy__.COL9 AS C_YTD_PAYMENT, __dummy__.COL10 AS C_PAYMENT_CNT, __dummy__.COL11 AS C_DELIVERY_CNT, __dummy__.COL12 AS C_STREET_1, __dummy__.COL13 AS C_STREET_2, __dummy__.COL14 AS C_CITY, __dummy__.COL15 AS C_STATE, __dummy__.COL16 AS C_ZIP, __dummy__.COL17 AS C_PHONE, __dummy__.COL18 AS C_SINCE, __dummy__.COL19 AS C_MIDDLE, __dummy__.COL20 AS C_DATA, __dummy__.COL21 AS C_LINEAGE FROM (SELECT part_del_d_customer_a22_0.COL0 AS COL0, part_del_d_customer_a22_0.COL1 AS COL1, part_del_d_customer_a22_0.COL2 AS COL2, part_del_d_customer_a22_0.COL3 AS COL3, part_del_d_customer_a22_0.COL4 AS COL4, part_del_d_customer_a22_0.COL5 AS COL5, part_del_d_customer_a22_0.COL6 AS COL6, part_del_d_customer_a22_0.COL7 AS COL7, part_del_d_customer_a22_0.COL8 AS COL8, part_del_d_customer_a22_0.COL9 AS COL9, part_del_d_customer_a22_0.COL10 AS COL10, part_del_d_customer_a22_0.COL11 AS COL11, part_del_d_customer_a22_0.COL12 AS COL12, part_del_d_customer_a22_0.COL13 AS COL13, part_del_d_customer_a22_0.COL14 AS COL14, part_del_d_customer_a22_0.COL15 AS COL15, part_del_d_customer_a22_0.COL16 AS COL16, part_del_d_customer_a22_0.COL17 AS COL17, part_del_d_customer_a22_0.COL18 AS COL18, part_del_d_customer_a22_0.COL19 AS COL19, part_del_d_customer_a22_0.COL20 AS COL20, part_del_d_customer_a22_0.COL21 AS COL21 FROM (SELECT p_0_a22_0.COL0 AS COL0, p_0_a22_0.COL1 AS COL1, p_0_a22_0.COL2 AS COL2, p_0_a22_0.COL3 AS COL3, p_0_a22_0.COL4 AS COL4, p_0_a22_0.COL5 AS COL5, p_0_a22_0.COL6 AS COL6, p_0_a22_0.COL7 AS COL7, p_0_a22_0.COL8 AS COL8, p_0_a22_0.COL9 AS COL9, p_0_a22_0.COL10 AS COL10, p_0_a22_0.COL11 AS COL11, p_0_a22_0.COL12 AS COL12, p_0_a22_0.COL13 AS COL13, p_0_a22_0.COL14 AS COL14, p_0_a22_0.COL15 AS COL15, p_0_a22_0.COL16 AS COL16, p_0_a22_0.COL17 AS COL17, p_0_a22_0.COL18 AS COL18, p_0_a22_0.COL19 AS COL19, p_0_a22_0.COL20 AS COL20, p_0_a22_0.COL21 AS COL21 FROM (SELECT __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_W_ID AS COL0, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_D_ID AS COL1, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_ID AS COL2, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_DISCOUNT AS COL3, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_CREDIT AS COL4, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_LAST AS COL5, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_FIRST AS COL6, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_CREDIT_LIM AS COL7, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_BALANCE AS COL8, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_YTD_PAYMENT AS COL9, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_PAYMENT_CNT AS COL10, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_DELIVERY_CNT AS COL11, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_STREET_1 AS COL12, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_STREET_2 AS COL13, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_CITY AS COL14, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_STATE AS COL15, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_ZIP AS COL16, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_PHONE AS COL17, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_SINCE AS COL18, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_MIDDLE AS COL19, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_DATA AS COL20, __tmp_delta_del_customer_for_d_customer_ar_a22_0.C_LINEAGE AS COL21 FROM __tmp_delta_del_customer_for_d_customer_ar AS __tmp_delta_del_customer_for_d_customer_ar_a22_0   ) AS p_0_a22_0   ) AS part_del_d_customer_a22_0   ) AS __dummy__   ) AS tbl;

        deletion_data := (
        SELECT (array_to_json(detected_deletions))::text);
        IF deletion_data IS NOT DISTINCT FROM NULL THEN
            deletion_data := '[]';
        END IF;
        IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN
            user_name := (SELECT session_user);
            IF NOT (user_name = 'dejima') THEN
                xid := (SELECT txid_current());
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.d_customer"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.d_customer_run_shell(json_data);
                IF result = 'true' THEN
                    DROP TABLE __tmp_delta_ins_customer_for_d_customer;
                    DROP TABLE __tmp_delta_del_customer_for_d_customer;
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
                -- DELETE FROM public.__dummy__d_customer_detected_deletions;
                INSERT INTO public.__dummy__d_customer_detected_deletions
                    ( SELECT xid, * FROM unnest(detected_deletions) as detected_deletions_alias );

                -- DELETE FROM public.__dummy__d_customer_detected_insertions;
                INSERT INTO public.__dummy__d_customer_detected_insertions
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
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the function public.customer_detect_update_on_d_customer() ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS customer_detect_update_on_d_customer ON public.customer;
CREATE CONSTRAINT TRIGGER customer_detect_update_on_d_customer
    AFTER INSERT OR UPDATE OR DELETE ON
    public.customer DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.customer_detect_update_on_d_customer();

CREATE OR REPLACE FUNCTION public.customer_propagate_updates_to_d_customer ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS public.customer_detect_update_on_d_customer IMMEDIATE;
    SET CONSTRAINTS public.customer_detect_update_on_d_customer DEFERRED;
    DROP TABLE IF EXISTS customer_detect_update_on_d_customer_flag;
    DROP TABLE IF EXISTS __tmp_delta_del_customer_for_d_customer;
    DROP TABLE IF EXISTS __tmp_delta_ins_customer_for_d_customer;
    RETURN true;
  END;
$$;



CREATE OR REPLACE FUNCTION public.d_customer_delta_action()
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
  array_delta_del public.d_customer[];
  array_delta_ins public.d_customer[];
  temprec_delta_del_customer public.customer%ROWTYPE;
            array_delta_del_customer public.customer[];
temprec_delta_ins_customer public.customer%ROWTYPE;
            array_delta_ins_customer public.customer[];
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'd_customer_delta_action_flag') THEN
        -- RAISE LOG 'execute procedure d_customer_delta_action';
        CREATE TEMPORARY TABLE d_customer_delta_action_flag ON COMMIT DROP AS (SELECT true as finish);
        IF EXISTS (SELECT WHERE false )
        THEN
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the view are violated';
        END IF;
        IF EXISTS (SELECT WHERE false )
        THEN
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the source relations are violated';
        END IF;
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_d_customer AS tbl;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_d_customer as tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_d_customer;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_d_customer;
        
            WITH __tmp_delta_del_d_customer_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_d_customer_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_del_customer FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11,COL12,COL13,COL14,COL15,COL16,COL17,COL18,COL19,COL20,COL21) :: public.customer).*
            FROM (SELECT delta_del_customer_a22_0.COL0 AS COL0, delta_del_customer_a22_0.COL1 AS COL1, delta_del_customer_a22_0.COL2 AS COL2, delta_del_customer_a22_0.COL3 AS COL3, delta_del_customer_a22_0.COL4 AS COL4, delta_del_customer_a22_0.COL5 AS COL5, delta_del_customer_a22_0.COL6 AS COL6, delta_del_customer_a22_0.COL7 AS COL7, delta_del_customer_a22_0.COL8 AS COL8, delta_del_customer_a22_0.COL9 AS COL9, delta_del_customer_a22_0.COL10 AS COL10, delta_del_customer_a22_0.COL11 AS COL11, delta_del_customer_a22_0.COL12 AS COL12, delta_del_customer_a22_0.COL13 AS COL13, delta_del_customer_a22_0.COL14 AS COL14, delta_del_customer_a22_0.COL15 AS COL15, delta_del_customer_a22_0.COL16 AS COL16, delta_del_customer_a22_0.COL17 AS COL17, delta_del_customer_a22_0.COL18 AS COL18, delta_del_customer_a22_0.COL19 AS COL19, delta_del_customer_a22_0.COL20 AS COL20, delta_del_customer_a22_0.COL21 AS COL21 FROM (SELECT p_0_a22_0.COL0 AS COL0, p_0_a22_0.COL1 AS COL1, p_0_a22_0.COL2 AS COL2, p_0_a22_0.COL3 AS COL3, p_0_a22_0.COL4 AS COL4, p_0_a22_0.COL5 AS COL5, p_0_a22_0.COL6 AS COL6, p_0_a22_0.COL7 AS COL7, p_0_a22_0.COL8 AS COL8, p_0_a22_0.COL9 AS COL9, p_0_a22_0.COL10 AS COL10, p_0_a22_0.COL11 AS COL11, p_0_a22_0.COL12 AS COL12, p_0_a22_0.COL13 AS COL13, p_0_a22_0.COL14 AS COL14, p_0_a22_0.COL15 AS COL15, p_0_a22_0.COL16 AS COL16, p_0_a22_0.COL17 AS COL17, p_0_a22_0.COL18 AS COL18, p_0_a22_0.COL19 AS COL19, p_0_a22_0.COL20 AS COL20, p_0_a22_0.COL21 AS COL21 FROM (SELECT customer_a22_1.C_W_ID AS COL0, customer_a22_1.C_D_ID AS COL1, customer_a22_1.C_ID AS COL2, customer_a22_1.C_DISCOUNT AS COL3, customer_a22_1.C_CREDIT AS COL4, customer_a22_1.C_LAST AS COL5, customer_a22_1.C_FIRST AS COL6, customer_a22_1.C_CREDIT_LIM AS COL7, customer_a22_1.C_BALANCE AS COL8, customer_a22_1.C_YTD_PAYMENT AS COL9, customer_a22_1.C_PAYMENT_CNT AS COL10, customer_a22_1.C_DELIVERY_CNT AS COL11, customer_a22_1.C_STREET_1 AS COL12, customer_a22_1.C_STREET_2 AS COL13, customer_a22_1.C_CITY AS COL14, customer_a22_1.C_STATE AS COL15, customer_a22_1.C_ZIP AS COL16, customer_a22_1.C_PHONE AS COL17, customer_a22_1.C_SINCE AS COL18, customer_a22_1.C_MIDDLE AS COL19, customer_a22_1.C_DATA AS COL20, customer_a22_1.C_LINEAGE AS COL21 FROM __tmp_delta_del_d_customer_ar AS __tmp_delta_del_d_customer_ar_a22_0, public.customer AS customer_a22_1 WHERE customer_a22_1.C_CREDIT_LIM = __tmp_delta_del_d_customer_ar_a22_0.C_CREDIT_LIM AND customer_a22_1.C_LAST = __tmp_delta_del_d_customer_ar_a22_0.C_LAST AND customer_a22_1.C_ID = __tmp_delta_del_d_customer_ar_a22_0.C_ID AND customer_a22_1.C_LINEAGE = __tmp_delta_del_d_customer_ar_a22_0.C_LINEAGE AND customer_a22_1.C_ZIP = __tmp_delta_del_d_customer_ar_a22_0.C_ZIP AND customer_a22_1.C_SINCE = __tmp_delta_del_d_customer_ar_a22_0.C_SINCE AND customer_a22_1.C_FIRST = __tmp_delta_del_d_customer_ar_a22_0.C_FIRST AND customer_a22_1.C_STREET_1 = __tmp_delta_del_d_customer_ar_a22_0.C_STREET_1 AND customer_a22_1.C_D_ID = __tmp_delta_del_d_customer_ar_a22_0.C_D_ID AND customer_a22_1.C_DISCOUNT = __tmp_delta_del_d_customer_ar_a22_0.C_DISCOUNT AND customer_a22_1.C_BALANCE = __tmp_delta_del_d_customer_ar_a22_0.C_BALANCE AND customer_a22_1.C_STATE = __tmp_delta_del_d_customer_ar_a22_0.C_STATE AND customer_a22_1.C_MIDDLE = __tmp_delta_del_d_customer_ar_a22_0.C_MIDDLE AND customer_a22_1.C_YTD_PAYMENT = __tmp_delta_del_d_customer_ar_a22_0.C_YTD_PAYMENT AND customer_a22_1.C_W_ID = __tmp_delta_del_d_customer_ar_a22_0.C_W_ID AND customer_a22_1.C_STREET_2 = __tmp_delta_del_d_customer_ar_a22_0.C_STREET_2 AND customer_a22_1.C_CITY = __tmp_delta_del_d_customer_ar_a22_0.C_CITY AND customer_a22_1.C_PAYMENT_CNT = __tmp_delta_del_d_customer_ar_a22_0.C_PAYMENT_CNT AND customer_a22_1.C_DATA = __tmp_delta_del_d_customer_ar_a22_0.C_DATA AND customer_a22_1.C_PHONE = __tmp_delta_del_d_customer_ar_a22_0.C_PHONE AND customer_a22_1.C_DELIVERY_CNT = __tmp_delta_del_d_customer_ar_a22_0.C_DELIVERY_CNT AND customer_a22_1.C_CREDIT = __tmp_delta_del_d_customer_ar_a22_0.C_CREDIT  ) AS p_0_a22_0   ) AS delta_del_customer_a22_0   ) AS delta_del_customer_extra_alias) AS tbl;


            WITH __tmp_delta_del_d_customer_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_d_customer_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_ins_customer FROM (SELECT (ROW(COL0,COL1,COL2,COL3,COL4,COL5,COL6,COL7,COL8,COL9,COL10,COL11,COL12,COL13,COL14,COL15,COL16,COL17,COL18,COL19,COL20,COL21) :: public.customer).*
            FROM (SELECT delta_ins_customer_a22_0.COL0 AS COL0, delta_ins_customer_a22_0.COL1 AS COL1, delta_ins_customer_a22_0.COL2 AS COL2, delta_ins_customer_a22_0.COL3 AS COL3, delta_ins_customer_a22_0.COL4 AS COL4, delta_ins_customer_a22_0.COL5 AS COL5, delta_ins_customer_a22_0.COL6 AS COL6, delta_ins_customer_a22_0.COL7 AS COL7, delta_ins_customer_a22_0.COL8 AS COL8, delta_ins_customer_a22_0.COL9 AS COL9, delta_ins_customer_a22_0.COL10 AS COL10, delta_ins_customer_a22_0.COL11 AS COL11, delta_ins_customer_a22_0.COL12 AS COL12, delta_ins_customer_a22_0.COL13 AS COL13, delta_ins_customer_a22_0.COL14 AS COL14, delta_ins_customer_a22_0.COL15 AS COL15, delta_ins_customer_a22_0.COL16 AS COL16, delta_ins_customer_a22_0.COL17 AS COL17, delta_ins_customer_a22_0.COL18 AS COL18, delta_ins_customer_a22_0.COL19 AS COL19, delta_ins_customer_a22_0.COL20 AS COL20, delta_ins_customer_a22_0.COL21 AS COL21 FROM (SELECT p_0_a22_0.COL0 AS COL0, p_0_a22_0.COL1 AS COL1, p_0_a22_0.COL2 AS COL2, p_0_a22_0.COL3 AS COL3, p_0_a22_0.COL4 AS COL4, p_0_a22_0.COL5 AS COL5, p_0_a22_0.COL6 AS COL6, p_0_a22_0.COL7 AS COL7, p_0_a22_0.COL8 AS COL8, p_0_a22_0.COL9 AS COL9, p_0_a22_0.COL10 AS COL10, p_0_a22_0.COL11 AS COL11, p_0_a22_0.COL12 AS COL12, p_0_a22_0.COL13 AS COL13, p_0_a22_0.COL14 AS COL14, p_0_a22_0.COL15 AS COL15, p_0_a22_0.COL16 AS COL16, p_0_a22_0.COL17 AS COL17, p_0_a22_0.COL18 AS COL18, p_0_a22_0.COL19 AS COL19, p_0_a22_0.COL20 AS COL20, p_0_a22_0.COL21 AS COL21 FROM (SELECT __tmp_delta_ins_d_customer_ar_a22_0.C_W_ID AS COL0, __tmp_delta_ins_d_customer_ar_a22_0.C_D_ID AS COL1, __tmp_delta_ins_d_customer_ar_a22_0.C_ID AS COL2, __tmp_delta_ins_d_customer_ar_a22_0.C_DISCOUNT AS COL3, __tmp_delta_ins_d_customer_ar_a22_0.C_CREDIT AS COL4, __tmp_delta_ins_d_customer_ar_a22_0.C_LAST AS COL5, __tmp_delta_ins_d_customer_ar_a22_0.C_FIRST AS COL6, __tmp_delta_ins_d_customer_ar_a22_0.C_CREDIT_LIM AS COL7, __tmp_delta_ins_d_customer_ar_a22_0.C_BALANCE AS COL8, __tmp_delta_ins_d_customer_ar_a22_0.C_YTD_PAYMENT AS COL9, __tmp_delta_ins_d_customer_ar_a22_0.C_PAYMENT_CNT AS COL10, __tmp_delta_ins_d_customer_ar_a22_0.C_DELIVERY_CNT AS COL11, __tmp_delta_ins_d_customer_ar_a22_0.C_STREET_1 AS COL12, __tmp_delta_ins_d_customer_ar_a22_0.C_STREET_2 AS COL13, __tmp_delta_ins_d_customer_ar_a22_0.C_CITY AS COL14, __tmp_delta_ins_d_customer_ar_a22_0.C_STATE AS COL15, __tmp_delta_ins_d_customer_ar_a22_0.C_ZIP AS COL16, __tmp_delta_ins_d_customer_ar_a22_0.C_PHONE AS COL17, __tmp_delta_ins_d_customer_ar_a22_0.C_SINCE AS COL18, __tmp_delta_ins_d_customer_ar_a22_0.C_MIDDLE AS COL19, __tmp_delta_ins_d_customer_ar_a22_0.C_DATA AS COL20, __tmp_delta_ins_d_customer_ar_a22_0.C_LINEAGE AS COL21 FROM __tmp_delta_ins_d_customer_ar AS __tmp_delta_ins_d_customer_ar_a22_0 WHERE NOT EXISTS ( SELECT * FROM public.customer AS customer_a22 WHERE customer_a22.C_LINEAGE = __tmp_delta_ins_d_customer_ar_a22_0.C_LINEAGE AND customer_a22.C_DATA = __tmp_delta_ins_d_customer_ar_a22_0.C_DATA AND customer_a22.C_MIDDLE = __tmp_delta_ins_d_customer_ar_a22_0.C_MIDDLE AND customer_a22.C_SINCE = __tmp_delta_ins_d_customer_ar_a22_0.C_SINCE AND customer_a22.C_PHONE = __tmp_delta_ins_d_customer_ar_a22_0.C_PHONE AND customer_a22.C_ZIP = __tmp_delta_ins_d_customer_ar_a22_0.C_ZIP AND customer_a22.C_STATE = __tmp_delta_ins_d_customer_ar_a22_0.C_STATE AND customer_a22.C_CITY = __tmp_delta_ins_d_customer_ar_a22_0.C_CITY AND customer_a22.C_STREET_2 = __tmp_delta_ins_d_customer_ar_a22_0.C_STREET_2 AND customer_a22.C_STREET_1 = __tmp_delta_ins_d_customer_ar_a22_0.C_STREET_1 AND customer_a22.C_DELIVERY_CNT = __tmp_delta_ins_d_customer_ar_a22_0.C_DELIVERY_CNT AND customer_a22.C_PAYMENT_CNT = __tmp_delta_ins_d_customer_ar_a22_0.C_PAYMENT_CNT AND customer_a22.C_YTD_PAYMENT = __tmp_delta_ins_d_customer_ar_a22_0.C_YTD_PAYMENT AND customer_a22.C_BALANCE = __tmp_delta_ins_d_customer_ar_a22_0.C_BALANCE AND customer_a22.C_CREDIT_LIM = __tmp_delta_ins_d_customer_ar_a22_0.C_CREDIT_LIM AND customer_a22.C_FIRST = __tmp_delta_ins_d_customer_ar_a22_0.C_FIRST AND customer_a22.C_LAST = __tmp_delta_ins_d_customer_ar_a22_0.C_LAST AND customer_a22.C_CREDIT = __tmp_delta_ins_d_customer_ar_a22_0.C_CREDIT AND customer_a22.C_DISCOUNT = __tmp_delta_ins_d_customer_ar_a22_0.C_DISCOUNT AND customer_a22.C_ID = __tmp_delta_ins_d_customer_ar_a22_0.C_ID AND customer_a22.C_D_ID = __tmp_delta_ins_d_customer_ar_a22_0.C_D_ID AND customer_a22.C_W_ID = __tmp_delta_ins_d_customer_ar_a22_0.C_W_ID )  ) AS p_0_a22_0   ) AS delta_ins_customer_a22_0   ) AS delta_ins_customer_extra_alias) AS tbl; 


            IF array_delta_del_customer IS DISTINCT FROM NULL THEN
                FOREACH temprec_delta_del_customer IN array array_delta_del_customer  LOOP
                   DELETE FROM public.customer WHERE C_W_ID = temprec_delta_del_customer.C_W_ID AND C_D_ID = temprec_delta_del_customer.C_D_ID AND C_ID = temprec_delta_del_customer.C_ID AND C_DISCOUNT = temprec_delta_del_customer.C_DISCOUNT AND C_CREDIT = temprec_delta_del_customer.C_CREDIT AND C_LAST = temprec_delta_del_customer.C_LAST AND C_FIRST = temprec_delta_del_customer.C_FIRST AND C_CREDIT_LIM = temprec_delta_del_customer.C_CREDIT_LIM AND C_BALANCE = temprec_delta_del_customer.C_BALANCE AND C_YTD_PAYMENT = temprec_delta_del_customer.C_YTD_PAYMENT AND C_PAYMENT_CNT = temprec_delta_del_customer.C_PAYMENT_CNT AND C_DELIVERY_CNT = temprec_delta_del_customer.C_DELIVERY_CNT AND C_STREET_1 = temprec_delta_del_customer.C_STREET_1 AND C_STREET_2 = temprec_delta_del_customer.C_STREET_2 AND C_CITY = temprec_delta_del_customer.C_CITY AND C_STATE = temprec_delta_del_customer.C_STATE AND C_ZIP = temprec_delta_del_customer.C_ZIP AND C_PHONE = temprec_delta_del_customer.C_PHONE AND C_SINCE = temprec_delta_del_customer.C_SINCE AND C_MIDDLE = temprec_delta_del_customer.C_MIDDLE AND C_DATA = temprec_delta_del_customer.C_DATA AND C_LINEAGE = temprec_delta_del_customer.C_LINEAGE;
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
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.d_customer"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.d_customer_run_shell(json_data);
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
                --DELETE FROM public.__dummy__d_customer_detected_deletions;
                INSERT INTO public.__dummy__d_customer_detected_deletions
                    SELECT xid, * FROM __tmp_delta_del_d_customer;

                --DELETE FROM public.__dummy__d_customer_detected_insertions;
                INSERT INTO public.__dummy__d_customer_detected_insertions
                    SELECT xid, * FROM __tmp_delta_ins_d_customer;
            END IF;
        END IF;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d_customer';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d_customer ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

CREATE OR REPLACE FUNCTION public.d_customer_materialization()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_d_customer' OR table_name = '__tmp_delta_del_d_customer')
    THEN
        -- RAISE LOG 'execute procedure d_customer_materialization';
        CREATE TEMPORARY TABLE __tmp_delta_ins_d_customer ( LIKE public.d_customer ) WITH OIDS ON COMMIT DROP;
        CREATE CONSTRAINT TRIGGER __tmp_d_customer_trigger_delta_action_ins
        AFTER INSERT OR UPDATE OR DELETE ON
            __tmp_delta_ins_d_customer DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW EXECUTE PROCEDURE public.d_customer_delta_action();

        CREATE TEMPORARY TABLE __tmp_delta_del_d_customer ( LIKE public.d_customer ) WITH OIDS ON COMMIT DROP;
        CREATE CONSTRAINT TRIGGER __tmp_d_customer_trigger_delta_action_del
        AFTER INSERT OR UPDATE OR DELETE ON
            __tmp_delta_del_d_customer DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW EXECUTE PROCEDURE public.d_customer_delta_action();
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d_customer';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d_customer ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS d_customer_trigger_materialization ON public.d_customer;
CREATE TRIGGER d_customer_trigger_materialization
    BEFORE INSERT OR UPDATE OR DELETE ON
      public.d_customer FOR EACH STATEMENT EXECUTE PROCEDURE public.d_customer_materialization();

CREATE OR REPLACE FUNCTION public.d_customer_update()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    -- RAISE LOG 'execute procedure d_customer_update';
    IF TG_OP = 'INSERT' THEN
      -- RAISE LOG 'NEW: %', NEW;
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_del_d_customer WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE) = NEW;
      INSERT INTO __tmp_delta_ins_d_customer SELECT (NEW).*;
    ELSIF TG_OP = 'UPDATE' THEN
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_ins_d_customer WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE) = OLD;
      INSERT INTO __tmp_delta_del_d_customer SELECT (OLD).*;
      DELETE FROM __tmp_delta_del_d_customer WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE) = NEW;
      INSERT INTO __tmp_delta_ins_d_customer SELECT (NEW).*;
    ELSIF TG_OP = 'DELETE' THEN
      -- RAISE LOG 'OLD: %', OLD;
      DELETE FROM __tmp_delta_ins_d_customer WHERE ROW(C_W_ID,C_D_ID,C_ID,C_DISCOUNT,C_CREDIT,C_LAST,C_FIRST,C_CREDIT_LIM,C_BALANCE,C_YTD_PAYMENT,C_PAYMENT_CNT,C_DELIVERY_CNT,C_STREET_1,C_STREET_2,C_CITY,C_STATE,C_ZIP,C_PHONE,C_SINCE,C_MIDDLE,C_DATA,C_LINEAGE) = OLD;
      INSERT INTO __tmp_delta_del_d_customer SELECT (OLD).*;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.d_customer';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.d_customer ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS d_customer_trigger_update ON public.d_customer;
CREATE TRIGGER d_customer_trigger_update
    INSTEAD OF INSERT OR UPDATE OR DELETE ON
      public.d_customer FOR EACH ROW EXECUTE PROCEDURE public.d_customer_update();

CREATE OR REPLACE FUNCTION public.d_customer_propagate_updates ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS __tmp_d_customer_trigger_delta_action_ins, __tmp_d_customer_trigger_delta_action_del IMMEDIATE;
    SET CONSTRAINTS __tmp_d_customer_trigger_delta_action_ins, __tmp_d_customer_trigger_delta_action_del DEFERRED;
    DROP TABLE IF EXISTS d_customer_delta_action_flag;
    DROP TABLE IF EXISTS __tmp_delta_del_d_customer;
    DROP TABLE IF EXISTS __tmp_delta_ins_d_customer;
    RETURN true;
  END;
$$;


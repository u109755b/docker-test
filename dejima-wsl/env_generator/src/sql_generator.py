# bt_name = "mt"
# bt_cnames = ["V", "L", "D", "R", "P", "LINEAGE", "COND1", "COND2", "COND3", "COND4", "COND5", "COND6", "COND7", "COND8", "COND9", "COND10"]
# cond_num = 10
# path = f"./RSAB/dnum_cond{cond_num}_al.sql"

bt_name = "bt"
bt_cnames = ["V", "L", "D", "R", "T", "AL1", "AL2", "AL3", "AL4", "AL5", "LINEAGE", "COND1", "COND2", "COND3", "COND4", "COND5", "COND6", "COND7", "COND8", "COND9", "COND10"]
cond_num = 10
path = f"./RSAB/dnum_cond{cond_num}_pr.sql"


csize = len(bt_cnames)

s = f"""CREATE OR REPLACE VIEW public.dnum AS 
SELECT {", ".join([f"__dummy__.COL{i} AS {bt_cnames[i]}" for i in range(csize)])} 
FROM (SELECT {", ".join([f"dnum_a{csize}_0.COL{i} AS COL{i}" for i in range(csize)])} 
FROM (SELECT {", ".join([f"{bt_name}_a{csize}_0.{bt_cnames[i]} AS COL{i}" for i in range(csize)])} 
FROM public.{bt_name} AS {bt_name}_a{csize}_0 
WHERE {bt_name}_a{csize}_0.COND{cond_num}  <  <border> ) AS dnum_a{csize}_0  ) AS __dummy__;

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
        -- calcuate the update data"""
s += """
        json_data := concat('{"view": ' , '"public.dnum"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');"""
s += f"""
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

CREATE OR REPLACE FUNCTION public.{bt_name}_materialization_for_dnum()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__tmp_delta_ins_{bt_name}_for_dnum' OR table_name = '__tmp_delta_del_{bt_name}_for_dnum')
    THEN
        -- RAISE LOG 'execute procedure {bt_name}_materialization_for_dnum';
        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_ins_{bt_name}_for_dnum ( LIKE public.{bt_name} ) WITH OIDS ON COMMIT DELETE ROWS;
        CREATE TEMPORARY TABLE IF NOT EXISTS __tmp_delta_del_{bt_name}_for_dnum ( LIKE public.{bt_name} ) WITH OIDS ON COMMIT DELETE ROWS;
        
    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.{bt_name}';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.{bt_name} ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS {bt_name}_trigger_materialization_for_dnum ON public.{bt_name};
CREATE TRIGGER {bt_name}_trigger_materialization_for_dnum
    BEFORE INSERT OR UPDATE OR DELETE ON
    public.{bt_name} FOR EACH STATEMENT EXECUTE PROCEDURE public.{bt_name}_materialization_for_dnum();

CREATE OR REPLACE FUNCTION public.{bt_name}_update_for_dnum()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
text_var1 text;
text_var2 text;
text_var3 text;
BEGIN
    -- RAISE LOG 'execute procedure {bt_name}_update_for_dnum';
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'dnum_delta_action_flag') THEN
        IF TG_OP = 'INSERT' THEN
        -- RAISE LOG 'NEW: %', NEW;
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_del_{bt_name}_for_dnum WHERE ROW({",".join(bt_cnames)}) = NEW;
        INSERT INTO __tmp_delta_ins_{bt_name}_for_dnum SELECT (NEW).*; 
        ELSIF TG_OP = 'UPDATE' THEN
        IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
            RAISE check_violation USING MESSAGE = 'Invalid update: null value is not accepted';
        END IF;
        DELETE FROM __tmp_delta_ins_{bt_name}_for_dnum WHERE ROW({",".join(bt_cnames)}) = OLD;
        INSERT INTO __tmp_delta_del_{bt_name}_for_dnum SELECT (OLD).*;
        DELETE FROM __tmp_delta_del_{bt_name}_for_dnum WHERE ROW({",".join(bt_cnames)}) = NEW;
        INSERT INTO __tmp_delta_ins_{bt_name}_for_dnum SELECT (NEW).*; 
        ELSIF TG_OP = 'DELETE' THEN
        -- RAISE LOG 'OLD: %', OLD;
        DELETE FROM __tmp_delta_ins_{bt_name}_for_dnum WHERE ROW({",".join(bt_cnames)}) = OLD;
        INSERT INTO __tmp_delta_del_{bt_name}_for_dnum SELECT (OLD).*;
        END IF;
    END IF;
    RETURN NULL;
EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.{bt_name}';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.{bt_name} ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS {bt_name}_trigger_update_for_dnum ON public.{bt_name};
CREATE TRIGGER {bt_name}_trigger_update_for_dnum
    AFTER INSERT OR UPDATE OR DELETE ON
    public.{bt_name} FOR EACH ROW EXECUTE PROCEDURE public.{bt_name}_update_for_dnum();

CREATE OR REPLACE FUNCTION public.{bt_name}_detect_update_on_dnum()
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
array_delta_del public.{bt_name}[];
array_delta_ins public.{bt_name}[];
detected_deletions public.dnum[];
detected_insertions public.dnum[];
delta_ins_size int;
delta_del_size int;
BEGIN
IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '{bt_name}_detect_update_on_dnum_flag') THEN
    CREATE TEMPORARY TABLE {bt_name}_detect_update_on_dnum_flag ON COMMIT DROP AS (SELECT true as finish);
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'dnum_delta_action_flag') THEN
        SELECT array_agg(tbl) INTO array_delta_ins FROM __tmp_delta_ins_{bt_name}_for_dnum AS tbl;
        select count(*) INTO delta_ins_size FROM __tmp_delta_ins_{bt_name}_for_dnum;
        SELECT array_agg(tbl) INTO array_delta_del FROM __tmp_delta_del_{bt_name}_for_dnum tbl;
        select count(*) INTO delta_del_size FROM __tmp_delta_del_{bt_name}_for_dnum;

        WITH __tmp_delta_ins_{bt_name}_for_dnum_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size), 
        __tmp_delta_del_{bt_name}_for_dnum_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_insertions FROM (SELECT {", ".join([f"__dummy__.COL{i} AS {bt_cnames[i]}" for i in range(csize)])} 
FROM (SELECT {", ".join([f"part_ins_dnum_a{csize}_0.COL{i} AS COL{i}" for i in range(csize)])} 
FROM (SELECT {", ".join([f"p_0_a{csize}_0.COL{i} AS COL{i}" for i in range(csize)])} 
FROM (SELECT {", ".join([f"__tmp_delta_ins_{bt_name}_for_dnum_ar_a{csize}_0.{bt_cnames[i]} AS COL{i}" for i in range(csize)])} 
FROM __tmp_delta_ins_{bt_name}_for_dnum_ar AS __tmp_delta_ins_{bt_name}_for_dnum_ar_a{csize}_0 
WHERE __tmp_delta_ins_{bt_name}_for_dnum_ar_a{csize}_0.COND{cond_num}  <  <border> ) AS p_0_a{csize}_0  ) AS part_ins_dnum_a{csize}_0  ) AS __dummy__) AS tbl;

        insertion_data := (SELECT (array_to_json(detected_insertions))::text);
        IF insertion_data IS NOT DISTINCT FROM NULL THEN 
            insertion_data := '[]';
        END IF; 

        WITH __tmp_delta_ins_{bt_name}_for_dnum_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size), 
        __tmp_delta_del_{bt_name}_for_dnum_ar as (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size)
        SELECT array_agg(tbl) INTO detected_deletions FROM (SELECT {", ".join([f"__dummy__.COL{i} AS {bt_cnames[i]}" for i in range(csize)])} 
FROM (SELECT {", ".join([f"part_del_dnum_a{csize}_0.COL{i} AS COL{i}" for i in range(csize)])} 
FROM (SELECT {", ".join([f"p_0_a{csize}_0.COL{i} AS COL{i}" for i in range(csize)])} 
FROM (SELECT {", ".join([f"__tmp_delta_del_{bt_name}_for_dnum_ar_a{csize}_0.{bt_cnames[i]} AS COL{i}" for i in range(csize)])} 
FROM __tmp_delta_del_{bt_name}_for_dnum_ar AS __tmp_delta_del_{bt_name}_for_dnum_ar_a{csize}_0 
WHERE __tmp_delta_del_{bt_name}_for_dnum_ar_a{csize}_0.COND{cond_num}  <  <border> ) AS p_0_a{csize}_0  ) AS part_del_dnum_a{csize}_0  ) AS __dummy__) AS tbl;

        deletion_data := (  
        SELECT (array_to_json(detected_deletions))::text);
        IF deletion_data IS NOT DISTINCT FROM NULL THEN 
            deletion_data := '[]';
        END IF; 
        IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN 
            user_name := (SELECT session_user);
            IF NOT (user_name = 'dejima') THEN 
                xid := (SELECT txid_current());"""
s += """
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.dnum"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');"""
s += f"""
                result := public.dnum_run_shell(json_data);
                IF result = 'true' THEN 
                    DROP TABLE __tmp_delta_ins_{bt_name}_for_dnum;
                    DROP TABLE __tmp_delta_del_{bt_name}_for_dnum;
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
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to public.{bt_name}';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the function public.{bt_name}_detect_update_on_dnum() ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS {bt_name}_detect_update_on_dnum ON public.{bt_name};
CREATE CONSTRAINT TRIGGER {bt_name}_detect_update_on_dnum
    AFTER INSERT OR UPDATE OR DELETE ON
    public.{bt_name} DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.{bt_name}_detect_update_on_dnum();

CREATE OR REPLACE FUNCTION public.{bt_name}_propagate_updates_to_dnum ()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    SET CONSTRAINTS public.{bt_name}_detect_update_on_dnum IMMEDIATE;
    SET CONSTRAINTS public.{bt_name}_detect_update_on_dnum DEFERRED;
    DROP TABLE IF EXISTS {bt_name}_detect_update_on_dnum_flag;
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
  temprec_delta_del_{bt_name} public.{bt_name}%ROWTYPE;
            array_delta_del_{bt_name} public.{bt_name}[];
temprec_delta_ins_{bt_name} public.{bt_name}%ROWTYPE;
            array_delta_ins_{bt_name} public.{bt_name}[];
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
            SELECT array_agg(tbl) INTO array_delta_del_{bt_name} FROM (SELECT (ROW({",".join([f"COL{i}" for i in range(csize)])}) :: public.{bt_name}).* 
            FROM (SELECT {", ".join([f"delta_del_{bt_name}_a{csize}_0.COL{i} AS COL{i}" for i in range(csize)])} 
FROM (SELECT {", ".join([f"p_0_a{csize}_0.COL{i} AS COL{i}" for i in range(csize)])} 
FROM (SELECT {", ".join([f"{bt_name}_a{csize}_1.{bt_cnames[i]} AS COL{i}" for i in range(csize)])} 
FROM __tmp_delta_del_dnum_ar AS __tmp_delta_del_dnum_ar_a{csize}_0, public.{bt_name} AS {bt_name}_a{csize}_1 
WHERE {" AND ".join([f"{bt_name}_a{csize}_1.{bt_cnames[i]} = __tmp_delta_del_dnum_ar_a{csize}_0.{bt_cnames[i]}" for i in range(csize)])} AND {bt_name}_a{csize}_1.COND{cond_num}  <  <border> ) AS p_0_a{csize}_0  ) AS delta_del_{bt_name}_a{csize}_0  ) AS delta_del_{bt_name}_extra_alias) AS tbl;


            WITH __tmp_delta_del_dnum_ar AS (SELECT * FROM unnest(array_delta_del) as array_delta_del_alias limit delta_del_size),
            __tmp_delta_ins_dnum_ar as (SELECT * FROM unnest(array_delta_ins) as array_delta_ins_alias limit delta_ins_size)
            SELECT array_agg(tbl) INTO array_delta_ins_{bt_name} FROM (SELECT (ROW({",".join([f"COL{i}" for i in range(csize)])}) :: public.{bt_name}).* 
            FROM (SELECT {", ".join([f"delta_ins_{bt_name}_a{csize}_0.COL{i} AS COL{i}" for i in range(csize)])} 
FROM (SELECT {", ".join([f"p_0_a{csize}_0.COL{i} AS COL{i}" for i in range(csize)])} 
FROM (SELECT {", ".join([f"__tmp_delta_ins_dnum_ar_a{csize}_0.{bt_cnames[i]} AS COL{i}" for i in range(csize)])} 
FROM __tmp_delta_ins_dnum_ar AS __tmp_delta_ins_dnum_ar_a{csize}_0 
WHERE __tmp_delta_ins_dnum_ar_a{csize}_0.COND{cond_num}  <  <border> AND NOT EXISTS ( SELECT * 
FROM public.{bt_name} AS {bt_name}_a{csize} 
WHERE {" AND ".join([f"{bt_name}_a{csize}.{bt_cnames[i]} = __tmp_delta_ins_dnum_ar_a{csize}_0.{bt_cnames[i]}" for i in range(csize)])} ) ) AS p_0_a{csize}_0  ) AS delta_ins_{bt_name}_a{csize}_0  ) AS delta_ins_{bt_name}_extra_alias) AS tbl; 


            IF array_delta_del_{bt_name} IS DISTINCT FROM NULL THEN 
                FOREACH temprec_delta_del_{bt_name} IN array array_delta_del_{bt_name}  LOOP 
                   DELETE FROM public.{bt_name} WHERE {" AND ".join([f"{bt_cnames[i]} =  temprec_delta_del_{bt_name}.{bt_cnames[i]}" for i in range(csize)])};
                END LOOP;
            END IF;


            IF array_delta_ins_{bt_name} IS DISTINCT FROM NULL THEN 
                INSERT INTO public.{bt_name} (SELECT * FROM unnest(array_delta_ins_{bt_name}) as array_delta_ins_{bt_name}_alias) ; 
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
                xid := (SELECT txid_current());"""
s += """
                json_data := concat('{"xid": "', xid, '" , "view": ' , '"public.dnum"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');"""
s += f"""
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
      DELETE FROM __tmp_delta_del_dnum WHERE ROW({",".join(bt_cnames)}) = NEW;
      INSERT INTO __tmp_delta_ins_dnum SELECT (NEW).*; 
    ELSIF TG_OP = 'UPDATE' THEN
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __tmp_delta_ins_dnum WHERE ROW({",".join(bt_cnames)}) = OLD;
      INSERT INTO __tmp_delta_del_dnum SELECT (OLD).*;
      DELETE FROM __tmp_delta_del_dnum WHERE ROW({",".join(bt_cnames)}) = NEW;
      INSERT INTO __tmp_delta_ins_dnum SELECT (NEW).*; 
    ELSIF TG_OP = 'DELETE' THEN
      -- RAISE LOG 'OLD: %', OLD;
      DELETE FROM __tmp_delta_ins_dnum WHERE ROW({",".join(bt_cnames)}) = OLD;
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
    public.{bt_name} DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE PROCEDURE public.clean_dummy_dnum();
"""


with open(path, mode="w", newline="\n") as f:
    f.write(s)
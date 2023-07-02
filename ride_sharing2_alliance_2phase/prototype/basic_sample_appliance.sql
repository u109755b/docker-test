
/*view definition (get):
a1(V, L, D, R) :- p_0(V, L, D, R).
p_0(V, L, D, R) :- COL4 = 'A' , mt(V, L, D, R, COL4).
*/

CREATE OR REPLACE VIEW public.a1 AS 
SELECT __dummy__.COL0 AS V,__dummy__.COL1 AS L,__dummy__.COL2 AS D,__dummy__.COL3 AS R 
FROM (SELECT a1_a4_0.COL0 AS COL0, a1_a4_0.COL1 AS COL1, a1_a4_0.COL2 AS COL2, a1_a4_0.COL3 AS COL3 
FROM (SELECT p_0_a4_0.COL0 AS COL0, p_0_a4_0.COL1 AS COL1, p_0_a4_0.COL2 AS COL2, p_0_a4_0.COL3 AS COL3 
FROM (SELECT mt_a5_0.V AS COL0, mt_a5_0.L AS COL1, mt_a5_0.D AS COL2, mt_a5_0.R AS COL3 
FROM public.mt AS mt_a5_0 
WHERE mt_a5_0.P = 'A' ) AS p_0_a4_0  ) AS a1_a4_0  ) AS __dummy__;

DROP MATERIALIZED VIEW IF EXISTS public.__dummy__materialized_a1;

CREATE  MATERIALIZED VIEW public.__dummy__materialized_a1 AS 
SELECT * FROM public.a1;

CREATE EXTENSION IF NOT EXISTS plsh;

CREATE OR REPLACE FUNCTION public.a1_run_shell(text) RETURNS text AS $$
#!/bin/sh
echo "true"
$$ LANGUAGE plsh;
CREATE OR REPLACE FUNCTION public.a1_detect_update()
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
  BEGIN
  IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'a1_delta_action_flag') THEN
    insertion_data := (SELECT (array_to_json(array_agg(t)))::text FROM (SELECT * FROM public.a1 EXCEPT SELECT * FROM public.__dummy__materialized_a1) as t);
    IF insertion_data IS NOT DISTINCT FROM NULL THEN 
        insertion_data := '[]';
    END IF; 
    deletion_data := (SELECT (array_to_json(array_agg(t)))::text FROM (SELECT * FROM public.__dummy__materialized_a1 EXCEPT SELECT * FROM public.a1) as t);
    IF deletion_data IS NOT DISTINCT FROM NULL THEN 
        deletion_data := '[]';
    END IF; 
    IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN 
        user_name := (SELECT session_user);
        IF NOT (user_name = 'dejima') THEN 
            json_data := concat('{"view": ' , '"public.a1"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
            result := public.a1_run_shell(json_data);
            IF result = 'true' THEN 
                REFRESH MATERIALIZED VIEW public.__dummy__materialized_a1;
                FOR func IN (select distinct trigger_schema||'.non_trigger_'||substring(action_statement, 19) as function 
                from information_schema.triggers where trigger_schema = 'public' and event_object_table='a1'
                and action_timing='AFTER' and (event_manipulation='INSERT' or event_manipulation='DELETE' or event_manipulation='UPDATE')
                and action_statement like 'EXECUTE PROCEDURE %') 
                LOOP
                    EXECUTE 'SELECT ' || func into tv;
                END LOOP;
            ELSE
                -- RAISE LOG 'result from running the sh script: %', result;
                RAISE check_violation USING MESSAGE = 'update on view is rejected by the external tool, result from running the sh script: ' 
                || result;
            END IF;
        ELSE 
            RAISE LOG 'function of detecting dejima update is called by % , no request sent to dejima proxy', user_name;
        END IF;
    END IF;
  END IF;
  RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.a1';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the function (non_trigger_)public.a1_detect_update() ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

CREATE OR REPLACE FUNCTION public.non_trigger_a1_detect_update()
RETURNS text 
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
  BEGIN
  IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'a1_delta_action_flag') THEN
    insertion_data := (SELECT (array_to_json(array_agg(t)))::text FROM (SELECT * FROM public.a1 EXCEPT SELECT * FROM public.__dummy__materialized_a1) as t);
    IF insertion_data IS NOT DISTINCT FROM NULL THEN 
        insertion_data := '[]';
    END IF; 
    deletion_data := (SELECT (array_to_json(array_agg(t)))::text FROM (SELECT * FROM public.__dummy__materialized_a1 EXCEPT SELECT * FROM public.a1) as t);
    IF deletion_data IS NOT DISTINCT FROM NULL THEN 
        deletion_data := '[]';
    END IF; 
    IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN 
        user_name := (SELECT session_user);
        IF NOT (user_name = 'dejima') THEN 
            json_data := concat('{"view": ' , '"public.a1"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
            result := public.a1_run_shell(json_data);
            IF result = 'true' THEN 
                REFRESH MATERIALIZED VIEW public.__dummy__materialized_a1;
                FOR func IN (select distinct trigger_schema||'.non_trigger_'||substring(action_statement, 19) as function 
                from information_schema.triggers where trigger_schema = 'public' and event_object_table='a1'
                and action_timing='AFTER' and (event_manipulation='INSERT' or event_manipulation='DELETE' or event_manipulation='UPDATE')
                and action_statement like 'EXECUTE PROCEDURE %') 
                LOOP
                    EXECUTE 'SELECT ' || func into tv;
                END LOOP;
            ELSE
                -- RAISE LOG 'result from running the sh script: %', result;
                RAISE check_violation USING MESSAGE = 'update on view is rejected by the external tool, result from running the sh script: ' 
                || result;
            END IF;
        ELSE 
            RAISE LOG 'function of detecting dejima update is called by % , no request sent to dejima proxy', user_name;
        END IF;
    END IF;
  END IF;
  RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.a1';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the function (non_trigger_)public.a1_detect_update() ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS mt_detect_update_a1 ON public.mt;
        CREATE TRIGGER mt_detect_update_a1
            AFTER INSERT OR UPDATE OR DELETE ON
            public.mt FOR EACH STATEMENT EXECUTE PROCEDURE public.a1_detect_update();

CREATE OR REPLACE FUNCTION public.a1_delta_action()
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
  temprecΔ_del_mt public.mt%ROWTYPE;
temprecΔ_ins_mt public.mt%ROWTYPE;
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'a1_delta_action_flag') THEN
        -- RAISE LOG 'execute procedure a1_delta_action';
        CREATE TEMPORARY TABLE a1_delta_action_flag ON COMMIT DROP AS (SELECT true as finish);
        IF EXISTS (SELECT WHERE false )
        THEN 
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the view are violated';
        END IF;
        IF EXISTS (SELECT WHERE false )
        THEN 
          RAISE check_violation USING MESSAGE = 'Invalid view update: constraints on the source relations are violated';
        END IF;
        CREATE TEMPORARY TABLE Δ_del_mt WITH OIDS ON COMMIT DROP AS SELECT (ROW(COL0,COL1,COL2,COL3,COL4) :: public.mt).* 
            FROM (SELECT Δ_del_mt_a5_0.COL0 AS COL0, Δ_del_mt_a5_0.COL1 AS COL1, Δ_del_mt_a5_0.COL2 AS COL2, Δ_del_mt_a5_0.COL3 AS COL3, Δ_del_mt_a5_0.COL4 AS COL4 
FROM (SELECT mt_a5_0.V AS COL0, mt_a5_0.L AS COL1, mt_a5_0.D AS COL2, mt_a5_0.R AS COL3, mt_a5_0.P AS COL4 
FROM public.mt AS mt_a5_0 
WHERE mt_a5_0.P = 'A' AND NOT EXISTS ( SELECT * 
FROM (SELECT a1_a4_0.V AS COL0, a1_a4_0.L AS COL1, a1_a4_0.D AS COL2, a1_a4_0.R AS COL3 
FROM public.a1 AS a1_a4_0 
WHERE NOT EXISTS ( SELECT * 
FROM __temp__Δ_del_a1 AS __temp__Δ_del_a1_a4 
WHERE __temp__Δ_del_a1_a4.R = a1_a4_0.R AND __temp__Δ_del_a1_a4.D = a1_a4_0.D AND __temp__Δ_del_a1_a4.L = a1_a4_0.L AND __temp__Δ_del_a1_a4.V = a1_a4_0.V )  UNION SELECT __temp__Δ_ins_a1_a4_0.V AS COL0, __temp__Δ_ins_a1_a4_0.L AS COL1, __temp__Δ_ins_a1_a4_0.D AS COL2, __temp__Δ_ins_a1_a4_0.R AS COL3 
FROM __temp__Δ_ins_a1 AS __temp__Δ_ins_a1_a4_0  ) AS new_a1_a4 
WHERE new_a1_a4.COL3 = mt_a5_0.R AND new_a1_a4.COL2 = mt_a5_0.D AND new_a1_a4.COL1 = mt_a5_0.L AND new_a1_a4.COL0 = mt_a5_0.V ) ) AS Δ_del_mt_a5_0  ) AS Δ_del_mt_extra_alias;

CREATE TEMPORARY TABLE Δ_ins_mt WITH OIDS ON COMMIT DROP AS SELECT (ROW(COL0,COL1,COL2,COL3,COL4) :: public.mt).* 
            FROM (SELECT Δ_ins_mt_a5_0.COL0 AS COL0, Δ_ins_mt_a5_0.COL1 AS COL1, Δ_ins_mt_a5_0.COL2 AS COL2, Δ_ins_mt_a5_0.COL3 AS COL3, Δ_ins_mt_a5_0.COL4 AS COL4 
FROM (SELECT new_a1_a4_0.COL0 AS COL0, new_a1_a4_0.COL1 AS COL1, new_a1_a4_0.COL2 AS COL2, new_a1_a4_0.COL3 AS COL3, 'A' AS COL4 
FROM (SELECT a1_a4_0.V AS COL0, a1_a4_0.L AS COL1, a1_a4_0.D AS COL2, a1_a4_0.R AS COL3 
FROM public.a1 AS a1_a4_0 
WHERE NOT EXISTS ( SELECT * 
FROM __temp__Δ_del_a1 AS __temp__Δ_del_a1_a4 
WHERE __temp__Δ_del_a1_a4.R = a1_a4_0.R AND __temp__Δ_del_a1_a4.D = a1_a4_0.D AND __temp__Δ_del_a1_a4.L = a1_a4_0.L AND __temp__Δ_del_a1_a4.V = a1_a4_0.V )  UNION SELECT __temp__Δ_ins_a1_a4_0.V AS COL0, __temp__Δ_ins_a1_a4_0.L AS COL1, __temp__Δ_ins_a1_a4_0.D AS COL2, __temp__Δ_ins_a1_a4_0.R AS COL3 
FROM __temp__Δ_ins_a1 AS __temp__Δ_ins_a1_a4_0  ) AS new_a1_a4_0 
WHERE NOT EXISTS ( SELECT * 
FROM public.mt AS mt_a5 
WHERE mt_a5.P = 'A' AND mt_a5.R = new_a1_a4_0.COL3 AND mt_a5.D = new_a1_a4_0.COL2 AND mt_a5.L = new_a1_a4_0.COL1 AND mt_a5.V = new_a1_a4_0.COL0 ) ) AS Δ_ins_mt_a5_0  ) AS Δ_ins_mt_extra_alia 
            EXCEPT 
            SELECT * FROM  public.mt; 

FOR temprecΔ_del_mt IN ( SELECT * FROM Δ_del_mt) LOOP 
            DELETE FROM public.mt WHERE ROW(V,L,D,R,P) =  temprecΔ_del_mt;
            END LOOP;
DROP TABLE Δ_del_mt;

INSERT INTO public.mt (SELECT * FROM  Δ_ins_mt) ; 
DROP TABLE Δ_ins_mt;
        
        insertion_data := (SELECT (array_to_json(array_agg(t)))::text FROM (SELECT * FROM __temp__Δ_ins_a1 EXCEPT SELECT * FROM public.__dummy__materialized_a1) as t);
        IF insertion_data IS NOT DISTINCT FROM NULL THEN 
            insertion_data := '[]';
        END IF; 
        deletion_data := (SELECT (array_to_json(array_agg(t)))::text FROM (SELECT * FROM __temp__Δ_del_a1 INTERSECT SELECT * FROM public.__dummy__materialized_a1) as t);
        IF deletion_data IS NOT DISTINCT FROM NULL THEN 
            deletion_data := '[]';
        END IF; 
        IF (insertion_data IS DISTINCT FROM '[]') OR (deletion_data IS DISTINCT FROM '[]') THEN 
            user_name := (SELECT session_user);
            IF NOT (user_name = 'dejima') THEN 
                json_data := concat('{"view": ' , '"public.a1"', ', ' , '"insertions": ' , insertion_data , ', ' , '"deletions": ' , deletion_data , '}');
                result := public.a1_run_shell(json_data);
                IF result = 'true' THEN 
                    REFRESH MATERIALIZED VIEW public.__dummy__materialized_a1;
                ELSE
                    -- RAISE LOG 'result from running the sh script: %', result;
                    RAISE check_violation USING MESSAGE = 'update on view is rejected by the external tool, result from running the sh script: ' 
                    || result;
                END IF;
            ELSE 
                RAISE LOG 'function of detecting dejima update is called by % , no request sent to dejima proxy', user_name;
            END IF;
        END IF;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.a1';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.a1 ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

CREATE OR REPLACE FUNCTION public.a1_materialization()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    IF NOT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = '__temp__Δ_ins_a1' OR table_name = '__temp__Δ_del_a1')
    THEN
        -- RAISE LOG 'execute procedure a1_materialization';
        CREATE TEMPORARY TABLE __temp__Δ_ins_a1 ( LIKE public.a1 INCLUDING ALL ) WITH OIDS ON COMMIT DROP;
        CREATE CONSTRAINT TRIGGER __temp__a1_trigger_delta_action
        AFTER INSERT OR UPDATE OR DELETE ON 
            __temp__Δ_ins_a1 DEFERRABLE INITIALLY DEFERRED 
            FOR EACH ROW EXECUTE PROCEDURE public.a1_delta_action();

        CREATE TEMPORARY TABLE __temp__Δ_del_a1 ( LIKE public.a1 INCLUDING ALL ) WITH OIDS ON COMMIT DROP;
        CREATE CONSTRAINT TRIGGER __temp__a1_trigger_delta_action
        AFTER INSERT OR UPDATE OR DELETE ON 
            __temp__Δ_del_a1 DEFERRABLE INITIALLY DEFERRED 
            FOR EACH ROW EXECUTE PROCEDURE public.a1_delta_action();
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.a1';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.a1 ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS a1_trigger_materialization ON public.a1;
CREATE TRIGGER a1_trigger_materialization
    BEFORE INSERT OR UPDATE OR DELETE ON
      public.a1 FOR EACH STATEMENT EXECUTE PROCEDURE public.a1_materialization();

CREATE OR REPLACE FUNCTION public.a1_update()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  DECLARE
  text_var1 text;
  text_var2 text;
  text_var3 text;
  BEGIN
    -- RAISE LOG 'execute procedure a1_update';
    IF TG_OP = 'INSERT' THEN
      -- RAISE LOG 'NEW: %', NEW;
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __temp__Δ_del_a1 WHERE ROW(V,L,D,R) = NEW;
      INSERT INTO __temp__Δ_ins_a1 SELECT (NEW).*; 
    ELSIF TG_OP = 'UPDATE' THEN
      IF (SELECT count(*) FILTER (WHERE j.value = jsonb 'null') FROM  jsonb_each(to_jsonb(NEW)) j) > 0 THEN 
        RAISE check_violation USING MESSAGE = 'Invalid update on view: view does not accept null value';
      END IF;
      DELETE FROM __temp__Δ_ins_a1 WHERE ROW(V,L,D,R) = OLD;
      INSERT INTO __temp__Δ_del_a1 SELECT (OLD).*;
      DELETE FROM __temp__Δ_del_a1 WHERE ROW(V,L,D,R) = NEW;
      INSERT INTO __temp__Δ_ins_a1 SELECT (NEW).*; 
    ELSIF TG_OP = 'DELETE' THEN
      -- RAISE LOG 'OLD: %', OLD;
      DELETE FROM __temp__Δ_ins_a1 WHERE ROW(V,L,D,R) = OLD;
      INSERT INTO __temp__Δ_del_a1 SELECT (OLD).*;
    END IF;
    RETURN NULL;
  EXCEPTION
    WHEN object_not_in_prerequisite_state THEN
        RAISE object_not_in_prerequisite_state USING MESSAGE = 'no permission to insert or delete or update to source relations of public.a1';
    WHEN OTHERS THEN
        GET STACKED DIAGNOSTICS text_var1 = RETURNED_SQLSTATE,
                                text_var2 = PG_EXCEPTION_DETAIL,
                                text_var3 = MESSAGE_TEXT;
        RAISE SQLSTATE 'DA000' USING MESSAGE = 'error on the trigger of public.a1 ; error code: ' || text_var1 || ' ; ' || text_var2 ||' ; ' || text_var3;
        RETURN NULL;
  END;
$$;

DROP TRIGGER IF EXISTS a1_trigger_update ON public.a1;
CREATE TRIGGER a1_trigger_update
    INSTEAD OF INSERT OR UPDATE OR DELETE ON
      public.a1 FOR EACH ROW EXECUTE PROCEDURE public.a1_update();


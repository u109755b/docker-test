CREATE OR REPLACE VIEW public.a1 AS 
SELECT __dummy__.COL0 AS V,__dummy__.COL1 AS L,__dummy__.COL2 AS D,__dummy__.COL3 AS R 
FROM (SELECT a1_a4_0.COL0 AS COL0, a1_a4_0.COL1 AS COL1, a1_a4_0.COL2 AS COL2, a1_a4_0.COL3 AS COL3 
FROM (SELECT bt_a4_0.V AS COL0, bt_a4_0.L AS COL1, bt_a4_0.D AS COL2, bt_a4_0.R AS COL3 
FROM public.bt AS bt_a4_0  ) AS a1_a4_0  ) AS __dummy__;


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
  temprecΔ_del_bt public.bt%ROWTYPE;
temprecΔ_ins_bt public.bt%ROWTYPE;
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
        CREATE TEMPORARY TABLE Δ_del_bt WITH OIDS ON COMMIT DROP AS SELECT (ROW(COL0,COL1,COL2,COL3) :: public.bt).* 
            FROM (SELECT Δ_del_bt_a4_0.COL0 AS COL0, Δ_del_bt_a4_0.COL1 AS COL1, Δ_del_bt_a4_0.COL2 AS COL2, Δ_del_bt_a4_0.COL3 AS COL3 
FROM (SELECT bt_a4_0.V AS COL0, bt_a4_0.L AS COL1, bt_a4_0.D AS COL2, bt_a4_0.R AS COL3 
FROM public.bt AS bt_a4_0 
WHERE NOT EXISTS ( SELECT * 
FROM (SELECT a1_a4_0.V AS COL0, a1_a4_0.L AS COL1, a1_a4_0.D AS COL2, a1_a4_0.R AS COL3 
FROM public.a1 AS a1_a4_0 
WHERE NOT EXISTS ( SELECT * 
FROM __temp__Δ_del_a1 AS __temp__Δ_del_a1_a4 
WHERE __temp__Δ_del_a1_a4.R = a1_a4_0.R AND __temp__Δ_del_a1_a4.D = a1_a4_0.D AND __temp__Δ_del_a1_a4.L = a1_a4_0.L AND __temp__Δ_del_a1_a4.V = a1_a4_0.V )  UNION SELECT __temp__Δ_ins_a1_a4_0.V AS COL0, __temp__Δ_ins_a1_a4_0.L AS COL1, __temp__Δ_ins_a1_a4_0.D AS COL2, __temp__Δ_ins_a1_a4_0.R AS COL3 
FROM __temp__Δ_ins_a1 AS __temp__Δ_ins_a1_a4_0  ) AS new_a1_a4 
WHERE new_a1_a4.COL3 = bt_a4_0.R AND new_a1_a4.COL2 = bt_a4_0.D AND new_a1_a4.COL1 = bt_a4_0.L AND new_a1_a4.COL0 = bt_a4_0.V ) ) AS Δ_del_bt_a4_0  ) AS Δ_del_bt_extra_alias;

CREATE TEMPORARY TABLE Δ_ins_bt WITH OIDS ON COMMIT DROP AS SELECT (ROW(COL0,COL1,COL2,COL3) :: public.bt).* 
            FROM (SELECT Δ_ins_bt_a4_0.COL0 AS COL0, Δ_ins_bt_a4_0.COL1 AS COL1, Δ_ins_bt_a4_0.COL2 AS COL2, Δ_ins_bt_a4_0.COL3 AS COL3 
FROM (SELECT new_a1_a4_0.COL0 AS COL0, new_a1_a4_0.COL1 AS COL1, new_a1_a4_0.COL2 AS COL2, new_a1_a4_0.COL3 AS COL3 
FROM (SELECT a1_a4_0.V AS COL0, a1_a4_0.L AS COL1, a1_a4_0.D AS COL2, a1_a4_0.R AS COL3 
FROM public.a1 AS a1_a4_0 
WHERE NOT EXISTS ( SELECT * 
FROM __temp__Δ_del_a1 AS __temp__Δ_del_a1_a4 
WHERE __temp__Δ_del_a1_a4.R = a1_a4_0.R AND __temp__Δ_del_a1_a4.D = a1_a4_0.D AND __temp__Δ_del_a1_a4.L = a1_a4_0.L AND __temp__Δ_del_a1_a4.V = a1_a4_0.V )  UNION SELECT __temp__Δ_ins_a1_a4_0.V AS COL0, __temp__Δ_ins_a1_a4_0.L AS COL1, __temp__Δ_ins_a1_a4_0.D AS COL2, __temp__Δ_ins_a1_a4_0.R AS COL3 
FROM __temp__Δ_ins_a1 AS __temp__Δ_ins_a1_a4_0  ) AS new_a1_a4_0 
WHERE NOT EXISTS ( SELECT * 
FROM public.bt AS bt_a4 
WHERE bt_a4.R = new_a1_a4_0.COL3 AND bt_a4.D = new_a1_a4_0.COL2 AND bt_a4.L = new_a1_a4_0.COL1 AND bt_a4.V = new_a1_a4_0.COL0 ) ) AS Δ_ins_bt_a4_0  ) AS Δ_ins_bt_extra_alia 
            EXCEPT 
            SELECT * FROM  public.bt; 

FOR temprecΔ_del_bt IN ( SELECT * FROM Δ_del_bt) LOOP 
            DELETE FROM public.bt WHERE ROW(V,L,D,R) =  temprecΔ_del_bt;
            END LOOP;
DROP TABLE Δ_del_bt;

INSERT INTO public.bt (SELECT * FROM  Δ_ins_bt) ; 
DROP TABLE Δ_ins_bt;
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


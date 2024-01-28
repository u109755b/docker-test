CREATE OR REPLACE FUNCTION public.bt_name_propagates_to_dt_name(txid int)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    DELETE FROM public.__dummy__dt_name_detected_deletions t where t.txid = $1;
    DELETE FROM public.__dummy__dt_name_detected_insertions t where t.txid = $1;
    PERFORM public.bt_name_propagate_updates_to_dt_name();
    RETURN true;
  END;
$$;

CREATE OR REPLACE FUNCTION public.dt_name_propagate(txid int)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    DELETE FROM public.__dummy__dt_name_detected_deletions t where t.txid = $1;
    DELETE FROM public.__dummy__dt_name_detected_insertions t where t.txid = $1;
    PERFORM public.dt_name_propagate_updates();
    RETURN true;
  END;
$$;

CREATE OR REPLACE FUNCTION public.remove_dummy_dt_name(txid int)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
  BEGIN
    DELETE FROM public.__dummy__dt_name_detected_deletions t where t.txid = $1;
    DELETE FROM public.__dummy__dt_name_detected_insertions t where t.txid = $1;
    RETURN true;
  END;
$$;
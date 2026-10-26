BEGIN;

ALTER TABLE public.cotizaciones
    ADD COLUMN IF NOT EXISTS compra NUMERIC(18, 6);

ALTER TABLE public.cotizaciones
    ADD COLUMN IF NOT EXISTS venta NUMERIC(18, 6);

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'cotizaciones'
          AND column_name = 'valor'
    ) THEN
        UPDATE public.cotizaciones
        SET compra = COALESCE(compra, valor),
            venta = COALESCE(venta, valor);

        ALTER TABLE public.cotizaciones
            DROP CONSTRAINT IF EXISTS ck_cotizaciones_valor_valido;

        ALTER TABLE public.cotizaciones
            DROP COLUMN valor;
    END IF;
END
$$;

UPDATE public.cotizaciones
SET compra = venta
WHERE compra IS NULL;

UPDATE public.cotizaciones
SET venta = compra
WHERE venta IS NULL;

ALTER TABLE public.cotizaciones
    ALTER COLUMN compra SET NOT NULL;

ALTER TABLE public.cotizaciones
    ALTER COLUMN venta SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'public.cotizaciones'::regclass
          AND conname = 'ck_cotizaciones_compra_valida'
    ) THEN
        ALTER TABLE public.cotizaciones
            ADD CONSTRAINT ck_cotizaciones_compra_valida
            CHECK (
                compra > 0
                AND compra < 'Infinity'::numeric
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'public.cotizaciones'::regclass
          AND conname = 'ck_cotizaciones_venta_valida'
    ) THEN
        ALTER TABLE public.cotizaciones
            ADD CONSTRAINT ck_cotizaciones_venta_valida
            CHECK (
                venta > 0
                AND venta < 'Infinity'::numeric
            );
    END IF;
END
$$;

COMMIT;
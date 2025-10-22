INSERT INTO "pfII_residuo" (tipo, preco_medio) VALUES
    ('plastico', 0.0),
    ('papel', 0.0),
    ('papelao', 0.0),
    ('vidro', 0.0),
    ('metais', 0.0)
ON CONFLICT (tipo) DO NOTHING;  -- Prevents errors if run twice
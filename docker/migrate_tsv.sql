-- Одноразовая миграция живой БД: добавить лексический индекс для гибридного поиска.
-- Генерируемая колонка пересчитается для всех существующих строк автоматически (без переэмбеддинга).
ALTER TABLE document_chunks
    ADD COLUMN IF NOT EXISTS tsv tsvector
    GENERATED ALWAYS AS (to_tsvector('russian', text)) STORED;

CREATE INDEX IF NOT EXISTS idx_chunks_tsv ON document_chunks USING GIN (tsv);

SELECT count(*) AS total, count(tsv) AS with_tsv FROM document_chunks;

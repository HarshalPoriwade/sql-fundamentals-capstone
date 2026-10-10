-- Trigger: when an animal's status changes to 'Released', write a row to release_log.
DROP TRIGGER IF EXISTS log_animal_release;

-- "OF status" means updates to other columns never fire it.
-- "OLD.status IS NOT 'Released'" stops a second log row when a released animal is saved again.
CREATE TRIGGER log_animal_release
AFTER UPDATE OF status ON animals
FOR EACH ROW
WHEN NEW.status = 'Released' AND OLD.status IS NOT 'Released'
BEGIN
    INSERT INTO release_log (animal_id, release_date, note)
    VALUES (
        NEW.animal_id,
        date('now'),
        NEW.name || ' (' || NEW.species || ') released after '
            || CAST(julianday(date('now')) - julianday(NEW.intake_date) AS INTEGER)
            || ' days in care'
    );
END;
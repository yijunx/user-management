migrate:
	@bash scripts/migrate.sh

up:
	@bash scripts/migrate.sh
	@bash scripts/start.sh

test:
	@bash scripts/migration.sh
	@bash scripts/test.sh
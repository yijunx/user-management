migrate:
	@bash scripts/migrate.sh

up:
	@python seed_users.py
	@bash scripts/migrate.sh
	@bash scripts/start.sh

test:
	@bash scripts/migrate.sh
	@bash scripts/test.sh
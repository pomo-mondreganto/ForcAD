.PHONY: lint-backend
lint-backend:
	flake8 --config .flake8

.PHONY: lint-frontend
lint-frontend:
	cd front && npx eslint .

.PHONY: lint
lint: lint-backend lint-frontend

.PHONY: clean
clean:
	./control.py reset || :
	./control.py clean

.PHONY: test
test: clean
	./scripts/run_tests.sh

.PHONY: build-base
build-base:
	./scripts/release_base.sh

.PHONY: release-base
release-base:
	./scripts/release_base.sh --push

.PHONY: start
start: clean
	./control.py setup
	./control.py start --fast
	./control.py rd logs -f initializer

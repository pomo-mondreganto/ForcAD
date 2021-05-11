.PHONY: lint
lint:
	flake8 --config .flake8

.PHONY: test
test:
	./scripts/run_tests.sh

.PHONY: clean
clean:
	./control.py reset
	./control.py clean

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
	./control.py rd logs -f inititializer

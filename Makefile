# **************************************************
# Copyright (c) 2025, Mayank Mishra
# **************************************************

update-precommit:
	pre-commit autoupdate

style:
	python copyright.py --repo ./ --header "Copyright (c) $$(date +%Y), Mayank Mishra"
	pre-commit run --all-files

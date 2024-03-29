isort --recursive  --force-single-line-imports app tests
autoflake --recursive --remove-all-unused-imports --remove-unused-variables --in-place app tests --exclude=__init__.py
black app tests
isort --recursive --multi-line=3 --trailing-comma --line-width 88 --force-grid-wrap=0 --combine-as app tests

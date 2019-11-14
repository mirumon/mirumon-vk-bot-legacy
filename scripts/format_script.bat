isort --recursive  --force-single-line-imports app tests

autoflake --recursive --remove-all-unused-imports --remove-unused-variables --in-place app tests --exclude=__init__.py
black app tests
isort --recursive app tests
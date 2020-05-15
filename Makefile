test:
    pytype
    python - m pytest

fmt:
    autopep8 - - in -place - -aggressive - -aggressive - r - -exclude README.md, requirements.txt *

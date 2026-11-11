"""Checks an installed wagtail-google-tag package has everything it needs."""

import sys

from importlib.metadata import version
from importlib.resources import files


package = files("wagtail_google_tag")
if "/site-packages/" not in str(package):
    sys.exit(f"Not the installed package: {package}")

missing = [
    path
    for path in (
        "templates/wagtail_google_tag/google_tag.html",
        "templatetags/wagtail_google_tag.py",
        "static/wagtail_google_tag/js/google-tag.js",
        "migrations/0001_initial.py",
        "migrations/0002_leave_out_of_tracking.py",
    )
    if not package.joinpath(path).is_file()
]
if missing:
    sys.exit(f"Missing from the package: {', '.join(missing)}")

print(f"wagtail-google-tag {version('wagtail-google-tag')}: package complete")

"""Mirror the portal's partner logos onto the Ministry's own domain.

Each tile on the entry portal can name the logo address supplied by the
structure it links to. Serving the image straight from that address works, but
leaves the portal depending on eleven other servers: if one is down, slow, or
drops to plain http, the tile breaks or the browser refuses to load it.

This command downloads each address once and stores the file against the
partner, after which `PartnerSite.logo_src` serves the local copy and the
portal stops reaching outside this domain. It is safe to re-run: a partner that
already has an uploaded file is skipped unless --force is given.

    python manage.py fetch_partner_logos
    python manage.py fetch_partner_logos --force        # re-download everything
    python manage.py fetch_partner_logos --dry-run      # report, change nothing
"""

import mimetypes
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.core.models import PartnerSite

TIMEOUT = 30
MAX_BYTES = 5 * 1024 * 1024
ALLOWED_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
}


class Command(BaseCommand):
    help = "Download each partner's supplied logo and serve it from this domain."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-download even for partners that already have an uploaded logo.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be downloaded without changing anything.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        dry_run = options["dry_run"]

        partners = PartnerSite.objects.exclude(logo_url="").order_by("column", "order")
        if not partners:
            self.stdout.write("No partner carries a logo address — nothing to fetch.")
            return

        fetched = skipped = failed = 0
        for partner in partners:
            label = partner.acronym or partner.name

            if partner.logo and not force:
                self.stdout.write(f"  {label}: already hosted here, skipping")
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(f"  {label}: would download {partner.logo_url}")
                continue

            try:
                content, extension = self._download(partner.logo_url)
            except Exception as error:  # noqa: BLE001 — report and carry on
                self.stderr.write(self.style.WARNING(f"  {label}: {error}"))
                failed += 1
                continue

            name = f"{slugify(label) or 'partenaire'}{extension}"
            partner.logo.save(name, ContentFile(content), save=True)
            self.stdout.write(self.style.SUCCESS(f"  {label}: saved as {partner.logo.name}"))
            fetched += 1

        if dry_run:
            return

        self.stdout.write("")
        self.stdout.write(f"Downloaded {fetched}, skipped {skipped}, failed {failed}.")
        if failed:
            self.stdout.write(
                "The tiles that failed keep using their supplied address; upload a "
                "file through Sites partenaires to host them here instead."
            )

    def _download(self, url):
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"unsupported address ({parsed.scheme or 'no scheme'})")

        request = Request(url, headers={"User-Agent": "MINEFOP-portal/1.0"})
        with urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310 — address comes from the admin
            content_type = (response.headers.get_content_type() or "").lower()
            # Read one byte past the cap so an oversized file is detected rather
            # than silently truncated.
            content = response.read(MAX_BYTES + 1)

        if len(content) > MAX_BYTES:
            raise ValueError(f"larger than {MAX_BYTES // (1024 * 1024)} MB")
        if not content:
            raise ValueError("empty response")

        extension = ALLOWED_TYPES.get(content_type)
        if extension is None:
            guessed = mimetypes.guess_type(parsed.path)[0]
            extension = ALLOWED_TYPES.get(guessed or "")
        if extension is None:
            raise ValueError(f"not an image we store ({content_type or 'unknown type'})")

        return content, extension

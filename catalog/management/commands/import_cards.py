"""
Import cards from a CSV file.

CSV format (with header row):
    code,name,version,notes

version values: NORMAL, FOIL, ALT_ART, SP, PRE

The script asks which image variant to use (e.g. blank=normal, _p1, _p2, _p3...).
You can also pass --image-suffix to skip the prompt.

Usage:
    uv run python manage.py import_cards cards.csv
    uv run python manage.py import_cards cards.csv --image-suffix _p1
    uv run python manage.py import_cards cards.csv --update
"""
import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from catalog.models import Card


class Command(BaseCommand):
    help = "Import cards from a CSV file (code, name, version, notes)"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing cards instead of skipping them",
        )
        parser.add_argument(
            "--image-suffix",
            type=str,
            default=None,
            help="Image suffix to use (e.g. '' for normal, '_p1', '_p2'). Skips interactive prompt.",
        )

    def handle(self, *args, **options):
        path = Path(options["csv_file"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        # Determine image suffix
        suffix = options["image_suffix"]
        if suffix is None:
            self.stdout.write(
                "\nBase image URL: https://en.onepiece-cardgame.com/images/cardlist/card/{CODE}{SUFFIX}.png"
            )
            self.stdout.write("Examples: blank → normal art, _p1 → first alternate, _p2 → second alternate\n")
            suffix = input("Image suffix for this batch (press Enter for normal): ").strip()

        self.stdout.write(f"Using image suffix: '{suffix}' (leave blank means normal art)")

        valid_versions = {v.value for v in Card.Version}
        created = updated = skipped = errors = 0

        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):  # row 1 is header
                code = row.get("code", "").strip()
                name = row.get("name", "").strip()
                version = row.get("version", "NORMAL").strip().upper()
                notes = row.get("notes", "").strip()

                if not code or not name:
                    self.stderr.write(f"Row {i}: missing code or name — skipped")
                    errors += 1
                    continue

                if version not in valid_versions:
                    self.stderr.write(f"Row {i}: unknown version '{version}', defaulting to NORMAL")
                    version = Card.Version.NORMAL

                card, is_new = Card.objects.get_or_create(
                    code=code,
                    version=version,
                    defaults={"name": name, "image_suffix": suffix, "notes": notes},
                )

                if is_new:
                    created += 1
                elif options["update"]:
                    card.name = name
                    card.image_suffix = suffix
                    card.notes = notes
                    card.save()
                    updated += 1
                else:
                    skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done — created: {created}, updated: {updated}, skipped: {skipped}, errors: {errors}"
            )
        )

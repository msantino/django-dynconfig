"""
Import configuration entries from JSON.

Usage:
    python manage.py importconfigs configs.json              # Import (skip existing)
    python manage.py importconfigs configs.json --overwrite   # Import (overwrite existing)
    python manage.py importconfigs configs.json --dry-run     # Preview without changes
"""

import json

from django.core.management.base import BaseCommand, CommandError

from dynconfig.models import ConfigEntry


class Command(BaseCommand):
    help = "Import dynamic configuration entries from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "file",
            type=str,
            help="Path to the JSON file to import.",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing config entries. Default is to skip them.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without writing to the database.",
        )

    def handle(self, *args, **options):
        try:
            with open(options["file"]) as f:
                entries = json.load(f)
        except FileNotFoundError:
            raise CommandError(f"File not found: {options['file']}") from None
        except json.JSONDecodeError as e:
            raise CommandError(f"Invalid JSON: {e}") from e

        if not isinstance(entries, list):
            raise CommandError("JSON file must contain a list of config entries.")

        created = 0
        updated = 0
        skipped = 0

        for item in entries:
            key = item.get("key")
            if not key:
                self.stderr.write(self.style.WARNING(f"Skipping entry without 'key': {item}"))
                skipped += 1
                continue

            exists = ConfigEntry.objects.filter(key=key).exists()

            if exists and not options["overwrite"]:
                self.stdout.write(f"  SKIP  {key} (already exists)")
                skipped += 1
                continue

            if options["dry_run"]:
                action = "UPDATE" if exists else "CREATE"
                self.stdout.write(f"  {action}  {key} = {item.get('value', '')[:50]}")
                if exists:
                    updated += 1
                else:
                    created += 1
                continue

            _, was_created = ConfigEntry.objects.update_or_create(
                key=key,
                defaults={
                    "value": item.get("value", ""),
                    "value_type": item.get("value_type", "string"),
                    "is_encrypted": item.get("is_encrypted", False),
                    "group": item.get("group", "general"),
                    "help_text_field": item.get("help_text", ""),
                },
            )

            if was_created:
                created += 1
                self.stdout.write(f"  CREATE  {key}")
            else:
                updated += 1
                self.stdout.write(f"  UPDATE  {key}")

        prefix = "[DRY RUN] " if options["dry_run"] else ""
        self.stdout.write(
            self.style.SUCCESS(f"\n{prefix}Done: {created} created, {updated} updated, {skipped} skipped.")
        )

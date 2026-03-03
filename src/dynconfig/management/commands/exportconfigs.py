"""
Export configuration entries to JSON.

Usage:
    python manage.py exportconfigs                    # All configs to stdout
    python manage.py exportconfigs -o configs.json    # All configs to file
    python manage.py exportconfigs -g billing          # Only "billing" group
    python manage.py exportconfigs --no-secrets        # Exclude encrypted values
"""

import json
import sys

from django.core.management.base import BaseCommand

from dynconfig.models import ConfigEntry


class Command(BaseCommand):
    help = "Export dynamic configuration entries to JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "-o", "--output",
            type=str,
            help="Output file path. Defaults to stdout.",
        )
        parser.add_argument(
            "-g", "--group",
            type=str,
            help="Export only configs in this group.",
        )
        parser.add_argument(
            "--no-secrets",
            action="store_true",
            help="Exclude encrypted config entries from the export.",
        )

    def handle(self, *args, **options):
        queryset = ConfigEntry.objects.all()

        if options["group"]:
            queryset = queryset.filter(group=options["group"])

        if options["no_secrets"]:
            queryset = queryset.filter(is_encrypted=False)

        entries = []
        for entry in queryset:
            entries.append({
                "key": entry.key,
                "value": entry.value,
                "value_type": entry.value_type,
                "is_encrypted": entry.is_encrypted,
                "group": entry.group,
                "help_text": entry.help_text_field,
            })

        output = json.dumps(entries, indent=2, ensure_ascii=False)

        if options["output"]:
            with open(options["output"], "w") as f:
                f.write(output)
            self.stdout.write(self.style.SUCCESS(f"Exported {len(entries)} config(s) to {options['output']}"))
        else:
            sys.stdout.write(output + "\n")

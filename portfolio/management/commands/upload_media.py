from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from portfolio.storage import SupabaseStorage


class Command(BaseCommand):
    help = "media/ papkasidagi mavjud fayllarni Supabase Storage'ga yuklaydi"

    def handle(self, *args, **options):
        if not (settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY):
            raise CommandError("SUPABASE_URL va SUPABASE_SERVICE_KEY o'rnatilmagan")

        storage = SupabaseStorage()
        storage.create_bucket()
        root = Path(settings.MEDIA_ROOT)
        files = [path for path in root.rglob('*') if path.is_file()]
        for path in files:
            name = path.relative_to(root).as_posix()
            storage.upload(name, path.read_bytes(), upsert=True)
            self.stdout.write(f"  {name}")
        self.stdout.write(self.style.SUCCESS(f"{len(files)} ta fayl yuklandi"))

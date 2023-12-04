from __future__ import annotations

from pathlib import Path

from tealprint import TealPrint

from .patch import Patch


class FtbBackup(Patch):
    file = Path("ftbbackups2.json")

    def __init__(self) -> None:
        super().__init__("FTB Backup")

    def patch(self) -> None:
        ftb_backup = self.load_raw(FtbBackup.file)

        # Change backups to every 6 hours instead of every 2 hours
        TealPrint.info("🔸 Changing backup interval from 2 hours to 6 hours")

        ftb_backup = ftb_backup.replace('"backup_cron": "0 0 */2 * * ?"', '"backup_cron": "0 0 */6 * * ?"')

        self.save_raw(FtbBackup.file, ftb_backup)

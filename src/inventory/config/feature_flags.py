"""
Feature Flags für den Inventory-Microservice.

Hierüber lassen sich bestimmte Funktionen (wie z.B. Excel-Export)
global aktivieren oder deaktivieren – z.B. über Umgebungsvariablen.
"""

import os

from inventory.config import env


# 🔁 Excel-Export aktivieren (z. B. für Admins, Debugging, Reporting)
excel_export_enabled: bool = env.EXCEL_EXPORT_ENABLED

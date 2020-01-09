"""
Reads queries from Metabase and writes to a migration table
"""

from metabase.properties import Properties
from metabase.report_card_repo import ReportCard, ReportCardRepo, ReportCardMigration
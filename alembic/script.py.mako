"""Generic script for Alembic migration generation."""

# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

file_template = """
Revision ID: %(rev)s
Revises: %(down_revision)s
Create Date: %(create_date)s

"""

#!/usr/bin/env python
"""
Compile .po to .mo using polib library.
Usage: python compile_with_polib.py
"""
import polib
import os

base_dir = r"d:\Thesis project\university_system"
po_file = os.path.join(base_dir, "locale", "zh_Hans", "LC_MESSAGES", "django.po")
mo_file = os.path.join(base_dir, "locale", "zh_Hans", "LC_MESSAGES", "django.mo")

# Delete old .mo file if exists
if os.path.exists(mo_file):
    os.remove(mo_file)
    print(f"Removed old {mo_file}")

# Load and compile
po = polib.pofile(po_file, encoding='utf-8')
po.save_as_mofile(mo_file)
print(f"Successfully compiled {po_file} -> {mo_file}")
print(f"Total translations: {len(po)}")

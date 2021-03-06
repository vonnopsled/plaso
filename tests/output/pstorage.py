#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for plaso.output.pstorage."""

import os
import unittest

from plaso.output import event_buffer
from plaso.output import pstorage
from plaso.storage import zip_file as storage_zip_file

from tests import test_lib as shared_test_lib
from tests.output import test_lib


class PstorageTest(test_lib.OutputModuleTestCase):
  """Tests for the plaso storage outputter."""

  def setUp(self):
    """Makes preparations before running an individual test."""
    self.test_filename = os.path.join(u'test_data', u'psort_test.proto.plaso')

  def testOutput(self):
    with shared_test_lib.TempDirectory() as temp_directory:
      # Copy events to pstorage dump.
      with storage_zip_file.StorageFile(
          self.test_filename, read_only=True) as storage_file:
        output_mediator = self._CreateOutputMediator(storage_file=storage_file)
        output_module = pstorage.PlasoStorageOutputModule(output_mediator)

        plaso_file = os.path.join(temp_directory, u'pstorage.plaso')
        output_module.SetFilePath(plaso_file)

        with event_buffer.EventBuffer(
            output_module, check_dedups=False) as output_buffer:
          for event_object in storage_file.GetSortedEntries():
            output_buffer.Append(event_object)

      # Make sure original and dump have the same events.
      original = storage_zip_file.StorageFile(
          self.test_filename, read_only=True)
      dump = storage_zip_file.StorageFile(plaso_file, read_only=True)
      event_object_original = original.GetSortedEntry()
      event_object_dump = dump.GetSortedEntry()
      original_list = []
      dump_list = []

      while event_object_original:
        original_list.append(event_object_original.EqualityString())
        dump_list.append(event_object_dump.EqualityString())
        event_object_original = original.GetSortedEntry()
        event_object_dump = dump.GetSortedEntry()

      self.assertFalse(event_object_dump)

      for original_str, dump_str in zip(
          sorted(original_list), sorted(dump_list)):
        self.assertEqual(original_str, dump_str)


if __name__ == '__main__':
  unittest.main()

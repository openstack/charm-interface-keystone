# Copyright 2012 Canonical Ltd.

# This file is part of lazr.restfulclient.
#
# lazr.restfulclient is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, version 3 of the
# License.
#
# lazr.restfulclient is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.restfulclient. If not, see <http://www.gnu.org/licenses/>.

"""Tests for the atomic file cache."""

__metaclass__ = type

import shutil
import tempfile
import unittest

import httplib2

from lazr.restfulclient._browser import AtomicFileCache


class TestFileCacheInterface(unittest.TestCase):
    """Tests for ``AtomicFileCache``."""

    file_cache_factory = httplib2.FileCache

    unicode_text = u'pa\u026a\u03b8\u0259n'

    def setUp(self):
        super(TestFileCacheInterface, self).setUp()
        self.cache_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.cache_dir)
        super(TestFileCacheInterface, self).tearDown()

    def make_file_cache(self):
        """Make a FileCache-like object to be tested."""
        return self.file_cache_factory(self.cache_dir)

    def test_get_non_existent_key(self):
        # get() returns None if the key does not exist.
        cache = self.make_file_cache()
        self.assertIs(None, cache.get('nonexistent'))

    def test_set_key(self):
        # A key set with set() can be got by get().
        cache = self.make_file_cache()
        cache.set('key', 'value')
        self.assertEqual('value', cache.get('key'))

    def test_set_twice_overrides(self):
        # Setting a key again overrides the value.
        cache = self.make_file_cache()
        cache.set('key', 'value')
        cache.set('key', 'new-value')
        self.assertEqual('new-value', cache.get('key'))

    def test_delete_absent_key(self):
        # Deleting a key that's not there does nothing.
        cache = self.make_file_cache()
        cache.delete('nonexistent')
        self.assertIs(None, cache.get('nonexistent'))

    def test_delete_key(self):
        # A key once set can be deleted.  Further attempts to get that key
        # return None.
        cache = self.make_file_cache()
        cache.set('key', 'value')
        cache.delete('key')
        self.assertIs(None, cache.get('key'))

    def test_get_non_string_key(self):
        # get() raises TypeError if asked to get a non-string key.
        cache = self.make_file_cache()
        self.assertRaises(TypeError, cache.get, 42)

    def test_delete_non_string_key(self):
        # delete() raises TypeError if asked to delete a non-string key.
        cache = self.make_file_cache()
        self.assertRaises(TypeError, cache.delete, 42)

    def test_set_non_string_key(self):
        # set() raises TypeError if asked to set a non-string key.
        cache = self.make_file_cache()
        self.assertRaises(TypeError, cache.set, 42, 'the answer')

    def test_set_non_string_value(self):
        # set() raises TypeError if asked to set a key to a non-string value.
        # Attempts to retrieve that value return the empty string.  This is
        # probably a bug in httplib2.FileCache.
        cache = self.make_file_cache()
        self.assertRaises(TypeError, cache.set, 'answer', 42)
        self.assertEqual('', cache.get('answer'))

    def test_get_unicode(self):
        # get() can retrieve unicode keys.
        cache = self.make_file_cache()
        self.assertIs(None, cache.get(self.unicode_text))

    def test_set_unicode_keys(self):
        cache = self.make_file_cache()
        cache.set(self.unicode_text, 'value')
        self.assertEqual('value', cache.get(self.unicode_text))

    def test_set_unicode_value(self):
        # set() cannot store unicode values.  Values must be bytes.
        cache = self.make_file_cache()
        self.assertRaises(
            UnicodeEncodeError, cache.set, 'key', self.unicode_text)

    def test_delete_unicode(self):
        # delete() can remove unicode keys.
        cache = self.make_file_cache()
        cache.set(self.unicode_text, 'value')
        cache.delete(self.unicode_text)
        self.assertIs(None, cache.get(self.unicode_text))


class TestAtomicFileCache(TestFileCacheInterface):
    """Tests for ``AtomicFileCache``."""

    file_cache_factory = AtomicFileCache

    def test_set_non_string_value(self):
        # set() raises TypeError if asked to set a key to a non-string value.
        # Attempts to retrieve that value act is if it were never set.
        #
        # Note: This behaviour differs from httplib2.FileCache.
        cache = self.make_file_cache()
        self.assertRaises(TypeError, cache.set, 'answer', 42)
        self.assertIs(None, cache.get('answer'))

    # Implementation-specific tests follow.

    def test_bad_safename_get(self):
        safename = lambda x: AtomicFileCache.TEMPFILE_PREFIX + x
        cache = AtomicFileCache(self.cache_dir, safename)
        self.assertRaises(ValueError, cache.get, 'key')

    def test_bad_safename_set(self):
        safename = lambda x: AtomicFileCache.TEMPFILE_PREFIX + x
        cache = AtomicFileCache(self.cache_dir, safename)
        self.assertRaises(ValueError, cache.set, 'key', 'value')

    def test_bad_safename_delete(self):
        safename = lambda x: AtomicFileCache.TEMPFILE_PREFIX + x
        cache = AtomicFileCache(self.cache_dir, safename)
        self.assertRaises(ValueError, cache.delete, 'key')

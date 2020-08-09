"""
Mock classes for open() and the file type.

The MIT License (MIT)

Copyright (c) 2015 Niv Ben-David

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
from io import TextIOWrapper

from unittest.mock import Mock, NonCallableMock, DEFAULT

if sys.version_info < (3, 0):
    try:
        from cStringIO import StringIO, StringIO as BytesIO
    except ImportError:
        from StringIO import StringIO, StringIO as BytesIO
else:
    from io import StringIO, BytesIO


class FileLikeMock(NonCallableMock):
    """Acts like a file object returned from open()."""
    def __init__(self, name=None, read_data='', *args, **kws):
        kws.update({'spec': TextIOWrapper, })
        super(FileLikeMock, self).__init__(*args, **kws)
        self.mode = None
        self.__is_closed = False
        self.read_data = read_data
        self.close.side_effect = self._close
        self.__contents.seek(0)

        self.__enter__ = Mock(side_effect=self._enter)
        self.__exit__ = Mock(side_effect=self._exit)

        if name is not None:
            self.name = name

    @property
    def closed(self):
        # pylint: disable=missing-docstring
        return self.__is_closed

    @property
    def read_data(self):
        """Bypass read function to access the contents of the file.

        This property should be used for testing purposes.
        """
        return self.__contents.getvalue()

    @read_data.setter
    def read_data(self, contents):
        # pylint: disable=missing-docstring
        # pylint: disable=attribute-defined-outside-init
        if isinstance(contents, str):
            self.__contents = StringIO()
        else:
            self.__contents = BytesIO()

        # Constructing a cStrinIO object with the input string would result
        # in a read-only object, so we write the contents after construction.
        self.__contents.write(contents)

        # Set tell/read/write/etc side effects to access the new contents
        # object.
        self.tell._mock_wraps = self.__contents.tell
        self.seek._mock_wraps = self.__contents.seek
        self.read._mock_wraps = self.__contents.read
        self.readline._mock_wraps = self.__contents.readline
        self.readlines._mock_wraps = self.__contents.readlines
        self.write._mock_wraps = self.__contents.write
        self.writelines._mock_wraps = self.__contents.writelines

    def __iter__(self):
        return iter(self.__contents)

    def set_properties(self, path, mode):
        """Set file's properties (name and mode).

        This function is also in charge of swapping between textual and
        binary streams.
        """
        self.name = path
        self.mode = mode

        if 'b' in self.mode:
            if not isinstance(self.read_data, bytes):
                self.read_data = bytes(self.read_data, encoding='utf8')
        else:
            if not isinstance(self.read_data, str):
                self.read_data = str(self.read_data, encoding='utf8')

    def reset_mock(self, visited=None):
        """Reset the default tell/read/write/etc side effects."""
        # In some versions of the mock library, `reset_mock` takes an argument
        # and in some it doesn't. We try to handle all situations.
        if visited is not None:
            super(FileLikeMock, self).reset_mock(visited)
        else:
            super(FileLikeMock, self).reset_mock()

        # Reset contents and tell/read/write/close side effects.
        self.read_data = ''
        self.close.side_effect = self._close

    def _enter(self):
        """Reset the position in buffer whenever entering context."""
        self.__contents.seek(0)

        return self

    def _exit(self, exception_type, exception, traceback):
        """Close file when exiting context."""
        # pylint: disable=unused-argument
        self.close()

    def _close(self):
        """Mark file as closed (used for side_effect)."""
        self.__is_closed = True
        return DEFAULT


class MockOpen(Mock):
    """A mock for the open() builtin function."""
    def __init__(self, read_data='', *args, **kws):
        kws.update({'spec': open, 'name': open.__name__, })
        super(MockOpen, self).__init__(*args, **kws)
        self.__files = {}
        self.__read_data = read_data

    def __call__(self, path, mode='r', *args, **kws):
        original_side_effect = self._mock_side_effect

        if path in self.__files:
            self._mock_return_value = self.__files[path]
            self._mock_side_effect = self._mock_return_value.side_effect

        try:
            child = super(MockOpen, self).__call__(path, mode, *args, **kws)
        finally:
            # Reset the side effect after each call so that the next call to
            # open() won't cause the same side_effect.
            self._mock_side_effect = original_side_effect

        # Consecutive calls to open() set `return_value` to the last file mock
        # created. If the paths differ (and child isn't a newly-created mock,
        # evident by its name attribute being unset) we create a new file mock
        # instead of returning to previous one.
        # noinspection PyTypeHints
        if not isinstance(child.name, Mock) and path != child.name:
            child = self._get_child_mock(_new_name='()', name=path)
            self.__files[path] = child

        child.set_properties(path, mode)

        if path not in self.__files:
            self.__files[path] = child

        self._mock_return_value = child
        return child

    def __getitem__(self, path):
        return self.__files.setdefault(path, self._get_child_mock(name=path))

    def __setitem__(self, path, value):
        value.__enter__ = lambda self: self
        value.__exit__ = lambda self, *args: None
        self.__files[path] = value

    def reset_mock(self, visited=None):
        # See comment in `FileLikeMock.reset_mock`.
        if visited is not None:
            super(MockOpen, self).reset_mock(visited)
        else:
            super(MockOpen, self).reset_mock()

        self.__files = {}
        self.__read_data = ''

    def _get_child_mock(self, **kws):
        """Create a new FileLikeMock instance.

        The new mock will inherit the parent's side_effect and read_data
        attributes.
        """
        kws.update({
            '_new_parent': self,
            'side_effect': self._mock_side_effect,
            'read_data': self.__read_data,
        })
        return FileLikeMock(**kws)

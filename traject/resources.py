import pathlib
from html_resources.library import Library

here = pathlib.Path(__file__).parent.resolve()


my_super_lib = Library.from_discovery('somelib', here / "static" / "top_lib")
dep = my_super_lib.bind('dep.js')

my_lib = Library.from_discovery('reha', here / "static" / "example")
whatever = my_lib.bind('lib.js', dependencies=[dep])
somejs = my_lib.bind('some.js', dependencies=[whatever])


static = Library.from_discovery(
    'misc', here / 'static' / 'misc', restrict=('*.jpg', "*.ico"))

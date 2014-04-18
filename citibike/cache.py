import gflags
from os import environ
from os.path import join

FLAGS = gflags.FLAGS


gflags.DEFINE_string('cache', "%(HOME)s/.citibike/cache" % environ, 'Location to write downloaded files.  Defaults to $HOME/.citibike/cache')


def cache_filename(name):
    return join(FLAGS.cache, name)

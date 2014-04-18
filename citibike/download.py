"""Download original citibike data.

This application downloads the original citibike data and reencodes it
from a zip to a bz2 file."""

from pipes import quote
from tempfile import TemporaryFile
from distutils.dir_util import mkpath
from os import environ,  makedirs, unlink
from os.path import join, exists
import errno
import requests
from bz2file import BZ2File
from zipfile import ZipFile
import gflags
from progressbar import ProgressBar
import citibike.reader

FLAGS = gflags.FLAGS

gflags.DEFINE_integer('year', 2013, 'Year of first file to download')
gflags.DEFINE_integer('month', 7, 'Month of first file to download')
gflags.DEFINE_string('filename', '%(year)04d%(month)02d-citibike-tripdata.zip', 'Template for building citibike filename/url')
gflags.DEFINE_string('url', 'https://s3.amazonaws.com/tripdata/%(filename)s', 'URL template from which to download')
gflags.DEFINE_string('csv', '%(year)04d-%(month)02d - Citi Bike trip data.csv', 'Name of CSV file in zip file')
gflags.DEFINE_string('compressed_csv', '%(year)04d-%(month)02d - Citi Bike trip data.csv.bz2', 'Name of bz2 compressed CSV file')
gflags.DEFINE_string('chunk_size', 2**20, 'Download chunk size')

def month_counter(year=None, month=None):
    year = year or FLAGS.year
    month = month or FLAGS.month
    while True:
        while month <= 12:
            yield year, month
            month += 1
        month = 1
        year += 1 

def path_csv_and_urls(year=None, month=None, filename=None, url=None):
    for year, month in month_counter(year, month):
        filename = FLAGS.filename % vars()
        url = FLAGS.url % vars()
        path = join(FLAGS.cache, FLAGS.compressed_csv % vars())
        csv = FLAGS.csv % vars()
        yield path, csv, url

def download(target=None):

    target = target or FLAGS.cache

    mkpath(target)
    print "Starting download"
    for path, csv, url in path_csv_and_urls():
        if exists(path):
            print("Skipping %s, %s exists" % (url, path))
            continue
        req = requests.get(url, stream=True)
        if req.status_code != 200:
            return req.status_code
        print("Downloading: %(url)s " % vars())
        with TemporaryFile() as tf:
            l = 0
            size = int(req.headers['content-length'])
            pb = ProgressBar(size).start()
            for chunk in req.iter_content(FLAGS.chunk_size):
                l += len(chunk)
                pb.update(l)
                tf.write(chunk)
            tf.flush()
            tf.seek(0)
            pb.finish()
            print("Recompressing to: " + quote(path))
            size = (i.file_size for i in ZipFile(tf).infolist() if i.filename==csv).next()
            l = 0
            try:
                with ZipFile(tf).open(csv) as csv_file:
                    pb = ProgressBar(size).start()
                    with BZ2File(path, "w") as target_file:
                        while True:
                            chunk = csv_file.read(FLAGS.chunk_size)
                            if not chunk:
                                break
                            l += len(chunk)
                            pb.update(l)
                            target_file.write(chunk)
            except KeyboardInterrupt:
                unlink(path)
                break
            finally:
                pb.finish()


def main(argv):
    try:
        argv = FLAGS(argv)[1:]
    except (gflags.FlagsError, KeyError, IndexError), e:
        sys.stderr.write("%s\nUsage: %s \n%s\n" % (
                e, os.path.basename(sys.argv[0]), FLAGS))
        return 1
    

    download()

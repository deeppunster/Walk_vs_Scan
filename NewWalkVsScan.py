"""
NewWalkVsScan.py - Simplified example of showing os.walk vs os.scandir.

usage: NewWalkVsScan.py [-h] [-d ROOTDIR] [-o OUTPUT]

Test using os.walk vs. using os.scandir to traverse a directory structure.

optional arguments:
  -h, --help            show this help message and exit
  -d ROOTDIR, --rootdir ROOTDIR
                        root directory of tree to be traversed
  -o OUTPUT, --output OUTPUT
                        output file to contain the results of walk vs. scan

"""
from argparse import ArgumentParser
from collections import deque
from contextlib import contextmanager
from logging import getLogger
from os import walk, scandir, sep, getcwd, stat
from os.path import join
from time import perf_counter, localtime

__author__ = 'Travis Risner'
__project__ = "walk_vs_scan"
__creation_date__ = "12/03/2016"
# "${CopyRight.py}"

log = getLogger(__name__)

printfile = 'new walk output.txt'
root_dir = '/Volumes/MBPC/Dvl/Python/PythonProjects'


class NewWalkVsScanClass:
    """
    NewWalkVsScanClass - Simplified example of showing os.walk vs os.scandir.
    """

    def __init__(self):
        """
        Setup for walk vs scan.
        """

        self.parser = ArgumentParser(
            description='Test using os.walk vs. using os.scandir to '
                        'traverse a directory structure.'
        )
        self.parser.add_argument(
            '-d', '--rootdir', default=root_dir,
            help='root directory of tree to be traversed'
        )
        self.parser.add_argument(
            '-o', '--output', default=printfile,
            help='output file to contain the results of walk vs. scan'
        )

        self.args = None
        self.arg_dict = None

    def extract_parameter_info(self):
        """
        Extract information from the input parameters.

        :return:
        """
        self.args = self.parser.parse_args()
        self.arg_dict = vars(self.args)
        global printfile
        global root_dir
        printfile = self.arg_dict.get('output', 'travers.txt')
        root_dir = self.arg_dict.get('rootdir', getcwd())


class TryWalk:
    """
    Traverse the target directory using os.walk.
    """

    def __init__(self) -> None:
        """
        Establish work areas needed by this class
        """
        self.root_walk_dir = None
        self.walk_dir_path = None
        self.walk_dir_names = None
        self.walk_file_names = None
        self.gen_this_dir = None
        self.gen_file = None
        self.walk_file_stat = None
        self.epoch_time = None
        self.local_time = None
        self.file_date = None
        self.file_size = None
        self.delete_list = list()

    def walk_dir(self, start_dir, out_file):
        """
        Use os.walk to recursively search the root directory.

        :param start_dir: starting directory to search
        :param out_file: output file to report the results
        :return:
        """
        self.root_walk_dir = start_dir

        # let os.walk generate a list of tuples
        for self.walk_dir_path, self.walk_dir_names, self.walk_file_names in \
                walk(self.root_walk_dir):

            # publish the directory path produced
            print('\nWalk path is {}'.format(
                self.walk_dir_path), file=out_file)

            # publish the directories produced
            if self.walk_dir_names == list():
                print('\t<<< No directories found for this pass >>>',
                      file=out_file)
            else:
                print('\tDirectories found:', file=out_file)
                for pos, directory in enumerate(self.walk_dir_names):
                    suffix = ''
                    # identify the directory(s) to be removed from the walk
                    if directory == '.git':
                        # add the position of directory to the list to be
                        # removed
                        self.delete_list.append(pos)
                        suffix = '- (omitted)'
                    print('\t\t{} {}'.format(directory, suffix), file=out_file)
                # if list is non-empty, remove the directoriess by position
                # note - removal is right to left so the positions are not
                # altered by previous removals
                if self.delete_list != list():
                    self.delete_list.sort(reverse=True)
                    for pos in self.delete_list:
                        del self.walk_dir_names[pos]
                    self.delete_list = list()

            # publish the list of files produced
            if self.walk_file_names == list():
                print('\t<<< No files found for this pass >>>', file=out_file)
            else:
                print('\tFiles found:', file=out_file)
                for file in self.walk_file_names:
                    self.walk_file_stat = stat(join(self.walk_dir_path, file))
                    self.epoch_time = self.walk_file_stat.st_mtime
                    self.local_time = localtime(self.epoch_time)
                    self.file_date = '{0}/{1}/{2}'.format(
                        str(self.local_time.tm_mon),
                        str(self.local_time.tm_mday),
                        str(self.local_time.tm_year))
                    self.file_size = self.walk_file_stat.st_size
                    print('\t\t{}  Last Modified Date: {}, Size: '
                          '{}'.format(file, self.file_date,
                                      self.file_size),
                          file=out_file)


class TryScandir:
    """
    Traverse the target directory using os.scandir
    """

    def __init__(self) -> None:
        """
        Establish work areas needed by this class
        """
        self.root_scan_dir = None
        self.root_length = None
        self.scan_dir_stack = None
        self.current_path = None
        self.scan_dir_name = None
        self.scan_file_name = None
        self.scan_dir_entry = None
        self.scan_full_name = None
        self.scan_file_stat = None
        self.file_date = None
        self.epoch_time = None
        self.local_time = None
        self.size = None

    def scan_dir(self, start_dir, out_file):
        """
        Use os.scandir to recursively search the root directory.

        :param start_dir: starting directory to search
        :param out_file: output file to report the results
        :return:
        """
        self.root_scan_dir = start_dir
        if self.root_scan_dir[-1] == sep:
            self.root_length = len(self.root_scan_dir)
        else:
            self.root_length = len(self.root_scan_dir) + len(sep)
        print('\tStarting path is {} whose length is {}'.format(
            self.root_scan_dir, self.root_length),
            file=out_file)

        # let os.scandir generate a list of files and directories
        #
        # 1. Start with an empty FIFO stack.
        # 2. Add the starting directory to the stack.
        # 3. Pull a directory from the stack and use scandir to create an
        #    iterator of directory entries.
        # 4. Walk through each entry of the iterator created by step 3.
        #   a. If the entry is a directory, put it on the directory stack.
        #   b. If the entry is a file, process it.
        # 5. Repeat starting from step 3 until the stack is empty again.

        # 1: Start with an empty FIFO stack.
        self.scan_dir_stack = deque()

        # 2. Add the starting directory to the stack.
        self.scan_dir_stack.append(self.root_scan_dir)

        # 3. Pull a directory from the stack and use scandir to create an
        #    iterator of directory entries.
        while len(self.scan_dir_stack) > 0:

            self.current_path = self.scan_dir_stack.popleft()
            print('\nScandir path is {}'.format(self.current_path),
                  file=out_file)

            for self.scan_dir_entry in scandir(self.current_path):
                # 4. Walk through each entry of the iterator created by step 3.
                print('\t\t{}'.format(self.scan_dir_entry.name),
                      file=out_file, end='')
                self.scan_full_name = self.scan_dir_entry.path
                # print(' - full name: {}'.format(self.scan_full_name),
                #       file=out_file, end='')

                #   a. If the entry is a directory, put it on the directory
                #      stack.
                if self.scan_dir_entry.is_dir():
                    # directory found, is it in the forbidden list?
                    if self.scan_dir_entry.name == '.git':
                        # yes, make a note of it
                        print(' - is a directory.  (omitted)',
                              file=out_file)
                    else:
                        # no, add it to the stack for directories for later
                        # scanning
                        print(' - is a directory.  Adding to stack',
                              file=out_file)
                        self.scan_dir_stack.append(self.scan_full_name)

                # b. If the entry is a file, process it.
                elif self.scan_dir_entry.is_file:
                    # print(' - was a file.  Processing file',
                    #       file=out_file)
                    self.scan_file_name = self.scan_full_name[
                                          self.root_length - 1:]
                    self.scan_file_stat = self.scan_dir_entry.stat()
                    self.epoch_time = self.scan_file_stat.st_mtime
                    self.local_time = localtime(self.epoch_time)
                    self.file_date = '{0}/{1}/{2}'.format(
                        str(self.local_time.tm_mon),
                        str(self.local_time.tm_mday),
                        str(self.local_time.tm_year))
                    self.size = self.scan_file_stat.st_size
                    print('  Last Modified Date: {}, Size: '
                          '{}'.format(self.file_date, self.size),
                          file=out_file)
                else:
                    print('\n\n\n<<< Entry is not a file or directory - {}'
                          ' >>>'.format(self.scan_full_name), file=out_file)


@contextmanager
def timing(label: str):
    """
    Timing routine using the context manager.

    From "20 Python Libraries You Aren’t Using (But Should)" by Caleb Hattingh.
    Copyright © 2016 O'Reilly Media, Inc.  ISBN: 978-1-491-96792-8

    :param label:
    :return:
    """
    t0 = perf_counter()
    yield lambda: (label, t1 - t0)
    t1 = perf_counter()


if __name__ == "__main__":
    nwvsc = NewWalkVsScanClass()
    nwvsc.extract_parameter_info()

    # open a file for each method to strut their stuff
    outstream = open(printfile, mode='w')

    # report parameters
    print('Directory to be scanned/walked is: {}'.format(root_dir))
    print('Output to file: {}\n'.format(printfile))

    # start with the older os.walk
    with timing('Using os.walk') as walk_timer:
        print('===== Try os.walk =====\n', file=outstream)
        dir_walk = TryWalk()
        dir_walk.walk_dir(root_dir, outstream)

    # now try the newer os.scandir
    with timing('Using os.scandir') as scan_timer:
        print('\n\n===== Now try os.scandir =====\n', file=outstream)
        dir_scan = TryScandir()
        dir_scan.scan_dir(root_dir, outstream)

    # close up shop
    print('\n\n=============================\n', file=outstream)
    print('{0[0]:20} took: {0[1]:.6f} seconds.'.format(walk_timer()))
    print('{0[0]:20} took: {0[1]:.6f} seconds.'.format(scan_timer()))
    outstream.close()

# EOF

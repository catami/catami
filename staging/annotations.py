"""Classes to help Parse annotation data files.
"""
import csv
import os

import itertools


class CPCFileParser:
    """Iterable to parse Coral Point Count files.

    Each file in this case describes a single image that was annotated
    at multiple points. The image name without extension is stored in 
    self.image_file_name.
    On construction from a file handle it will iterate and return a dict
    with 'x', 'y', 'id', 'label' and 'notes' as keys.
    """

    def __init__(self, file_handle):
        self.file_handle = file_handle

        reader = csv.reader(self.file_handle)

        lines = [line for line in reader]

        # extract header information
        path_list = lines[0][1].split('\\')
        self.image_file_name = os.path.splitext(path_list[-1])[
            0]  # no extension

        h_scale, v_scale = (float(l) for l in lines[0][2:4])

        header_lines = 6
        num_points = int(lines[header_lines - 1][0])
        assert len(lines) == header_lines + 2 * num_points

        # get the coordinates of the hand labelled points
        point_coords = ((float(x) / h_scale, float(y) / v_scale) for x, y in
                        lines[header_lines:header_lines + num_points])

        # all values should be between 0 and 1

        # get the annotations with each point
        annotations = lines[
                      header_lines + num_points:header_lines + 2 * num_points]

        # join annotation and point_coords here
        self.data = iter(map(itertools.chain, point_coords, annotations))

        # create the matching header (to create dictionary)
        self.header = ["x", "y", "id", "label", "notes"]

    def next(self):
        # return the dictionary describing the point
        return dict(zip(self.header, self.data.next()))

    def __iter__(self):
        return self

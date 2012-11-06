import csv
import os
import itertools

class CPCFileParser:
    def __init__(self, file_handle):
        self.file_handle = file_handle

        reader = csv.reader(self.file_handle)

        lines = [line for line in reader]

        # extract header information
        path_list = lines[0][1].split('\\')
        self.image_file_name = os.path.splitext(path_list[-1])[0] # no extension

        h_scale, v_scale = (float(l) for l in lines[0][2:4])

        HEADERLINES = 6
        num_points = int(lines[HEADERLINES-1][0])
        assert len(lines) == HEADERLINES + 2 * num_points

        # get the coordinates of the hand labelled points
        point_coords = ((float(x) / h_scale, float(y) / v_scale) for x, y in lines[HEADERLINES:HEADERLINES+num_points])

        # all values should be between 0 and 1


        # get the annotations with each point
        annotations = lines[HEADERLINES + num_points:HEADERLINES + 2 * num_points]

        # join annotation and point_coords here
        self.data = iter(map(itertools.chain, point_coords, annotations))

        # create the matching header (to create dictionary)
        self.header = ["x", "y", "id", "label", "notes"]

    def next(self):
        # return the dictionary describing the point
        return dict(zip(self.header, self.data.next()))

    def __iter__(self):
        return self

#
# Quick code sample for disparity computation for SystemX
# Copyright (C) 2015 OpenWide
# Author Jimmy Durand Wesolowski <jimmy.durand-wesolowski@openwide.fr>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

#! /usr/bin/env python

import sys
import os
import png
from numpy import mean


class Disparity:
    PATH_DATA = "data"
    PATH_DATAR = "right"
    PATH_DATAL = "left"
    IMGR = "0000000000.png"
    IMGL = IMGR
    DISP_MAX = 50
    GREY_MAX = 255


    def __init__(self, window_x = 1, window_y = 1):
        path = os.curdir + os.path.sep + self.PATH_DATA + os.path.sep
        pathr = path + self.PATH_DATAR + os.path.sep
        pathl = path + self.PATH_DATAL + os.path.sep
        self.imgr = pathr + self.IMGR
        self.imgl = pathl + self.IMGL
        self.window_x = window_x
        self.window_y = window_y

        if (not os.path.isfile(self.imgr)):
            print "Cannot find the right image"
            exit(1)

        if (not os.path.isfile(self.imgl)):
            print "Cannot find the left image"
            exit(1)

        png_reader_r = png.Reader(self.imgr)
        png_reader_l = png.Reader(self.imgl)
        wr, hr, pr, _ = png_reader_r.read_flat()
        wl, hl, pl, _ = png_reader_l.read_flat()

        if (wr != wl or hr != hl):
            print "Images do not have the same dimensions"
            exit(1)

        self.w = wr
        self.h = hr
        self.datar = pr
        self.datal = pl
        self.disparity_map = [0 for x in range(0, self.w * self.h)]
        self.cury = 0


    def cost_point(self, x1, x2):
        return (self.datar[self.cury + x1] - self.datal[self.cury + x2]) ** 2


    def cost_block(self, x1, x2):
        cost = 0
        for off in range(x2 - self.window_x, x2 + self.window_x):
            cost += self.cost_point(x1, off)
        return cost


    def disparity_point(self, x):
        costs = []

        for off in range(0, self.DISP_MAX):
            costs.append(self.cost_block(x, x + off))
        return min(costs)


    def compute(self):
        self.cury = 0

        for y in range(self.window_y, self.h - self.window_y):
            self.cury = y * self.w
            for x in range(self.window_x, self.w - self.window_x):
                self.disparity_map[self.cury + x] = self.disparity_point(x)
        cost_max = mean(self.disparity_map)
        for x in range(0, self.w * self.h):
            self.disparity_map[x] *= self.GREY_MAX
            self.disparity_map[x] /= cost_max
            if (self.disparity_map[x] > self.GREY_MAX):
                self.disparity_map[x] = self.GREY_MAX

    def output(self):
        disparity.compute()
        output = file("output.png", 'w')
        writer = png.Writer(width = self.w, height = self.h, greyscale = True)
        return writer.write_array(output, self.disparity_map)


disparity = Disparity()
disparity.output()

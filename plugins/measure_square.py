#!/usr/bin/env python
# -*- coding: utf-8 -*-
# distance.py
"""dicompyler plugin that calculates the area of polygon that is given by two
points"""

import wx
from wx.lib.pubsub import Publisher as pub
from math import sqrt


EXPERT_FACTOR = 0.53


def pluginProperties():
    """Properties of the plugin."""

    props = {}
    props['name'] = 'Measure Area of Polygon'
    props['description'] = "Measures the distance between two points"
    props['author'] = 'Rafal Buzun'
    props['version'] = '0.1.9'
    props['plugin_type'] = '2dview'
    props['plugin_version'] = 1
    props['min_dicom'] = ['images']
    props['recommended_dicom'] = ['images']

    return props


class plugin:

    def __init__(self, parent):

        self.parent = parent

        # Set up pubsub
        pub.subscribe(self.OnUpdateImage, '2dview.updated.image')
        pub.subscribe(self.OnMouseDown, '2dview.mousedown')

        # Plugin is not ready to measure until the menu has been launched
        self.start_measuring = False

    def pluginMenu(self, evt):
        """Start the measure distance plugin."""

        # Set up variables
        self.point_one = None
        self.point_two = None
        self.start_measuring = True
        self.z = 0

        # Refresh the 2D display to get the latest image data
        self.parent.Refresh()

    def OnUpdateImage(self, msg):
        """Update and load the image data."""

        if self.start_measuring:
            # Get the image data when the 2D view is updated
            self.imagedata = msg.data
            self.gc = self.imagedata['gc']
            self.gc.Scale(self.imagedata['scale'], self.imagedata['scale'])
            self.gc.Translate(self.imagedata['transx'],
                              self.imagedata['transy'])
            self.DrawMeasurement()

    def OnMouseDown(self, msg):
        """Get the cursor position when the left mouse button is clicked."""

        # Make sure that we are measuring
        # This only occurs after the plugin has been launched via the menu
        if self.start_measuring:

            # Get the mouse cursor position point
            point = msg.data

            if (self.point_one is None):
                self.point_one = point
                # Record the z plane of the first point
                self.z = self.imagedata['number'] - 1
            elif (self.point_two is None):
                # Make sure that the second point is on the same z plane
                if (self.z == self.imagedata['number'] - 1):
                    self.point_two = point
                    # Measure the distance between the two points
                    self.MeasureDistance()
                # Otherwise re-obtain first point since this is a new z plane
                else:
                    # Record the z plane of the first point
                    self.z = self.imagedata['number'] - 1
                    self.point_one = point

    def MeasureDistance(self):
        """Measure the distance between the two points."""

        # Get the differences between the two points

        px = self.point_one['xmm'] - self.point_two['xmm']
        py = self.point_one['ymm'] - self.point_two['ymm']

        self.poly_area = abs(self.point_one['xmm'] -self.point_two['xmm']) * abs(self.point_one['ymm'] - self.point_two['ymm']) * EXPERT_FACTOR
        # Calculate the distance
        # Distance is reported in mm so convert to cm
        self.dist_cm = sqrt((px) ** 2 + (py) ** 2) * 0.1

        # Refresh the 2D display to draw the measured distance
        self.parent.Refresh()

    def DrawMeasurement(self):
        """Draws the measurement line."""

        # Make sure that the second point has been clicked
        if not (self.point_two is None):

            # If the slice number doesn't match the z plane
            # don't draw the measurement line
            if not (self.z == self.imagedata['number'] - 1):
                return

            # Set the color of the line
            c = wx.Colour(255, 0, 0)
            self.gc.SetBrush(wx.Brush(c, style=wx.TRANSPARENT))
            self.gc.SetPen(wx.Pen(c, style=wx.SOLID))

            self.gc.DrawRectangle(self.point_one['x'], self.point_one['y'],
                                  abs(self.point_one['x'] - self.point_two['x']),
                                  abs(self.point_one['y'] - self.point_two['y']))

            self.gc.DrawText('%.2f' % self.poly_area + ' mm^2',
                             self.point_two['x'] + 2, self.point_two['y'] + 2)


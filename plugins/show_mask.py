#!/usr/bin/env python
# -*- coding: utf-8 -*-
# distance.py
"""dicompyler plugin that shows mask on top of image"""

import os
import time
import wx
from wx.lib.pubsub import Publisher as pub
from math import sqrt

import numpy as np
from PIL import Image
from subprocess import Popen, PIPE
import subprocess

CURRENT_MASK = 'current_mask.png'
CURRENT_IMAGE = 'current_image.png'
IMG_SIZE = 400

def pluginProperties():
    """Properties of the plugin."""

    props = {}
    props['name'] = 'show_mask'
    props['description'] = "Show mask on top of 2d dicom image"
    props['author'] = 'Rafal Buzun'
    props['version'] = '0.0.1'
    props['plugin_type'] = '2dview'
    props['plugin_version'] = 1
    props['min_dicom'] = ['images']
    props['recommended_dicom'] = ['images']

    return props


class plugin:

    def __init__(self, parent):

        self.parent = parent
        self.images = []
        self.old_imagenum = 0
        pub.subscribe(self.OnUpdatePatient, 'patient.updated.parsed_data')
        pub.subscribe(self.OnUpdateImage, '2dview.updated.image')

    def pluginMenu(self, evt):
        """Start the measure distance plugin."""

        # Refresh the 2D display to get the latest image data
        raise Exception("IKS DE")
        self.parent.Refresh()

    def OnUpdateImage(self, msg):
        """Update and load the image data."""

        # Get the image data when the 2D view is updated
        self.imagedata = msg.data
        self.imagenum = msg.data['number']
        if self.imagenum != self.old_imagenum:
            self.old_imagenum = self.imagenum
            self.save_current_image()


        self.gc = self.imagedata['gc']
        self.gc.Scale(self.imagedata['scale'], self.imagedata['scale'])
        self.gc.Translate(self.imagedata['transx'],
                          self.imagedata['transy'])

        self.mask = wx.EmptyBitmap(IMG_SIZE, IMG_SIZE)
        mask_path = '{0}/{1}.png'.format(self.patient_id, self.imagenum)
        if os.path.exists(mask_path):
            self.mask.LoadFile('{0}/{1}.png'.format(self.patient_id, self.imagenum), wx.BITMAP_TYPE_ANY)
        else:
            if os.path.exists(CURRENT_MASK):
                last_date = os.stat(CURRENT_MASK)[8]
                waited = 0
                while last_date == os.stat(CURRENT_MASK)[8]:
                    if waited > 1:
                        return
                    time.sleep(0.1)
                    waited += 0.1

                self.mask.LoadFile(CURRENT_MASK, wx.BITMAP_TYPE_ANY)

        self.DrawMask()

    def OnUpdatePatient(self, msg):
        """Update and load the patient data."""

        self.patient_id = msg.data['id']
        if not os.path.exists(self.patient_id + '/'):
            os.makedirs('{0}/'.format(self.patient_id))
        self.images = msg.data['images']
        self.imagenum = 1
        if len(self.images) > 1:
            self.imagenum = int(len(self.images)/2)

    def DrawMask(self):
        """Draws predicted mask """
        self.gc.DrawBitmap(self.mask, 0, 0, 400,400)
        self.save_current_mask(self.mask)

    def save_current_image(self):
        self.image = self.images[self.imagenum-1].GetImage()
        self.image.save(CURRENT_IMAGE, "PNG")

    def save_current_mask(self, mask):
        mask_to_save = mask.ConvertToImage()
        mask_to_save.SaveFile('{0}/{1}.png'.format(self.patient_id, self.imagenum), wx.BITMAP_TYPE_PNG)


#!/usr/bin/python3
#
# PyAndroidImage
# Copyright (C) 2018  Luca Cireddu (sardylan@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import getopt
import os
import sys

from PIL import Image

PYANDROIDIMAGE_VERSION = "1.0.1"


class PyAndroidImage:
    def __init__(self):
        self._input = ""
        self._output = ""
        self._dpi = 640
        self._mode = "normal"

        self._x = 0
        self._y = 0
        self._aspect = 0

        self._use_box = False
        self._box_x = 0
        self._box_y = 0

        self._basename = ""
        self._dirtype = "drawable"

    def main(self):
        self.check_opt()
        self.compute_params()
        self.display_description()
        self.scale_images()

    def check_opt(self):
        if len(sys.argv) == 1:
            self.help_and_exit()

        try:
            opts, args = getopt.getopt(sys.argv[1:], "hi:o:d:lans", [
                "help",
                "input=", "output=", "dpi=",
                "launcher", "actionbar", "notification", "smallcontextual"
            ])
        except getopt.GetoptError as err:
            print(str(err))
            self.usage()
            sys.exit(1)

        for param, value in opts:
            if param in ("-h", "--help"):
                self.help_and_exit()
            elif param in ("-i", "--input"):
                self._input = value
            elif param in ("-o", "--output"):
                self._output = value
            elif param in ("-d", "--dpi"):
                self._dpi = int(value)
            elif param in ("-l", "--launcher"):
                self._mode = "launcher"
                self._dirtype = "mipmap"
            elif param in ("-a", "--actionbar"):
                self._mode = "actionbar"
            elif param in ("-n", "--notification"):
                self._mode = "notification"
            elif param in ("-s", "--smallcontextual"):
                self._mode = "smallcontextual"

        if not os.path.isfile(self._input):
            print("Input file doesn't exists")
            sys.exit(2)

        if not os.path.isdir(self._output):
            print("Output directory doesn't exists")
            sys.exit(2)

    def help_and_exit(self):
        self.usage()
        sys.exit(0)

    def compute_params(self):
        self._basename = os.path.basename(self._input)
        image = Image.open(self._input)
        self._x, self._y = image.size

        if self._mode == "launcher":
            self._basename = "ic_launcher.png"
            self._dpi = 640
            self._aspect = 1
            self._x = 192
            self._y = 192
        elif self._mode == "actionbar":
            self._dpi = 640
            self._aspect = 1
            self._x = 128
            self._y = 128
            self._use_box = True
            self._box_x = 96
            self._box_y = 96
        elif self._mode == "notification":
            self._dpi = 640
            self._aspect = 1
            self._x = 96
            self._y = 96
            self._use_box = True
            self._box_x = 88
            self._box_y = 88
        elif self._mode == "smallcontextual":
            self._dpi = 640
            self._aspect = 1
            self._x = 64
            self._y = 64

    def scale_images(self):
        self.scale_image(640, "xxxhdpi")
        self.scale_image(480, "xxhdpi")
        self.scale_image(320, "xhdpi")
        self.scale_image(240, "hdpi")
        self.scale_image(160, "mdpi")
        self.scale_image(120, "ldpi")

    def scale_image(self, dpi, dirname):
        output = os.path.join(self._output, "%s-%s" % (self._dirtype, dirname))
        output_name = os.path.join(output, self._basename)
        self.create_dir(output)
        self.image_desctiption(dirname, dpi, output_name)

        x, y = self.compute_resolution(dpi)
        image = Image.open(self._input, "r")
        if self._use_box:
            box_x, box_y = self.compute_box_resolution(dpi)
            bbox = image.getbbox()
            image = image.crop(bbox)
            (bb_x, bb_y) = image.size
            if bb_x >= bb_y:
                image_size = (box_x, int(float(box_y) / (float(bb_x) / bb_y)))
            else:
                image_size = (int(float(box_x) / (float(bb_y) / bb_x)), box_y)

            image = image.resize(image_size)
            image_x, image_y = image_size
            offset = (int(float(x - image_x) / 2), int(float(y - image_y) / 2))
            out_image = Image.new("RGBA", (x, y), (0, 0, 0, 0))
            out_image.paste(image, offset)

            out_image.save(output_name, "PNG")
        else:
            image = image.resize((x, y))
            image.save(output_name, "PNG")

    def compute_resolution(self, dpi):
        x = int((float(self._x) / self._dpi) * dpi)
        y = int((float(self._y) / self._dpi) * dpi)
        return x, y

    def compute_box_resolution(self, dpi):
        box_x = int((float(self._box_x) / self._dpi) * dpi)
        box_y = int((float(self._box_y) / self._dpi) * dpi)
        return box_x, box_y

    def image_desctiption(self, res, dpi, output):
        print("%s (%d dpi): %s " % (res.ljust(7), dpi, output))

    def display_description(self):
        print("")
        print("Input file: %s (%dx%d)" % (self._input, self._x, self._y))
        print("Output dir: %s" % self._output)
        print("")

    @staticmethod
    def create_dir(directory):
        if not os.path.isdir(directory):
            os.makedirs(directory, 0o755)

    @staticmethod
    def usage():
        print("")
        print("PyAndroidImage %s" % PYANDROIDIMAGE_VERSION)
        print("Copyright (C) 2018  Luca Cireddu (sardylan@gmail.com)")
        print("")
        print("This program comes with ABSOLUTELY NO WARRANTY; for details type use --help.")
        print("This is free software, and you are welcome to redistribute it under GPLv3 conditions.")
        print("")
        print("")
        print("Usage: %s [options]" % sys.argv[0])
        print("")
        print("")
        print("")
        print(" -h | --help                     Shows this message")
        print("")
        print(" -i | --input=<filename>         Input filename")
        print(" -o | --output=<dirpath>         Output resource directory")
        print("                                   e.g. app/src/main/res")
        print("")
        print(" -d | --dpi=<dpi>                DPI of source image")
        print("                                   default to 640")
        print("")
        print("")
        print("")
        print("Fixed resolutions values for icons:")
        print("(Resolution values as per 640dpi)")
        print("")
        print(" -l | --launcher                 Launcher (192x192)")
        print(" -a | --actionbar                ActionBar (128x128 with 96x96 area)")
        print(" -n | --notification             Notification (96x96  with 88x88 area)")
        print(" -s | --smallcontextual          Small contextual (64x64)")
        print("")
        print("")


if __name__ == "__main__":
    pai = PyAndroidImage()
    pai.main()

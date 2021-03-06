#
# Shoulder
# Copyright (C) 2018 Assured Information Security, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from collections import namedtuple

from shoulder.logger import logger

class Field(object):
    """ Models a single named field of a fieldset """
    def __init__(self, name, msb, lsb, long_name=None, access="rw"):
        self.name = name
        self.long_name = long_name
        self.msb = msb
        self.lsb = lsb
        self.access = access

class Fieldset(object):
    """ Models a collection of named fields that apply to a register either """
    """ always or under a particular condition """
    def __init__(self, size):
        self.size = int(size)
        self.condition = None
        self.fields = []

    def __str__(self):
        if self.condition is not None:
            msg = "Fieldset when {condition}: ".format(condition=self.condition)
        else:
            msg = "Fieldset: "

        for field in self.fields:
            msg += "{name}=({msb}:{lsb}) ".format(
                name = field.name,
                msb = field.msb,
                lsb = field.lsb
            )

        return msg

    def add_field(self, name, msb, lsb, long_name=None, access="rw"):
        self.fields.append(Field(str(name), int(msb), int(lsb), long_name=long_name, access=access))

    def is_valid(self):
        expected_total_set = set(range(0, self.size))
        total_set = set()

        for f_idx, f in enumerate(self.fields):
            # Check individual field ranges
            if not (0 <= f.lsb <= f.msb < self.size):
                logger.debug(
                    "Invalid field position for \"{name}\" ({msb}:{lsb})".format(
                        name = f.name,
                        msb = f.msb,
                        lsb = f.lsb
                ))
                return False

            # Check for intersections with other fields in this fieldset
            f_set = set(range(f.lsb, f.msb + 1))
            total_set = total_set.union(f_set)
            for x_idx, x in enumerate(self.fields):
                if f_idx == x_idx: continue
                x_set = set(range(x.lsb, x.msb + 1))
                intersect = f_set.intersection(x_set)
                if len(intersect) > 0:
                    logger.debug(
                        "Invalid field overlap, \"{f_name}\" ({f_msb}:{f_lsb}) "
                        "overlaps with \"{x_name}\" ({x_msb}:{x_lsb})".format(
                            f_name = f.name, f_msb = f.msb, f_lsb = f.lsb,
                            x_name = x.name, x_msb = x.msb, x_lsb = x.lsb
                    ))
                    return False


        # Check all bits accounted for in this fieldset
        #  if total_set != expected_total_set: return False
        return True

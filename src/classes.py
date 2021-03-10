# SPDX-FileCopyrightText: 2021 Franck Jullien <franck.jullien@gmail.com>
# SPDX-License-Identifier: BSD-3-Clause

import math

# Scale between orcad units and Kicad units
grid_scale = 0.254

def arange(start, end, step):
    array = []
    val = start
    while val < end:
        array.append(val)
        val += step
    return array

class SymbolDisplayProp:
    def __init__(self, element, grid_scale = 0.254):
        self.et = element
        self.locX = int(element.find('Defn').attrib['locX']) * grid_scale
        self.locY = -int(element.find('Defn').attrib['locY']) * grid_scale
        self.name = element.find('Defn').attrib['name']
        self.rotation = element.find('Defn').attrib['rotation']
        self.italic = ''
        self.bold = ''

        if element.find('PropFont').find('Defn').attrib['italic'] == '1':
            dp.italic = 'ITALIC'

        weight = int(element.find('PropFont').find('Defn').attrib['weight'])
        if weight > 400:
            dp.bold = 'BOLD'

class PhyPart:
    def __init__(self, element):
        self.et = element
        self.pins = {}

class SymbolPinScalar:
    def __init__(self, element, grid_scale = 0.254):
        self.et = element
        self.defn = element.find('Defn').attrib.copy()
        self.clock = element.find('IsClock').find('Defn').attrib['val']
        self.dot = element.find('IsDot').find('Defn').attrib['val']
        self.grid_scale = grid_scale

    def get_type_string(self):
        types = ['input',
                 'bidirectional',
                 'output',
                 'open_collector',
                 'passive',
                 'tri_state',
                 'open_collector',
                 'power_in',
                 'unspecified']
        return types[int(self.defn['type'])]

    def shape(self):
        if (self.clock == '1') and (self.dot == '1'):
            return 'inverted_clock'
        if self.dot == '1':
            return 'inverted'
        if self.clock == '1':
            return 'clock'

        return 'line'

    def name(self):

        name = self.defn['name']

        inv = False
        skip = False
        name_out = ''
        for c in range(len(name)):
            if skip is True:
                skip = False
                continue

            if name[c] == '\\':
                continue

            if c < (len(name) - 1):
                if (name[c + 1] == '\\'):
                    skip = True
                    if inv == False:
                        name_out +='~'
                        inv = True

                else:
                    if inv is True:
                        inv = False
                        name_out +='~'

            name_out += name[c]

        return name_out

    def x1(self):
        return int(self.defn['hotptX']) * self.grid_scale

    def y1(self):
        return -int(self.defn['hotptY']) * self.grid_scale

    def x2(self):
        return int(self.defn['startX']) * self.grid_scale

    def y2(self):
        return -int(self.defn['startY']) * self.grid_scale

    def len(self):
        if (self.x1() - self.x2()) != 0:
            return round(abs(self.x2() - self.x1()), 2)
        if (self.y1() - self.y2()) != 0:
            return round(abs(self.y2() - self.y1()), 2)
        if ((self.x1() - self.x2()) == 0) and ((self.y1() - self.y2()) == 0):
            return 0

    def angle(self):
        if (self.x1() - self.x2()) > 0:
            return 180
        if (self.x1() - self.x2()) < 0:
            return 0
        if (self.y1() - self.y2()) > 0:
            return 270
        if (self.y1() - self.y2()) < 0:
            return 90
        if ((self.x1() - self.x2()) == 0) and ((self.y1() - self.y2()) == 0):
            return 0

    def draw(self, f, phy, pin_nb_sz = 1.5, pin_name_sz = 1.7):
        f.write('      (pin {} {} (at {} {} {}) (length {})\n'.format(self.get_type_string(), self.shape(), self.x1(), self.y1(), self.angle(), self.len()))
        f.write('        (name "{}" (effects (font (size {} {}))))\n'.format(self.name(), pin_name_sz, pin_name_sz))
        f.write('        (number "{}" (effects (font (size {} {}))))\n'.format(phy.pins[self.defn['position']], pin_nb_sz, pin_nb_sz))
        f.write('      )\n')

class Rectangle:
    def __init__(self, element, grid_scale = 0.254):
        self.et = element
        self.defn = element.find('Defn').attrib
        self.grid_scale = grid_scale

    def draw(self, f):
        x1 = round(int(self.defn['x1']) * self.grid_scale, 2)
        x2 = round(int(self.defn['x2']) * self.grid_scale, 2)
        y1 = round(-int(self.defn['y1']) * self.grid_scale, 2)
        y2 = round(-int(self.defn['y2']) * self.grid_scale, 2)

        fillstyle = 'outline'
        if self.defn['fillStyle'] == '1':
            fillstyle = 'none'

        f.write('      (rectangle (start {} {}) (end {} {})\n'.format(x1, y1, x2, y2))
        f.write('      (stroke (width 0.0006)) (fill (type {}))\n'.format(fillstyle))
        f.write('      )\n')


class Polygon:
    def __init__(self, element, grid_scale = 0.254):
        self.et = element
        self.defn = element.find('Defn').attrib
        self.points = []
        self.grid_scale = grid_scale

        for point in element.findall('PolylinePoint'):
            x = round(int(point.find('Defn').attrib['x']) * grid_scale, 2)
            y = round(-int(point.find('Defn').attrib['y']) * grid_scale, 2)
            self.points.append((x, y))

        for point in element.findall('PolygonPoint'):
            x = round(int(point.find('Defn').attrib['x']) * grid_scale, 2)
            y = round(-int(point.find('Defn').attrib['y']) * grid_scale, 2)
            self.points.append((x, y))

    def draw(self, f):
        f.write('      (polyline\n')
        f.write('        (pts\n')

        for x, y in self.points:
                f.write('          (xy {} {})\n'.format(x, y))

        fill = 'none'
        if 'fillStyle' in self.defn:
            if self.defn['fillStyle'] != '1':
                fill = 'outline'

        f.write('        )\n')
        f.write('        (stroke (width 0.0006)) (fill (type {}))\n'.format(fill))
        f.write('      )\n')

class Arc:
    def __init__(self, element, grid_scale = 0.254):
        self.et = element
        self.defn = element.find('Defn').attrib
        self.grid_scale = grid_scale

    def draw(self, f):
        x1 = int(self.defn['x1']) * self.grid_scale
        x2 = int(self.defn['x2']) * self.grid_scale
        y1 = -int(self.defn['y1']) * self.grid_scale
        y2 = -int(self.defn['y2']) * self.grid_scale
        sx = int(self.defn['startX']) * self.grid_scale
        sy = -int(self.defn['startY']) * self.grid_scale
        ex = int(self.defn['endX']) * self.grid_scale
        ey = -int(self.defn['endY']) * self.grid_scale

        rx = math.fabs((x2 - x1) / 2.0)
        ry = math.fabs((y2 - y1) / 2.0)

        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0

        start_angle = math.atan2(sy - cy, sx - cx)
        end_angle = math.atan2(ey - cy, ex - cx)

        if end_angle <= 0:
            end_angle = (2.0 * math.pi) + end_angle

        if start_angle < 0:
            start_angle = (2.0 * math.pi) + start_angle

        if end_angle < start_angle:
            end_angle = end_angle + (2.0 * math.pi)

        step = math.fabs(end_angle - start_angle) / 40.0;

        f.write('      (polyline\n')
        f.write('      (pts\n')

        angles = arange(start_angle, end_angle, step)

        for angle in angles:
            x = cx + (rx * math.cos(angle))
            y = cy + (ry * math.sin(angle))
            f.write('        (xy {} {})\n'.format(x, y))

        f.write('        (xy {} {})\n'.format(ex, ey))

        f.write('      )\n')
        f.write('      (stroke (width 0.0006)) (fill (type none))\n')
        f.write('      )\n')

class Ellipse:
    def __init__(self, element, grid_scale = 0.254):
        self.et = element
        self.defn = element.find('Defn').attrib
        self.grid_scale = grid_scale

    def draw(self, f):
        x1 = int(self.defn['x1']) * self.grid_scale
        x2 = int(self.defn['x2']) * self.grid_scale
        y1 = -int(self.defn['y1']) * self.grid_scale
        y2 = -int(self.defn['y2']) * self.grid_scale

        rx = math.fabs((x2 - x1) / 2.0)
        ry = math.fabs((y2 - y1) / 2.0)

        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0

        fillstyle = 'outline'
        if self.defn['fillStyle'] == '1':
            fillstyle = 'none'

        if rx == ry:
            f.write('      (circle (center {} {}) (radius {}) (stroke (width 0.0006)) (fill (type none)))\n'.format(cx, cy, rx, fillstyle))
            return

        step = 2 * math.pi / 40.0;

        f.write('      (polyline\n')
        f.write('      (pts\n')

        angles = arange(0, 2 * math.pi, step)

        for angle in angles:
            x = cx + (rx * math.cos(angle))
            y = cy + (ry * math.sin(angle))
            f.write('        (xy {} {})\n'.format(x, y))

        f.write('        (xy {} {})\n'.format(cx + rx, cy))

        f.write('      )\n')
        f.write('      (stroke (width 0.0006)) (fill (type {}))\n'.format(fillstyle))
        f.write('      )\n')

class Text:
    def __init__(self, element, grid_scale = 0.254):
        self.et = element
        self.defn = element.find('Defn').attrib
        self.font = element.find('TextFont').find('Defn').attrib
        self.grid_scale = grid_scale

    def draw(self, f):
        name = self.defn['name']
        x = round(int(self.defn['locX']) * self.grid_scale, 2)
        y = round(-int(self.defn['locY']) * self.grid_scale, 2)
        angle = int(self.font['escapement'])

        italic = ''
        if self.font['italic'] == '1':
            italic = 'italic'

        names = name.splitlines()
        height = -(int(self.font['height']) * 0.127)

        for t in names:
            justify = '(justify left top)'
            if (angle == 1800):
                justify = '(justify right bottom)'
            if (angle == 900):
                justify = '(justify right)'

            f.write('      (text "{}" (at {} {} {})\n'.format(t, x, y, angle))
            f.write('        (effects (font (size {} {}) {}) {})\n'.format(height, height, italic, justify))
            f.write('      )\n')

            if angle == 0:
                y = y - (height * 2);
            if angle == 900:
                x = x + (height * 2);
            if angle == 1800:
                y = y + (height * 2);
            if angle == 2700:
                x = x - (height * 2);

class Line:
    def __init__(self, element, grid_scale = 0.254):
        self.et = element
        self.defn = element.find('Defn').attrib
        self.grid_scale = grid_scale

    def draw(self, f):
            x1 = round(int(self.defn['x1']) * self.grid_scale, 2)
            x2 = round(int(self.defn['x2']) * self.grid_scale, 2)
            y1 = round(-int(self.defn['y1']) * self.grid_scale, 2)
            y2 = round(-int(self.defn['y2']) * self.grid_scale, 2)

            f.write('      (polyline\n')
            f.write('      (pts\n')
            f.write('        (xy {} {})\n'.format(x1, y1))
            f.write('        (xy {} {})\n'.format(x2, y2))
            f.write('      )\n')
            f.write('      (stroke (width 0.0006)) (fill (type none))\n')
            f.write('      )\n')

class LibPart:
    def __init__(self, element):
        self.et = element
        self.phypart = []
        self.pinNumbersVisible = False
        self.pinNamesVisible = False
        self.value = ''
        self.part_reference = ''
        self.displayProp = []
        self.userProp = []
        self.bbox = {}
        self.pins = []
        self.rect = []
        self.line = []
        self.text = []
        self.polygon = []
        self.arc = []
        self.ellipse = []

    def get_pin_by_pos(self, position):
        for pin in self.pins:
            if pin.defn['position'] == position:
                return pin

class Symbol:
    def __init__(self, name, refdes, footprint, homo):
        self.name         = name.replace(' ', '_').replace('/', '_').replace('\t', '')
        self.footprint    = footprint
        self.refdes       = refdes
        self.libpart      = []
        self.homogeneous  = False

        if homo == '1':
            self.homogeneous  = True

    def print_properties(self, f, text_size = 1.27, grid_scale = 0.254):
        height = text_size
        width  = text_size

        x = self.libpart[0].displayProp[0].locX
        y = self.libpart[0].displayProp[0].locY
        f.write('    (property "Reference" "{}" (id 0) (at {} {} 0)\n'.format(self.refdes, x, y))
        f.write('      (effects (font (size {} {})) (justify left))\n'.format(height, width))
        f.write('    )\n')

        if len(self.libpart[0].displayProp) > 1:
            x = self.libpart[0].displayProp[1].locX
            y = self.libpart[0].displayProp[1].locY - 2
        else:
            x = int(self.libpart[0].bbox['x1']) * grid_scale
            y = int(self.libpart[0].bbox['y2']) * -grid_scale

        val = self.libpart[0].value
        if val == '':
            val = self.name
        f.write('    (property "PartValue" "{}" (id 4) (at {} {} 0)\n'.format(val, x, y))
        f.write('      (effects (font (size {} {})) (justify left))\n'.format(height, width))
        f.write('    )\n')

        x = int(self.libpart[0].bbox['x1']) * grid_scale
        y = int(self.libpart[0].bbox['y2']) * -grid_scale
        y = y - 10
        # Put Value value below so we can read it
        f.write('    (property "Value" "{}" (id 1) (at {} {} 0)\n'.format(self.name, x, y))
        f.write('      (effects (font (size {} {})) (justify left) hide)\n'.format(height, width))
        f.write('    )\n')

        y = y - height -1
        f.write('    (property "Footprint" "{}" (id 2) (at {} {} 0)\n'.format(self.footprint, x, y))
        f.write('      (effects (font (size {} {})) (justify left) hide)\n'.format(height, width))
        f.write('    )\n')

        f.write('    (property "Datasheet" "" (id 3) (at 0 0 0)\n')
        f.write('      (effects (font (size 0 0)) hide)\n')
        f.write('    )\n')

        y = y - height -1
        nb_user_prop = len(self.libpart[0].userProp)
        if nb_user_prop > 1:
            for i, p in enumerate(self.libpart[0].userProp):
                f.write('    (property "{}" "{}" (id {}) (at {} {} 0)\n'.format(p['name'], p['val'], i + 5, x, y))
                f.write('      (effects (font (size {} {})) (justify left) hide)\n'.format(height, width))
                f.write('    )\n')
                y = y - height - 1

        if (self.homogeneous == False) and (len(self.libpart) > 1):
            f.write('    (property "ki_locked" "" (id {}) (at 0 0 0)\n'.format(nb_user_prop + 5))
            f.write('      (effects (font (size 1.27 1.27)))\n')
            f.write('    )\n')

        return True

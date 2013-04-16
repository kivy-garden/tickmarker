'''
TickMarker
======

The :class:`TickMarker` widget places ticks in the center of the widget so
that when combined with another widget e.g. a slider it would mark intervals.
It supports horizontal and vertical orientation, minor/major ticks and log10
representation.

To create a log slider from 0.1 to 10 starting at 1 with major tick marks at
every decade, and minor ticks at every 0.2 decades::

    from kivy.uix.slider import Slider
    from kivy.collective.tickmarker import TickMarker
    class TickSlider(Slider, TickMarker):
        pass
    s = TickSlider(log=True, min_log=.1, max_log=10, value_log=1,
                   ticks_major=1, ticks_minor=5)

    Or a linear slider from 10 to 200 starting at 60 with major tick marks at
    every 50 units from start, and minor ticks at every 10 units
    s = TickSlider(min=10, max=200, value=60, ticks_major=50, ticks_minor=5)


To create a log progress bar from 10 to 1000 starting at 500 with major tick
marks at every decade, and minor ticks at every 0.1 decades::

    from kivy.uix.progressbar import ProgressBar
    from kivy.collective.tickmarker import TickMarker
    class TickBar(ProgressBar, TickMarker):
        padding = NumericProperty(0)
        min = NumericProperty(0)
        orientation = OptionProperty('horizontal', options=('horizontal'))
    s = TickBar(log=True, min_log=10, max_log=1000, value_log=500,
                ticks_major=1, ticks_minor=10)

When combining with another widget such as a slider, the widget must have
min, max, value, orientation, and padding fields. See the second example above
as to how you would do this with a ProgressBar. When the final widget is
logarithmic you access the fields from min_log, max_log and value_log instead
of from min, max, and value.

'''
__all__ = ('TickMarker', )

import kivy
kivy.require('1.4.0')
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, AliasProperty, OptionProperty, \
        ReferenceListProperty, BoundedNumericProperty, ObjectProperty, \
        BooleanProperty
from kivy.clock import Clock
from kivy.graphics import Mesh
from kivy import metrics
from math import log10, floor, ceil
from decimal import Decimal


class TickMarker(Widget):
    '''Class for creating a TickMarker widget.

    Check module documentation for more details.
    '''

    def _set_log_value(self, value):
        self.value = log10(value)

    def _get_log_value(self):
        return 10 ** self.value
    value_log = AliasProperty(_get_log_value, _set_log_value, bind=('value', ))
    '''Current logarithmic value used for the widget.

    :data:`value_log` is a :class:`~kivy.properties.AliasProperty` of
    :data:`value`.
    '''

    def _set_log_min(self, value):
        self.min = log10(value)

    def _get_log_min(self):
        return 10 ** self.min
    min_log = AliasProperty(_get_log_min, _set_log_min, bind=('min', ))
    '''Minimum value allowed for :data:`value_log` when using logarithms.

    :data:`min_log` is a :class:`~kivy.properties.AliasProperty`
    of :data:`min`.
    '''

    def _set_log_max(self, value):
        self.max = log10(value)

    def _get_log_max(self):
        return 10 ** self.max
    max_log = AliasProperty(_get_log_max, _set_log_max, bind=('max', ))
    '''Maximum value allowed for :data:`value_log` when using logarithms.

    :data:`max_log` is a :class:`~kivy.properties.AliasProperty` of
    :data:`max`.
    '''

    log = BooleanProperty(False)
    '''Determines whether the ticks should be displayed logarithmically (True)
    or linearly (False).

    :data:`log` is a :class:`~kivy.properties.BooleanProperty`, defaults
    to False.
    '''

    ticks_major = BoundedNumericProperty(0, min=0)
    '''Distance between major tick marks.

    Determines the distance between the major tick marks. Major tick marks
    start from min and re-occur at every ticks_major until :data:`max`.
    If :data:`max` doesn't overlap with a integer multiple of ticks_major,
    no tick will occur at :data:`max`. Zero indicates no tick marks.

    If :data:`log` is true, then this indicates the distance between ticks
    in multiples of current decade. E.g. if :data:`min_log` is 0.1 and
    ticks_major is 0.1, it means there will be a tick at every 10th of the
    decade, i.e. 0.1 ... 0.9, 1, 2... If it is 0.3, the ticks will occur at
    0.1, 0.3, 0.6, 0.9, 2, 5, 8, 10. You'll notice that it went from 8 to 10
    instead of to 20, that's so that we can say 0.5 and have ticks at every
    half decade, e.g. 0.1, 0.5, 1, 5, 10, 50... Similarly, if ticks_major is
    1.5, there will be ticks at 0.1, 5, 100, 5,000... Also notice, that there's
    always a major tick at the start. Finally, if e.g. :data:`min_log` is 0.6
    and this 0.5 there will be ticks at 0.6, 1, 5...

    :data:`ticks_major` is a :class:`~kivy.properties.BoundedNumericProperty`,
    defaults to 0.
    '''

    ticks_minor = BoundedNumericProperty(0, min=0)
    '''The number of sub-intervals that divide ticks_major.

    Determines the number of sub-intervals into which ticks_major is divided,
    if non-zero. The actual number of minor ticks between the major ticks is
    ticks_minor - 1. Only used if ticks_major is non-zero. If there's no major
    tick at max then the number of minor ticks after the last major
    tick will be however many ticks fit until max.

    If self.log is true, then this indicates the number of intervals the
    distance between major ticks is divided. The result is the number of
    multiples of decades between ticks. I.e. if ticks_minor is 10, then if
    ticks_major is 1, there will be ticks at 0.1, 0.2...0.9, 1, 2, 3... If
    ticks_major is 0.3, ticks will occur at 0.1, 0.12, 0.15, 0.18... Finally,
    as is common, if ticks major is 1, and ticks minor is 5, there will be
    ticks at 0.1, 0.2, 0.4... 0.8, 1, 2...

    :data:`ticks_minor` is a :class:`~kivy.properties.BoundedNumericProperty`,
    defaults to 0.
    '''

    # Internals properties used for graphical representation.

    _mesh = ObjectProperty(None, allownone=True)

    _trigger = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(TickMarker, self).__init__(**kwargs)

        self._trigger = Clock.create_trigger(self._set_ticks)
        self.bind(center=self._trigger, ticks_major=self._trigger,
                  ticks_minor=self._trigger, padding=self._trigger,
                  min=self._trigger, max=self._trigger,
                  orientation=self._trigger)
        self._trigger()

    def _set_ticks(self, *args):
        mesh = self._mesh
        s_max = self.max
        s_min = self.min
        if self.ticks_major and s_max > s_min:
            if not mesh:
                mesh = Mesh(mode='lines', group=str('TickMarker%d' % id(self)))
                self._mesh = mesh
                self.canvas.add(mesh)
            indices = mesh.indices
            vertices = mesh.vertices
            ticks_minor = self.ticks_minor
            ticks_major = self.ticks_major
            padding = self.padding
            log = self.log

            if log:
                # count the decades in min - max. This is in actual decades,
                # not logs.
                n_decades = floor(s_max - s_min)
                # for the fractional part of the last decade, we need to
                # convert the log value, x, to 10**x but need to handle
                # differently if the last incomplete decade has a decade
                # boundary in it
                if floor(s_min + n_decades) != floor(s_max):
                    n_decades += 1 - (10 ** (s_min + n_decades + 1) - 10 **
                                      s_max) / 10 ** floor(s_max + 1)
                else:
                    n_decades += ((10 ** s_max - 10 ** (s_min + n_decades)) /
                                  10 ** floor(s_max + 1))
                # this might be larger than what is needed, but we delete
                # excess later
                n_ticks = n_decades / float(ticks_major)
                n_ticks = int(floor(n_ticks * (ticks_minor if ticks_minor >=
                                               1. else 1.0))) + 2
                # in decade multiples, e.g. 0.1 of the decade, the distance
                # between ticks
                decade_dist = ticks_major / float(ticks_minor if
                                                  ticks_minor else 1.0)

                points = [0] * n_ticks
                points[0] = (0., True)  # first element is always a major tick
                k = 1  # position in points
                # because each decade is missing 0.1 of the decade, if a tick
                # falls in < min_pos skip it
                min_pos = 0.1 - 0.00001 * decade_dist
                s_min_low = floor(s_min)
                # first real tick location. value is in fractions of decades
                # from the start we have to use decimals here, otherwise
                # floating point inaccuracies results in bad values
                start_dec = ceil((10 ** Decimal(s_min - s_min_low - 1)) /
                                 Decimal(decade_dist)) * decade_dist
                count_min = (0 if not ticks_minor else
                             floor(start_dec / decade_dist) % ticks_minor)
                start_dec += s_min_low
                count = 0  # number of ticks we currently have passed start
                while True:
                    # this is the current position in decade that we are.
                    # e.g. -0.9 means that we're at 0.1 of the 10**ceil(-0.9)
                    # decade
                    pos_dec = start_dec + decade_dist * count
                    pos_dec_low = floor(pos_dec)
                    diff = pos_dec - pos_dec_low
                    zero = abs(diff) < 0.001 * decade_dist
                    if zero:
                        # the same value as pos_dec but in log scale
                        pos_log = pos_dec_low
                    else:
                        pos_log = log10((pos_dec - pos_dec_low
                                         ) * 10 ** ceil(pos_dec))
                    if pos_log > s_max:
                        break
                    count += 1
                    if zero or diff >= min_pos:
                        points[k] = (pos_log - s_min, ticks_minor
                                     and not count_min % ticks_minor)
                        k += 1
                    count_min += 1
                del points[k:]
                n_ticks = len(points)
            else:
                # distance between each tick
                tick_dist = ticks_major / float(ticks_minor if
                                                ticks_minor else 1.0)
                n_ticks = int(floor((s_max - s_min) / tick_dist) + 1)

            count = len(indices) / 2
            # adjust mesh size
            if count > n_ticks:
                del vertices[n_ticks * 8:]
                del indices[n_ticks * 2:]
            elif count < n_ticks:
                    vertices.extend([0] * (8 * (n_ticks - count)))
                    indices.extend(xrange(2 * count, 2 * n_ticks))

            if self.orientation == 'horizontal':
                center = self.center_y
                axis_dist = self.width
                start = self.x + padding
                above, below, dist1, dist2 = 1, 5, 0, 4
            else:
                center = self.center_x
                axis_dist = self.height
                start = self.y + padding
                above, below, dist1, dist2 = 0, 4, 1, 5
            # now, the physical distance between ticks
            tick_dist = (axis_dist - 2 * padding
                         ) / float(s_max - s_min) * (tick_dist if not log
                                                     else 1.0)
            # amounts that ticks extend above/below axis
            maj_plus = center + metrics.dp(12)
            maj_minus = center - metrics.dp(12)
            min_plus = center + metrics.dp(6)
            min_minus = center - metrics.dp(6)

            if log:
                for k in xrange(0, n_ticks):
                    m = k * 8
                    vertices[m + dist1] = start + points[k][0] * tick_dist
                    vertices[m + dist2] = vertices[m + dist1]
                    if not points[k][1]:
                        vertices[m + above] = min_plus
                        vertices[m + below] = min_minus
                    else:
                        vertices[m + above] = maj_plus
                        vertices[m + below] = maj_minus
            else:
                for k in xrange(0, n_ticks):
                    m = k * 8
                    vertices[m + dist1] = start + k * tick_dist
                    vertices[m + dist2] = vertices[m + dist1]
                    if ticks_minor and k % ticks_minor:
                        vertices[m + above] = min_plus
                        vertices[m + below] = min_minus
                    else:
                        vertices[m + above] = maj_plus
                        vertices[m + below] = maj_minus
            mesh.vertices = vertices
            mesh.indices = indices
        else:
            if mesh:
                self.canvas.remove_group(str('TickMarker%d' % id(self)))
                self._mesh = None

if __name__ == '__main__':
    from kivy.app import App
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.slider import Slider
    from kivy.uix.progressbar import ProgressBar

    class TickSlider(Slider, TickMarker):
        pass

    class TickBar(ProgressBar, TickMarker):
        padding = NumericProperty(0)
        min = NumericProperty(0)
        orientation = OptionProperty('horizontal', options=('horizontal'))

    class TickApp(App):

        def build(self):
            layout = GridLayout(cols=2)
            c1 = Label(size_hint=(.2, .15))
            c2 = TickSlider(log=True, min_log=.1, max_log=10, value_log=1,
                            padding=25, ticks_major=1, ticks_minor=5,
                            size_hint=(.8, .15))
            c3 = Label(size_hint=(.2, .15))
            c4 = TickSlider(min=10, max=200, value=60, padding=25,
                            ticks_major=50, ticks_minor=5, size_hint=(.8, .15))
            c5 = Label(size_hint=(.2, .15))
            c6 = TickBar(log=True, min_log=10, max_log=1000, value_log=500.1,
                         ticks_major=1, ticks_minor=10, size_hint=(.8, .15))
            c7 = Label(size_hint=(.2, .55))
            c8 = TickSlider(min=10, max=200, value=60, padding=25,
                            ticks_major=50, ticks_minor=5, size_hint=(.8, .55),
                            orientation='vertical')
            layout.add_widget(c1)
            layout.add_widget(c2)
            layout.add_widget(c3)
            layout.add_widget(c4)
            layout.add_widget(c5)
            layout.add_widget(c6)
            layout.add_widget(c7)
            layout.add_widget(c8)

            def update_value(instance, value):
                if instance is c2:
                    label = c1
                elif instance is c4:
                    label = c3
                elif instance is c6:
                    label = c5
                elif instance is c8:
                    label = c7
                label.text = '%g' % (instance.value_log if instance.log
                                     else instance.value)

            c2.bind(value=update_value)
            c4.bind(value=update_value)
            c6.bind(value=update_value)
            c8.bind(value=update_value)
            c2.value_log = 0.1
            c4.value = 50
            c6.value_log = 500
            c8.value = 50
            return layout

    TickApp().run()

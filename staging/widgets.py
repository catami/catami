from django.forms import Widget, MultiWidget
from django.forms import Field, MultiValueField, ChoiceField
from django.forms import Select, RadioSelect
from django.forms import FloatField, TextInput
from django.forms import TimeInput, DateInput

from django.core import validators
from django.core.exceptions import ValidationError

import re

import logging

logger = logging.getLogger(__name__)


class PointWidget(MultiWidget):
    """A form widget to represent the gis Point model field."""

    def __init__(self, attrs=None):
        widgets = (
            TextInput(attrs=attrs),
            TextInput(attrs=attrs)
        )

        super(PointWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        float_pattern = "[-+]?[0-9]*\.?[0-9]+"
        point_pattern = "POINT\s*\(\s*(?P<lon>{0})\s+(?P<lat>{0})\s*\)".format(float_pattern)

        if value:
            match = re.search(point_pattern, value)

            if match:
                lat = float(match.group('lat'))
                lon = float(match.group('lon'))

                return [lat, lon]

        return [None, None]


class PointField(MultiValueField):
    """A form field to represent the gis Point model field."""
    widget = PointWidget

    def __init__(self, *args, **kwargs):
        lat_errors = {
            'required': u'Latitude is required.',
            'invalid': u'Enter a valid latitude.',
        }
        lon_errors = {
            'required': u'Longitude is required.',
            'invalid': u'Enter a valid longitude.',
        }
        fields = (
            FloatField(error_messages=lat_errors, initial='latitude', min_value=-90.0, max_value=90.0),
            FloatField(error_messages=lon_errors, initial='longitude', min_value=-180.0, max_value=180.0)
        )
        super(PointField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            if data_list[0] in validators.EMPTY_VALUES:
                raise ValidationError("Latitude empty")
            if data_list[1] in validators.EMPTY_VALUES:
                raise ValidationError("Longitude Empty")
            result = "POINT({lon} {lat})".format(lon=data_list[1], lat=data_list[0])
            return result
        return None


class ExtractData:
    # this is used in the multisource widgets etc.
    # it takes the three arguments to work out what to return
    # for a given field in the database model
    # ie either a fixed value or one parsed from the input data stream

    def __init__(self, base_field, source, column_labels, fixed_data):
        """Creates an object to be used in processing data."""
        self.source = source  # the string denoting the source 'fixed' or 'column'
        self.column_labels = column_labels  # the labels to be used
        self.fixed_data = fixed_data  # the fixed value to use
        self.base_field = base_field

    def decompress(self):
        return [self.source, self.column_labels, self.fixed_data]

    def get_data(self, input_dict):
        if self.source == 'fixed':
            return self.fixed_data
        else:
            # now need to filter this data through the
            # matching validation for the base field
            # somehow... and return the clean data
            # could really call clean...
            value = []
            # columns are combined to create the decompressed
            # value
            labels = self.column_labels
            base = self.base_field

            for label in self.column_labels:
                value.append(input_dict[label])

            # pass to the multisourcefield to clean the values
            if len(value) == 1:
                return self.base_field.clean(value[0])
            else:
                return self.base_field.clean(value)


class MultiSourceWidget(MultiWidget):
    """This widget enables fixed values or read from a column.

    It renders as radioboxes allowing selection of with method to
    use to import the data.
    """

    def __init__(self, base_widget, attrs=None):
        self.radio = RadioSelect(attrs=attrs)
        self.cols = MultiColumnWidget(base_widget, attrs=attrs)
        self.base = base_widget
        widgets = (
            self.radio,
            self.cols,
            self.base
        )
        logger.debug('MultiSourceWidget has child widgets: %s', widgets)
        # need to add the column selector widgets and the fixed widgets
        # want to derive the column from the fixed (ie number of columns)

        super(MultiSourceWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.decompress()
        else:
            return ["column", [None] * self.cols.length, None]

    def render(self, name, value, attrs=None):
        """This renders the MultiSourceWidget and its subwidgets.

        It includes a large number of custom attributes built in and handles
        enabling/disabling via javascript of the not in use option.
        """
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized

        if not isinstance(value, list):
            value = self.decompress(value)

        # we want to render a table, labels down the side
        output = []
        base_attrs = self.build_attrs(attrs)
        id_ = base_attrs.get('id', None)

        if id_:
            # make the handler script for the top here...
            script = """
<script>
function swapSource(column_radio, column_id_base, fixed_id_base)
{
    if ($("#"+column_radio).attr("checked"))
    {
        // checked enable column, disable fixed
        $("[id^=" + column_id_base +"]").removeClass("uneditable-input");
        $("[id^=" + column_id_base +"]").attr("disabled", false);
        $("[id^=" + fixed_id_base + "]").addClass("uneditable-input");
        $("[id^=" + fixed_id_base + "]").attr("disabled", true);
    }
    else
    {
        // unchecked disable column, enable fixed
        $("[id^=" + column_id_base +"]").addClass("uneditable-input");
        $("[id^=" + column_id_base +"]").attr("disabled", true);
        $("[id^=" + fixed_id_base + "]").removeClass("uneditable-input");
        $("[id^=" + fixed_id_base + "]").attr("disabled", false);
    }
}
</script>"""
            output.append(script)

        # make the heading...
        output.append(u'<table><thead><tr>')

        output.append(u'<th>Data Source</th>')

        if id_:
            column_id_base = "{0}_{1}".format(id_, 1)
            fixed_id_base = "{0}_{1}".format(id_, 2)
            radio_id_first = "{0}_{1}_{2}".format(id_, 0, 0)
            onchange = "swapSource('{0}', '{1}', '{2}')".format(radio_id_first, column_id_base, fixed_id_base)
            radio_attrs = dict(base_attrs, id="{0}_{1}".format(id_, 0), onchange=onchange)
        else:
            radio_attrs = base_attrs

        for ri in self.widgets[0].subwidgets("{0}_{1}".format(name, 0), value[0], radio_attrs):
            output.append(u'<th>{0}</th>'.format(ri))

        final_attrs = base_attrs

        output.append(u'</tr></thead>')

        # make the entry rows
        output.append(u'<tbody>')

        # if we are looking at a single value field
        if len(self.widgets[1].widgets) == 1:
            # only a single column/value
            col_widget = self.widgets[1].widgets[0]
            base_widget = self.widgets[2]

            logger.debug('MultSourceWidget.render (single)')
            logger.debug('{0} {1}'.format(col_widget, base_widget))

            if id_:
                final_attrs = dict(final_attrs, id="{0}_{1}".format(column_id_base, 0))
            subname = "{0}_{1}_{2}".format(name, 1, 0)
            col_widget_output = col_widget.render(subname, value[1][0], final_attrs)
            if id_:
                final_attrs = dict(final_attrs, id="{0}_{1}".format(fixed_id_base, 2))

            subname = "{0}_{1}".format(name, 2)
            base_widget_output = base_widget.render(subname, value[2], final_attrs)

            label = ""  # self.widgets[2]

            output.append(u'<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>'.format(label, col_widget_output, base_widget_output))
        else:
            # multiple!
            if not isinstance(value[2], list):
                base_sub_values = self.widgets[2].decompress(value[2])
            else:
                base_sub_values = value[2]
            for i, widgets in enumerate(zip(self.widgets[1].widgets, self.widgets[2].widgets)):
                col_widget, base_widget = widgets

                if id_:
                    final_attrs = dict(final_attrs, id="{0}_{1}".format(column_id_base, i))
                subname = "{0}_{1}_{2}".format(name, 1, i)
                col_widget_output = col_widget.render(subname, value[1][i], final_attrs)

                if id_:
                    final_attrs = dict(final_attrs, id="{0}_{1}".format(fixed_id_base, i))
                subname = "{0}_{1}_{2}".format(name, 2, i)
                base_widget_output = base_widget.render(subname, base_sub_values[i], final_attrs)

                label = ""
                if isinstance(base_widget, DateInput):
                    label = "Date:"
                elif isinstance(base_widget, TimeInput):
                    label = "Time:"
                elif isinstance(base_widget, TextInput):
                    # check if this is a point widget
                    if isinstance(self.widgets[2], PointWidget):
                        # now get the labels...
                        pass
                #label = "{0}".format(dir(base_widget))
                #label = "{0}".format(base_widget.id_for_label)

                output.append(u'<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>'.format(label, col_widget_output, base_widget_output))

        output.append(u'</tbody></table>')

        return u''.join(output)


class MultiColumnWidget(MultiWidget):
    def __init__(self, base_widget, choices=(), attrs=None):
        widgets = []
        logger.debug('MultiColumnWidget initialising')

        if issubclass(base_widget.__class__, MultiWidget):
            # it is a subclass, add a select for every column
            logger.debug('MultiColumnWidget based on MultiWidget')
            for source_widget in base_widget.widgets:
                # take the label from the field it is replicating
                logger.debug('MultiColumnWidget creating subwidget for %s', source_widget)
                widgets.append(Select(choices=choices))

        else:
            # not a subclass of multi, add a single select
            logger.debug('MultiColumnWidget based on single Widget')
            widgets.append(Select(choices=choices))

        self.length = len(widgets)

        super(MultiColumnWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value
        else:
            return [None] * self.length
        #raise Exception("Decompress not implemented!")


class MultiSourceField(MultiValueField):

    default_error_messages = {
        'invalid_source': u'Please select a data source.',
        'invalid_value': u'Please enter a valid constant value.',
        'invalid_columns': u'Please select a valid column.',
    }

    def __init__(self, *args, **kwargs):
        # an instance of the field that is to be used
        base_field = kwargs.pop('base_field')
        columns = kwargs.pop('columns')
        logger.debug("MultiSourceField creating for field type '%s', label '%s'", base_field.__class__.__name__, base_field.label)
        selections = (
            ('column', 'Parse Column(s)'),
            ('fixed', 'Constant Value')
        )

        logger.debug("MultiSourceField base widget type '%s'", base_field.widget.__class__.__name__)

        # create an instance of the widget
        widget = MultiSourceWidget(base_field.widget)

        fields = (
            ChoiceField(initial="column", widget=widget.radio, choices=selections),
            MultiColumnField(widget=widget.cols, base_field=base_field, columns=columns, required=False),
            base_field
        )
        super(MultiSourceField, self).__init__(fields, widget=widget, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            source = data_list[0]

            # check the data isn't empty for the selected option
            # also check that there is a selected option
            if data_list[0] in validators.EMPTY_VALUES:
                raise ValidationError(self.error_messages['invalid_source'])
            if source == 'column' and data_list[1] in validators.EMPTY_VALUES:
                raise ValidationError(self.error_messages['invalid_columns'])
            if source == 'fixed' and data_list[2] in validators.EMPTY_VALUES:
                raise ValidationError(self.error_messages['invalid_value'])

            return ExtractData(self.fields[2], *data_list)

        return None


class MultiColumnField(MultiValueField):

    def __init__(self, base_field, columns, *args, **kwargs):
        """Create a set of ChoiceFields with choices=columns.

        It has as many columns are there are fields in the given
        base_field_type.
        """
        logger.debug("MultiColumnField creating for field %s", base_field)
        widget = kwargs.pop('widget')

        fields = []
        if issubclass(base_field.__class__, MultiValueField):
            logger.debug("MultiColumnField based on a MultiValueField")
            for source_field, col_widget in zip(base_field.fields, widget.widgets):
                # take the label from the field it is replicating
                logger.debug("MultiColumnField creating subfield for '%s'", source_field)
                fields.append(ChoiceField(choices=columns, widget=col_widget, label=source_field.label))
        elif issubclass(base_field.__class__, Field):
            logger.debug("MultiColumnField based on a Field")
            # take the label from the field it is replicating
            fields.append(ChoiceField(choices=columns, widget=widget.widgets[0], label=base_field.label))
        else:
            raise Exception("base_field not based on Field or MultiValueField")

        super(MultiColumnField, self).__init__(fields, **kwargs)

    def compress(self, data_list):
        n = len(self.fields)
        if data_list:
            for val in data_list:
                if val in validators.EMPTY_VALUES:
                    raise ValidationError("MultiColumnField values empty")
            # probably should combine at this point, comma separated?
            return data_list

        return None

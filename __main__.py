# Hello world!
#
# This board serves as reference and a live demo for all the features
# currently available in Bitdeli scripts.
#
# Something broken or missing? Help us improve the documentation for
# everybody by letting us know at team@bitdeli.com

# The bitdeli module contains all the functionality for accessing the
# data and creating the widgets
import bitdeli
from bitdeli import Widget

# Feel free to use any modules in the Python Standard Library
import random
from datetime import date, datetime, timedelta
from collections import Counter
from operator import attrgetter


# TODO: move to widgets.py
class Timeline(Widget):
    defaults = {'size': [3,3]}

class Line(Widget):
    defaults = {'size': [3,3]}

class Users(Widget):
    defaults = {'size': [3,3]}


# The set_theme method changes the color theme of the board. Each
# theme contains a background color and three foreground colors. To
# change the color of a widget, use the color option (details below).
bitdeli.set_theme('bank')

# Here's a list of currently supported themes, try them out! bluered
# (default), phosphor, dream, beach, builder, june, i3, lime, arctic,
# lipstick, eighties, safari, bright, bank, sail, casino, clouds,
# valentine, fed, space, purple, playground, vintage, gray, flamingo


# Metrics by country
countries = Counter()

# Metrics by weekday
days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
daily_sales = Counter()
daily_beer = Counter()

# Metrics by product
returns = Counter()
sales = Counter()
feedback_pos = Counter()
feedback_neg = Counter()

# User aggregates
users = {}


# Iterate over all profiles in the data
for profile in bitdeli.profiles():
    # Check the Profiles tab in the left side of the editor to see the
    # fields contained in each profile

    # Create objects for customer aggregates
    if profile.uid not in users:
        first_event = profile['events'][0]
        users[profile.uid] = dict(
            country=first_event['country'],
            stats=Counter())
        if 'gravatar' in first_event:
            users[profile.uid]['gravatar'] = first_event['gravatar']
    user = users[profile.uid]

    # Iterate over all events stored in the profile
    # and update metrics accordingly
    for event in profile['events']:
        if event['event'] == 'buy':
            user['stats']['sales'] += event['price']
            sales[event['product']] += 1
            countries[event['country']] += event['price']
            daily_sales[event['day']] += event['price']
            if event['product'] == 'Beer':
                daily_beer[event['day']] += event['price']
        if event['event'] == 'return':
            user['stats']['returns'] += event['price']
            returns[event['product']] += 1
        if event['event'] == 'feedback-positive':
            user['stats']['pos'] += 1
            feedback_pos[event['product']] += 1
        if event['event'] == 'feedback-negative':
            user['stats']['neg'] += 1
            feedback_neg[event['product']] += 1


# Widget reference:
#
# The rest of this script generates the actual widgets shown on the
# board. The widgets are shown on the board in the order they are
# created in the script.
#
# Options common to all widgets:
# label:  a string that will be shown in the top left
#         corner of a widget
# data:   the data to be displayed, format depends on the widget type
# size:   the size of the widget on the board (see below)
#         size=[x, y] where x and y are positive integer values
# color:  an integer between 1-3, picks a color from the current theme
# group:  define the widget group for this widget (see below)


# About board layout and widget sizing:
#
# The widgets are laid out on a grid that has 12 columns and infinite
# rows. The size option of a widget corresponds to these grid units,
# making 12 the maximum x size of a widget.


# Map widget:
# bitdeli.Map(options)
#
# Displays a map with countries colored according to given data.
# The color scale and map position are determined automatically.
#
# Options:
# data:   a dictionary where keys are 2-letter country codes
#         (ISO 3166-1 alpha-2) and values are numbers

bitdeli.Map(label='Revenue by country',
            data=countries,
            size=[5,4],
            color=3)


# Widget group:
# bitdeli.Group(options)
#
# A widget group can be used to take better control of how the widgets
# are positioned on a board. A widget group behaves like a single
# widget in the board layout.
#
# To add widgets to a group, use the group option when creating
# other widgets.
#
# Note that the size of a group is determined by its contents and can
# not be manually set.
#
# Options:
# layout:   "vertical" or "horizontal" (default)

# This group is used to make sure that the following line and bar
# charts stay together in the board layout
daily_group = bitdeli.Group(layout="vertical")


# Prepare data for the line widget
def get_line_data(sales):
    data = []
    i = 0
    days_tot = 30
    while i < days_tot:
        weekday = i % 7
        tstamp = date.today() - timedelta(days=days_tot-i)
        data.append((tstamp.isoformat(),
                     sales[days[weekday]] / 100 ))
        i += 1
    return data


# Line widget:
# bitdeli.Line(options)
#
# Displays a line chart of time series data.
#
# Options:
# data:   a list of (timestamp, value) tuples, where
#         timestamp is a string in the ISO 8601 format
#         and value is a number
#
# OR to show multiple series on the same chart:
# data:   a list of {label, data} objects, where
#         label is a string shown in the chart legend
#         and data is a list of tuples as defined before

Line(label='Revenue for past 30 days',
             data=[{
                 "label": "Total",
                 "data": get_line_data(daily_sales)
             }, {
                 "label": "Beer",
                 "data": get_line_data(daily_beer)
             }],
             size=(7,2),
             group=daily_group)


# Bar widget:
# bitdeli.Bar(options)
#
# Displays an ordinal bar chart.
#
# Options:
# data:   a list of (label, value) tuples, where
#         label is the label for each bar on the x-axis
#         value is a number determining the height of the bar

bitdeli.Bar(label='% of beer sales from revenue',
            data=[(d, float(daily_beer[d])/daily_sales[d]*100)
                  for d in days],
            size=[5,2],
            group=daily_group)


# Another group for showing top products (text widgets)
top_group = bitdeli.Group(layout="vertical")


# Text widget:
# bitdeli.Text(options)
#
# Displays a large colored text and/or a paragraph
#
# Options:
# head:    a string that will be colored and fitted to be
#          as large as the widget size allows
# text:    a string that will be shown as a normal-sized paragraph
#          below the heading

bitdeli.Text(label='Top selling product',
             head=sales.most_common(1)[0][0],
             color=3,
             size=[4,1],
             group=top_group)

bitdeli.Text(label='Most returns',
             head=returns.most_common(1)[0][0],
             color=2,
             size=[4,1],
             group=top_group)

feedback_tot = dict( (p, feedback_pos.get(p, 0)-
                         feedback_neg.get(p, 0))
                    for p in set(feedback_pos)|set(feedback_neg) )
feedback_tot = Counter(feedback_tot)
most_liked = feedback_tot.most_common(1)[0][0]

bitdeli.Text(label='Most liked product',
             head=most_liked,
             color=1,
             size=[4,1],
             group=top_group)

bitdeli.Text(label='Most liked product',
             text=( "%d positive\n%d negative" %
                   (feedback_pos.get(most_liked, 0),
                    feedback_neg.get(most_liked, 0)) ),
             size=[4,1],
             group=top_group)


# Prepare data for the customers table
customers = []
for uid, u in users.iteritems():
    user = u.copy()
    del user['stats']
    user['id'] = uid
    user.update(u['stats'])
    customers.append(user)

top_customers = sorted(customers,
                       key=lambda c: c.get('sales', 0),
                       reverse=True)

def get_table_data():
    sales_top = top_customers[0]['sales']
    for c in top_customers:
        yield {"Country": c['country'],
               "ID": c['id'],
               "Feedback": ( "+%d/-%d" % (c.get('pos', 0),
                                          c.get('neg', 0)) ),
               "Returns": ("$%d.00" % c.get('returns', 0)),
               "Sales": ("$%d.00" % c.get('sales', 0)),
               "Sales (rel)": float(c.get('sales', 0)) / sales_top}


# Table widget:
# bitdeli.Table(options)
#
# Displays a table of objects with keys as headers and values
# as cell contents.
#
# Options:
# data:   a list of objects
# chart:  To visualize numbers inside the table, provide
#         an object with {header_name: chart_type} pairings.
#         The values in the corresponding column must be
#         normalized between 0 and 1.
#         ("bar" is the only type currently supported)

bitdeli.Table(label='Top 10 customers by sales',
              data=list(get_table_data())[:10],
              chart={"Sales (rel)": "bar"},
              color=2,
              size=[8,4])


# Prepare data for the timeline and users widgets
gravatar_users = [u for u in customers if 'gravatar' in u]

def get_join_event(user):
    return dict(gravatar_hash=user['gravatar'],
                username=user['id'],
                message="Signed up from "+user['country'],
                color=1,
                timestamp=datetime.now().isoformat())

join_events = [get_join_event(u) for u in gravatar_users]


# Empty widgets can be used as spacers
bitdeli.Widget(size=[12,1])


# Timeline widget:
# bitdeli.Timeline(options)
#
# Displays a list of messages with optional avatars and timestamps.
#
# Options:
# data:   a list of timeline event objects
#
# Event object fields:
# gravatar_hash: a MD5 hash of the user's email address
# username:      a string shown before the message
# message:       a string that describes the event
# color:         a theme color (integer between 1-3)
# timestamp:     an ISO 8601 timestamp

Timeline(label='Latest signups',
         data=join_events,
         size=[4,4])


# Users widget:
# bitdeli.Users(options)
#
# Displays a list of users using avatar images from Gravatar.com.
#
# Options:
# data:   a list of user objects
# large:  True -> use double-size avatars (default: False)
#
# User object fields:
# gravatar_hash: a MD5 hash of the user's email address
# username:      a string shown when hovering over the avatar

Users(label='Top customers today',
      large=True,
      size=[4,4],
      data=join_events[:6])

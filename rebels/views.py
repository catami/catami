"""Views for the administratorbot"""
# Create your views here.
#import pylab
#!import scipy
#import matplotlib.pyplot as mpl
#from mpl import figure, axes, pie, title, plot
#!from matplotlib.backends.backend_agg import FigureCanvasAgg
#!from django.http import HttpResponse
#!from django.db import connection, transaction
#!from django.test.client import RequestFactory

#import Force

def query_database_size(request):
    pass

    #!cursor = connection.cursor()
    #!f = mpl.figure(figsize=(10, 10))
    #!mpl.subplot(1, 2, 1)

    #!query = "SELECT nspname || '.' || relname AS \"relation\", pg_size_pretty(pg_total_relation_size(C.oid)) AS \"total_size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN ('pg_catalog', 'information_schema') AND C.relkind <> 'i' AND nspname !~ '^pg_toast' ORDER BY pg_total_relation_size(C.oid) DESC LIMIT 10;"

    #!cursor = connection.cursor()

    #!cursor.execute("SELECT pg_database_size('Force')")
    #!p = cursor.fetchone()
    #!mpl.bar(0, p[0] / 100000)
    #!mpl.title('Database size (mB)')

    #!db_size_str = []
    #!db_size = []
    #!bar_label = []
    #!cursor.execute(query)
    #!for p in cursor.fetchall():
        #!bar_label.append(p[0])
        #!db_size_str.append(p[1])

    
    #!for i in range(0, len(db_size_str)):
        #!temp = db_size_str[i].split(" ")
        #!db_size.append(temp[0])
        #!if temp[1] == 'kB':
            #!db_size[i] = scipy.float32(db_size[i]) * 1000.0
        #!if temp[1] == 'mB':
            #!db_size[i] = db_size[i] * 1000000.0
        #!if temp[1] == 'gB':
            #!db_size[i] = db_size[i] * 1000000000.0

    #!ax = mpl.subplot(1, 2, 2)
    #x = scipy.arange(len(db_size))

    #y = scipy.float32(db_size) / 1000000.0
    #!mpl.bar(x, y, align='center')
    #!mpl.title('Top 10 Table size (mB)')
    #ax.set_xticklabels(bar_label)
    #ax.set_xticks(x)
    #f.autofmt_xdate()

    #canvas = FigureCanvasAgg(f)
    #!response = HttpResponse(content_type='image/png')
    #!canvas.print_png(response)
    #matplotlib.pyplot.close(f)
    #!return response

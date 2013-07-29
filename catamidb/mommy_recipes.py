from datetime import datetime
from model_mommy.recipe import Recipe
from django.contrib.gis.geos import Point, Polygon
from catamidb.models import Image, Deployment

Image1 = Recipe(
    Image,
    position=Point(12.4604, 43.9420),
    depth=27.5,
    date_time=datetime.now()     
)   

Image2 = Recipe(
    Image,
    position=Point(12.4604, 43.9420),
    depth=27.5,
    date_time=datetime.now()     
)          

Image3 = Recipe(
    Image,
    position=Point(12.4604, 43.9420),
    depth=27.5,
    date_time=datetime.now()     
)        

Deployment1 = Recipe(
    Deployment,
    type = 'AUV',
    short_name = 'gdp1',
    operator = '',
    start_position=Point(12.4604, 43.9420),
    end_position=Point(12.4604, 43.9420),
    start_time_stamp=datetime.now(),
    end_time_stamp=datetime.now(),
    min_depth=10.0,
    max_depth=50.0,
    transect_shape=Polygon(((0.0, 0.0),
                            (0.0, 50.0),
                            (50.0, 50.0),
                            (50.0, 0.0),
                            (0.0, 0.0)))
)

Deployment2 = Recipe(
    Deployment,
    type = 'AUV',   
    short_name = 'gdp2',
    operator = '',
    start_position=Point(12.4604, 43.9420),
    end_position=Point(12.4604, 43.9420),
    start_time_stamp=datetime.now(),
    end_time_stamp=datetime.now(),
    min_depth=10.0,
    max_depth=50.0,
    transect_shape=Polygon(((0.0, 0.0),
                            (0.0, 50.0),
                            (50.0, 50.0),
                            (50.0, 0.0),
                            (0.0, 0.0)))
)

Deployment3 = Recipe(
    Deployment,
    type = 'AUV',   
    short_name = 'gdp3',
    operator = '',
    start_position=Point(12.4604, 43.9420),
    end_position=Point(12.4604, 43.9420),
    start_time_stamp=datetime.now(),
    end_time_stamp=datetime.now(),
    min_depth=10.0,
    max_depth=50.0,
    transect_shape=Polygon(((0.0, 0.0),
                            (0.0, 50.0),
                            (50.0, 50.0),
                            (50.0, 0.0),
                            (0.0, 0.0)))
)
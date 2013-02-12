from datetime import datetime
from model_mommy.recipe import Recipe
from django.contrib.gis.geos import Point, Polygon
from Force.models import AUVDeployment, DOVDeployment,BRUVDeployment, TVDeployment, TIDeployment

#model_mommy is supposed to auto fill unassigned fields.  She's a bit of a liar.
auvdeployment= Recipe(AUVDeployment,
    start_position = Point(12.4604, 43.9420),
    start_time_stamp = datetime.now(),
    end_time_stamp = datetime.now(),
    min_depth = 10.0,
    max_depth = 50.0,
    distance_covered=100.0,
    transect_shape = Polygon( ((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0)) )
)

dovdeployment= Recipe(DOVDeployment,
    start_position = Point(12.4604, 43.9420),
    start_time_stamp = datetime.now(),
    end_time_stamp = datetime.now(),
    min_depth = 10.0,
    max_depth = 50.0
)

bruvdeployment= Recipe(BRUVDeployment,
    start_position = Point(12.4604, 43.9420),
    start_time_stamp = datetime.now(),
    end_time_stamp = datetime.now(),
    min_depth = 10.0,
    max_depth = 50.0
)

tvdeployment= Recipe(TVDeployment,
    start_position = Point(12.4604, 43.9420),
    start_time_stamp = datetime.now(),
    end_time_stamp = datetime.now(),
    min_depth = 10.0,
    max_depth = 50.0
)

tideployment= Recipe(TIDeployment,
    start_position = Point(12.4604, 43.9420),
    start_time_stamp = datetime.now(),
    end_time_stamp = datetime.now(),
    min_depth = 10.0,
    max_depth = 50.0
)
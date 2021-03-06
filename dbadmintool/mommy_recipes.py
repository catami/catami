from django.contrib.gis.geos import Point, Polygon
from django.utils.datetime_safe import datetime
from model_mommy.recipe import Recipe
from catamidb.models import AUVDeployment, DOVDeployment, BRUVDeployment, \
    TVDeployment, TIDeployment

auvdeployment1 = Recipe(AUVDeployment,
                        start_position=Point(12.4604, 43.9420),
                        end_position=Point(12.4604, 43.9420),
                        start_time_stamp=datetime.now(),
                        end_time_stamp=datetime.now(),
                        min_depth=10.0,
                        max_depth=50.0,
                        transect_shape=Polygon((
                        (0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0),
                        (0.0, 0.0)))
)

auvdeployment2 = Recipe(AUVDeployment,
                        start_position=Point(12.4604, 43.9420),
                        end_position=Point(12.4604, 43.9420),
                        start_time_stamp=datetime.now(),
                        end_time_stamp=datetime.now(),
                        min_depth=10.0,
                        max_depth=50.0,
                        transect_shape=Polygon((
                        (0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0),
                        (0.0, 0.0)))
)

auvdeployment = Recipe(AUVDeployment,
                       start_position=Point(12.4604, 43.9420),
                       end_position=Point(12.4604, 43.9420),
                       start_time_stamp=datetime.now(),
                       end_time_stamp=datetime.now(),
                       min_depth=10.0,
                       max_depth=50.0,
                       transect_shape=Polygon((
                       (0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0),
                       (0.0, 0.0)))
)

dovdeployment = Recipe(DOVDeployment,
                       start_position=Point(12.4604, 43.9420),
                       end_position=Point(12.4604, 43.9420),
                       start_time_stamp=datetime.now(),
                       end_time_stamp=datetime.now(),
                       min_depth=10.0,
                       max_depth=50.0
)

bruvdeployment = Recipe(BRUVDeployment,
                        start_position=Point(12.4604, 43.9420),
                        end_position=Point(12.4604, 43.9420),
                        start_time_stamp=datetime.now(),
                        end_time_stamp=datetime.now(),
                        min_depth=10.0,
                        max_depth=50.0
)

tvdeployment = Recipe(TVDeployment,
                      start_position=Point(12.4604, 43.9420),
                      end_position=Point(12.4604, 43.9420),
                      start_time_stamp=datetime.now(),
                      end_time_stamp=datetime.now(),
                      min_depth=10.0,
                      max_depth=50.0
)

tideployment = Recipe(TIDeployment,
                      start_position=Point(12.4604, 43.9420),
                      end_position=Point(12.4604, 43.9420),
                      start_time_stamp=datetime.now(),
                      end_time_stamp=datetime.now(),
                      min_depth=10.0,
                      max_depth=50.0
)

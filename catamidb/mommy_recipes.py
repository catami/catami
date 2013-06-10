from datetime import datetime
from model_mommy.recipe import Recipe
from django.contrib.gis.geos import Point, Polygon
from catamidb.models import AUVDeployment, DOVDeployment, BRUVDeployment, TVDeployment, TIDeployment, Pose, GenericImage, GenericDeployment

pose1 = Recipe(
    Pose,
    position=Point(12.4604, 43.9420),
    depth=27.5,
    date_time=datetime.now()
)

pose2 = Recipe(
    Pose,
    position=Point(12.4604, 43.9420),
    depth=27.5,
    date_time=datetime.now()
)

pose3 = Recipe(
    Pose,
    position=Point(12.4604, 43.9420),
    depth=27.5,
    date_time=datetime.now()
)

genericImage1 = Recipe(
    GenericImage,
    position=Point(12.4604, 43.9420),
    depth=27.5,
    date_time=datetime.now()     
)   

genericImage2 = Recipe(
    GenericImage,
    position=Point(12.4604, 43.9420),
    depth=27.5,
    date_time=datetime.now()     
)          

genericImage3 = Recipe(
    GenericImage,
    position=Point(12.4604, 43.9420),
    depth=27.5,
    date_time=datetime.now()     
)        

genericDeployment1 = Recipe(
    GenericDeployment,
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

genericDeployment2 = Recipe(
    GenericDeployment,
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

genericDeployment3 = Recipe(
    GenericDeployment,
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

auvdeployment1 = Recipe(
    AUVDeployment,
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

auvdeployment2 = Recipe(
    AUVDeployment,
    start_position=Point(12.4604, 43.9420),
    end_position=Point(12.4604, 43.9420),
    start_time_stamp=datetime.now(),
    end_time_stamp=datetime.now(),
    min_depth=10.0,
    max_depth=50.0,
    short_name = 'bob',
    transect_shape=Polygon(((0.0, 0.0),
                            (0.0, 50.0),
                            (50.0, 50.0),
                            (50.0, 0.0),
                            (0.0, 0.0)))
)

auvdeployment = Recipe(
    AUVDeployment,
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

dovdeployment = Recipe(
    DOVDeployment,
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

bruvdeployment = Recipe(
    BRUVDeployment,
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

tvdeployment = Recipe(
    TVDeployment,
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

tideployment = Recipe(
    TIDeployment,
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
                            (0.0, 0.0))))

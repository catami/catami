from datetime import datetime
from model_mommy.recipe import Recipe
from django.contrib.gis.geos import Point, Polygon
from catamidb.models import GenericImage
from projects.models import Project

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

project1 = Recipe(
    Project,
    creation_date=datetime.now(),
    modified_date=datetime.now(),
    #images = ManyToManyField(Image, related_name='collections')
)
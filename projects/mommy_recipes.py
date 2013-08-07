from datetime import datetime
from model_mommy.recipe import Recipe
from django.contrib.gis.geos import Point, Polygon
from catamidb.models import Image
from projects.models import Project

Image1 = Recipe(
    Image,
    image_name = 'Image1',
    position=Point(12.4604, 43.9420),
    depth=27.5,
    date_time=datetime.now()
)

Image2 = Recipe(
    Image,
    image_name = 'Image2',
    position=Point(4.561, 23.1420),
    depth=27.5,
    date_time=datetime.now()
)

Image3 = Recipe(
    Image,
    image_name = 'Image3',
    position=Point(62.4151, 41.2234),
    depth=27.5,
    date_time=datetime.now()
)

project1 = Recipe(
    Project,
    creation_date=datetime.now(),
    modified_date=datetime.now(),
    #images = ManyToManyField(Image, related_name='collections')
)
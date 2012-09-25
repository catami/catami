import datetime
from haystack import indexes
from Force.models import Campaign

class CampaignIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    short_name = indexes.CharField(model_attr='short_name')
    #description = indexes.TextField(model_attr='description')
 
    def get_model(self):
        return Campaign
 
    def index_queryset(self):
        return self.get_model().objects.all()

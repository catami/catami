import datetime
from haystack import indexes
from Force.models import Campaign, Deployment

class CampaignIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
 
    def get_model(self):
        return Campaign
 
    def index_queryset(self):
        return self.get_model().objects.all()


class DeploymentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
 
    def get_model(self):
        return Deployment
 
    def index_queryset(self):
        return self.get_model().objects.all()

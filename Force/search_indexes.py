"""@brief HayStack search indexes for Catami data.

Created Mark Gray 10/09/2012
markg@ivec.org

Edits :: Name : Date : description

"""
from haystack import indexes
from Force.models import Campaign, AUVDeployment, BRUVDeployment, Deployment


class CampaignIndex(indexes.SearchIndex, indexes.Indexable):
    """@brief Campaign Index

    """
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Campaign

    def index_queryset(self):
        return self.get_model().objects.all()


class DeploymentIndex(indexes.SearchIndex, indexes.Indexable):
    """@brief Deployment Index

    """
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Deployment

    def index_queryset(self):
        return self.get_model().objects.all()


class AUVDeploymentIndex(indexes.SearchIndex, indexes.Indexable):
    """@brief AUVDeployment Index

    """
    text = indexes.CharField(document=True, use_template=True)
    location = indexes.LocationField(model_attr='start_position')

    def get_model(self):
        return AUVDeployment

    def index_queryset(self):
        return self.get_model().objects.all()


class BRUVDeploymentIndex(indexes.SearchIndex, indexes.Indexable):
    """@brief BRUVDeployment Index

    """
    text = indexes.CharField(document=True, use_template=True)
    location = indexes.LocationField(model_attr='start_position')

    def get_model(self):
        return BRUVDeployment

    def index_queryset(self):
        return self.get_model().objects.all()

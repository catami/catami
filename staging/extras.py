from staging.models import Progress

def update_progress(key, progress):
    obj = Progress.objects.get(pk=key)
    obj.progress = progress
    obj.save()

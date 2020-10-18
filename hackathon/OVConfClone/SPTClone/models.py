from django.db import models

# Create your models here.

class Config(models.Model):
    ov_name = models.CharField(max_length=300)
    ip = models.CharField(max_length=300)
    user_name = models.CharField(max_length=300)
    password = models.CharField(max_length=300)
    api_version = models.IntegerField()
    source_SPT_name = models.CharField(max_length=300)

    def __str__(self):
        return self.ov_name
    
class Spt(models.Model):
    spt_data = models.TextField()
    ov_name = models.ForeignKey('Config', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.spt_name
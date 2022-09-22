

from dipay import models
from django.db.models.deletion import Collector

obj = models.Customer.objects.get(pk=9)

collector = Collector(using='default')
collector.collect([obj,])
dependencies = collector.dependencies.get(obj.__classs__, set())

print(dependencies, type(dependencies))



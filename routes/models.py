from typing import List, Tuple
from collections import Counter
import datetime
from django.db.models import F
from django.db import models


class Driver(models.Model):
    email = models.CharField(max_length=50)
    active = models.BooleanField()


class LastCacheDate(models.Model):
    date = models.DateField()

    class Meta:
        ordering = ['-date']


class Visit(models.Model):
    delivery_date = models.DateField()
    member_id = models.CharField(max_length=15)
    driver = models.CharField(max_length=50) # driver email
    
    def as_tuple(self):
        return (self.driver, self.member_id)

    def __str__(self):
        return f'{self.driver} visited {self.member_id} on {self.delivery_date}'


def digest_visits(date_start, date_end) -> List[Tuple[str, str]]:
    visits: List[Visit] = Visit.objects.filter(delivery_date__gte=date_start, 
                                               delivery_date__lt=date_end)
    return [visit.as_tuple() for visit in visits]


def update_relationships() -> None:
    """This is probably kind of cumbersome to run, maybe it only
       runs once a week or something out of the shell."""
    date_start = LastCacheDate.objects.first()
    date_end = datetime.datetime.today().date()
    counts = Counter(digest_visits(date_start, date_end))
    LastCacheDate.objects.create(date=date_end)

    for (driver, member_id), quantity in counts.items():
        ship = RelationshipCache.objects.filter(driver=driver, member_id=member_id)
        if ship:
            ship.update(cache_date=date_end, 
                        visit_count=F('visit_count') + quantity
            )
        else:
            RelationshipCache.objects.create(cache_date=date_end,
                                             driver=driver,
                                             member_id=member_id,
                                             visit_count=quantity)


class RelationshipCache(models.Model):
    """This is what the app uses to decide on drivers."""
    cache_date = models.DateField()
    member_id = models.CharField(max_length=15)
    driver = models.CharField(max_length=50, default='') # driver email
    visit_count = models.IntegerField()

    def as_tuple(self):
        return ((self.member_id, self.driver), self.visit_count)

    def __str__(self):
        return f"Driver {self.driver} has visited {self.member_id} {self.visit_count} times. Last updated {self.cache_date}"

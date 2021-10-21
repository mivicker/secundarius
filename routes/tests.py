import datetime
from django.test import TestCase
from .logic.adapter import build_relationship_lookup 
from .models import update_relationships, Visit, RelationshipCache, LastCacheDate
from .logic.van import assign_drivers


class Relationships(TestCase):
    def test_update_relationships(self):
        yesterday = (datetime.datetime.today()- datetime.timedelta(days=1)).date() 
        two_days_ago = (datetime.datetime.today() - datetime.timedelta(days=2)).date()

        LastCacheDate.objects.create(date=two_days_ago)

        relationships = [('101010', 'mvickers@gcfb.org', yesterday),
                         ('101010', 'mvickers@gcfb.org', yesterday),
                         ('101020', 'bvickers@coffee.com', yesterday)]

        for relationship in relationships:
            Visit.objects.create(
                date = relationship[2],
                member_id = relationship[0],
                driver = relationship[1]
            )

        update_relationships()

        cache:RelationshipCache = RelationshipCache.objects.get(driver='mvickers@gcfb.org', 
                                                                member_id='101010')

        self.assertEqual(cache.visit_count, 2)

    def test_algorithm(self):
        yesterday = (datetime.datetime.today()- datetime.timedelta(days=1)).date() 
        two_days_ago = (datetime.datetime.today() - datetime.timedelta(days=2)).date()

        LastCacheDate.objects.create(date=two_days_ago)

        relationships = [('101010', 'mvickers@gcfb.org', yesterday),
                         ('101010', 'mvickers@gcfb.org', yesterday),
                         ('101020', 'bvickers@coffee.com', yesterday),
                         ('101030', 'hamilton', yesterday),
                         ('101010', 'hamilton', yesterday),
                         ('101020', 'hamilton', yesterday)]

        for relationship in relationships:
            Visit.objects.create(
                date = relationship[2],
                member_id = relationship[0],
                driver = relationship[1]
            )

        update_relationships()

        route_one = ['101010']
        route_two = ['101020']
        route_three = ['101030']

        counts = build_relationship_lookup()
        
        assignments = assign_drivers(
            ['hamilton', 'bvickers@coffee.com', 'mvickers@gcfb.org'],
            [route_one, route_two, route_three],
            counts
            )

        self.assertEqual(assignments[0], 'mvickers@gcfb.org')
        self.assertEqual(assignments[1], 'bvickers@coffee.com')

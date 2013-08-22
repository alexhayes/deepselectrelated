from django import test
from deepselectrelated.models import Staff, Task
from django.contrib.auth import get_user_model

class DeepSelectRelatedTestCase(test.TestCase):
    fixtures = ['deepselectrelated.yaml']
    
    def setUp(self):
        self.creator = Staff.objects.get(pk=1)
        self.owner = Staff.objects.get(pk=2)
    
    def test_without_select_related(self):
        """
        This test passes.
        """
        task = Task.objects.get(pk=1)
        self.assertEqual(task.creator.staffuser.staff, self.creator)
        self.assertEqual(task.owner.staffuser.staff, self.owner)
    
    def test_with_select_related(self):
        """
        This test fails on django master at [c5f768f8cc53a54686bcb1867cc4400393427ffe]
        """
        qs = Task.objects.select_related('creator__staffuser__staff', 'owner__staffuser__staff')
        # Debug the sql statement...
        print "%s" % qs.query
        task = qs.get(pk=1)
        self.assertEqual(task.creator.staffuser.staff, self.creator)
        self.assertEqual(task.owner.staffuser.staff, self.owner)
    
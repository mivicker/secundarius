from django.db import models

class Words(models.Model):
	created = models.DateTimeField(auto_now=True)
	words = models.TextField()

	class Meta:
		ordering = ['-created']

	def __str__(self):
		if len(self.words) > 25:
			return self.words[:25] + "..."
		return self.words
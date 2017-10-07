import random

class advert(object):
	"""Class for advert"""
	def __init__(self, category, expensive, clusterCat, location):
		super(advert, self).__init__()
		self.category = category
		self.cost = cost
		self.clusterCat = clusterCat
		self.location = location
		self.accepted = 0.0 # Number of times ad was clicked on
		self.total = 0.0	# Total number of times ad was offered
		self.availableClusters = [] # List of all cluster that this advert can switch to if it is rejeced too many times

	def updateClusterCat(self,globalClusterRatio,globalPeopleRatio):
		"""updates cluster category for the advertisement if too many people reject it"""
		acceptRatio = self.accepted/self.total
		if acceptRatio < globalClusterRatio:
			self.availableClusters.remove(self.clusterCat)
			self.clusterCat = random.choice(self.availableClusters)









		
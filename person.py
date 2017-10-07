import numpy as np

class person(object):
	"""docstring for person"""
	def __init__(self, id,name,age,gender,home,native,employment,maritalStatus,checkins,category,availableClusters):
		super(person, self).__init__()
		self.ID = ID # Unique ID
		self.age = age 
		self.gender = gender
		self.Home = home # Current Location
		self.native = native # Native Location
		self.employment = employment # Designation
		self.maritalStatus = maritalStatus 
		self.checkins = lastCheckin # numpy array lists of the format [[string,datetime],[string,datetime]] string=status
		self.category = category # 
		self.accepted = 0
		self.totaled = 0
		self.availableClusters = availableClusters[availableClusters[:,1]].argsort()[::-1] # sorts the clusters in decreasing weight order
																						   # numpy array of format [[cluster,weight],[cluster,weight]]
		
	def updateCategory(self,globalPeopleRatio):
		"""updates cluster category for the person if too many people reject it"""
		acceptRatio = self.accepted/self.total
		if acceptRatio < globalPeopleRatio:
			self.availableClusters = self.availableClusters[self.availableClusters[:,0]!=category] # all clusters except the current one
			self.clusterCat = self.availableClusters[0,0] # pick the next highest weighted cluster, which should be the first one


		
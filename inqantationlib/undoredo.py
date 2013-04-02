from PyQt4 import QtGui,QtCore

class SwapCommand(QtGui.QUndoCommand):
	def __init__(self, el, el2):
		super().__init__("Swap {} with {}".format(
						el.getroottree().getpath(el),
						el2.getroottree().getpath(el2)))
		#save as much as we can about the first node's original position
		self.el=el
		self.idx=el.getparent().index(el)
		self.p=self.el.getparent()

		#save as much as we can about the second node's original position
		self.el2=el2
		self.idx2=el2.getparent().index(el2)
		self.p2=self.el2.getparent()

	def redo(self):
		#moves the first element specified to where
		#the second element used to be and vice versa
		self.p.remove(self.el)
		self.p2.remove(self.el2)
		self.p.insert(self.idx, self.el2)
		self.p2.insert(self.idx2, self.el)

	def undo(self):
		#returns the nodes to their appropriate positions
		self.p.remove(self.el2)
		self.p2.remove(self.el)
		self.p.insert(self.idx, self.el)
		self.p2.insert(self.idx2, self.el2)

class InsertCommand(QtGui.QUndoCommand):
	def __init__(self, parent, el, position=None):
		super().__init__("Place a {} in {} at {}".format(el.tag, 
						parent.getroottree().getpath(parent),
						"<end>" if position is None else position))
		self.parent=parent
		self.el=el
		self.position=position

	def redo(self):
		if self.position is None:
			self.parent.append(self.el)
			#self.position=self.parent.index(self.el)
		else:
			self.parent.insert(self.position, self.el)

	def undo(self):
		self.parent.remove(self.el)

class RemoveCommand(QtGui.QUndoCommand):
	def __init__(self, el):
		self.parent=el.getparent()
		self.el=el
		self.position=self.parent.index(self.el)
		super().__init__("Removing {} from {}".format(el.tag,
						self.parent.getroottree().getpath(self.parent)))
	def redo(self):
		self.parent.remove(el)
	
	def undo(self):
		self.parent.insert(position, el)

class SetElementTextCommand(QtGui.QUndoCommand):
	def __init__(self, el, newtext):
		super().__init__("Set {}'s text to {}".format(
						el.getroottree().getpath(el),newtext[:256]))
		self.newtext=newtext
		self.el=el
		self.oldtext=el.text

	def redo(self):
		self.el.text=self.newtext

	def undo(self):
		self.el.text=self.oldtext

class AddAttributeCommand(QtGui.QUndoCommand):
	def __init__(self, el, key, val):
		super().__init__("Add/Set {}'s {} attribute to {}".format(
						el.getroottree().getpath(el),key,val))
		self.didexistbefore=key in el.attrib
		self.el=el
		self.key=key
		self.val=val
		if self.didexistbefore: self.oldval=self.el.attrib[self.key]
	def redo(self):
		self.el.attrib[self.key]=self.val
	def undo(self):
		if self.didexistbefore:
			self.el.attrib[self.key]=self.oldval
		else:
			del self.el.attrib[self.key]

class RemoveAttributeCommand(QtGui.QUndoCommand):
	def __init__(self, el, key, val):
		super().__init__("Remove {}'s {} attribute to {}".format(
						el.getroottree().getpath(el),key,val))
		self.el=el
		self.key=key
		self.val=val
	def redo(self):
		del self.el.attrib[self.key]
	def undo(self):
		self.el.attrib[self.key]=self.val

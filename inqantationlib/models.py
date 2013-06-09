from PyQt4 import QtGui,QtCore
from . import xmlobjects
from .xmlobjects import etree
'''
class ListyDelegate(QtGui.QStyledItemDelegate):
	def paint(self, painter, option, index):
		super().paint(painter,option,index)
		data = index.data(QtCore.Qt.UserRole) #<- get out xmlly stuff from here!
		if data.tag == 'FaveColor':
			rect=option.rect
			c=QtGui.QColor.fromHslF(data.color.hue,
					data.color.saturation,
					data.color.value)
			print(c.name())
			print(data.color.hue,
					data.color.saturation,
					data.color.value)
			painter.setBrush(QtGui.QBrush(c))
			painter.setPen(QtGui.QPen(c))
			painter.fillRect(1,1,option.rect.height()-2,option.rect.height()-2,c)
'''

class AbstractXPathModel(QtCore.QAbstractListModel):
	def __init__(self, tree, xpath):
		super().__init__()
		self._tree=tree
		self._xpath=xpath
	def _allElements(self):
		if isinstance(self._xpath, str):
			self._xpath=etree.XPath(self._xpath)
			return self._allElements()
		else:
			return self._xpath(self._tree)
	def data(self, index, role):
		if not index.isValid():
			return None
		el=self._allElements()[index.row()]
		if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
			return self._displayRole(el)
		elif role == QtCore.Qt.DecorationRole:
			return self._decorationRole(el)
		elif role == QtCore.Qt.UserRole:
			return el
		elif role == QtCore.Qt.CheckStateRole:
			return self._checkRole(el)
	def _displayRole(self, el): return el.tag
	def _decorationRole(self, el): pass
	def _checkRole(self, el): pass
	def rowCount(self, index=QtCore.QModelIndex()):
		return len(self._allElements())

class FaveColorModel(AbstractXPathModel):
	def __init__(self, tree, xpath=xmlobjects.ALLCOLS):
		super().__init__(tree, xpath)
	def _decorationRole(self, el):
		return QtGui.QColor.fromHsvF(el.color.hue,
				el.color.saturation,
				el.color.value)
	def _displayRole(self, el):
		return "{}\nEffects: {}".format(el.label.text,
				', '.join(e.effectkw.text for e in el.effects()))

class IngredientModel(AbstractXPathModel):
	def __init__(self, tree, xpath=xmlobjects.ALLINGS):
		super().__init__(tree, xpath)
	def _decorationRole(self, el):
		pass
	def _displayRole(self, el):
		return "{}\nEffects: {}".format(el.label.text,
			', '.join(e.effectkw.text for e in el.effects()))

class RecipeModel(AbstractXPathModel):
	def __init__(self, tree, xpath=xmlobjects.ALLREPS):
		super().__init__(tree, xpath)
	def _decorationRole(self, el):
		pass
	def _displayRole(self, el):
		filler=', '.join([e.label.text for e in el.usedIngredients()])
		filler2list=[]
		for e in el.usedColors():
			filler2list.append("{} ({},{},{})".format(e.label.text,
						e.color.hue,
						e.color.saturation,
						e.color.value))
		filler2=', '.join(filler2list)
		return ("Recipe: {}\nNeeded Ingredients: {}"
			"\nNeeded Energy: {}").format(el.label.text, filler, filler2)

class StepModel(AbstractXPathModel):
	def __init__(self, tree, xpath=xmlobjects.ALLSTPS):
		super().__init__(tree, xpath)
	def _decorationRole(self, el):
		pass
	def _displayRole(self, el):
		if len(el.usedColor()) > 0:
			filler="{} ({},{},{})".format(el.usedColor()[0].label.text,
						el.usedColor()[0].color.hue,
						el.usedColor()[0].color.saturation,
						el.usedColor()[0].color.value)
		else:
			filler=el.usedIngredient()[0].label.text
		return "Step: {}\nNeeded: {}".format(el.details.text, filler)

class EffectModel(AbstractXPathModel):
	def __init__(self, tree, xpath=xmlobjects.ALLFXS):
		super().__init__(tree, xpath)
	def _decorationRole(self, el):
		pass
	def _displayRole(self, el):
		return el.effectkw.text
	def flags(self, idx):
		return super().flags(idx)|QtCore.Qt.ItemIsEditable
	def setData(self, idx, val, role):
		if idx.isValid() and role == QtCore.Qt.EditRole:
			idx.data(QtCore.Qt.UserRole).effectkw = val
			self.dataChanged.emit(idx, idx)
			return True
		else:
			return False
	def insertRow(self, row, parent=QtCore.QModelIndex()):
		return self.insertRows(row, 1, parent=parent)
	def insertRows(self, row, count, parent=QtCore.QModelIndex()):
		self.beginInsertRows(parent, row, row+count-1)
		new_node = self._tree.getroot().newEffect()
		if row == self.rowCount():
			start_here = self.data(self.index(self.rowCount()-1,0), QtCore.Qt.UserRole)
			start_here.addnext(new_node)
		elif row == 0:
			start_here = self.data(self.index(0,0), QtCore.Qt.UserRole)
			start_here.addprevious(new_node)
		else:
			start_here = self.data(self.index(row,0), QtCore.Qt.UserRole)
			start_here.addprevious(new_node)
		for x in range(count-1):
			new_node2 = self.tree.getroot().newEffect()
			new_node.addnext(new_node2)
			new_node=new_node2
		
		"""
		if row == 0:
			pass
		elif row == self.rowCount(parent):
			pass
		elif not parent.child(0,0).isValid(): # this will always be the case...
			pass
		else: #we've got children and we need to insert $count rows before the $row row
			pass
		"""
		
		self.endInsertRows()
		return True
	def removeRow(self, row, parent=QtCore.QModelIndex()):
		return self.removeRows(row, 1, parent=parent)
	def removeRows(self, row, count, parent=QtCore.QModelIndex()):
		self.beginRemoveRows(parent, row, row+count)
		if row < 0 or row == self.rowCount() or count > self.rowCount():
			self.endRemoveRows()
			return False
		else:
			print(row)
			start_here = self.data(self.index(row,0), QtCore.Qt.UserRole)
			stop = 0
			for x in reversed(list(start_here.itersiblings(tag=start_here.tag))[:count]):
				if stop == count: break
				self._tree.getroot().remove(x)
				stop+=1
		
		"""
		if row == 0:
			pass
		elif row == self.rowCount(parent):
			pass
		elif not parent.child(0,0).isValid():
			pass
		else: #we've got children and we need to remove $count rows starting at the $row row
			pass
		"""
		self.endRemoveRows()
		return True

class EffectTaggerModel(EffectModel):
	def __init__(self, taggable):
		super().__init__()
		self.taggable=taggable
	def _decorationRole(self, el):
		pass
	def _displayRole(self, el):
		return el.effectkw.text
	def flags (self, index):
		# ?
		return self.flags()|self.isCheckable()
	def setData(self, index, role):
		if role == QtCore.Qt.CheckStateRole:
			#we're going to start taggin!
			#code that does tagging
			#emit a signal that we've finished tagging
			pass
	def _checkRole(self, el):
		if self.taggable.tag == 'FaveColor':
			return el in self.taggable.effects(nocalc=True)
		else:
			return el in self.taggable.effects()
		
		

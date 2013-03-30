from PyQt4 import QtGui,QtCore
from . import xmlobjects
'''
class ListyDelegate(QtGui.QStyledItemDelegate):
	def paint(self, painter, option, index):
		super().paint(painter,option,index)
		data = index.data(QtCore.Qt.UserRole) #<- get out xmlly stuff from here!
		if data.tag == 'FaveColor':
			rect=option.rect
			c=QtGui.QColor.fromHslF(data.color.hue,
					data.color.saturation,
					data.color.luminosity)
			print(c.name())
			print(data.color.hue,
					data.color.saturation,
					data.color.luminosity)
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
			return self._tree.xpath(self._xpath)
		else:
			return self._xpath(self._tree)
	def data(self, index, role):
		if not index.isValid():
			return None
		el=self._allElements()[index.row()]
		if role == QtCore.Qt.DisplayRole:
			return self._displayRole(el)
		elif role == QtCore.Qt.DecorationRole:
			return self._decorationRole(el)
		elif role == QtCore.Qt.UserRole:
			return el
	def _displayRole(self, el):
		return el.tag
	def _decorationRole(self, el):
		pass
	def rowCount(self, index):
		return len(self._allElements())

class FaveColorModel(AbstractXPathModel):
	def __init__(self, tree, xpath='//FaveColor'):
		super().__init__(tree, xpath)
	def _decorationRole(self, el):
		return QtGui.QColor.fromHsvF(el.color.hue,
				el.color.saturation,
				el.color.luminosity)
	def _displayRole(self, el):
		return "{}\nEffects: {}".format(el.label.text,
				', '.join(e.effectkw.text for e in el.effects()))

class IngredientModel(AbstractXPathModel):
	def __init__(self, tree, xpath='//Ingredient'):
		super().__init__(tree, xpath)
	def _decorationRole(self, el):
		pass
	def _displayRole(self, el):
		return "{}\nEffects: {}".format(el.label.text,
			', '.join(e.effectkw.text for e in el.effects()))

class RecipeModel(AbstractXPathModel):
	def __init__(self, tree, xpath='//Recipe'):
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
						e.color.luminosity))
		filler2=', '.join(filler2list)
		return ("Recipe: {}\nNeeded Ingredients: {}"
			"\nNeeded Energy: {}").format(el.label.text, filler, filler2)

class StepModel(AbstractXPathModel):
	def __init__(self, tree, xpath='//Step'):
		super().__init__(tree, xpath)
	def _decorationRole(self, el):
		pass
	def _displayRole(self, el):
		if len(el.usedColor()) > 0:
			filler="{} ({},{},{})".format(el.usedColor()[0].label.text,
						el.usedColor()[0].color.hue,
						el.usedColor()[0].color.saturation,
						el.usedColor()[0].color.luminosity)
		else:
			filler=el.usedIngredient()[0].label.text
		return "Step: {}\nNeeded: {}".format(el.details.text, filler)

class EffectModel(AbstractXPathModel):
	def __init__(self, tree, xpath='//Effect'):
		super().__init__(tree, xpath)
	def _decorationRole(self, el):
		pass
	def _displayRole(self, el):
		return el.effectkw.text

def main():
	import os
	app = QtGui.QApplication(os.sys.argv)
	blah=QtGui.QWidget()
	l=QtGui.QListView()
	l2=QtGui.QListView()
	l3=QtGui.QListView()
	l4=QtGui.QListView()
	l5=QtGui.QListView()
	layout=QtGui.QHBoxLayout(blah)
	layout.addWidget(l)
	layout.addWidget(l2)
	layout.addWidget(l3)
	layout.addWidget(l4)
	layout.addWidget(l5)
	
	tree=xmlobjects.objectify.parse('satanism.xml',parser=xmlobjects.parser)
	model=FaveColorModel(tree)
	model2=IngredientModel(tree)
	model3=StepModel(tree)
	model4=RecipeModel(tree)
	model5=EffectModel(tree)
	l.setModel(model)
	l2.setModel(model2)
	l3.setModel(model3)
	l4.setModel(model4)
	l5.setModel(model5)
	#blah.setItemDelegate(ListyDelegate(model))
	blah.show()
	os.sys.exit(app.exec_())

if __name__ == "__main__":
	main()

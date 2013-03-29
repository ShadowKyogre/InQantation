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
class XPathModel(QtGui.QStandardItemModel):
	def __init__(self, tree, xpath):
		super().__init__()
		self._tree=tree
		self._xpath=xpath
	def refill(self):
		self.clear()
		for el in self._tree.xpath(self._xpath):
			item=QtGui.QStandardItem()
			item.setData(el,QtCore.Qt.UserRole)
			#these need to be separated out into custom models...
			if el.tag == 'FaveColor':
				c=QtGui.QColor.fromHsvF(el.color.hue,
					el.color.saturation,
					el.color.luminosity)
				item.setData(c,QtCore.Qt.DecorationRole)
				label="{}\nEffects: {}".format(el.label.text,
				', '.join(e.effectkw.text for e in el.effects()))
				item.setData(label,QtCore.Qt.DisplayRole)
			elif el.tag == 'Ingredient':
				label="{}\nEffects: {}".format(el.label.text,
				', '.join(e.effectkw.text for e in el.effects()))
				item.setData(label,QtCore.Qt.DisplayRole)
			elif el.tag == 'Step':
				if len(el.usedColor()) > 0:
					filler="{} ({},{},{})".format(el.usedColor()[0].label.text,
								el.usedColor()[0].color.hue,
								el.usedColor()[0].color.saturation,
								el.usedColor()[0].color.luminosity)
				else:
					filler=el.usedIngredient()[0].label.text
				label="Step: {}\nNeeded: {}".format(el.details.text, filler)
				item.setData(label,QtCore.Qt.DisplayRole)
			elif el.tag == 'Recipe':
				filler=', '.join([e.label.text for e in el.usedIngredients()])
				filler2list=[]
				for e in el.usedColors():
					filler2list.append("{} ({},{},{})".format(e.label.text,
								e.color.hue,
								e.color.saturation,
								e.color.luminosity))
				filler2=', '.join(filler2list)
				label=("Recipe: {}\nNeeded Ingredients: {}"
						"\nNeeded Energy: {}").format(el.label.text, filler, filler2)
				item.setData(label,QtCore.Qt.DisplayRole)
			self.appendRow(item)

def main():
	import os
	app = QtGui.QApplication(os.sys.argv)
	blah=QtGui.QListView()
	tree=xmlobjects.objectify.parse('satanism.xml',parser=xmlobjects.parser)
	model=XPathModel(tree, '//FaveColor|//Ingredient|//Step|//Recipe')
	model.refill()
	blah.setModel(model)
	#blah.setItemDelegate(ListyDelegate(model))
	blah.show()
	os.sys.exit(app.exec_())

if __name__ == "__main__":
	main()

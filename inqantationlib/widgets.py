from PyQt4 import QtGui,QtCore
from . import xmlobjects

#http://imgur.com/a/AoNjD#1 <- WIP GUI
#http://imgur.com/lcSmcmW current WIP shots of editing widgets

class FaveColorEdit (QtGui.QWidget):
	def __init__(self, color=None):
		super().__init__()
		layout=QtGui.QHBoxLayout(self)
		layout.setMargin(0)
		layout.addWidget(QtGui.QPushButton("Color!"))
		layout.addWidget(QtGui.QPushButton("Effects"))
		layout.addWidget(QtGui.QLineEdit("I am a mighty name!"))

class IngredientEdit (QtGui.QWidget):
	def __init__(self, ing=None):
		super().__init__()
		layout=QtGui.QHBoxLayout(self)
		layout.setMargin(0)
		layout.addWidget(QtGui.QPushButton("Categories"))
		layout.addWidget(QtGui.QPushButton("Effects"))
		layout.addWidget(QtGui.QLineEdit("I am a mighty name!"))

class EffectTagger (QtGui.QWidget):
	pass

class StepEdit (QtGui.QWidget):
	#probably needs window
	def __init__(self, step=None):
		super().__init__()
		layout=QtGui.QGridLayout(self)
		layout.setMargin(0)
		self.usethis=QtGui.QComboBox()
		self.usethis.addItems(["Ingredient","Color"])
		#connect to properly handle combobox change
		layout.addWidget(self.usethis,0,0)
		layout.addWidget(QtGui.QComboBox(),0,1)
		layout.addWidget(QtGui.QPlainTextEdit("I am powerful text!"),1,0,1,2)


class RecipeEdit (QtGui.QWidget):
	#probably needs window
	def __init__(self, recipe=None):
		super().__init__()
		layout=QtGui.QGridLayout(self)
		layout.addWidget(QtGui.QLineEdit(),0,0,1,4)
		#disappear for readonly
		layout.addWidget(QtGui.QComboBox(),1,2,1,2)
		layout.addWidget(QtGui.QPushButton("Add Step"),1,1)
		layout.addWidget(QtGui.QPushButton("Remove step"),1,0)
		#
		layout.addWidget(QtGui.QListView(),2,0,1,4)
		#disappear for readonly
		layout.addWidget(QtGui.QPushButton("Move up"),3,0,1,2)
		layout.addWidget(QtGui.QPushButton("Move down"),3,2,1,2)
		#

'''
When the user is editing, there's some stuff to edit the things for the color 
or ingredient and a button that says "Effects...". Clicking that button would 
raise a dialog that shows the available affects and whether the current 
component you're editing uses these. One can then check or uncheck certain 
effects and click OK to confirm the changes.
'''

def main():
	import os
	app = QtGui.QApplication(os.sys.argv)
	blah=QtGui.QWidget()
	l=QtGui.QFormLayout(blah)
	l.addRow("RecipeEdit", RecipeEdit())
	l.addRow("StepEdit", StepEdit())
	l.addRow("FaveColorEdit", FaveColorEdit())
	l.addRow("IngredientEdit", IngredientEdit())
	blah.show()
	os.sys.exit(app.exec_())

if __name__ == "__main__":
	main()

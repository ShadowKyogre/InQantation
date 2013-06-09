from PyQt4 import QtGui,QtCore
from collections import OrderedDict as od
import os
import datetime

from . import APPNAME,APPVERSION,AUTHOR,DESCRIPTION,YEAR,PAGE,EMAIL
from . import xmlobjects, models, widgets
from .guiconfig import InQantationConfig

class InQantation(QtGui.QMainWindow):
	def __init__(self, spellbook):
		super().__init__()
		self.setWindowTitle(APPNAME)
		self.undoStack=QtGui.QUndoStack(self)

		self.tree=xmlobjects.objectify.parse(spellbook,
											parser=xmlobjects.parser)

		self.fcmodel=models.FaveColorModel(self.tree)
		self.imodel=models.IngredientModel(self.tree)
		self.smodel=models.StepModel(self.tree)
		self.rmodel=models.RecipeModel(self.tree)
		self.fxmodel=models.EffectModel(self.tree)

		exitAction = QtGui.QAction(QtGui.QIcon.fromTheme('application-exit'), 'Exit', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Exit application')
		exitAction.triggered.connect(self.close)

		openAction = QtGui.QAction(QtGui.QIcon.fromTheme('document-open'), 'Open file', self)
		openAction.setShortcut('Ctrl+O')
		openAction.setStatusTip('Open file')
		#openAction.triggered.connect(self.viewPerson)


		saveAction = QtGui.QAction(QtGui.QIcon.fromTheme('document-save'), 'Save', self)
		saveAction.setShortcut('Ctrl+S')
		saveAction.setStatusTip('Save')
		#saveAction.triggered.connect(self.saveData)

		aboutAction=QtGui.QAction(QtGui.QIcon.fromTheme('help-about'), 'About', self)
		aboutAction.triggered.connect(self.about)

		toolbar = self.addToolBar('Exit')
		toolbar.addAction(exitAction)
		toolbar.addAction(openAction)
		toolbar.addAction(saveAction)
		toolbar.addAction(aboutAction)

		self.tabs = QtGui.QTabWidget(self)
		self.setCentralWidget(self.tabs)

		self.makeEffectsTab()
		self.makeColorsTab()
		self.makeIngredientsTab()
		self.makeStepsTab()
		self.makeRecipesTab()

	### GUI SETUP ###
	def makeEffectsTab(self):
		pane=QtGui.QWidget(self)
		panel = QtGui.QGridLayout(pane)
		l = QtGui.QListView(self)
		l.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
		l.setModel(self.fxmodel)
		newb=QtGui.QPushButton('New')
		newb.clicked.connect(lambda: self.fxmodel.insertRow(self.fxmodel.rowCount()))
		newd=QtGui.QPushButton('Delete')
		newd.clicked.connect(lambda: self.delete(self.fxmodel,l))
		fxsc=QtGui.QPushButton('Colors w/this')
		fxsi=QtGui.QPushButton('Ingredients w/this')
		panel.addWidget(newb,0,0)
		panel.addWidget(newd,0,1)
		panel.addWidget(fxsc,0,2)
		panel.addWidget(fxsi,0,3)
		panel.addWidget(l,1,0,1,4)
		self.tabs.addTab(pane, "Effects")

	def makeColorsTab(self):
		pane=QtGui.QWidget(self)
		panel = QtGui.QGridLayout(pane)
		l = QtGui.QListView(self)
		l.setModel(self.fcmodel)
		l2 = QtGui.QTreeWidget(self)
		l3 = QtGui.QTreeWidget(self)
		le = QtGui.QLineEdit(self)
		panel.addWidget(QtGui.QLabel("Search by Label"),0,0,1,3)
		panel.addWidget(le,0,3,1,3)
		panel.addWidget(QtGui.QLabel("Search by Color (HSL and fuzziness)"),1,0,1,2)
		panel.addWidget(QtGui.QSpinBox(),1,2)
		panel.addWidget(QtGui.QSpinBox(),1,3)
		panel.addWidget(QtGui.QSpinBox(),1,4)
		panel.addWidget(QtGui.QSpinBox(),1,5)
		panel.addWidget(QtGui.QPushButton("New"),2,0,1,3)
		panel.addWidget(QtGui.QPushButton("Delete"),2,3,1,3)
		panel.addWidget(l,3,0,1,6)
		panel.addWidget(l2,4,0,1,3)
		panel.addWidget(l3,4,3,1,3)
		self.tabs.addTab(pane, "Energy Colors")

	def makeIngredientsTab(self):
		pane=QtGui.QWidget(self)
		panel = QtGui.QGridLayout(pane)
		l = QtGui.QListView(self)
		l.setModel(self.imodel)
		ning=QtGui.QPushButton("New")
		ding=QtGui.QPushButton("Delete")
		panel.addWidget(ning,0,0)
		panel.addWidget(ding,0,1)
		panel.addWidget(l,1,0,1,2)
		self.tabs.addTab(pane, "Ingredients")

	def makeStepsTab(self):
		pane=QtGui.QWidget(self)
		panel = QtGui.QGridLayout(pane)
		l = QtGui.QListView(self)
		l.setModel(self.smodel)
		nstep = QtGui.QPushButton("New")
		dstep = QtGui.QPushButton("Delete")
		panel.addWidget(nstep,0,0)
		panel.addWidget(dstep,0,1)
		panel.addWidget(l,1,0,1,2)
		self.tabs.addTab(pane, "Steps")

	def makeRecipesTab(self):
		pane=QtGui.QWidget(self)
		panel = QtGui.QGridLayout(pane)
		l = QtGui.QListView(self)
		l.setModel(self.rmodel)
		nrep = QtGui.QPushButton("New")
		drep = QtGui.QPushButton("Delete")
		panel.addWidget(nrep,0,0)
		panel.addWidget(drep,0,1)
		panel.addWidget(l,1,0,1,2)
		self.tabs.addTab(pane, "Recipes")

	### SIGNAL HANDLERS ###
	def delete(self, model, view):
		sel = reversed(view.selectionModel().selectedRows())
		for idx in sel:
			model.removeRow(idx.row())

	def about(self):
		QtGui.QMessageBox.about (self, "About {}".format(APPNAME),
		("<center><big><b>{0} {1}</b></big>"
		"<br />{2}<br />(C) <a href=\"mailto:{3}\">{4}</a> {5}<br />"
		"<a href=\"{6}\">{0} Homepage</a></center>")\
		.format(APPNAME,APPVERSION,DESCRIPTION,EMAIL,AUTHOR,YEAR,PAGE))

	def closeEvent(self,event):
		#print("Saving configuration...")
		#qtrcfg.save_settings()
		super().closeEvent(event)

	def saveDataAsTXT(self, filename):
		pass

	def saveDataAsIMG(self, filename, fmt):
		pass

	def saveData(self,filename=None):
		if not filename:
			filename=str(QtGui.QFileDialog.getSaveFileName(self, caption="Save Current Reading",
				filter="Images (%s);;Text (*.txt)" %(' '.join(formats))))
		if filename:
			fmt=filename.split(".",1)[-1]
			if fmt == 'txt':
				self.saveDataAsTXT(filename)
			elif "*.{}".fmt in formats:
				self.saveDataAsIMG(filename,fmt)
			else:
				QtGui.QMessageBox.critical(self, "Save Current Reading", \
				"Invalid format ({}) specified for {}!".fmt)

def main():
	global formats
	global app
	global qtrcfg

	formats=set(["*."+''.join(i).lower() for i in \
		QtGui.QImageWriter.supportedImageFormats()])

	formats=sorted(list(formats),key=str.lower)
	try:
		formats.remove('*.bw')
	except ValueError:
		pass
	try:
		formats.remove('*.rgb')
	except ValueError:
		pass
	try:
		formats.remove('*.rgba')
	except ValueError:
		pass
	app = QtGui.QApplication(os.sys.argv)

	app.setWindowIcon(QtGui.QIcon.fromTheme(APPNAME.lower()))
	app.setApplicationName(APPNAME)
	app.setApplicationVersion(APPVERSION)
	qtrcfg = InQantationConfig()

	if len(os.sys.argv[1:]) < 1 or not os.path.exists(os.sys.argv[1]):
		print("There's no spellbook to edit!", file=os.sys.stderr)
		os.sys.exit(1)
	window = InQantation (os.sys.argv[1])
	window.show()
	os.sys.exit(app.exec_())

if __name__ == "__main__":
	main()

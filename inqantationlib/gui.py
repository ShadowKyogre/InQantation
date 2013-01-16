from PyQt4 import QtGui,QtCore
from collections import OrderedDict as od
import os
import datetime

from . import APPNAME,APPVERSION,AUTHOR,DESCRIPTION,YEAR,PAGE,EMAIL
#from . import core
from .guiconfig import InQantationConfig

class InQantation(QtGui.QMainWindow):
	def __init__(self, *args, **kwargs):
		super().__init__()
		self.setWindowTitle(APPNAME)
		self.undoStack=QtGui.QUndoStack(self)

		exitAction = QtGui.QAction(QtGui.QIcon.fromTheme('application-exit'), 'Exit', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Exit application')
		exitAction.triggered.connect(self.close)

		saveAction = QtGui.QAction(QtGui.QIcon.fromTheme('document-save'), 'Save', self)
		saveAction.setShortcut('Ctrl+S')
		saveAction.setStatusTip('Save')
		saveAction.triggered.connect(self.saveData)

		aboutAction=QtGui.QAction(QtGui.QIcon.fromTheme('help-about'), 'About', self)
		aboutAction.triggered.connect(self.about)

		toolbar = self.addToolBar('Exit')
		toolbar.addAction(exitAction)
		toolbar.addAction(saveAction)
		toolbar.addAction(aboutAction)

		tabs = QtGui.QTabWidget(self)
		tabs.addTab(QtGui.QListView(self), "Energy Colors")
		tabs.addTab(QtGui.QListView(self), "Ingredients")
		tabs.addTab(QtGui.QListView(self), "Effects")
		tabs.addTab(QtGui.QListView(self), "Steps")
		tabs.addTab(QtGui.QListView(self), "Recipes")
		self.setCentralWidget(tabs)

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
	qtrcfg = InQantationConfig ()

	window = InQantation ()
	window.show()
	os.sys.exit(app.exec_())

if __name__ == "__main__":
	main()

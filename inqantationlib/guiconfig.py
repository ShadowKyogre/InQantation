from PyQt4 import QtGui,QtCore

from . import APPNAME,APPVERSION,AUTHOR,DESCRIPTION,YEAR,PAGE

class InQantationConfig:

	def __init__(self):
		self.settings=QtCore.QSettings(QtCore.QSettings.IniFormat,
						QtCore.QSettings.UserScope,
						AUTHOR,APPNAME)
		self.sys_icotheme=QtGui.QIcon.themeName()
		self.reset_settings()
	
	def reset_settings(self):
		self.current_icon_override=self.settings.value("stIconTheme", "")
		if self.current_icon_override > "":
			QtGui.QIcon.setThemeName(self.current_icon_override)
		else:
			QtGui.QIcon.setThemeName(self.sys_icotheme)

	def save_settings(self):
		self.settings.setValue("stIconTheme",self.current_icon_override)
		self.settings.sync()	


import colorsys
import sys
import re
import sqlite

HEXCODEFORMAT=re.compile(r'#?([0-9a-f]{3}|[0-9a-f]{6})',re.I)

#current errors: emphasis on might
#possible mixing of effects with white and black

def html2rgb(string):
	r=int(string[:2],16)/255
	g=int(string[2:4],16)/255
	b=int(string[4:],16)/255
	return r,g,b

class IngredientsDB:
	def __init__(self, fname):
		self.con = sqlite.connect(fname)
		cursor=self.con.cursor()
		cursor.execute(('create table Ingredients(name TEXT, category TEXT, '
						'fxid INT, id INT PRIMARY KEY) if not exists Ingredients'))
		cursor.execute('create table Effects(id INT PRIMARY KEY, body TEXT) if not exists Effects')
		cursor.execute('create table HueEffects(order INT PRIMARY KEY, fxid INT) if not exists HueEffects')
		cursor.execute('create table LumEffects(order INT PRIMARY KEY, fxid INT) if not exists LumEffects')
		cursor.execute(('create table FaveColors(hue INT, lum INT, '
						'sat INT, name TEXT, PRIMARY KEY (hue, lum, sat))'
						' if not exists FaveColors'))
	def lookupRGB(self, r, g, b):
		return self.lookupHSL(*colorsys.rgb_to_hsv(r,g,b))
	def lookupHSL(self, h, s, l):
		pass
	def byCategory(self, fx):
		pass
	def byEffects(self, fx):
		pass

class EnergyColor:
	HUEFX=["passion","creative","knowledge","healing","occult+","astral+"]
	LUMFX=["sponge","maim","protection"]
	def __init__(self, h, s, l, huefxrng=HUEFX, lumfxrng=LUMFX):
		self.hue,self.luminosity,self.saturation=h,s,l
		self.lumfxrng=lumfxrng
		self.huefxrng=huefxrng
	@property
	def huefxpositive(self):
		#Whether the effect of the energy due to its hue is beneficial
		if self.saturation >= 1E-3:
			return self.luminosity>=0.5
	@property
	def purity(self):
		#How much of the energy's effect is due to the hue
		return self.saturation if self.saturation >= 1E-3 else 1.0
	@property
	def luminosityfx(self):
		#Energy's effect due to its luminosity
		if self.saturation < 1:
			idx=int(len(self.lumfxrng)*self.luminosity)
			fx2=self.lumfxrng[idx]
		else:
			fx2=None
		return fx2
	@property
	def huefx(self):
		#Energy's effect due to its hue
		if self.saturation <= 1E-3:
			return None
		idx=len(self.huefxrng)*self.hue
		intifiedidx=int(idx)
		if idx>intifiedidx:
			fx=(self.huefxrng[intifiedidx],self.huefxrng[(intifiedidx+1)%len(self.huefxrng)])
		else:
			fx=self.huefxrng[intifiedidx]
		return fx
	@classmethod
	def fromRGB(cls, r, g, b, huefxrng=HUEFX, lumfxrng=LUMFX):
		return cls(*colorsys.rgb_to_hsv(r,g,b), huefxrng, lumfxrng)
	@classmethod
	def fromHex(cls, hexcode, huefxrng=HUEFX, lumfxrng=LUMFX):
		#Create an energy color from a hex code (the leading # is optional)
		hexcode=HEXCODEFORMAT.findall(hexcode)[0]
		if len(hexcode) == 3:
			 return cls.fromRGB(*html2rgb("{0}{0}{1}{1}{2}{2}".format(*hexcode)), huefxrng=huefxrng, lumfxrng=lumfxrng)
		else:
			return cls.fromRGB(*html2rgb(hexcode), huefxrng=huefxrng, lumfxrng=lumfxrng)
	@classmethod
	def fromCSSName(cls, cssname, huefxrng=HUEFX, lumfxrng=LUMFX):
		#Create an energy color from a css color name (note: requires webcolors module)
		try:
			import webcolors
			return cls.fromHex(webcolors.name_to_hex(cssname), huefxrng=huefxrng, lumfxrng=lumfxrng)
		except ImportError as e:
			raise ValueError(('Unable to find web colors, making an energy'
				' color from {!r} is not possible'.format(cssname)),file=sys.stderr)

if __name__ == "__main__":
	for i in sys.argv[1:]:
		if HEXCODEFORMAT.match(i) is not None:
			e=EnergyColor.fromHex(i)
		else:
			try:
				e=EnergyColor.fromCSSName(i)
			except ValueError as e:
				print(e.message)
				continue
		print('Color name:',i)
		print('Energy from hue positive?:',e.huefxpositive)
		print('Energy effect due to hue:',e.huefx)
		print('Energy effect due to luminosity:',e.luminosityfx)
		print('Presence of energy effect: {:.2f}'.format(e.purity*100))

from lxml import etree,objectify


class Spellbook(objectify.ObjectifiedElement):
	def usedColors(self, rpid):
		#//FaveColor
		pass
	def usedIngredients(self, rpid):
		#//Ingredient
		pass
	def effectSummary(self, rpid):
		#self.usedIngredients+self.usedColors
		pass
	def inRecipes(self, stid):
		#//Recipes[step/@stid={}]
		pass

class ColorDB(objectify.ObjectifiedElement):
	def lookupRGB(self, r, g, b):
		return self.lookupHSL(*colorsys.rgb_to_hsv(r,g,b))
	def lookupHSL(self, h, s, l):
		pass
	def byLabel(self, label, regex=False):
		#//FaveColor[label[starts-with(text(),{})]]
		#//FaveColor[label[text()={}]]
		pass
	def byEffects(self, fx):
		#//Ingredients[effect[@fxid={}]]
		pass

class IngredientsDB(objectify.ObjectifiedElement):
	def byLabel(self, label, regex=False):
		#//Ingredient[label[starts-with(text(),{})]]
		#//Ingredient[label[text()={}]]
		pass
	def byCategory(self, category, exact=False):
		#//Ingredient[category[starts-with(text(),{})]]
		#//Ingredient[category[text()={}]]
		pass
	def byEffects(self, fx):
		#//Ingredients[effect[@fxid={}]]
		pass

class Ingredient(objectify.ObjectifiedElement):
	@property
	def effects(self):
		# <- selects effects for an ingredient
		return self.xpath('//Effect[@fxid=//Ingredient[@igid=./@igid]/effect/@fxid]')

class EnergyColor(objectify.ObjectifiedElement):
	#'//Step[uses[color=./color]]' <- selects steps the color is in
	#'//Step[uses[ingredient[@igid=./@igid]]]' <- selects steps the ingredient is in
	@property
	def huefxrange(self):
		return self.xpath('//Effect[@fxid = //HueEffect/@fxid]')
	@property
	def lumfxrange(self):
		return self.xpath('//Effect[@fxid = //LuminosityEffect/@fxid]')
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
	@property
	def effects(self):
		if not self.attrib['noCalculate']:
			return self.huefx+self.luminosityfx
		else:
			return self.xpath('//Effect[@fxid = //FaveColor[color=./color]/effect/@fxid]')

lookup = etree.ElementNamespaceClassLookup(objectify.ObjectifyElementClassLookup())
parser = etree.XMLParser(remove_blank_text=True)
parser.set_element_class_lookup(lookup)

namespace = lookup.get_namespace('')
namespace['Spellbook']=Spellbook
#namespace['FaveColor']=FaveColor

# ~~~ Shalalalala ~~~

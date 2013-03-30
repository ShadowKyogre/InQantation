from lxml import etree,objectify


class Recipe(objectify.ObjectifiedElement):
	def usedColors(self):
		#//FaveColor[color=./color] <- for each step
		r=[]
		for i in self.xpath('//Step[@stid=//Recipe[@rpid={}]/step/@stid and color]'.format(self.attrib['rpid'])):
			r.append(i.usedColor()[0])
		#return self.xpath('//FaveColor[color=//Step[contains(@stid,./step/@stid)]/color]')
		return r
	def usedIngredients(self):
		#//Ingredient[@igid=//Step[@stid=./@stid]/ingredient/@igid] <- for each ingredient
		return self.xpath(('//Ingredient[@igid=//Step[@stid='
						'//Recipe[@rpid={}]/step/@stid]'
						'/ingredient/@igid]').format(self.attrib['rpid']))
	'''
	def effectSummary(self):
		#self.usedIngredients+self.usedColors
		pass
	'''

'''
class ColorDB:
	def lookupRGB(self, r, g, b):
		return self.lookupHSL(*colorsys.rgb_to_hsv(r,g,b))
	def lookupHSL(self, h, s, l):
		pass
	def byLabel(self, label, regex=False):
		#//FaveColor[label[starts-with(text(),{})]]
		#//FaveColor[label[text()={}]]
		pass

class IngredientsDB:
	def byLabel(self, label, regex=False):
		#//Ingredient[label[starts-with(text(),{})]]
		#//Ingredient[label[text()={}]]
		pass
	def byCategory(self, category, exact=False):
		#//Ingredient[category[starts-with(text(),{})]]
		#//Ingredient[category[text()={}]]
		pass
'''

class Step(objectify.ObjectifiedElement):
	def inRecipes(self):
		return self.xpath('//Recipe[step[@stid={}]]'.format(self.attrib['stid']))
	def usedIngredient(self):
		if not hasattr(self,'ingredient'):
			return []
		return self.xpath('//Ingredient[@igid={}]'.format(self.ingredient.attrib['igid']))
	def usedColor(self):
		#:I still doesn't work like expected
		if not hasattr(self,'color'):
			return []
		c="hue={} and saturation={} and luminosity={}"\
			.format(self.color.hue,self.color.saturation,self.color.luminosity)
		return self.xpath('//FaveColor[color[{}]]'.format(c))

class Effect(objectify.ObjectifiedElement):
	def colorsWithThis(self, onlyNoCalc=False):
		if onlyNoCalc:
			colors=self.xpath('//FaveColor[@noCalculate="true"'
						' and effect[@fxid={}]]'.format(self.attrib['fxid']))
			return colors
		else:
			colors=self.xpath('//FaveColor')
			#we need to do this because we can't autostore
			#the effects for things that have noCalculate!
			return [c for c in colors if self in c.effects]
	def ingredientsWithThis(self):
		return self.xpath('//Ingredient[effect[@fxid=./@fxid]]')

class Ingredient(objectify.ObjectifiedElement):
	def effects(self):
		# <- selects effects for an ingredient
		return self.xpath('//Effect[@fxid=//Ingredient[@igid={}]/effect/@fxid]'.format(self.attrib['igid']))
	def inSteps(self):
		# selects steps the ingredient is in
		return self.xpath('//Step[ingredient[@igid=./@igid]]')

class FaveColor(objectify.ObjectifiedElement):
	def huefxrng(self):
		return self.xpath('//Effect[@fxid = //HueEffect/@fxid]')
	def lumfxrng(self):
		return self.xpath('//Effect[@fxid = //LuminosityEffect/@fxid]')
	def huefxpositive(self):
		#Whether the effect of the energy due to its hue is beneficial
		if self.saturation >= 1E-3:
			return self.luminosity>=0.5
	def purity(self):
		#How much of the energy's effect is due to the hue
		return self.saturation if self.saturation >= 1E-3 else 1.0
	def luminosityfx(self):
		#Energy's effect due to its luminosity
		if self.color.saturation < 1:
			idx=int(len(self.lumfxrng())*self.color.luminosity)-1
			fx2=[self.lumfxrng()[idx]]
		else:
			fx2=[]
		return fx2
	def huefx(self):
		#Energy's effect due to its hue
		if self.color.saturation <= 1E-3:
			return []
		idx=len(self.huefxrng())*self.color.hue
		intifiedidx=int(idx)
		if idx>intifiedidx:
			fx=[self.huefxrng()[intifiedidx],self.huefxrng()[(intifiedidx+1)%len(self.huefxrng())]]
		else:
			fx=[self.huefxrng()[intifiedidx]]
		return fx
	def inSteps(self):
		#selects steps the color is in
		c="hue={} and saturation={} and luminosity={}"\
			.format(self.color.hue,self.color.saturation,self.color.luminosity)
		return self.xpath('//Step[color[{}]]'.format(c))

	def effects(self):
		if 'noCalculate' not in self.attrib or not self.attrib['noCalculate']:
			return self.huefx()+self.luminosityfx()
		else:
			c="hue={} and saturation={} and luminosity={}"\
			.format(self.color.hue,self.color.saturation,self.color.luminosity)
			return self.xpath('//Effect[@fxid = //FaveColor[color[{}]]/effect/@fxid]'.format(c))

class Encyclopedia(objectify.ObjectifiedElement):
	def remove(self, el):
		if el.tag == 'Step':
			#remove all mentions from it from existing recipes
			for r in el.inRecipes():
				for s in r.xpath('./step[@stid={}]'.format(el.attrib['stid']):
					r.remove(s)
		elif el.tag in ('FaveColor','Ingredient'):
			#remove all steps that this is mentioned in
			for s in el.inSteps():
				self.remove(s)
		elif el.tag == 'Effect':
			#remove all mentions of this effect in hue effect
			for he in el.xpath('//HueEffect[@fxid={}]'.format(el.attrib['fxid'])):
				self.remove(he)

			#remove all mentions of this effect in luminosity effect
			for he in el.xpath('//LuminosityEffect[@fxid={}]'.format(el.attrib['fxid'])):
				self.remove(he)

			#remove all mentions of this effect in colors that aren't calculated
			for c in el.colorsWithThis(True):
				for e in c.xpath('./effect[@fxid={}]'.format(el.attrib['fxid'])):
					c.remove(e)

			#remove all mentions of this effect in ingredients
			for i in el.ingredientsWithThis():
				for e in c.xpath('./effect[@fxid={}]'.format(el.attrib['fxid'])):
					i.remove(e)

		#now that we're done cleaning up dependencies, remove this for good
		super().remove(el)

lookup = etree.ElementNamespaceClassLookup(objectify.ObjectifyElementClassLookup())
parser = etree.XMLParser(remove_blank_text=True)
parser.set_element_class_lookup(lookup)

namespace = lookup.get_namespace('')
namespace['Encyclopedia']=Encyclopedia
namespace['FaveColor']=FaveColor
namespace['Ingredient']=Ingredient
namespace['Effect']=Effect
namespace['Recipe']=Recipe
namespace['Step']=Step

# ~~~ Shalalalala ~~~

from lxml import etree,objectify
from copy import deepcopy

### Constants ###
#### XPath expressions for sections of book ###
ALLCOLS=etree.XPath('//FaveColor')
ALLINGS=etree.XPath('//Ingredient')
ALLREPS=etree.XPath('//Recipe')
ALLSTPS=etree.XPath('//Step')
ALLFXS=etree.XPath('//Effect')

#### Ones used by multiple classes ####
COLSEARCH=etree.XPath('//FaveColor[color[hue=$h and saturation=$s and value=$v]]')

#### Useful for generating new element IDs ####
#http://stackoverflow.com/questions/3786443/xpath-to-get-the-element-with-the-highest-id
LASTFXID=etree.XPath('//Effect[not(../Effect/@fxid>@fxid)]/@fxid')
LASTRPID=etree.XPath('//Recipe[not(../Recipe/@rpid>@rpid)]/@rpid')
LASTSTID=etree.XPath('//Step[not(../Step/@stid>@stid)]/@stid')
LASTIGID=etree.XPath('//Ingredient[not(../Ingredient/@igid>@igid)]/@igid')
#note on how to swap positions in parent:
'''
el.getparent().remove(el)
i=el2.getparent().index(el2)
if after: i+=1
el2.getparent().insert(i, el)
'''

### Classes ###

class Recipe(objectify.ObjectifiedElement):
	UCOLS=etree.XPath('//Step[@stid=//Recipe[@rpid=$r]/step/@stid and color]')
	UINGS=etree.XPath('//Ingredient[@igid=//Step[@stid='
					'//Recipe[@rpid=$r]/step/@stid]/ingredient/@igid]')
	STEPREFS=etree.XPath('./step')
	def usedColors(self):
		#//FaveColor[color=./color] <- for each step
		r=[]
		for i in self.UCOLS(self,r=self.attrib['rpid']):
			r.append(i.usedColor()[0])
		#return self.xpath('//FaveColor[color=//Step[contains(@stid,./step/@stid)]/color]')
		return r
	def usedIngredients(self):
		#//Ingredient[@igid=//Step[@stid=./@stid]/ingredient/@igid] <- for each ingredient
		return self.UINGS(self,r=self.attrib['rpid'])
	'''
	def effectSummary(self):
		#self.usedIngredients+self.usedColors
		pass
	'''

class Step(objectify.ObjectifiedElement):
	INREPS=etree.XPath('//Recipe[step[@stid=$s]]')
	HASINGS=etree.XPath('//Ingredient[@igid=$i]')
	def inRecipes(self):
		return self.INREPS(self,s=self.attrib['stid'])
	def usedIngredient(self):
		if not hasattr(self,'ingredient'):
			return []
		return self.HASINGS(self,i=self.ingredient.attrib['igid'])
	def usedColor(self):
		if not hasattr(self,'color'):
			return []
		return COLSEARCH(self, h=self.color.hue,
						s=self.color.saturation, v=self.color.value)

class Effect(objectify.ObjectifiedElement):
	INCOLSNC=etree.XPath('//FaveColor[@noCalculate="true" and effect[@fxid=$f]]')
	ININGS=etree.XPath('//Ingredient[effect[@fxid=./@fxid]]')
	def colorsWithThis(self, onlyNoCalc=False):
		if onlyNoCalc:
			colors=self.INCOLSNC(self,f=self.attrib['fxid'])
			return colors
		else:
			colors=self.xpath('//FaveColor')
			#we need to do this because we can't autostore
			#the effects for things that have noCalculate!
			return [c for c in colors if self in c.effects]
	def ingredientsWithThis(self):
		return self.ININGS(self)

class Ingredient(objectify.ObjectifiedElement):
	IHASFX=etree.XPath('//Effect[@fxid=//Ingredient[@igid=$i]/effect/@fxid]')
	IINSTEPS=etree.XPath('//Step[ingredient[@igid=./@igid]]')
	def effects(self):
		# <- selects effects for an ingredient
		return self.IHASFX(self,i=self.attrib['igid'])
	def inSteps(self):
		# selects steps the ingredient is in
		return self.IINSTEPS(self)

class FaveColor(objectify.ObjectifiedElement):
	HFXRNG=etree.XPath('//Effect[@fxid = //HueEffect/@fxid]')
	LFXRNG=etree.XPath('//Effect[@fxid = //ValueEffect/@fxid]')
	CINSTEPS=etree.XPath('//Step[color[hue=$h and saturation=$s and value=$v]]')
	CNCHASFX=etree.XPath('//Effect[@fxid = //FaveColor[color[hue=$h and'
						' saturation=$s and value=$v]]/effect/@fxid]')
	def huefxrng(self):
		return self.HFXRNG(self)
	def lumfxrng(self):
		return self.LFXRNG(self)
	def huefxpositive(self):
		#Whether the effect of the energy due to its hue is beneficial
		if self.saturation >= 1E-3:
			return self.value>=0.5
	def purity(self):
		#How much of the energy's effect is due to the hue
		return self.saturation if self.saturation >= 1E-3 else 1.0
	def valuefx(self):
		#Energy's effect due to its value
		if self.color.saturation < 1:
			idx=int(len(self.lumfxrng())*self.color.value)-1
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
		return self.CINSTEPS(self,h=self.color.hue,
						s=self.color.saturation,v=self.color.value)

	def effects(self, nocalc=False):
		if not nocalc or self.attrib.get('noCalculate') in ('1','true'):
			return self.huefx()+self.valuefx()
		else:
			return self.CNCHASFX(self,h=self.color.hue,
						s=self.color.saturation,v=self.color.value)

class Encyclopedia(objectify.ObjectifiedElement):
	def newEffect(self):
		id=str(int(LASTFXID(self)[0])+1)
		return Effect(etree.Element('effectkw'), attrib={'fxid':id})
	def newStep(self, uses=None):
		id=str(int(LASTSTID(self)[0])+1)
		s = Step(details='', attrib={'stid':id})
		if uses is not None:
			if uses.tag == 'FaveColor':
				c=deepcopy(uses.color)
				s.append(c)
			elif uses.tag == 'Ingredient':
				i=parser.makeelement('ingredient')
				i.attrib['igid']=deepcopy(uses.attrib['igid'])
				s.append(i)
		return s
	def newRecipe(self, steps=[]):
		#we expect a list of Steps here if wanted
		id=str(int(LASTRPID(self)[0])+1)
		r=Recipe(label='', attrib={'rpid':id})
		for step in steps:
			s=parser.makeelement('step')
			if isinstance(step,Step):
				s.attrib['stid']=deepcopy(step.attrib['stid'])
			elif isinstance(step,int) or isinstance(step,str):
				s.attrib['stid']=step
			else:
				raise ValueError("The list provided contains something that isn't an int, str, or Step!")
			r.append(s)
		return r
	def newIngredient(self, effects=[], categories=[]):
		#we expect a list of Effects or fxids
		#or a list of strings or categories elements
		id=str(int(LASTIGID(self)[0])+1)
		i=Ingredient(label='')
		for category in categories:
			if isinstance(category, str):
				cat=parser.makeelement('category')
				cat.text=category
			elif isinstance(category, objectify.ObjectifiedElement):
				cat=category
			else:
				raise ValueError("The list provided contains something that isn't a str or category!")
			i.append(cat)
		for effect in effects:
			fx=parser.makeelement('effect')
			if isinstance(effect, int):
				fx.attrib['fxid']=effect
			elif isinstance(effect, Effect):
				fx.attrib['fxid']=deepcopy(effect.attrib['fxid'])
			else:
				raise ValueError("The list provided contains something that isn't an int or Effect!")
		
	def ingByLabel(self, label, regex=False):
		#//Ingredient[label[starts-with(text(),{})]]
		#//Ingredient[label[text()={}]]
		pass
	def ingByCategory(self, category, exact=False):
		#//Ingredient[category[starts-with(text(),{})]]
		#//Ingredient[category[text()={}]]
		pass
	def colorByRGB(self, r, g, b):
		return self.lookupHSL(*colorsys.rgb_to_hsv(r,g,b))
	def colorByHSL(self, h, s, v):
		return COLSEARCH(self,h=h,s=s,v=v)
	def colorByLabel(self, label, regex=False):
		#//FaveColor[label[starts-with(text(),{})]]
		#//FaveColor[label[text()={}]]
		pass
	def remove(self, el):
		if el.tag == 'Step':
			#remove all mentions from it from existing recipes
			for r in el.inRecipes():
				for s in r.xpath('./step[@stid={}]'.format(el.attrib['stid'])):
					r.remove(s)
		elif el.tag in ('FaveColor','Ingredient'):
			#remove all steps that this is mentioned in
			for s in el.inSteps():
				self.remove(s)
		elif el.tag == 'Effect':
			#remove all mentions of this effect in hue effect
			for he in el.xpath('//HueEffect[@fxid={}]'.format(el.attrib['fxid'])):
				self.remove(he)

			#remove all mentions of this effect in value effect
			for le in el.xpath('//ValueEffect[@fxid={}]'.format(el.attrib['fxid'])):
				self.remove(le)

			#remove all mentions of this effect in colors that aren't calculated
			for c in el.colorsWithThis(True):
				for e in c.xpath('./effect[@fxid={}]'.format(el.attrib['fxid'])):
					c.remove(e)

			#remove all mentions of this effect in ingredients
			for i in el.ingredientsWithThis():
				for e in i.xpath('./effect[@fxid={}]'.format(el.attrib['fxid'])):
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

#note: etree.tostring(el, pretty_print=True, encoding='unicode')

# ~~~ Shalalalala ~~~

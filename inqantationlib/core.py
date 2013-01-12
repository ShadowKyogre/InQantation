import colorsys
import sys

FX=["passion","creative","knowledge","healing","occult+","astral+"]
FX2=["protection","maim","sponge"]

#current errors: emphasis on might
#possible mixing of effects with white and black

def get_effects(hue,saturation,luminosity):
	print(hue,saturation,luminosity)
	positive=(luminosity>=0.5)
	purity=saturation if saturation >= 1E-3 else 1.0
	idx=len(FX)*hue
	intifiedidx=int(idx)
	if idx>intifiedidx:
		fx=(FX[intifiedidx],FX[(intifiedidx+1)%len(FX)])
	else:
		fx=FX[intifiedidx]

	if saturation < 1:
		if luminosity >= 0.5:
			if saturation == 1:
				idx=2
			else:
				idx=1
		else:
			if saturation == 0:
				idx=0
			else:
				idx=1
		fx2=FX2[idx]
	else:
		fx2=None
	return purity,fx,fx2

def html2rgb(string):
	print(string[:2],string[2:4],string[4:])
	r=int(string[:2],16)/255
	g=int(string[2:4],16)/255
	b=int(string[4:],16)/255
	print(r,g,b)
	return r,g,b

for i in sys.argv[1:]:
	print(get_effects(*colorsys.rgb_to_hsv(*html2rgb(i))))

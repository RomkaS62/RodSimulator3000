import time

STEP = 1.0 / 60.0
AVOGADRO_NUMBER = 6.02214e23

class Simulation:

	def __init__(self):
		self.objects = list()

	def addObject(self, obj):
		self.objects.append(obj)

	# delta taken to be a step in seconds
	def tick(self, delta):
		for obj in self.objects:
			obj.tick(delta)

	def run(self):
		now = time.time()
		prev = now

		while True:
			delta= now - prev
			self.tick(delta)
			if delta < STEP:
				time.sleep(STEP - delta)
			prev = now
			now = time.time()

class HeatSource:

	# power in watts
	def __init__(self, power):
		self.power = power
		self.on = False

	def setTarget(self, obj):
		self.target = obj

	def setPower(self, power):
		self.power = power

	def turnOn(self):
		self.on = True

	def turnOff(self):
		self.on = False

	def tick(self, delta):
		if self.target == None or not self.on:
			pass
		self.target.modifyHeat(delta * self.power)

class Rod:

	# length and diameter are metres. Specified at normal temperature and
	# pressure.
	def __init__(self, material, length, diameter):
		self.STPLength = length
		self.STPDiameter = diameter
		self.mass = length * diameter * material.density
		self.material = material
		self.heat = 0.0
		self.lastPrint = time.time()
		self.setTemperature(273 + 20)
		self.printed = False

	def volume(self):
		return self.STPVolume() * self.volumeExpansion()

	def length(self):
		return self.STPLength * self.volumeExpansion()

	def diameter(self):
		return self.STPDiameter * self.volumeExpansion()

	def expansionTemperature(self):
		return self.temperature() - 273.0 - 20.0

	def volumeExpansion(self):
		return 1.0 + (self.material.expansionCoefficient * 3.0 * self.expansionTemperature())

	# An approximation. A full calculation involves an integral.
	def linearExpansion(self):
		return 1.0 + self.volumeExpansion() * self.expansionTemperature()

	def STPVolume(self):
		return self.length() * (self.diameter() / 2.0) ** 2

	def setTemperature(self, kelvin):
		self.heat = self.material.specificHeat * kelvin * self.mass

	def temperature(self):
		return self.heat / self.material.specificHeat / self.mass

	def modifyHeat(self, heatDelta):
		self.heat += heatDelta

	def tick(self, delta):
		now = time.time()
		elapsed = now - self.lastPrint
		lengthExpansion = self.length() - self.STPLength
		diameterExpansion = self.diameter() - self.STPDiameter
		if not self.printed:
			header = "| {0:16s} | {1:20s} | {2:20s} | {3:20s} | {4:20s} |"		\
					.format("Heat", "Length expansion", "Diameter expansion",	\
							"Temperature", "Time elapsed")
			print(header)
			print('-' * len(header))
			self.printed = True
		if elapsed >= 1.0:
			print(f"| {self.heat:16f} | {lengthExpansion:20f} | {diameterExpansion:20f} | {self.temperature() - 273.0:20f} | {elapsed:20f} |")
			self.lastPrint += 1.0


class Material:

	# density:					kg/m^3
	#
	# specificHeat:				J/(kg * C)
	#							Joules of heat it takes to raise temperature of
	#							1kg of material by 1K.
	#
	# expansion coefficient:	K^(-1)
	#							Factor by which volume changes for every degree
	#							of temperature gained.
	def __init__(self, density, specificHeat, expansionCoefficient):
		self.density = density
		self.specificHeat = specificHeat
		self.expansionCoefficient = expansionCoefficient

def molarToMassHeatCapacity(molarCapacity, molarMass):
	return molarCapacity / molarMass

simulator = Simulation()
h = molarToMassHeatCapacity(25.1, 0.055845)
print(f"Heat capacity: {h:f} J/(kg * C)")
iron = Material(7.874, h, 11.8e-6)
rod = Rod(iron, 1, 0.05)
heater = HeatSource(100)
heater.setTarget(rod)
simulator.addObject(heater)
simulator.addObject(rod)
simulator.run()
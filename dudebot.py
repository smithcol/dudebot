#! /usr/bin/env python3
import discord
from discord.ext import commands
import os
import requests
import json
import random
import asyncio
import RPi.GPIO as GPIO
import morse
from camcontrol import get_image
from states import get_param, set_param
import distributed
#from servotest import turn_servo


async def main():
	print('Starting up DudeBot...')

	#list of trigger words for dudebot to auto respond to
	opinions = [
		"opinion",
		"think",
		"assessment",
		"assumption",
		"attitude",
		"conclusion",
		"feeling",
		"idea",
		"impression",
		"judgement",
		"mind",
		"notion",
		"pov",
		"POV",
		"reaction",
		"sentiment",
		"speculate",
		"speculation",
		"theory",
		"thought",
		"view",
		"viewpoint"
	]

	big = [
		"big",
		"large",
		"huge",
		"ginormous",
		"colossal",
		"considerable",
		"enormous",
		"fat",
		"full",
		"gigantic",
		"hefty",
		"immense",
		"massive",
		"sizable",
		"substantial",
		"tremendous",
		"vast",
		"obese",
		"lorge",
		"rotund",
		"gargantuan"
	]

	#sets up pins for RGB LED light
	RED_PIN = 17
	GREEN_PIN = 27
	BLUE_PIN = 22

	#pin for arm servo signals
	#arm servos are numbered, 1 for manipulator to 6 for base
	SERVO1_PIN = 14
	SERVO2_PIN = 15
	SERVO3_PIN = 18
	SERVO4_PIN = 23
	SERVO5_PIN = 24
	SERVO6_PIN = 25

	#if the servo receives a duty cycle of 0, it holds position
	SERVO_DO_NOTHING_DUTY = 0

	#uses broadcom pin names instead of board names
	GPIO.setmode(GPIO.BCM)

	#turns off warnings and clears all previous GPIO states
	GPIO.setwarnings(False)
	GPIO.cleanup()

	#establishes pins as output
	GPIO.setup(RED_PIN, GPIO.OUT)
	GPIO.setup(GREEN_PIN, GPIO.OUT)
	GPIO.setup(BLUE_PIN, GPIO.OUT)

	#sets the servo signal pin as an output
	GPIO.setup(SERVO1_PIN, GPIO.OUT)
	GPIO.setup(SERVO2_PIN, GPIO.OUT)
	GPIO.setup(SERVO3_PIN, GPIO.OUT)
	GPIO.setup(SERVO4_PIN, GPIO.OUT)
	GPIO.setup(SERVO5_PIN, GPIO.OUT)
	GPIO.setup(SERVO6_PIN, GPIO.OUT)

	#sets LED PWM cycles at 50Hz starting at 0% duty cycle
	redpwm = GPIO.PWM(RED_PIN, 50)
	redpwm.start(0)

	greenpwm = GPIO.PWM(GREEN_PIN, 50)
	greenpwm.start(0)

	bluepwm = GPIO.PWM(BLUE_PIN, 50)
	bluepwm.start(0)

	#sets all servo PWMS to 50Hz starting at 0% duty cycle
	servo1 = GPIO.PWM(SERVO1_PIN, 50)
	servo1.start(0)

	servo2 = GPIO.PWM(SERVO2_PIN, 50)
	servo2.start(0)

	servo3 = GPIO.PWM(SERVO3_PIN, 50)
	servo3.start(0)

	servo4 = GPIO.PWM(SERVO4_PIN, 50)
	servo4.start(0)

	servo5 = GPIO.PWM(SERVO5_PIN, 50)
	servo5.start(0)

	servo6 = GPIO.PWM(SERVO6_PIN, 50)
	servo6.start(0)

	servolist = [servo1, servo2, servo3, servo4, servo5, servo6]

	BIGDANCE_PATH = '/home/pi/dudebot/media/big-dance.gif'
	MONKEYTYPE_PATH = '/home/pi/dudebot/media/monkey type.jpg'

	intents = discord.Intents.all()
	client = commands.Bot(command_prefix='.', intents=intents)

	await client.add_cog(distributed.Node(client, callerid='dudebot'))

	#uses the zenquotes api to receive a quote and the author
	def get_quote():
		response = requests.get("https://zenquotes.io/api/random")
		json_data = json.loads(response.text)
		quote = json_data[0]['q'] + " -" + json_data[0]['a']
		return(quote)

	#takes an array of ints and checks if input for RGB values are within compliance
	def check_values(values):
		check = True

		#iterates over each value and checks if they're within 0 and 255
		for num in range(len(values)):
			if values[num] < 0 or values[num] > 255:
				check = False
		
		return(check)

	#takes an array of ints and updates the PWM duty cycles to change RGB LED
	def set_colors(values):
		#grabs the color values from their respective index
		redval = values[0]
		greenval = values[1]
		blueval = values[2]

		#converts the color value to a percentage duty cycle
		redcol = (redval / 255) * 100
		greencol = (greenval / 255) * 100
		bluecol = (blueval / 255) * 100

		#updates the PWM duty cycle for each LED color pin
		redpwm.ChangeDutyCycle(redcol)
		greenpwm.ChangeDutyCycle(greencol)
		bluepwm.ChangeDutyCycle(bluecol)

	#generates a random color for the RGB LED if user doesn't specify values
	def rand_rgb():
		red = random.randint(0, 255)
		green = random.randint(0, 255)
		blue = random.randint(0, 255)

		colors = [red, green, blue]
		set_colors(colors)

		return colors

	#prints to the terminal when dudebot is ready for operation
	@client.event
	async def on_ready():
		print('Logged in as {0.user}'.format(client))

	#sends a quote from zenquotes	
	@client.command(help="sends a quote from zenquotes")
	async def wisdom(ctx):
		quote = get_quote()
		await ctx.send(quote)

	#controls an RGB light using PWM signals
	@client.command(help="controls an RGB LED - input values from 0 to 255 in format R G B," + 
		" leave blank for random, or type off to turn LED off")
	async def rgb(ctx, *split_values):
		#if user doesn't provide input, generate random color
		if len(split_values) == 0:
			rand_color = rand_rgb()
			await ctx.send('Generating random color of - red: ' + str(rand_color[0]) + 
				' / green: ' + str(rand_color[1]) + ' / blue: ' + str(rand_color[2]))
			await picture(ctx)
			return

		#sets the PWM duty cycles to 0 to turn the LED off when commanded
		if len(split_values) == 1:
			if split_values[0] == 'off':
				off = [0, 0, 0]
				set_colors(off)
				await ctx.send('Turning RGB LED off')
				return

		#checks if the user entered more or less than 3 inputs
		if len(split_values) != 3:
			await ctx.send('Please enter the correct number of values')
			return

		#attempts to pull integers from the input and verify they're actually integers
		try:
			colors = [int(split_values[0]), int(split_values[1]), int(split_values[2])]
		except:
			await ctx.send('Please enter valid values')
			return

		#sets the PWM values for the LED if the values are within compliance
		if check_values(colors):
			set_colors(colors)
			await ctx.send('Setting color to - red: ' + str(colors[0]) + 
				' / green: ' + str(colors[1]) + ' / blue: ' + str(colors[2]))
			await picture(ctx)
		else:
			await ctx.send('Please enter valid values')

	#captures an image from the raspberry pi camera and sends it to discord
	@client.command(help="captures an image from the raspberry pi camera")
	async def picture(ctx):
		#function taken from camcontrol
		fp = get_image()
		await ctx.send(file = discord.File(fp))

	#verifies the angle input is valid and maps it to the correct duty cycle range
	def angle_to_duty(angle):
		if angle >= 0 and angle <= 180:
			angle /= 180
			angle *= 10
			angle += 2
			return angle
		return None

	#if the angle input is valid, set the duty cycle to the angle position
	async def set_servo_angle_and_wait(servo, angle, wait_secs=0.1):
		duty = angle_to_duty(angle)

		if angle is None:
			return

		servo.ChangeDutyCycle(duty)
		print(duty)

		#allows the servo to move to the position
		await asyncio.sleep(wait_secs)

		servo.ChangeDutyCycle(SERVO_DO_NOTHING_DUTY) # do nothing

	#turns servo on predetermined route
	async def turn_servo(ctx):
		await ctx.send("Waiting for 2 seconds")
		await asyncio.sleep(2)

		duty = 2

		while duty <= 12:
			servo1.ChangeDutyCycle(duty)
			await asyncio.sleep(1)
			servo1.ChangeDutyCycle(0)
			await asyncio.sleep(1)
			duty += 1

		await ctx.send("Turning back to 90 degrees for 2 seconds")
		servo1.ChangeDutyCycle(7)
		await asyncio.sleep(2)

		await ctx.send("Turning back to 0 degrees")
		servo1.ChangeDutyCycle(2)
		await asyncio.sleep(0.5)
		servo1.ChangeDutyCycle(0)

	#turns servo through a sweep of predetermined angles
	async def turn_servo_two(step_size): # removed context for distributed usage

		for angle in range(90, 180, step_size):
			#rapidly sending messages aka angle readings stalls the program via discord timeouts lol
			#await ctx.send(f"{angle} degrees.")
			await set_servo_angle_and_wait(servo1, angle)
			await asyncio.sleep(0.1)

		await set_servo_angle_and_wait(servo1, 90, 1)

	#the actual discord command to move the servo
	@client.command(help="moves an attached servo over a predefined range of angles")
	async def moveservo(ctx):
		await ctx.send('Turning servo')
		await turn_servo_two(3)
		await ctx.send('Done')

	#moves the robotic arm
	@client.command(help="moves the robotic arm, put in form servo angle")
	async def arm(ctx, *arg):
		#checks for inputs about status and turning on the robotic arm
		#will be fully implemented later
		if len(arg) == 1:
			if arg[0] == "status":
				await ctx.send('Arm status: off')
			elif arg[0] == "on":
				await ctx.send('Temporarily unavailable')
			elif arg[0] == "off":
				for num in range(6):
					servolist[num].ChangeDutyCycle(SERVO_DO_NOTHING_DUTY)
				await ctx.send('Arm status: off')
			return

		#continues if the input is even, or there are adequate servo and angle pairs
		if len(arg) % 2 == 1:
			await ctx.send('Please enter the correct number of parameters')
			return

		stack = iter(arg)

		#iterates through input and checks that each command entered is 
		#valid within given arm constraints for each servo
		for num in range(int(len(arg) / 2)):
			servo = int(next(stack))
			pos = int(next(stack))

			#servo input must be for 1 of 6 arm servos
			if servo < 1 or servo > 6:
				await ctx.send('Please enter a valid servo')
				return
			
			#angle for each servo must be within the 180 degree limit
			if pos < 0 or pos > 180:
				await ctx.send('Please enter a valid angle')
				return

			#the end effector servo only has a range between 90 (open) and 180 (closed)
			if servo == 1 and (pos < 90 or pos > 180):
				await ctx.send('End effector (servo 1) angle must be between 90 and 180 degrees')
				return

			#assigns the angle position to each servo and prints to discord
			await set_servo_angle_and_wait(servolist[servo - 1], pos, 1)
			await ctx.send('Setting servo ' + str(servo) + ' to angle ' + str(pos))

	#returns the input message, used mostly for testing	
	@client.command(help="returns the input message, used mostly for testing")
	async def hello(ctx, *arg):
		await ctx.send(arg)

	#sends the github url for source code
	@client.command(help="sends the github url for source code")
	async def source(ctx):
		await ctx.send('https://github.com/smithcol/dudebot')
		
	#scans all messages send on the server
	@client.event
	async def on_message(message):
		#does nothing if the bot is the message sender
		if message.author == client.user:
			return
		
		#converts text to lowercase for easier text processing
		message_lower = message.content.lower()

		#sends dude if dude is in message
		if "dude" in message_lower and random.random() < 0.1:
			await message.channel.send("Dude...")

		#sends thinking emoji if someone is thinking
		if "mmm" in message_lower:
			chance = random.random()
			if chance < 0.25:
				await message.channel.send('https://tenor.com/view/hmm-emoji-thinking-emoji-let-me-think-gif-16435497')
			elif chance >= 0.25 and chance < 0.5:
				await message.channel.send('https://tenor.com/view/emoji-thinking-emoji-think-confused-hmm-gif-15742715')
			elif chance >= 0.5 and chance < 0.75:
				await message.channel.send('https://tenor.com/view/meme-thinking-gif-23334820')

		#sends the famous The Dude quote if a word from opinions array is found
		if any(word in message_lower for word in opinions):
			if random.random() < 0.25:
				await message.channel.send("that's just, like, your opinion, man")

		#sends the dancing big man if someone uses a word from big array
		if any(word in message_lower for word in big) and random.random() < 0.25:
			await message.reply('https://tenor.com/view/big-dance-party-rock-funny-haha-poop-gif-18703825')

		#deploy the monkey when the dude deems it necessary
		if random.random() < 0.005:
			await message.reply(file = discord.File(MONKEYTYPE_PATH))

		if "morb" in message_lower and random.random() < 1:
			await message.channel.send('Stop it, get help')

		if "test" in message_lower and random.random() < 0.15:
			await message.channel.send('Testes deez nuts')

		#non-ascii quote delimiter used? fuck you (maybe)
		if "’" in message_lower:
			chance = random.random()
			if chance < 0.01:
				await message.channel.send('Fuck off')
			elif chance >= 0.01 and chance <= 0.1:
				await message.channel.send(':(')
			elif chance >= 0.1 and chance < 0.2:
				await message.channel.send('Why do you do this to me?')
			return

		#on_message overrides commands, so this is needed for commands to work
		await client.process_commands(message)

	async def arm_endpoint(node, **kwargs):
		"""
		args: angle step size
		returns: sweeps the fingers
		"""
		step_size = int(kwargs['step_size'])
		await turn_servo_two(step_size)
		return dict(result='ok')

	async def camera_endpoint(node, **kwargs):
		"""
		args: none
		returns: my balls in pic form
		"""
		fp = get_image()
		url = await node.send_file(fp)
		return dict(result='ok', url=url)

	distributed.register_endpoint(client, '/arm', arm_endpoint)
	distributed.register_endpoint(client, '/camera', camera_endpoint)

	#runs with the specific key for dudebot
	await client.start(get_param("DUDEBOT_TOKEN"))
	
if __name__ == "__main__":
    asyncio.run(main())
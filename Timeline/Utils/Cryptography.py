'''
Timeline - An AS3 CPPS emulator, written by dote, in python. Extensively using Twisted modules and is event driven.
Cryptography is a tool which helps in calculating the cyrpto-algorithemic functions.
'''
from Timeline.Server.Constants import TIMELINE_LOGGER
from Timeline.Utils.Events import Event

from collections import deque
from string import *
from random import shuffle, choice
import string
from hashlib import md5 as MD5
import logging

class Crypto(object):

	def __init__(self, penguin):
		super(Crypto, self).__init__()

		self.penguin = penguin
		self.logger = logging.getLogger(TIMELINE_LOGGER)
		self.random_literals = list(ascii_letters + str(digits) + punctuation)
		self.randomKey = self.random(5) + "-" + self.random(4)
		self.salt = "a1ebe00441f5aecb185d0ec178ca2305Y(02.>'H}t\":E1_root"

	def swap(self, text, length):
		return text[length:] + text[:length]

	def md5(self, text):
		return MD5(text).hexdigest()

	def pureMD5(self, text):
		return MD5(text)

	def random(self, length = 10):
		shuffle(self.random_literals)
		letters = [choice(self.random_literals) for _ in range(length)]

		return join(letters, "")

	def loginHash(self):
		if self.penguin["password"] == None:
			return None

		_hash = self.swap(self.penguin["password"], 16)
		_hash += self.randomKey
		_hash += self.salt

		return self.swap(self.md5(_hash),16)

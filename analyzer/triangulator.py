import paho.mqtt.client as mqtt
import paho.mqtt.publish as publisher
import time
import json
import numpy as np
import sys
import copy
import signal
from flask import Flask, abort, Response, request
from threading import Thread, Lock

class Triangulate(Thread):
    """
        Thread performing the triangulation

        Instances:
            __time				: time to wait before performing triagulation
            __beaconTable		: reference to the table of beacons
			__beaconTableLocker	: reference to the lock of the beacon table
			__database			: reference to the database interface
    """

    def __init__(self, time, beaconTab, beaconTabLock, dbref):
		""" Constructor """
        Thread.__init__(self)
        self.__time = time
        self.__beaconTable = beaconTab
        self.__beaconTableLocker = beaconTabLock
        self.__database = dbref
	
    def run(self):
		""" Perform triangulation every __time seconds"""
		
		while(True):
			time.sleep(self.__time)

			self.__beaconTableLocker.acquire(True)
			# copy of the current beacon table
			temp_table = copy.deepcopy(self.__beaconTable)
			# beacon table reset
			for b in self.__beaconTable :
				self.__beaconTable[b].cleanInfo()

			self.__beaconTableLocker.release()

			for bea in temp_table :
				# For each beacon

				info = {}
				sumLen = 0

				for pos in temp_table[bea].getMap():
					# For each room

					s = sum(temp_table[bea].getMap()[pos])
					l = len(temp_table[bea].getMap()[pos])
					sumLen += l

					info[pos] = dict()
					info[pos]["lis"] = temp_table[bea].getMap()[pos]
					if l == 0 :
						# No msg received
						info[pos]["mean"] = float("-inf")
						info[pos]["var"] = float("-inf")
						info[pos]["len"] = float("-inf")
					else:
						info[pos]["mean"] = s / l
						info[pos]["var"] = float(np.var(info[pos]["lis"]))
						info[pos]["len"] = l

				# Get located room
				MAXIMO = float("-inf")
				stanza = ""
				for pos in info :

					if info[pos]["mean"] > MAXIMO:
						stanza = pos					
						MAXIMO = info[pos]["mean"]
				
				if stanza != "":
					self.__beaconTable[bea].setLast(stanza)
					self.__database.insert_db_entry(bea, stanza)
					print(bea + " - " + stanza)

			print("---------------------------------------------")
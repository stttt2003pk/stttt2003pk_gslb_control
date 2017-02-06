#!/usr/bin/env python
# -*- coding: utf-8 -*-
from value import *

class Topology(object):

    def __init__(self):
        self.score = 0
        self.priority         = 9
        self.datacenterStatus = 1

    def getFromStr(self, gtmTopology):
        index = gtmTopology.strip().split(' ')
 
        if index[0] == 'region':    #like:  region yinchuan server: SZ_OANet_OA
            self.location   = index[1]
            self.datacenter = index[3]
            self.calcService()
        else :
            print "Bad input use not region nor subnet!"

    @property
    def service(self):
        return self._service

    def calcService(self):
        if self.datacenter.find('NB') >= 0:
            self._service = "NB"
        elif self.datacenter.find('OA') >= 0:
            self._service = 'OA'
        elif self.datacenter.find('CBS') >= 0:
            self._service = 'CBS'
        elif self.datacenter.find('CDN') >= 0:
            self._service = 'CDN'
        else:
            print "serivce of datacenter undefined!"

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if not isinstance(value, int):
            raise ValueError('score must be an integer!')
        if value < 0 or value > 67108864:
            raise ValueError('score must between 0 - 67108864!')
        self._score = value 

    @property 
    def priority(self):
        return self._priority
    @priority.setter
    def priority(self, value):
        self._priority = value

    def __str__(self):
        result =  "dc.\""+self.datacenter+"\"   " +   "user.\""+self.location+"\"    " +str(self._score) +'\n'
        ####result =  "create gtm topology ldns: region " + self.location +   " server: datacenter "+self.datacenter + ' score ' + str(self._score) +'\n'
        ##create gtm topology ldns: region cmbsecc server: datacenter SH_OANet_NB
        return result

    def countScore(self):
        if self.location == 'global':
            priority = self.priority +4
        elif self._service == 'CDN':
            priority = self.priority -1
        else:
            priority = self.priority

       ## self._score = self.datacenterStatus * 2**24 + \
       ##               priority_value[priority] * 2**20 + \
       ##               location_value[self.location] * 2**16 + \
       ##               datacenter_value[self.datacenter] * 2**0
        self._score = str(0x1000000|(priority_value[priority]<<20)|(location_value[self.location]<<6)|(datacenter_value[self.datacenter]))



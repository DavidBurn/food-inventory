#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 00:06:12 2019

An inventory tracker, planned as a simple freezer item class. Morphed into 
creating a user friendly interface for adding/removing storage locations
and items.

@author: dave
"""
from collections import defaultdict
import json
import glob
import sys

class Food_storage:
    def __init__(self, name, food=None):
        self.name = name
        if food:
            self.storage = food
            for key in self.storage.keys():
                self.storage[key] = defaultdict(int, self.storage[key])
        else:
            self.storage = {}
    
    def add_location(self, name):
        if type(name) == list:
            for n in name:
                self.storage[n] = defaultdict(int)
        else:
            self.storage[name] = defaultdict(int)
        
    def add_food(self, food, location):
        """
        Drawer locations (Top to bottom):
            Shelf 1
            Shelf 2
            Ice Tray
            Drawer 1 - 5
        """
        for f in food.split(','):
            if location not in self.storage:
                self.add_location(location)
            self.storage[location][f.strip()] += 1
    
    def remove_location(self, name):
        del self.storage[name]
        
    def remove_food(self, food, location):
        self.storage[location][food] -= 1
        if self.storage[location][food] == 0:
            del self.storage[location][food]
    
    def whats_in_the_freezer(self):
        print('{:*^40}'.format(self.name))
        for key in self.storage.keys():
            print(key)
            for food, num in self.storage[key].items():
                print('    {:<20} : {}'.format(food, num))
        print('*'*40)
    
    def is_there(self, item):
        total = 0
        for loc in self.storage.keys():
            for k, v in self.storage[loc].items():
                subtotal = 0
                if item in k:
                    subtotal += v
                    total += 1
                    print('{} {} found in {}'.format(subtotal, k, loc))
        if total == 0:
            print('>>> {} not found in the {}'.format(item, self.name))
    
    def save_to_disk(self, path='freezer.json'):
        with open(path, 'w') as file:
            json.dump(self.storage, file)
            
def load_storage():
    storage_objects = []
    for path in glob.glob('*.json'):
        with open(path) as file:
            data = json.load(file)
            storage = Food_storage(path.strip('.json'),data)
            storage_objects.append(storage)
    return storage_objects

def add_food_loop(obj):
    while True:
        locations = obj.storage.keys()
        food = input('Enter an item or items to add to {}, or type done to finish  : '.format(obj.name))
        if food == 'done':
            break
        if locations:
            print('\nCurrent location(s) : {}. (you can also add a new one)'
                  .format(', '.join([l for l in locations])))
        loc = input('Enter a location : ')
        obj.add_food(food, loc)
        print('>>> {} added to {}'.format(food, loc))

def remove_food_loop(obj):
    while True:
        food = input('Enter an item to remove from {}, type done to finish  : '.format(obj.name))
        if food == 'done':
            break
        total = 0
        for loc in obj.storage.keys():
            if food in obj.storage[loc]:
                num = obj.storage[loc][food]
                total += num
                print('>>> We have {} {} in the {}'.format(num, food, loc))
        if total == 0:
            print('>>> {} not found in the {}'.format(food, obj.name))
            continue
        loc = input('Enter a location : ')
        obj.remove_food(food, loc)
        print('>>> {} removed from {}'.format(food, loc))

def find(obj):
    print('-'*20)
    print('Find an item in the {}'.format(obj.name))
    print('-'*20)
    item = input('What are you looking for? Type all or part of an item : ')
    obj.is_there(item)
        
def add_location(obj):
    print('-'*20)
    print('Add new location')
    print('-'*20)
    print('Current locations : {}'.format(', '.join([l for l in obj.storage.keys()])))
    loc = input('Enter name for the new location : ')
    obj.add_location(loc)
    print('Added {} to locations.'.format(loc))
    
def remove_location(obj):
    print('-'*20)
    print('Remove location')
    print('-'*20)
    print('Current locations : {}'.format(', '.join([l for l in obj.storage.keys()])))
    loc = input('Enter location to remove : ')
    obj.remove_location(loc)
    print('Removed {} from locations.'.format(loc))
    
def whats_for_tea(obj):
    obj.whats_in_the_freezer()

def save(obj):
    default = '{}.json'.format(obj.name)
    print('Saving {} to disk, default path = "{}"'.format(obj.name, default))
    path = input('Type a different path or press enter to use default')
    if not path:
        path = default
    obj.save_to_disk(path=path)
    print('>>> {} saved to {}'.format(obj.name, path))
    
def create_obj():
    print('-'*20)
    print('Create a new storage object')
    print('-'*20)
    name = input('Type a name for your object : ')
    print(' {:*>20} {:*<20} '.format(name, 'created'))
    return Food_storage(name)

def switch_object(obj):
    objs = load_storage()
    s = input('Save changes to {}? y/n : '.format(obj.name))
    if s in ['y','yes']:
        save(obj)
    print('-'*20)
    print('Your loaded objects: '.format(len(objs)))
    print('-'*20)
    for o in objs:
        print('   {}'.format(o.name))
    n = input('Type the name to edit existing object or type new to create a new object. \n\n')
    
    global active_obj
    if n == 'new':
        active_obj = create_obj()
    for o in objs:
        if o.name == n:
            active_obj =  o

def obj_menu(obj):
    print('-'*20,
          '{} menu'.format(obj.name),
          '-'*10,
          'a = add food',
          'r = remove food',
          'al = add location',
          'rl = remove location',
          'f = find location of item',
          'w = whats in the {}'.format(obj.name),
          's = save {} to disk'.format(obj.name),
          'l = load a different object or create a new one',
          'exit = exit',
          '-'*20,
          sep = '\n', end='\n')
    sel = input()
    if sel == 'exit':
        s = input('Save changes to {}? y/n : '.format(obj.name))
        if s in ['y','yes']:
            save(obj)
        sys.exit()
    menu = {'a' : add_food_loop, 
            'al' : add_location,
            'r' : remove_food_loop,
            'rl' : remove_location,
            'f' : find,
            'w' : whats_for_tea, 
            's' : save,
            'l' : switch_object }
    menu[sel](obj)

if __name__ == "__main__":
    # Load JSON objects in working directory if they exist
    objs = load_storage()
    if objs:
        print('Your loaded objects: '
              .format(len(objs)))
        for o in objs:
            print('   {}'.format(o.name))
        n = input('Type the name to edit existing object or type new to create a new object. \n\n')
        if n == 'new':
            active_obv = create_obj()
        for o in objs:
            if o.name == n:
                active_obj = o
            
            
    # User creates new storage object if none exist
    else:
        active_obj = create_obj()
        print('\n   Time to add some food   \n')
        add_food_loop(active_obj)
    
    while True:
        obj_menu(active_obj)
    
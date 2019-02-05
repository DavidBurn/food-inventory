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
import re

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
        
    def add_food(self, food, location, quantity=1):
        """
        Drawer locations (Top to bottom):
            Shelf 1
            Shelf 2
            Ice Tray
            Drawer 1 - 5
        """
        if location not in self.storage:
            self.add_location(location)
        self.storage[location][food] += quantity
    
    def remove_location(self, name):
        del self.storage[name]
        
    def remove_food(self, food, location, quantity):
        self.storage[location][food] -= quantity
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

def split_food_and_quantity(string):
    split_list = string.split(',')
    entries = []
    pattern = r'([a-z\sA-Z]+)|([0-9]+)'
    for entry in split_list:       
        objects = []
        for m in re.finditer(pattern, entry):
            match = m.group(0).strip()
            try:
                match = int(match)
            except ValueError:
                pass
            if match == '':
                continue
            objects.append(match)
        entries.append(objects)  
    return entries

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
        entries = split_food_and_quantity(food)
        for entry in entries:
            quantity = 1
            for num_or_word in entry:
                if type(num_or_word) == str:
                    f = num_or_word
                if type(num_or_word) == int:
                    quantity = num_or_word
            obj.add_food(f, loc, quantity=quantity)
            print('>>> {} {} added to {}'.format(quantity, f, loc))

def remove_food_loop(obj):
    while True:
        food = input('Enter an item to remove from {}, type done to finish  : '.format(obj.name))
        if food == 'done':
            break
        total = 0
        # Find quanitities of item if applicable, food now = f
        entries = split_food_and_quantity(food)
        for entry in entries:
            quantity = 1
            for num_or_word in entry:
                if type(num_or_word) == str:
                    f = num_or_word
                if type(num_or_word) == int:
                    quantity = num_or_word
        # Find locations of the item
        o = obj.storage
        for loc in o.keys():
            if f in o[loc]:
                num = o[loc][f]
                total += num
                print('>>> We have {} {} in the {}'.format(num, f, loc))
        # Check if number to be removed exists in the store
        if total == 0:
            print('>>> No {} found in the {}'.format(f, obj.name))
            continue
        elif total < quantity:
            print('>>> Only {} {} found in the {}, please check quantities'.format(total, f, obj.name))
            continue
        # If quantity exists, enter a location
        loc = input('Enter a location : ')
        # Clause for when quantity to remove is greater than in the store
        if o[loc][f] < quantity:
            while True:
                num_available = o[loc][f]
                obj.remove_food(f, loc, num_available)
                quantity -= num_available
                if quantity == 0:
                    break
                print('>>> {} {} removed from {}'.format(num_available, f, loc))
                print('{} still remaining to remove'.format(quantity))
                for loc in o.keys():
                    if f in o[loc]:
                        num = o[loc][f]
                        total += num
                        print('>>> We have {} {} in the {}'.format(num, f, loc))
                loc = input('Enter a location : ')
                
        else:
            obj.remove_food(f, loc, quantity)
            print('>>> {} {} removed from {}'.format(quantity, f, loc))

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
        n = input('Type the name to edit existing object or press enter to create a new object. \n\n')
        for o in objs:
            if o.name == n:
                active_obj = o
            else:
                active_obj = create_obj()
            
            
    # User creates new storage object if none exist
    else:
        active_obj = create_obj()
        print('\n   Time to add some food   \n')
        add_food_loop(active_obj)
    
    while True:
        obj_menu(active_obj)
    
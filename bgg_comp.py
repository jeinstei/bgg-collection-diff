#!/usr/bin/python
"""Collection compare and viewing for BGG

   Currently this can print out any number of user's collections
   and create a unique set of what each user owns together.
   
   It can also print a set of """

__author__ = "Joshua Einstein-Curtis"
__version__ = "0.2.0"
__maintainer__ = "Joshua Einstein-Curtis"
__email__ = "jeinstei@gmail.com"

import sys

from boardgamegeek.api import BoardGameGeek

class c_bgg(BoardGameGeek):
    
    def __init__(self):
        BoardGameGeek.__init__(self)

    def process(self, users, option='all', gtype='all', action='union', all_lists=False, verbose=True, alpha_sort=True):
        
        if verbose:
            print("Getting collections for users {0}".format(users))
            
        collection_list = []
        for user in users:
            try:
                collection = self.collection(user_name=user)
            except Exception, e:
                print("Error getting collection for {0}:\n{1}".format(user, e))
                sys.exit()
            collection_list.append(collection)

        master_set = set()
        if action == 'union':
            master_set = self.__union(collection_list, option)
        elif action == 'diff' and len(collection_list) > 1:
            master_set = self.__diff(collection_list, option, all_lists)
        elif action == 'intersect' and len(collection_list) > 1:
            master_set = self.__intersect(collection_list, option, all_lists)
        else:
            if verbose:
                print("Action ignored due to single user specified. Returning user collection")
            master_set = self.__union(collection_list, option)

        # Get specific type if requested
        master_set = self.__filter(master_set, gtype)

        if alpha_sort:
            # from https://stackoverflow.com/questions/2669059/how-to-sort-alpha-numeric-set-in-python
            master_set = sorted(master_set, key=lambda item: (int(item.partition(' ')[0])
                               if item[0].isdigit() else float('inf'), item))

        return master_set

    def __diff(self, clist, option, all_lists):
        """Return set of items on first user's list but not the others"""
        
        if not all_lists:
            if option == 'all':
                inset = set([item.name for item in clist[0].items])
            else:
                inset = set([item.name for item in clist[0].items if getattr(item, option)])
        
        outset = set()
        if all_lists:
            outset = inset
            for collection in clist[1:len(clist)]:
                if option == 'all':
                    outset = outset.difference([item.name for item in collection.items])
                else:
                    outset = outset.difference([item.name for item in collection.items if getattr(item, option)])

        else:
            for collection in clist[1:len(clist)]:
                if option == 'all':
                    diffset = inset.difference([item.name for item in collection.items])
                else:
                    diffset = inset.difference([item.name for item in collection.items if getattr(item, option)])
                outset = outset.union(diffset)
                
        return outset

    def __union(self, clist, option):
        """Create union of collection set"""
        
        outset = set()
        for collection in clist:
            if option == 'all':
                outset = outset.union([item.name for item in collection.items])
            else:
                outset = outset.union([item.name for item in collection.items if getattr(item, option)])
        return outset

    def __intersect(self, clist, option, all_lists):
        """Create intersection of collections based on first user"""
        
        if not all_lists:
            if option == 'all':
                inset = set([item.name for item in clist[0].items])
            else:
                inset = set([item.name for item in clist[0].items if getattr(item, option)])
        
        outset = set()
        if all_lists:
            outset = inset
            for collection in clist[1:len(clist)]:
                if option == 'all':
                    outset = outset.intersection([item.name for item in collection.items])
                else:
                    outset = outset.intersection([item.name for item in collection.items if getattr(item, option)])

        else:
            for collection in clist[1:len(clist)]:
                if option == 'all':
                    intset = inset.intersection([item.name for item in collection.items])
                else:
                    intset = inset.intersection([item.name for item in collection.items if getattr(item, option)])
                
                outset = outset.union(intset)

        return outset

    def __filter(self, inset, gtype):
        """Perform filtering based on item type"""
        
        if gtype != 'all':
            if verbose:
                print("Filter type {0} in collections".format(gtype))
            remove_list = []
            for item in inset:
                do_transact = True
                while(do_transact):
                    game = self.game(name=item)
                    
                    if game is None:
                        continue
                    
                    do_transact = False
                    
                isexpansion = game.expansion
                
                if ((gtype == 'expansion' and not isexpansion) or
                   (gtype == 'base' and isexpansion)):
                    remove_list.append(item)

            [inset.discard(item) for item in remove_list]
            
        return inset

if __name__ == '__main__':
    
    options = [
        'all',
        'for_trade',
        'owned',
        'prev_owned',
        'want',
        'want_to_buy',
        'want_to_play',
        'preordered',
        'wishlist',
    ]


    # Currently ignoring filtering by type due to processing issues
    types = [
        #'expansion',
        #'base',
        'all'
    ]
    
    actions = [
        'diff',
        'union',
        'intersect'
    ]
    
    from argparse import ArgumentParser
    
    parser = ArgumentParser(description="BGG compare collection tool")
    parser.add_argument("-o", "--option", default='owned', choices=options, help="Collection option")
    parser.add_argument("-t", "--type", dest='gtype', default='all', choices=types, help="Type option")
    parser.add_argument("-a", "--action", choices=actions, help="intersect: Return set of items on first user's list but not the others; \
                                                                 diff: Return set of items on first user's list but not the others")
    parser.add_argument("--opall", action="store_true", help="Perform operation on all collections, not just comparing to first user")                                                             
    parser.add_argument("users", nargs="+", help="USer to display or users to compare")
    args = parser.parse_args()
    
    users = args.users

    # BGG requests >5 seconds between requests to not have issues
    bgg = c_bgg()

    result =  bgg.process(users, args.option, args.gtype, args.action, args.opall)
    print("{0}\nFound {1} entries\n".format(result, len(result)))

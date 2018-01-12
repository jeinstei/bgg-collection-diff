#!/usr/bin/python
"""Collection compare and viewing for BGG

   Currently this can print out any number of user's collections
   and create a unique set of what each user owns together.
   
   It can also print a set of """

__author__ = "Joshua Einstein-Curtis"
__version__ = "0.1.0"
__maintainer__ = "Joshua Einstein-Curtis"
__email__ = "jeinstei@gmail.com"

import sys

from boardgamegeek.api import BoardGameGeek

class c_bgg(BoardGameGeek):
    
    def __init__(self):
        BoardGameGeek.__init__(self)

    def process(self, users, option='all', gtype='all', diff=False, verbose=True, alpha_sort=True):
        
        if verbose:
            print("Getting collections for users {0}".format(users))
            
        collection_list = []
        for user in users:
            collection = self.collection(user_name=user)
            collection_list.append(collection)

        if not diff:
            master_list = set()

            # Build up set of all games combined
            for collection in collection_list:
                if option == 'all':
                    [master_list.add(item.name) for item in collection.items]
                else:
                    [master_list.add(item.name) for item in collection.items if getattr(item, option)]

        # Perform diff or combine as requested
        elif diff and len(collection_list) > 1:
            diff_list = set()
            for collection in collection_list[1:len(collection_list)]:
                if option == 'all':
                    [diff_list.add(item.name) for item in collection.items if item not in collection_list[0]]
                else:
                    [diff_list.add(item.name) for item in collection.items if (getattr(item, option) and (item not in collection_list[0]))]

            master_list = diff_list
        else:
            if verbose:
                print("diff ignored due to single user specified.")

        # Get specific type if requested
        if gtype != 'all':
            if verbose:
                print("Filter type {0} in collections".format(gtype))
            remove_list = []
            for item in master_list:
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

            [master_list.discard(item) for item in remove_list]

        if alpha_sort:
            # from https://stackoverflow.com/questions/2669059/how-to-sort-alpha-numeric-set-in-python
            master_list = sorted(master_list, key=lambda item: (int(item.partition(' ')[0])
                               if item[0].isdigit() else float('inf'), item))

        return master_list

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

    types = [
        #'expansion',
        #'base',
        'all'
    ]
    
    from argparse import ArgumentParser
    
    parser = ArgumentParser(description="BGG compare collection tool")
    parser.add_argument("-o", "--option", default='owned', choices=options, help="Collection option")
    parser.add_argument("-t", "--type", dest='gtype', default='all', choices=types, help="Type option")
    parser.add_argument("-d", "--diff", action="store_true", help="Print games not in first user's collection")
    parser.add_argument("users", nargs="+", help="USer to display or users to compare")
    args = parser.parse_args()
    
    users = args.users

    # BGG requests >5 seconds between requests to not have issues
    bgg = c_bgg()

    result =  bgg.process(users, args.option, args.gtype, diff=args.diff)
    print("Found {0} entries\n{1}".format(len(result), result))

from matplotlib.pyplot import disconnect

S_ALONE = 0
S_TALKING = 1

# ==============================================================================
# Group class:
# member fields:
#   - An array of items, each a Member class
#   - A dictionary that keeps who is a chat group
# member functions:
#    - join: first time in
#    - leave: leave the system, and the group
#    - list_my_peers: who is in chatting with me?
#    - list_all: who is in the system, and the chat groups
#    - connect: connect to a peer in a chat group, and become part of the group
#    - disconnect: leave the chat group but stay in the system
# ==============================================================================

S_ALONE = 0
S_TALKING = 1

class Group:

    def __init__(self):
        self.members = {}
        self.chat_grps = {}
        self.grp_ever = 0

    def join(self, name):
        self.members[name] = S_ALONE
        return

    def is_member(self, name):
        return name in self.members.keys()
    # implement
    def leave(self, name):
        self.disconnect(name)
        del self.members[name]

    def find_group(self, name):
        """
        Auxiliary function internal to the class; return two
        variables: whether "name" is in a group, and if true
        the key to its group
        """

        found = False
        group_key = 0
        for g_key,members in self.chat_grps.items():
            if name in members:
                found=True
                group_key=g_key
                break


        # ---- end of your code --- #
        return found, group_key

    def connect(self, me, peer):
        """
        me is alone, connecting peer.
        if peer is in a group, join it
        otherwise, create a new group with you and your peer
        """
        peer_in_group, group_key = self.find_group(peer)
        me_in_group,group_key_me=self.find_group(me)

        if peer_in_group:
            self.chat_grps[group_key].append(me)
        elif me_in_group:
            self.chat_grps[group_key_me].append(peer)
        else:
            self.chat_grps[self.grp_ever+1]=[me,peer]
            self.grp_ever+=1
        self.members[me]=S_TALKING
        self.members[peer]=S_TALKING


    # implement
    def disconnect(self, me):
        """
        find myself in the group, quit, but stay in the system
        """
        me_in_group, group_key = self.find_group(me)
        if me_in_group:
            member_count=len(self.chat_grps[group_key])
            if member_count==2:
                del self.chat_grps[group_key]
                self.grp_ever -= 1
            else:
                self.chat_grps[group_key].remove(me)


        return

    def list_all(self):
        # a simple minded implementation
        full_list = "Users: ------------" + "\n"
        full_list += str(self.members) + "\n"
        full_list += "Groups: -----------" + "\n"
        full_list += str(self.chat_grps) + "\n"
        return full_list

    # implement
    def list_me(self, me):
        """
        return a list, "me" followed by other peers in my group
        """
        my_list = []
        my_list.append(me)
        peer_in_group, group_key=self.find_group(me)
        if peer_in_group:
            all_members=self.chat_grps[group_key]
            for member in all_members:
                if member!=me:
                    my_list.append(member)
        return my_list


if __name__ == "__main__":
    g = Group()
    g.join('a')
    g.join('b')
    g.join('c')
    g.join('d')
    print(g.list_all())

    g.connect('a', 'b')
    print(g.list_all())
    g.connect('c', 'a')
    print(g.list_all())
    print(g.list_me('a'))
    print()
    g.leave('c')
    print(g.list_all())
    g.disconnect('b')
    print(g.list_all())


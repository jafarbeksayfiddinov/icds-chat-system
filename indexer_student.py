import pickle


class Index:
    def __init__(self, name):
        self.name = name
        self.msgs = []
        """
        ["1st_line", "2nd_line", "3rd_line", ...]
        Example:
        "How are you?\nI am fine.\n" will be stored as
        ["How are you?", "I am fine." ]
        """

        self.index = {}
        """
        {word1: [line_number_of_1st_occurrence,
                 line_number_of_2nd_occurrence,
                 ...]
         word2: [line_number_of_1st_occurrence,
                  line_number_of_2nd_occurrence,
                  ...]
         ...
        }
        """

        self.total_msgs = 0
        self.total_words = 0

    def get_total_words(self):
        return self.total_words

    def get_msg_size(self):
        return self.total_msgs

    def get_msg(self, n):
        return self.msgs[n]

    def add_msg(self, m):

        self.msgs.append(m)
        self.total_msgs += 1

    def add_msg_and_index(self, m):
        self.add_msg(m)
        line_at = self.total_msgs - 1
        self.indexing(m, line_at)

    def indexing(self, m, l):

        words=m.split()
        self.total_words += len(words)
        for w in words:
            w=w.lower()
            self.index[w]=self.index.get(w, [])+[l]

    def search(self, terms):
        """
        return a list of tupple.
        Example:
        if index the first sonnet (p1.txt),
        then search('thy') will return the following:
        [(7, " Feed'st thy light's flame with self-substantial fuel,"),
         (9, ' Thy self thy foe, to thy sweet self too cruel:'),
         (9, ' Thy self thy foe, to thy sweet self too cruel:'),
         (12, ' Within thine own bud buriest thy content,')]
        """
        msgs = []
        term=terms.split()
        if term[0] in self.index.keys():
            indices=self.index[term[0]]
            for i in indices:
                if terms in self.msgs[i]:
                    msgs.append((i,self.msgs[i]))
        return msgs
class PIndex(Index):
    def __init__(self, name):
        super().__init__(name)
        roman_int_f = open('roman.txt.pk', 'rb')
        self.int2roman = pickle.load(roman_int_f)
        roman_int_f.close()
        self.load_poems()

    def load_poems(self):
        """
        open the file for read, then call
        the base class's add_msg_and_index()
        """
        lines=open(self.name,'r').readlines()
        for l in lines:
            if l.rstrip()[:-1] not in self.int2roman.values():
                self.add_msg_and_index(l.rstrip()[:-1])
            else:
                self.add_msg_and_index(l.rstrip())

    def get_poem(self, p):
        """
        p is an integer, get_poem(1) returns a list,
        each item is one line of the 1st sonnet

        Example:
        get_poem(1) should return:
        ['I.', '', 'From fairest creatures we desire increase,',
         " That thereby beauty's rose might never die,",
         ' But as the riper should by time decease,',
         ' His tender heir might bear his memory:',
         ' But thou contracted to thine own bright eyes,',
         " Feed'st thy light's flame with self-substantial fuel,",
         ' Making a famine where abundance lies,',
         ' Thy self thy foe, to thy sweet self too cruel:',
         " Thou that art now the world's fresh ornament,",
         ' And only herald to the gaudy spring,',
         ' Within thine own bud buriest thy content,',
         " And, tender churl, mak'st waste in niggarding:",
         ' Pity the world, or else this glutton be,',
         " To eat the world's due, by the grave and thee.",
         '', '', '']
        """
        poem = []

        p_str=self.int2roman[p]+'.'
        p_next_str=self.int2roman[p+1]+'.'
        temp=self.search(p_str)
        if temp:
            [(go_line,m)]=temp
        else:
            return []
        poem=[]
        end=self.get_msg_size()
        while go_line<end:
            this_line=self.get_msg(go_line)
            if this_line==p_next_str:
                break
            poem.append(this_line)
            go_line+=1
        return poem
if __name__ == "__main__":
    sonnets = PIndex("AllSonnets.txt")
    # the next two lines are just for testing
    p3 = sonnets.get_poem(2)
    print(p3)
    s_love = sonnets.search("five")
    print(s_love)



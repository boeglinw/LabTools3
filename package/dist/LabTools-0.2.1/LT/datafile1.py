"""

Reads a file containing columns of data and creates a dictionary according to header information
using the following format:

1. comments start with ``#`` in the **first column** : ``# My Comment``

2. header information starts with ``#!``, where ``#`` is also in the **first column**. It must precede the data.
   
3. each columns is represented by ``name[dtype, col.nr.]/``,  *dtype* (optional) is the data type and *col.nr*
   (starting at 0) is the column number

4. data are separated by white space **NOT commas!**

5. data types:

      - s : string
      - f : float
      - i : integer

6. blank lines are ignored

 **NOTE**: if data formats are entered they should be specified for all columns

Example data:: 

   #! p_miss[0]/ siglt[2]/ s01[3]/ alt[4]/
   200. 1.35e-4 -1.e-3    0.1
   220. 2.56e-4 -2.e-4    -0.1
   230. 3.47e-6 -3.e-5    1.1

The header can also contain data type information:: 

   #! p_miss[f,0]/ siglt[f,2]/ s01[f,3]/ alt[f,4]/

   200. 1.35e-4 -1.e-3    0.1
   220. 2.56e-4 -2.e-4    -0.1
   230. 3.47e-6 -3.e-5    1.1


Example that opens a file and create a dfile object::

   >>> f0 = dfile('sig_LT.dat')

Loop over content::

   >>> for l in f0:
   >>> ...pm = l['p_miss']
   >>> ...sig_lt = l['siglt']*10000.
   >>> ...print pm, sig_lt, l['alt']
   >>> # end for l

Variable names are also called keys.

---------------------------------------------------------

"""

import sys
import os
import string
import math
import re
import pdb
# function to create a dictionary from 2 lists: key, values

# create a dictionary from  an array of keys and values

class dfile:
    """
    Open a file, read and interpret the contents and return a dfile object:

    >>> df = dfile('my_datafile')
    
    """
    def __init__(self, filename, debug = False, new=False):
	self.H=re.compile("^#\!") # pattern for header
	self.C=re.compile("^#")   # pattern for comment
        # pattern for splitting header
        # currently:
        # ^#\! : matches line beginning with #!
        # \[[0-9]+\]\/: matches [0]/ ... [8796]/
        # \[ *\w+ *, *\w *\]\/ : matches [   f  , blabla   ]/
        # 
	self.S=re.compile("^#\!|\[[0-9]+\]\/|\[ *\w *, *\w+ *\]\/") 
        # pattern to find format information in the header 
        self.F=re.compile("\w+ *, *\w+") 
        # pattern to find a character
        self.Fc=re.compile("[a-zA-Z]")
        # supported formats: the output format dictionary key must match the supported formats
        self.fmt_characters = ['f','i','s']
        self.output_format= {'f':'%r ','i':'%d ','s':'%s '}
        # empty dictionary for the formats
        self.formats = {} 
        # flag for printing debugging information
        self.debug = debug
        #
	self.header = None
	self.data = []
        self.adata = []
	self.fdata=[]
        self.keys=[]
        self.new = False
        if new:
            new=True
            self.filename = filename
            self.keys.append('indx')
            self.headindex=0
            self.adata.append('#! ')
            return
	# pdb.set_trace()
	# open file
	self.filename = filename
	i=open(filename,"r")      # open file
	self.adata=i.readlines()   # read all data
        if self.debug :
            print("datafile --> data read !")
	# remove leading and trailing spaces
	self.adata = list(map(string.strip,self.adata))
        if self.debug :
            print("datafile --> spaces removed read !")
	self.remove_blanks()
        if self.debug :
            print("datafile --> blank lines removed read !")
	i.close()
	if (self.find_header() != 0): # find the header 
	    print("cannot interpret data")
	    return
        if self.debug :
            print("datafile --> create arrays !")
	self.make_array()  # read data
        if self.debug :
            print("datafile --> arrays created !")
    def __getitem__(self,i):
        # allows 'direct' access to the data
        if type(i) is int:
            # it'sm index
            return self.data[i]
        elif type(i) is str:
            # its a lkey return the list of data
            return self.get_data(i)
    def __len__(self):
        return len(self.data)
    def remove_blanks(self): 
        # work through the list in reverse order
        indices = list(range( len( self.adata ))) # list of indices
	indices.reverse() # reverse order
	for i in indices: # loop through from the top
	    if len(self.adata[i].strip()) == 0:
		del self.adata[i] 
    def find_header(self):
	# find header information : look for a line starting with #!
	for l in self.adata:
	    if (self.H.match(l) != None):
		self.headindex=self.adata.index(l)
		self.header=re.split(self.S,l)[1:-1] # remove first and last element
		self.keys=list(map(string.strip,self.header))
		self.keys.append('indx') # store the index into the original
                # handle data format
                # pdb.set_trace()
                fmt = re.findall(self.F,l)
                # no format specification, set default format
                if fmt == []:
                    for k in self.keys[:-1] : # skip index
                        self.formats[k] = 'f'
                # use format specifications
                else:
                    for i,f in enumerate(fmt):
                        fc = re.findall(self.Fc,f)[0] # use 1st char. for format
                        self.formats[self.keys[i]] = fc
                # addformat for the index
                self.formats['indx'] ='i'
		# adata array
                # do some checks
                if (len(self.keys)  != len(self.formats)):
                    print(self.filename,": problem in data formats !")
                    print(self.adata)
                    return -1
		return 0
	    #
	print(self.filename,": no header information !")
	print('data dump : ')
	print(self.adata)
	return -1

    def parse_line(self, l):
	if (self.C.match(l) != None) : # not a comment
            return None
	ll=l.split()
	# handle file format problems
	if len(ll) > (len(self.keys)-1) : 
	    n_data = (len(self.keys)-1)
	    print(self.filename, ' error: more data than variable names !'+\
		' ---> check header !')
	    sys.exit()
	if len(ll) < (len(self.keys)-1) : 
	    print(self.filename, ' error: too few variable names !'+\
		' ---> check header !')
	    sys.exit()
	f = []
        # now convert to values
	for i,k in enumerate(ll):
            # check if there are format specifications
            f_err = False
            try:
                fmt = self.formats[self.keys[i]]
                fc = fmt
                # check that the format is supported
                fi = self.fmt_characters.index(fmt) 
            except:
                f_err = True
                print('unknown format : ', fc, ' set to f')
                fc = 'f'
                self.formats[self.keys[i]] = 'f'
            # now try to convert according to the format
	    try:
                if fc == 'f':
                    f.append(float(k)) # create a float 
                if fc == 'i':
                    f.append(int(k))   # create an integer 
                if fc == 's':
                    f.append(k)        # leave as string
	    except:
		f.append(k) # if not possible leave it, 
                # but make a comment
                if len(self.formats) == 0 :
                    print('cannot convert : ', k, ' to float ')
                else: 
                    if (f_err ):
                        print('cannot convert : ', k, \
                            ', problem with unknown format : ', fmt)
                    else:
                        print('cannot convert : ', k, \
                            ', with format :', fmt)
	f.append(self.adata.index(l))
        # pdb.set_trace()
        return f

    def make_array(self):
	# create an array of dictionaries
        n_data = len(self.adata)
	for line_n, l in enumerate(self.adata):
            f = self.parse_line(l)
            if f == None:
                continue
            self.data.append(self.make_dict(self.keys,f) ) 
            if self.debug:
                print("processed data : ", line_n, " out of ", n_data)
    def make_dict(self,keys,values):
	# create a dictionary from a list of keys and values
	p = []
	for j,key in enumerate(keys): # loop over keys
	    try:
		p.append( (key.strip(),values[j]) ) # an array of tuples
		d=dict(p) # create a dictionary
	    except:
		print('problem in data : ', key, values, j)
	    #
	return d
    def scale(self, key, factor):
        """
        multiply all values of key with a factor
        """
        for i, d in enumerate(self.data):
            self.data[i][key] = factor*d[key]
        #
            
    def sort(self, key, **kwargs):
        """
        sort the data according to the values in key
        """
        index_array = []
        for d in self.data:
            index_array.append((d[key], self.data.index(d))) # store index and values pair
        sorted_array = sorted(index_array,**kwargs) # create a sorted array
        temp = []
        for ip in sorted_array:
            temp.append(self.data[ip[1]])
        self.data = temp
        temp=[]
            
    def name(self):
	"""
	print the filename associate with this instance 

	"""
	print("Input file name : ", self.filename)
    def show_keys(self):
	"""
	print a list of variable names in the dictionary

	"""
	print(self.keys)
    def get_keys(self):
	"""

	return a list of keys

	"""
	return self.keys
    def get_header(self):
	"""

	return the header lines

	"""
        return self.adata[self.headindex]


    def show_data(self,keylist): 
	"""

	print all the data corresponding to the key list::

	   >>> df.show_data('key1:key2:key3')

	"""
	akey=keylist.split(":")
	for l in self.data:
	    ll=[]
	    for i in akey:
                format = self.output_format[ self.formats[i] ]
		ll.append( format%( l[i] ) )
	    print(ll)


    def check_data(self, func, data, key, *args):
        """
        
        function used to check if data fulfill a condition provided
        by the user. The function is assumed to return True of False.

        """
        return func( data, key, *args)

    def select_data(self, sel_func = None, sel_args = None):
        """
        returns an iterator for the data. As in get_data() a selector function and
        its arguments can be supplied:

        conditions can be applied:
        
        1) sel_func: a user provided function returning True or False

        2) sel_args: a list of arguments used in the sel_func function

        The iterator returned can be used as follows:

        >>> for d in df.select_data():
        >>> ...print d

        or the result can be converted to a list:

        >>> list(df.select_data())

        Using a selector function:

        Example: assume the data contain a variable (key) called 'name'
           you want to select only those data where name contains a certain substring 'sub'

        Define this function:

        >>> def myfind(data, key , what):
        >>> ...where = data[key]
        >>> ...return (str.find(where, what) >= 0)

        now you can select the data using:

        >>> list( df.select_data( myfind, 'name', 'sub') )
        
        """
        if sel_func == None:
            for i,data in enumerate(self.data):
                yield data
        else:
            for i,data in enumerate(self.data):
                if self.check_data(sel_func, data, *sel_args):
                    yield data
        # that's all

    def select_data_eval(self, eval_str):
        """
        returns an iterator for data selected with an *eval* expression
        stored in the string `eval_str` each dataset item is accessed using the name data::

        >>> df.select_data_eval("data['x'] >= 0.")

        returns only those data items where the value of the x-column in the file
        is larger than or equal to 0.
        
        """
        for i,data in enumerate(self.data):
            if eval( eval_str):
                yield data
        # that's all

    def eval_data(self, eval_str):
        """
        iterator over all data evaluating an expression contained in eval_str
        """
        for i,data in enumerate(self.data):
            yield eval(eval_str)
        # that's all

    def get_data(self,key, sel_func = None, sel_args = None): 
	"""

	return all data for `key` subject to the results of a selector function.  

        one can define a selector function (`sel_func`) using the arguments stored in `sel_args`.
        This function is evaluated for each data record and only
        those data are returned for which the condition is fulfilled.
        
        1) sel_func: a user provided function returning True or False

        2) sel_args: a list of arguments used in the sel_func function

        Example::
           assume the data contain a variable (key) called 'name'
           you want to select only those data where name contains a certain substring 'Jo'

        Define this function::

        >>> def myfind(data, key , what):
        >>> ...where = data[key]
        >>> ...return (str.find(where, what) >= 0)

        now you can select the data using::

        >>> df.get_data('name',myfind, ['name','Jo'] )

        This should return a list of names containing the substring 'Jo'

	"""
	array=[]
	for l in self.data:
            if sel_func == None:
                array.append(l[key])
            else :
                if self.check_data( sel_func, l, *sel_args):
                    array.append(l[key])
	return array
    
    def get_data_eval(self,key,eval_str): # return data for a  key
	"""
        
	return all data for the `key` under the condition that the expression in `eval_str` 
	is True.

	"""
	array=[]
        for l in self.select_data_eval(eval_str):
            array.append(l[key])
	return array
    
    def get_data_list(self,keylist, sel_func = None, sel_args = None): 

	"""

	return all the data corresponding to the key list
	as follows::

	   >>> a = df.get_data_list('key1:key2:key3')
           
	   >>> a = df.get_data_list('key1:key2:key3', myfind, ['name','J'])

        return those data where the `name` values contain the character `J`

        *a* contains the list of data

	"""
    
	akey=keylist.split(":")
	dd = []
        if sel_func == None:
            for l in self.data:
                ll=[]
                for i in akey:
                    ll.append( l[i] )
                dd.append(ll)
            return dd
        else:
            for l in self.data:
                if self.check_data(sel_func, l, *sel_args):
                    ll=[]
                    for i in akey:
                        ll.append( l[i] )
                    dd.append(ll)
            return dd

    def get_data_list_eval(self,keylist, eval_str): 
	"""

        similar function as select_data_eval but it only returns the
        values for the keys defined in `keylist`.
        
	"""
	akey=keylist.split(":")
	dd = []

        for l in self.select_data_eval(eval_str):
            ll=[]
            for i in akey:
                ll.append( l[i] )
            dd.append(ll)
        return dd    

    def show_all_data(self):
	"""

	print all data and keys stored

	"""
	for l in self.data:
	    print(l)
    def get_all_data(self):
	"""

	return a list of all data stored

	"""
	return self.data
    def write_complete_header(self,fp):
	"""
	write entire header including comments and internal parameters
	"""
        for i,l in enumerate(self.adata[0:self.headindex]):
            fp.write(l+'\n')
	# write header line
	h = '#! '
	n = 0
	for k in self.keys[:-1]:
	    h = h + k+'['+'%s,%d'%(self.formats[k],n)+']/ '
	    n = n +1
	fp.write(h+'\n')
    def update_header(self,fp):
	"""
       update header line of this data file including format
	"""
	# write header line
	h = '#! '
	n = 0
	for k in self.keys[:-1]:
	    h = h + k+'['+'%s,%d'%(self.formats[k],n)+']/ '
	    n = n +1
	self.adata[headindex]=h
    def write_header(self,fp):
	"""
	write only header line of this data file into file fp, including format
	"""
	# write header line
	h = '#! '
	n = 0
	for k in self.keys[:-1]:
	    h = h + k+'['+'%s,%d'%(self.formats[k],n)+']/ '
	    n = n +1
	fp.write(h+'\n')
    def write_line(self,fp, i):
	"""
	write line i into file fp 
	"""
	l = ''
        # check array boundary
        ndata = len(self.data)
        if (i<0) :
            print('index below lower bound, set to 0')
            i = 0
        if (i>=ndata):
            print('index above upper bound, set to : ', ndata-1)
	for k in self.keys[:-1]:
            format = self.output_format[ self.formats[k] ]
            l = l + format%(self.data[i][k])
	fp.write(l+'\n')
    def write_all(self,fp, complete_header = False):
	"""
	write all data to a file associated to fp

        if complete_header = True include the complete header including all comments
	"""
        if complete_header:
            self.write_complete_header(fp)
        else:
            self.write_header(fp)
	for i in range(len(self.data)):
	    self.write_line(fp, i)
	fp.close()
    #   new function to add a key
    def write_selected(self,fp,index_list, complete_header = False):
        """
        write a new datafile with an identical header but enter only
        those data with an index given in index_list. If the index does not
        exist print a message and skip it.

        if complete_header = True include the complete header including all comments

        """
        if complete_header:
            self.write_complete_header(fp)
        else:
            self.write_header(fp)
	for i in index_list:
            try:
                self.write_line(fp, i)
            except:
                print('cannot write index : ', i, ' does it exist ?')
	fp.close()
        
    def add_key(self,key,format='f'):
        """
        add a new key, this is useful if you want to add new data
        assign new values using a loop like::

        >>> df.add_key('newkey',format='i')

        The new data need to be stored as follows::
        
        >>> for d in df.data:
        >>>     d['newkey']= some_new_value
        
        where df is the datafile and 'newkey' the new key. The new data set 
        can be saved using ``fp = open('new_file','w')`` and ``df.write_all(fp)``
        """
        for d in self.data:
            d[key] = None
        # add the new key at the end of the keys list but before indx 
        self.keys.insert(len(self.keys)-1,key)
        # add the format information
        try:
            fi = self.fmt_characters.index(format)
        except:
            print('unknown format : ', format, ' use f instead')
            format = 'f'
        self.formats[key] =  format
    # end
    def delete_key(self,key):
        """
        remove a key and all values associated with it
        """
        # remove the data for the key
        for d in self.data:
            del d[key]
        # remove the format for this key
        fmt = self.formats.pop(key)
        # now remove the key from the key list
        self.keys.remove(key)
        print('key : ', key , ' and format : ', fmt, ' removed')
    # end

    def add_data(self, keys,line):
        key_l = keys.split(':')
        # check the key list
        key_index=[]
        for k in self.keys[:-1]:  # skip the indx
            try:
                ki = key_l.index(k)
                key_index.append(ki)
            except:
                print(k, ' does not exist !, nothing added')
                return
        # sorht the argumens according to the sequence of the keys
        fline = [line.split(' ')[i] for i in key_index]
        line = ''
        for fl in fline: line += fl+' '
        self.adata.append(line)
        print(line)
        f = self.parse_line(line)
        self.data.append(self.make_dict(self.keys,f) ) 
        
    def add_header_comment(self, text):
        """
        add a comment line to the header. The # at the beginning is automatically added !

        * for a normal comment start with a space
        * to add a parameter start the comment with a \
        """
        self.adata.insert(self.headindex, '#' + text)
        self.headindex += 1
    def save(self, file = None):
        """

        Save the current datafile.
        
        With the keyword: *file* = 'new_file'

        the datafile will be written into the new file name

        """
        if file == None:
            o = open(self.filename,'w')
        else:
            o = open( file, 'w')
        self.write_all(o, complete_header = True)
    
#

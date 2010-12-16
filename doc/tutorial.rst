---------
Tutorials
---------

Tutorial on carray objects
==========================

Creating carrays
----------------

A carray can be created from any NumPy ndarray by using its `carray`
constructor::

  >>> a = np.arange(10)
  >>> b = ca.carray(a)

Now, `b` is a carray object.  Just check this::

  >>> type(b)
  <type 'carray.carrayExtension.carray'>

You can have a peek at it by using its string form::

  >>> print b
  [0, 1, 2... 7, 8, 9]

And get more info about uncompressed size (nbytes), compressed
(cbytes) and the compression ratio (ratio = nbytes/cbytes), by using
its representation form::

  >>> b   # <==> print repr(b)
  carray((10,), int64)  nbytes: 80; cbytes: 4.00 KB; ratio: 0.02
    cparams := cparams(clevel=5, shuffle=True)
  [0 1 2 3 4 5 6 7 8 9]

As you can see, the compressed size is much larger than the
uncompressed one.  How this can be?  Well, it turns out that carray
wears an I/O buffer for accelerating some internal operations.  So,
for small arrays (typically those taking less than 1 MB), there is
little point in using a carray.

However, when creating carrays larger than 1 MB (its natural
scenario), the size of the I/O buffer is generally negligible in
comparison::

  >>> a = np.arange(1e7)
  >>> b = ca.carray(np.arange(1e7))
  >>> b
  carray((10000000,), float64)  nbytes: 76.29 MB; cbytes: 2.57 MB; ratio: 29.72
    cparams := cparams(clevel=5, shuffle=True)
  [0.0, 1.0, 2.0, ..., 9999997.0, 9999998.0, 9999999.0]

You can always get a hint on how much space it takes your carray by
using `sys.getsizeof()`::

  >>> import sys
  >>> sys.getsizeof(b)
  2691754

An interesting possibility is that you can create carrays from scratch
via the `fromiter()` constructor::

  >>> ca.fromiter((i*2. for i in xrange(1000*1000)), dtype="f4")
  carray((1000000,), float32)  nbytes: 3.81 MB; cbytes: 543.63 KB; ratio: 7.19
    cparams := cparams(clevel=5, shuffle=True)
  [0.0, 2.0, 4.0, ..., 1999994.0, 1999996.0, 1999998.0]

that means that you can create very large arrays without the need to
create a NumPy array first (that could not fit in memory) --but you
can achieve the same goal by using the `.append()` method discussed
later on.

Finally, you can get a copy of your created carrays by using the
`copy()` method::

  >>> b.copy()
  carray((10000000,), float64)  nbytes: 76.29 MB; cbytes: 2.57 MB; ratio: 29.72
    cparams := cparams(clevel=5, shuffle=True)
  [0.0, 1.0, 2.0, ..., 9999997.0, 9999998.0, 9999999.0]

and you can control parameters for the newly created copy::

  >>> b.copy(cparams=ca.cparams(clevel=9))
  carray((10000000,), float64)  nbytes: 76.29 MB; cbytes: 1.04 MB; ratio: 73.52
    cparams := cparams(clevel=9, shuffle=True)
  [0.0, 1.0, 2.0, ..., 9999997.0, 9999998.0, 9999999.0]

Enlarging your carray
---------------------

One of the nicest features of carray objects is that they can be
enlarged very efficiently.  This can be done via the `carray.append()`
method.

For example, if `b` is a carray with 10 million elements::

  >>> b
  carray((10000000,), float64)  nbytes: 80000000; cbytes: 2691722; ratio: 29.72
    cparams := cparams(clevel=5, shuffle=True)
  [0.0, 1.0, 2.0... 9999997.0, 9999998.0, 9999999.0]

it can be enlarged by 10 elements with::

  >>> b.append(np.arange(10.))
  >>> b
  carray((10000010,), float64)  nbytes: 80000080; cbytes: 2691722;  ratio: 29.72
    cparams := cparams(clevel=5, shuffle=True)
  [0.0, 1.0, 2.0... 7.0, 8.0, 9.0]

Let's check how fast appending can be::

  >>> a = np.arange(1e7)
  >>> b = ca.carray(a)
  >>> %time b.append(np.arange(1e7))
  CPU times: user 0.11 s, sys: 0.03 s, total: 0.14 s
  Wall time: 0.14 s
  >>> %time np.concatenate((a, np.arange(1e7)))
  CPU times: user 0.11 s, sys: 0.09 s, total: 0.20 s
  Wall time: 0.22 s    # 1.6x slower than carray
  array([  0.00000000e+00,   1.00000000e+00,   2.00000000e+00, ...,
           9.99999700e+06,   9.99999800e+06,   9.99999900e+06])

This is specially true when appending small bits to large arrays::

  >>> b = ca.carray(a)
  >>> %timeit b.append(np.arange(1e1))
  100000 loops, best of 3: 3.17 µs per loop
  >>> %timeit np.concatenate((a, np.arange(1e1)))
  10 loops, best of 3: 64 ms per loop  # 2000x slower than carray

Definitely, appending is one of the strongest points of carray
objects, so do not be afraid to use that feature extensively.

Compression level and shuffle filter
------------------------------------

carray uses Blosc as the internal compressor, and Blosc can be
directed to use different compression levels and to use (or not) its
internal shuffle filter.  The shuffle filter is a way to improve
compression when using items that have type sizes > 1 byte, although
it might be counter-productive (very rarely) for some data
distributions.

By default carrays are compressed using Blosc with compression level 5
with shuffle active.  But depending on you needs, you can use other
compression levels too::

  >>> ca.carray(a, ca.cparams(clevel=1))
  carray((10000000,), float64)  nbytes: 76.29 MB; cbytes: 9.88 MB; ratio: 7.72
    cparams := cparams(clevel=1, shuffle=True)
  [0.0, 1.0, 2.0, ..., 9999997.0, 9999998.0, 9999999.0]
  >>> ca.carray(a, ca.cparams(clevel=9))
  carray((10000000,), float64)  nbytes: 76.29 MB; cbytes: 1.11 MB; ratio: 68.60
    cparams := cparams(clevel=9, shuffle=True)
  [0.0, 1.0, 2.0, ..., 9999997.0, 9999998.0, 9999999.0]

Also, you can decide if you want to disable the shuffle filter that
comes with Blosc::

  >>> ca.carray(a, ca.cparams(shuffle=False))
  carray((10000000,), float64)  nbytes: 80000000; cbytes: 38203113; ratio: 2.09
    cparams := cparams(clevel=5, shuffle=False)
  [0.0, 1.0, 2.0... 9999997.0, 9999998.0, 9999999.0]

but, as can be seen, the compression ratio is much worse in this case.
In general it is recommend to let shuffle active (unless you are
fine-tuning the performance for an specific carray).

See ``Optimization tips`` section for info on how you can change other
internal parameters like the size of the chunk.

Accessing carray data
---------------------

The way to access carray data is very similar to the NumPy indexing
scheme, and in fact, supports all the indexing methods supported by
NumPy.

Specifying an index or slice::

  >>> a = np.arange(10)
  >>> b = ca.carray(a)
  >>> b[0]
  0
  >>> b[-1]
  9
  >>> b[2:4]
  array([2, 3])
  >>> b[::2]
  array([0, 2, 4, 6, 8])
  >>> b[3:9:3]
  array([3, 6])

Note that NumPy objects are returned as the result of an indexing
operation.  This is on purpose because normally NumPy objects are more
featured and flexible (specially if they are small).  In fact, a handy
way to get a NumPy array out of a carray object is asking for the
complete range::

  >>> b[:]
  array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

Fancy indexing is supported too.  Boolean arrays::

  >>> barr = np.array([True]*5+[False]*5)
  >>> b[barr]
  array([0, 1, 2, 3, 4])
  >>> b[ca.carray(barr)]
  array([0, 1, 2, 3, 4])

List of indices::

  >>> b[[2,3,0,2]]
  array([2, 3, 0, 2])
  >>> b[ca.carray([2,3,0,2])]
  array([2, 3, 0, 2])

Querying carrays
----------------

carrays can be queried in different ways.  The most easy, yet powerful
way is using its iterator::

  >>> a = np.arange(1e7)
  >>> b = ca.carray(a)
  >>> %time sum(v for v in a if v < 10)
  CPU times: user 8.02 s, sys: 0.00 s, total: 8.03 s
  Wall time: 8.33 s
  45.0
  >>> %time sum(v for v in b if v < 10)
  CPU times: user 0.89 s, sys: 0.00 s, total: 0.90 s
  Wall time: 0.93 s   # 9x faster than NumPy
  45.0

Also, you can quickly retrieve the indices of a boolean carray that
have a true value::

  >>> barr = ca.carray(a < 10)
  >>> [i for i in barr.wheretrue()]
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

And get the values where a boolean array is true::

  >>> [i for i in b.where(barr)]
  [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]

The advantage of the carray iterators is that you can use them in
generator contexts and hence, you don't need to waste memory for
creating temporaries, which can be important when dealing with large
arrays.

Finally, all these iterators are very fast, so try to express your
problems in a way that you can use them extensively.

Modifying carrays
-----------------

Although it is not a very efficient operation, carrays can be
modified too: You can do it by specifying scalar or slice indices::

  >>> a = np.arange(10)
  >>> b = ca.carray(a)
  >>> b[1] = 10
  >>> print b
  [ 0 10  2  3  4  5  6  7  8  9]
  >>> b[1:4] = 10
  >>> print b
  [ 0 10 10 10  4  5  6  7  8  9]
  >>> b[1::3] = 10
  >>> print b
  [ 0 10 10 10 10  5  6 10  8  9]

and fancy indexing is supported too::

  >>> barr = np.array([True]*5+[False]*5)
  >>> b[barr] = -5
  >>> print b
  [-5 -5 -5 -5 -5  5  6 10  8  9]
  >>> b[[1,2,4,1]] = -10
  >>> print b
  [ -5 -10 -10  -5 -10   5   6  10   8   9]

However, modifying a carray is expensive::

  >>> a = np.arange(1e7)
  >>> b = ca.carray(a)
  >>> %timeit a[2] = 3
  10000000 loops, best of 3: 101 ns per loop
  >>> %timeit b[2] = 3
  10000 loops, best of 3: 161 µs per loop  # 1600x slower than NumPy

although modifying values in latest chunk is somewhat more cheaper::

  >>> %timeit a[-1] = 3
  10000000 loops, best of 3: 102 ns per loop
  >>> %timeit b[-1] = 3
  10000 loops, best of 3: 42.9 µs per loop  # 420x slower than NumPy

So, in general, you should avoid abusing of this feature when using
carrays.

Operating with carrays
----------------------

carrays can be operated pretty easily if you have the Numexpr package
installed::

  >>> a = np.arange(1e7)
  >>> x = ca.carray(a)
  >>> y = ca.eval(".5x**3+2.1*x**2")
  >>> y
  carray((10000000,), float64)  nbytes: 76.29 MB; cbytes: 38.00 MB; ratio: 2.01
    cparams := cparams(clevel=5, shuffle=True)
  [0.0, 2.6, 12.4, ..., 4.9999976e+20, 4.9999991e+20, 5.0000006e+20]

Note how the output of `eval()` is also a carray object.  You can pass
other parameters of the carray constructor too.  Let's force maximum
compression for the output::

  >>> y = ca.eval(".5*x**3+2.1*x**2", cparams=ca.cparams(9))
  >>> y
  carray((10000000,), float64)  nbytes: 76.29 MB; cbytes: 35.66 MB; ratio: 2.14
    cparams := cparams(clevel=9, shuffle=True)
  [0.0, 2.6, 12.4, ..., 4.9999976e+20, 4.9999991e+20, 5.0000006e+20]


carray metadata
---------------

carray implements a couple of attributes, `dtype` and `shape` that
makes it to 'quack' like a NumPy array::

  >>> a = np.arange(1e7)
  >>> b = ca.carray(a)
  >>> b.dtype
  dtype('float64')
  >>> b.shape
  (10000000,)

In addition, it implements the `cbytes` attribute that tells how many
bytes in memory uses the carray object::

  >>> b.cbytes
  2691722

This figure is approximate (the real one is a little larger) and it is
generally lower than the original (uncompressed) datasize can be
accessed by using `nbytes` attribute::

  >>> b.nbytes
  80000000

which is the same than the original NumPy array::

  >>> a.size*a.dtype.itemsize
  80000000

For knowing the compression level used and other optional filters, use
the `cparams` read-only attribute::

  >>> b.cparams
  cparams(clevel=5, shuffle=True)

Finally, you can access the `chunklen` (the length for each chunk) for
this carray::

  >>> b.chunklen
  16384


Tutorial on ctable objects
==========================

The carray package comes with a handy object that arranges data by
column (and not by row, as in NumPy's structured arrays).  This allows
for much better performance for walking tabular data by column and
also for adding and deleting columns.  A small tutorial for its use
follows.

Creating a ctable
-----------------

You can build ctable objects in many different ways, but the easiest
one is using a structured array as data source::

  >>> t = np.fromiter(((i,i*i) for i in xrange(100*1000)), dtype="i4,f8")
  >>> ct = ca.ctable(t)
  >>> ct
  ctable((100000,), |V12) nbytes: 1.14 MB; cbytes: 279.89 KB; ratio: 4.19
    cparams := cparams(clevel=5, shuffle=True)
  [(0, 0.0), (1, 1.0), (2, 4.0), ..., (99997, 9999400009.0),
   (99998, 9999600004.0), (99999, 9999800001.0)]

But in case you don't want to waste memory space for the intermediate
NumPy object, here it is the canonical way, a loop::

  >>> ct = ca.ctable(np.empty(0, dtype="i4,f8"))
  >>> for i in xrange(100*1000):
  ...:    ct.append((i, i**2))
  ...:
  >>> ct
  ctable((100000,), |V12) nbytes: 1.14 MB; cbytes: 355.48 KB; ratio: 3.30
    cparams := cparams(clevel=5, shuffle=True)
  [(0, 0.0), (1, 1.0), (2, 4.0), ..., (99997, 9999400009.0),
   (99998, 9999600004.0), (99999, 9999800001.0)]

However, we can see how the latter approach does not compress as well.
Why?  Well, carray has machinery for computing 'optimal' chunksizes
depending on the number of entries.  For the first case carray can
figure out the number of entries in final array, but not for the loop
case.  You can solve this by passing the final length with the
`expectedlen` argument to the ctable constructor::

  >>> ct = ca.ctable(np.empty(0, dtype="i4,f8"), expectedlen=100*1000)
  >>> for i in xrange(100*1000):
  ...:    ct.append((i, i**2))
  ...:
  >>> ct
  ctable((100000,), |V12) nbytes: 1.14 MB; cbytes: 279.89 KB; ratio: 4.19
    cparams := cparams(clevel=5, shuffle=True)
  [(0, 0.0), (1, 1.0), (2, 4.0), ..., (99997, 9999400009.0),
   (99998, 9999600004.0), (99999, 9999800001.0)]

Okay, the compression ratio is the same now.

Accessing and setting rows
--------------------------

The ctable object supports the most common indexing operations in
NumPy::

  >>> ct[1]
  (1, 1.0)
  >>> type(ct[1])
  <type 'numpy.void'>
  >>> ct[1:6]
  array([(1, 1.0), (2, 4.0), (3, 9.0), (4, 16.0), (5, 25.0)],
        dtype=[('f0', '<i4'), ('f1', '<f8')])

The first thing to have in mind is that, similarly to carray objects,
the result of an indexing operation is a native NumPy object (in the
case above a scalar and a structured array).

Fancy indexing is also supported::

  >>> ct[[1,6,13]]
  array([(1, 1.0), (6, 36.0), (13, 169.0)],
        dtype=[('f0', '<i4'), ('f1', '<f8')])
  >>> ct["(f0>0) & (f1<10)"]
  array([(1, 1.0), (2, 4.0), (3, 9.0)],
        dtype=[('f0', '<i4'), ('f1', '<f8')])

Note that conditions over columns are expressed as string expressions
(in order to use Numexpr under the hood), and that the column names
are understood correctly.

Setting rows is also supported::

  >>> ct[1] = (0,0)
  >>> ct
  ctable((100000,), |V12) nbytes: 1.14 MB; cbytes: 279.89 KB; ratio: 4.19
    cparams := cparams(clevel=5, shuffle=True)
  [(0, 0.0), (0, 0.0), (2, 4.0), ...,
   (99997, 9999400009.0), (99998, 9999600004.0), (99999, 9999800001.0)]
  >>> ct[1:6]
  array([(0, 0.0), (0, 0.0), (0, 0.0), (0, 0.0), (0, 0.0)],
        dtype=[('f0', '<i4'), ('f1', '<f8')])

And in combination with fancy indexing too::

  >>> ct[[1,6,13]] = (1,1)
  >>> ct[[1,6,13]]
  array([(1, 1.0), (1, 1.0), (1, 1.0)],
        dtype=[('f0', '<i4'), ('f1', '<f8')])
  >>> ct["(f0>=0) & (f1<10)"] = (2,2)
  >>> ct[:7]
  array([(2, 2.0), (2, 2.0), (2, 2.0), (2, 2.0), (2, 2.0), (2, 2.0),
         (6, 36.0)],
        dtype=[('f0', '<i4'), ('f1', '<f8')])

As you may have noticed, fancy indexing in combination with conditions
is a very powerful feature.

Adding and deleting columns
---------------------------

Adding and deleting columns is easy and, due to the column-wise data
arrangement, very efficient.  Let's add a new column on an existing
ctable::

  >>> t = np.fromiter(((i,i*i) for i in xrange(100*1000)), dtype="i4,f8")
  >>> ct = ca.ctable(t)
  >>> new_col = np.linspace(0, 1, 100*1000)
  >>> ct.addcol(new_col)
  >>> ct
  ctable((100000,), |V20) nbytes: 1.91 MB; cbytes: 528.83 KB; ratio: 3.69
    cparams := cparams(clevel=5, shuffle=True)
  [(0, 0.0, 0.0), (1, 1.0, 1.000010000100001e-05),
   (2, 4.0, 2.000020000200002e-05), ...,
   (99997, 9999400009.0, 0.99997999979999797),
   (99998, 9999600004.0, 0.99998999989999904), (99999, 9999800001.0, 1.0)]

Now, remove the already existing 'f1' column::

  >>> ct.delcol('f1')
  >>> ct
  ctable((100000,), |V12) nbytes: 1.14 MB; cbytes: 318.68 KB; ratio: 3.68
    cparams := cparams(clevel=5, shuffle=True)
  [(0, 0.0), (1, 1.000010000100001e-05), (2, 2.000020000200002e-05), ...,
   (99997, 0.99997999979999797), (99998, 0.99998999989999904), (99999, 1.0)]

Iterating over ctable data
--------------------------

You can make use of the `iter()` method in order to easily iterate
over the values of a ctable.  `iter()` has support for start, stop and
step parameters::

  >>> t = np.fromiter(((i,i*i) for i in xrange(100*1000)), dtype="i4,f8")
  >>> ct = ca.ctable(t)
  >>> [row for row in ct.iter(1,10,3)]
  [(1, 1.0), (4, 16.0), (7, 49.0)]

Also, you can select specific fields to be read via the `outcols`
parameter::

  >>> [row for row in ct.iter(1,10,3, outcols=['f0'])]
  [(1,), (4,), (7,)]
  >>> [row for row in ct.iter(1,10,3, outcols=['__nrow__', 'f0'])]
  [(1, 1), (4, 4), (7, 7)]

Please note the use of the special '__nrow__' label for referring to
the current row.

Iterating over output of conditions along columns
-------------------------------------------------

One of the most powerful capabilities of the ctable is the ability to
iterate over the rows whose fields fulfill some conditions (without
the need to put the results in a NumPy container, as described in the
"Accessing and setting rows" section above).  This can be very useful
for performing operations on very large ctables without consuming lots
of memory.

Here it is an example of use::

  >>> t = np.fromiter(((i,i*i) for i in xrange(1000*1000)), dtype="i4,f8")
  >>> ct = ca.ctable(t)
  >>> [row for row in ct.where("(f0>0) & (f1<10)")]
  [(1, 1.0), (2, 4.0), (3, 9.0)]
  >>> sum([row[1] for row in ct.where("(f1>10)")])
  3.3333283333312755e+17

And by using the `outcols` parameter, you can specify the fields that
you want to be returned::

  >>> [row for row in ct.where("(f0>0) & (f1<10)", ["f1"])]
  [(1.0,), (4.0,), (9.0,)]

You can even specify the row number fulfilling the condition::

  >>> [row for row in ct.where("(f0>0) & (f1<10)", ["f1", "__nrow__"])]
  [(1.0, 1), (4.0, 2), (9.0, 3)]

Performing operations on ctable columns
---------------------------------------

The ctable object also wears an `eval()` method that is handy for
carrying out operations among columns::

  >>> ct.eval("cos((3+f0)/sqrt(2*f1))")
  carray((1000000,), float64)  nbytes: 7.63 MB; cbytes: 2.21 MB; ratio: 3.45
    cparams := cparams(clevel=5, shuffle=True)
  [nan, -0.951363128126, -0.195699435691, ...,
   0.760243218982, 0.760243218983, 0.760243218984]

Here, one can see an exception in ctable methods behaviour: the
resulting output is a ctable, and not a NumPy structured array.  This
is so because the output of `eval()` is of the same length than the
ctable, and thus it can be pretty large, so compression maybe of help
to reduce its memory needs.
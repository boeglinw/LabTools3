.. _box:

=======
box
=======

.. automodule:: LT.box

Box Content:

   * :func:`~LT.box.get_file`
   * :func:`~LT.box.get_data`
   * :func:`~LT.box.get_spectrum`
   * :class:`~LT.box.histo`
   * :class:`~LT.box.histo2d`

----------------------------

.. autofunction:: LT.box.get_file

----------------------------

.. autofunction:: get_data

----------------------------

.. autofunction:: get_spectrum

----------------------------

.. autoclass:: histo
   :members:

----------------------------
      
.. autoclass:: histo2d
   :members:


Histogram Operations
--------------------

The following operations are defined for Histograms (1-D and 2-D)
(:class:`~LT.box.histo` ):

.. sourcecode:: ipython

    In [1]: hr = h1 + h2        #  addition
    In [2]: hr = h1 - h2        # subtraction
    In [3]: hr = 2.*h1          # mutiplication by a number
    In [4]: hr = 5.5*h1 - 2.*h2 # combination of the above

**Note**: When adding histograms they need to be of the same type (the
  same number of bins, same bin-center values). Labels and titles are
  not copied.



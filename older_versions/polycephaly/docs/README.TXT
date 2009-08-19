==============
    RuXXer
==============

What is RuXXer:
---------------
    RuXXer is a C-like language designed specifcally for 
protocol replication and fuzzing. It is designed specifically
for the rapid construction, mutation, and delivery of complex datatypes.
Using protocol definitions written in RuXXer, using its
proprietary datatypes, it can automatically generate and 
execute test cases.  The power of Ruxxer is in its
ability to intelligently and rapidly generate many mutations
of data structures, with limited resources.
However, it is not entirely necessary to write directly
in Ruxxer. Ruxxer, can also be leveraged as a "fuzzing framework"
by developing in Python to the Ruxxer API.


How Does Ruxxer Compare to the Other "Really Good" Fuzzers:
----------------------------------------------------

    There is definitely a inverse relationship between
"time saving usability" and "extensibility/power".
Fuzzes are so niche, that there isnt currently a single
protocol aware fuzzer that marries the ease of data structure
construction with really good and deep programmatic a`
There are only really two powerful "protocol aware"
fuzzers currently available that are really worth mention: Peach
and Sulley.

    Peach
        Peach leverages the power of a GUI to represent
    the heirarchy of abstract datatypes. It makes the 
    construction of complex datastructures very simple. Its shortcoming
    however that it doesnt offer very much programmatic access to 
    the structures that it generates. This is absolutely critical 
    when describing complex protocols and grammars.

    Sulley
        Sulley is a powerful API-based Framework that offers 
    a powerful and extensible way to construct protocol definitions.
    With all the strengths and considerations made within the Sulley
    Object Model the logic in the engine responsible for generating
    test cases is VERY atrophied and leaves much to be desired.

    Ruxxer
        Ruxxer leverages the strengths of a "framework" like Sulley
    with the GUI representation and data modeling of Peach, but 
    also exposes an extremely simple scripting and modeling language
    that keeps with the spirit of simplicity and time-saving.
    Furthemore, Ruxxer applies use some core tenets of "Set Theory"
    within the engine to intelligently generate mutations
    of the data modeled in the language.
        Because of the native language it is written in (Python)
    Ruxxer is open-source, and because of the way it's been
    architected (with extensibility in mind) Ruxxer can be leveraged
    as a API based Framework. However because Ruxxer includes
    a very simple and primitive language to sit on top of the API
    it is MUCH easier to use.
        All this core logic is contained and leveraged through an IDE 
    which also serves as the interpreter for the Ruxxer scripting language.
    And to make life even easier, Ruxxer is distributed bundled as a
    "single executable".

Writing RuXXer Code:
--------------------
    Underlying the language are special RuXXer objects
that make rapid prototype and test case generation possible.
(You may use these if you wish to develop directly in Python)
These objects are two major categories:

    * Primitives
    * Structures

PRIMITIVES:
Primitives are the basic building blocks of RuXXer sessions
and protocol definitions. They are declared in C-style
type definitions:

    <type> <name>

For Example:

    string emailaddy
    emailaddy = "person@place.com"

They exist as the more basic/standard types you may be familiar
with, such as: 

    * Short
    * Long
    * Double
    * Char
    * String

The extensibility of Ruxxer (under the hood) allows for easy creation
of new abstract primitives. Examples of these are:

    * EmailAddr
    * Hostname
    * Gzdata
    * Long_lc
    * Short_lc
    * Double_lc

    The strength and power of RuXXer is in these abstracted datatypes that
are offered through the Ruxxer language as primitives.
You undoubtedly noticed the types ending in "_lc". These types are 
specific examples of the power of RuXXer. These types are special
"length calculator" types. Anyone familiar with protocol replication
, file formats, or protocol analysis understands that length
calculators are the most fundamental type of "metadata". RuXXer
offers these "_lc" types as special primitives that derive their value from
the length of another variable instance. For example, consider the following
snippet of RuXXer code:
    
    string blingin
    blingin = "This is a test."
    short_lc bling_len
    bling_len = blingin

In this case,  bling_len's value is 15 (not including null) and is stored
as a short. if a "long_lc" was used in place of "short_lc" in the example
above, the value 15 would be stored as a long.

STRUCTURES:
    As mentioned early on in this section, the second most important 
object in the Ruxxer object model is the Structure. Structures are just
storage containers for Primitives. They can contain any number of 
Primitives or other Structures, and as such are the oject that
makes the building of complex data types possible.
    
Declaration:
    structure blingin

Once you have declared your structure type, you can then begin adding
data to it. This is done like so:

Adding Data to a Structure:

    int test_int;
    long test_long;
    short test_short;
    structure blingin; 

    push(blingin, test_int);
    push(blingin, test_long);
    push(blingin, test_short);
    #--- Or you can do this all at once:
    #push(blingin, test_int, test_long, test_short);

*** Keep in mind that Structures can only contain declared primitives and 
other Structures.

For all intents and purposes, Structures act logically like FILO queues.
While we use the term "push" to add data into them,
there is no functional reason to "pop" from them. You may however want to change
a value within a structure after you have added it. You may do this by referring
to the field within that structure by the name you used to push it in
previously:

Setting data in a structure by name:
    set(blingin, test_int, 0x77777777);

in C-speak this might be logically similar to:

    blingin.test_int = 0x77777777;
or:
    blingin->test_int = 0x77777777;

    Ruxxer being a simple and easy to use language, there is no difference between
variable definition and variable instances. Thus, there is no concept of
user definable "typedef"s. In this way, unlike C, you dont "define" a strucure
type naming fields in it. Instead you simply create the strucure, and the act of
pushing data into it achieves this for you. (It is also important to note that presently 
Ruxxer maintains all variable names and such within the same namespace even
though a Primitive may have been pushed into Structure, it technically exists
within the global namespace!)

Putting it Together So Far:
---------------------------
    Now that we have reviewed the most basic Ruxxer objects, we can now use 
Primitives and Structures to build something resembling a more real-world
protocol definition. We can define a simple Type-Length-Value protocol 
strucure something like this:
   
    #declaration 
    short typeval;
    string datafield;
    short_lc structlen;
    structure tlvpacket;
  
    #assignment
    typeval = 0xFFEE #something the protocol knows
    datafield = "This is a buncha data that is held within this field."
    structlen = tlvpacket;

    #build our structure 
    push(tlvpacket, typeval, datafield, tlvpacket);
      
    Thats it! The magic of the length calculator primitives combined with
Structures make it such that even if you were to dynamically change the size of 
data within the strucure like so:

    set(tlvpacket,datafield,"This is a test...")

You would never have to "update" the length calculator field. By resetting
the "structlen" field inside the "tlvpacket" structure. It effectively "autoupdates".
This saves quite a bit of time especially when buildng more complex protocols. This a 
fundamental example of the power of having a language on top of a fuzzing
framework. 

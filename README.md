Ruxxer: Fuzzing Framework
=====

Ruxxer is a fuzzing Framework that has been in development since 2006. It is still
actively used by Xipiter. You can reach the main tree at [the Ruxxer main repository](http://www.ruxxer.com)

It was relased publicly at PacSec 2007 (the same conference that Peach Fuzzer was released at).
It has not been maintained for public use although it is publicly available. 

The easiest thing for folks to start with is [Blitzer](https://github.com/s7ephen/Ruxxer/blob/master/blitzer/blitzer.py) which uses the basiccombinatorics engine in Ruxxer to iterate through a file fuzzing it at a byte level. It can generate all the permutations (mutations)
of the file on the filesystem or serve them back to a browser using it's build-in webserver. This minor tool alone has found a handful
of browser vulns. Ruxxer (the polycephaly branch) has been used to privately find many more bugs.


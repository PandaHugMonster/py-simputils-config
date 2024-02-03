# Disclaimers


## Potential package collision 2024
Developer of this project has nothing to do with `simputils` package of pypi.
And installation of both might cause broken code.

On the end of this project, the namespace `simputils` is made "shareable".
But the structure of another developer's package is not designed in such way

----

I was developing PHP package [spaf/simputils](https://github.com/PandaHugMonster/php-simputils).
And was carefully choosing name to avoid collisions on both PHP and Python, 
because I was planning to implement set of utils not only for PHP, but similar (not the same)
functionality/framework for python as well.

Recently I implemented this project, naively, assuming that nobody used that `simputils` 
prefix/namespace in pypi at this point.
But sadly, shortly after pushing first release, I realized about the collision, 
and have no opportunity to fix it at this point.

I will try to find another way to fix it in the future, but right now I don't have a solution
for that. 

I was thinking to contact the developer, but I don't have suitable means of communication
with them, and the design of their package is very much incompatible with this one and further
libraries of the series I'm planning to implement. 
So no solution at this point for that.

Neither their, nor mine packages are very much used at this point, so there are some
very thin chances that our packages will be used simultaneously anyway.

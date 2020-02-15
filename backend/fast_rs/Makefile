INCLUDEDIRS := -I.
INCLUDEDIRS += -I$(shell pg_config --includedir-server)
INCLUDEDIRS += -I$(shell pg_config --includedir)
LIBDIR = -L$(shell pg_config --libdir)
LIBINSTALL = $(shell pg_config --pkglibdir)

rs.so: rs.c Makefile
			gcc -fpic -o rs.o -c rs.c $(INCLUDEDIRS)
			gcc -shared -o rs.so rs.o $(LIBDIR) -lpq -lm
			cp rs.so $(LIBINSTALL)